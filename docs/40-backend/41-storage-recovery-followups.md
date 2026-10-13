# 存储追问诊所：未知提交、重放顺序与旧写保护

[后端目录](README.md) · [主学习路线](../00-guide/expanded-map-and-study-plan.md#topic-map) · [源码与29项测试](../../examples/interview_followups/README.md)

先读[B21–B35](02-databases-and-sql.md#b21)、[Redis基础](03-redis-and-caching.md)、[消息与幂等](04-messaging-and-idempotency.md)、[分布式租约](34-distributed-systems-details.md#fb54)。按教学情境画出提交、重放与过期写入的失败窗口。

配套实验执行 SQLite 本地事务、文件重开和内存状态模型；MySQL、Redis、Kafka 及真实断电、杀进程恢复尚未验证。一手结论按MySQL8.4、Kafka4.0系列API和核验日2026-10-11的Redis文档限定。

<a id="storage-unknown-outcome"></a>
## 1. 客户端超时，为什么不能立即换个ID重做

**起手问：** 库存扣减接口超时，客户端重试，怎样确保库存没扣两次？

先把结果分类：确定未接纳、确定失败且未提交、确定已提交、未知是否提交。网络断开通常只告诉你没拿到回复。服务端可能已经提交，只是回复丢失。对未知结果，沿用同一业务操作身份查询或安全重试，不重新生成“这次重试”的身份。[AWS幂等API](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

**实验时间线：** `Store.apply`在同一个SQLite事务中记录(tenant,key,payload)、库存变化及outbox；`after_commit`在提交之后抛UnknownOutcome。重复相同tenant/key/delta返回原结果，库存不再变化。相同身份却换delta会拒绝，而不是假装相同操作。

**继续追问：返回原quantity，是否就是当前库存？** 不是。它是该命令完成时的收据；后续命令可能已经改变库存。查询当前状态与重放原响应是两个API合同，不能混用。测试在另一命令完成后再次重放旧命令，检查原收据不变。

**身份还要讲清：** 租户范围、规范化参数、保留期限、并发冲突和敏感字段。示例用无歧义JSON身份求摘要，不把`tenant + ':' + key`当永远无碰撞的编码；数据库唯一约束仍检查事件身份冲突。示例保留全部命令，生产必须设计空间上限与到期后重放语义。

<a id="storage-outbox-recovery"></a>
## 2. Outbox会重复，怎样把重复变成可恢复事实

写业务后再发MQ存在双写窗口。Outbox把业务和待发送事件放进同一个本地事务，但发布到MQ之后、标记sent之前仍可能崩溃。因此它不是去重器，更不是外部副作用恰好一次证明。[AWS Outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

**具体状态表：** 未提交→业务与事件都不存在；已提交待发→可继续投递；发出但未标记→允许重复投递；已确认标记→按清理政策归档。不能把“写了outbox”直接显示为“下游已处理”。`test_fault_after_effect_rolls_back`与`test_fault_after_event_rolls_back`验证两种本地提交前异常；`test_outbox_mark_and_duplicate_delivery`验证重复投递后效果只改变一次。

Inbox把event_id与本地效果放在同一SQLite事务中。若在效果后、事务提交前失败，二者都回滚，下一次可以重新处理。若email、支付或其他远端副作用已经发生，本地rollback不能撤销它；仍须远端幂等合同、结果查询和对账。

**追问：清理完去重表，旧消息又来了？** 正确性依赖保留窗口。结合最大可重放时间、事件归档、备份恢复与操作身份设计，不能只按“七天省空间”随手删。监控outbox最老待发年龄和inbox冲突，而不仅是消息数量。

<a id="storage-offset-frontier"></a>
## 3. 并行消费时，提交最大的完成offset为什么会漏处理

**原创反例：** 同一分区交付100、101、102；102先成功，100随后成功，101仍在运行。如果提交到103，重启就可能跳过未成功的101。应跟踪每个分区**已交付记录序列中的连续完成前缀**，只推进安全恢复边界，不能用最大完成值。

配套`OffsetPrefix`故意只模型化连续整数offset：先完成102仍返回100；完成100返回101；完成101才返回103。对0–4的全部120种完成排列逐步检查前缀。这是五个记录的有限穷举，不是一般正确性证明。

**关键追加追问：实际Kafka的offset一定连续吗？** 不保证，压缩日志和事务等会出现跳号。真实实现必须依据poll实际交付的记录及下一恢复位置管理frontier，不能等一个从来没有交付的整数。官方提交API要求使用下一待处理记录的位置，也提供`ConsumerRecords.nextOffsets()`等元数据；本模型不能直接替换KafkaConsumer。[Kafka4.0系列Consumer API](https://kafka.apache.org/40/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html)

**继续追问：重平衡时旧worker晚完成？** 分区所有权改变后不能让旧任务推进新持有者的位点。给本地分配生命周期关联epoch，停止旧任务接纳、按预算等待或取消，并把提交与当前分配核对。KafkaConsumer本身的线程安全与poll节奏也要按客户端合同组织，不让任意worker随手调用它。

**资源边界：** 如果前面一个任务永远失败，后面完成集合会持续增大。示例设置max_pending并拒绝继续扩大；实际服务应暂停该分区新分发、隔离失败事件或明确顺序降级政策，不能无限攒结果，也不能悄悄跳过。

<a id="storage-fencing-resource"></a>
## 4. Redis锁已经过期，为什么解锁正确仍会写错

分开两种保护：随机所有者token防止A删除B的锁；单调fencing token让资源端拒绝恢复后的旧执行者。前者不是后者。A获取41后暂停，B获取42并提交，A恢复后提交41，若资源端只检查“你曾获得过锁”，仍会被覆盖。[Redis锁模式及假设](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)

`FencedValue`以资源端最高token拒绝旧写，相同token相同操作可重放，相同token不同内容冲突。它不负责生成token，也不是Redis锁实现。生产需要一个能提供正确单调身份的权威分配机制，并把检查与效果放入资源的同一原子边界；多个进程各自在内存自增不成立。

**追问：token重启归零？跨资源共用？** 说明身份作用域、持久化和恢复。若资源端也丢了最高token，旧写保护失效；若不同资源误用同一比较状态，可能错误拒绝合法请求。看门狗续租可以改善活跃持有者续期，不会把网络暂停和进程恢复问题全部消除。

<a id="storage-cache-version-floor"></a>
## 5. 更新后删缓存，为何旧查询还会把旧值填回来

**时间线：** R读取数据库v1→W提交v2并删缓存→R把v1写回。只盯写路径会漏掉正在飞行的读路径。允许短暂陈旧时可用TTL和重试修复；严格不回填旧版本时需要读值携带权威版本，在写入缓存时与版本底线比较。

`VersionFloorCache`记录不下降的floor：先得知v2，再拒绝v1；乱序v1失效通知不能降低v3底线；同版本不同值是冲突。示例128个key后明确拒绝扩展，**不静默淘汰floor**。floor消失而旧读仍在路上，会重新开放旧写窗口。

**继续追问：floor放在缓存里，缓存被逐出或重启呢？** 本例是内存教学模型，没有证明恢复一致性。生产需要分析floor的权威来源、保留期限、epoch及更新/填充原子性，或接受并声明可控陈旧窗口。删除数据还需独立墓碑策略；这里不把普通invalidation等同于永久删除。方案选择由业务一致性要求决定，不能声称一个Lua脚本解决所有跨DB竞争。

<a id="storage-lock-retry"></a>
## 6. MySQL死锁与锁等待超时，重试范围一样吗

不一样。MySQL8.4中死锁可回滚整个事务，应重新执行完整事务；锁等待超时默认回滚当前语句，配置`innodb_rollback_on_timeout`会改变范围。驱动、框架可能再做额外处理，必须检查当前事务是否已rollback-only或应主动回滚，不能直接从“异常发生”推出“此前写入都没了”。[InnoDB错误处理](https://dev.mysql.com/doc/refman/8.4/en/innodb-error-handling.html)

**双事务演练，未在MySQL执行：** T1按A→B更新，T2按B→A更新。画出持有与等待的环，选择统一访问顺序、合适索引、短事务和有界完整重试。索引会改变扫描与锁范围；按唯一索引定位已有单行与范围扫描不能混为一谈。[锁类型](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html) · [死锁处理](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks-handling.html)

**追问：串行化隔离就没有死锁？** 隔离级别不是“禁止等待环”的开关。即使设计降低概率，也要保留重试、错误分类和监测。重试整段事务时，段内不能包含已不可撤销的远端动作。

## 复验与口述验收

```bash
python3 -B -m unittest discover -s examples/interview_followups -p test_storage_lab.py -v
```

[storage_lab.py](../../examples/interview_followups/storage_lab.py) · [test_storage_lab.py](../../examples/interview_followups/test_storage_lab.py)。29个测试方法分为14个SQLite事务/Inbox场景、5个有限frontier场景、4个fencing场景、6个缓存floor场景。参数循环和120种排列不另外膨胀测试计数。

每个回答最后补三句话：我的权威状态在哪里；未知结果如何查；崩溃/重复/旧worker回来时哪个原子边界仍成立。性能、实际断电耐久、MySQL锁、Redis故障转移和Kafka重平衡均需真实目标环境另测。[验证边界](../../coverage/INTERVIEW_FOLLOWUPS_VALIDATION.md)
