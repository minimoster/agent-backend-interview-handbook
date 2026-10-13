# 消息队列：语义、复制与失败恢复

[返回总目录](../../README.md) · [题目索引](../../QUESTION_INDEX.md) · [版本与纠错](../../errata/README.md)

官方资料核查于2026-10-09。示例参数用于教学推演，代码、SQL 与实验的执行情况在对应题中标注。

- [FB01 如何比较 Kafka、RocketMQ 和 RabbitMQ，而不背吞吐排行榜](#fb01)
- [FB02 多副本为什么仍可能丢写或暂停服务](#fb02)
- [FB03 如何把消息可靠性拆成可验证的三个交接点](#fb03)
- [FB04 Kafka 为什么吞吐高，什么情况下优化会失效](#fb04)
- [FB05 按业务键有序与生产者幂等各保证到哪一层](#fb05)
- [FB06 死信、延后重试与优先级为什么不能混为一谈](#fb06)
- [FB07 RocketMQ 半消息回查应查询什么事实](#fb07)
- [FB08 mmap 与 sendfile 的数据路径如何解释](#fb08)
- [FB09 订单超时关闭如何使用定时消息与 TTL](#fb09)

<a id="fb01"></a>

### FB01 如何比较 Kafka、RocketMQ 和 RabbitMQ，而不背吞吐排行榜

**优先级：P0**

**知识点详解**：先确定工作负载：事件留存与重放、单键顺序、任务路由、定时投递、业务事务衔接、跨可用区恢复。Kafka 的分区日志与多消费组适合可重放事件流；RocketMQ 的业务消息类型便于表达事务和定时投递；RabbitMQ 的 exchange 与 routing key 适合灵活路由。三者都要配置确认、复制、限额和监控。拉取可以长轮询，不能推导“拉必然慢”。性能应在相同消息大小、持久化、确认、复制和延迟目标下测量。

**具体例子**：日志管道需要保留七天并允许多个团队重放，可优先验证 Kafka；订单关闭需要延时触发，可验证 RocketMQ 定时消息或调度表。这里是选型假设，不是已经得到的压测结论。

**面试答法**：我先列功能约束和故障容忍，再用候选产品实现同一小样本链路。比成功吞吐时同时看 p99、重复率、积压恢复时间与运维成本。

**追问**：同样十万条/秒为什么不能直接比较？若一个关闭持久化、另一个跨区多数确认，测到的不是同一承诺。

**常见误区**：把某产品固定说成百万 TPS；把“没有内建业务死信队列”说成不能建立失败主题；为了履历热词同时引入三种 MQ。

**来源**：[FB-S001 Kafka 4.0 设计与交付语义](https://kafka.apache.org/40/design/design/)、[FB-S004 RabbitMQ Quorum Queues](https://www.rabbitmq.com/docs/quorum-queues)、[FB-S007 RocketMQ 5.x 事务消息](https://rocketmq.apache.org/docs/featureBehavior/04transactionmessage/)、[FB-S008 RocketMQ 5.x 定时消息](https://rocketmq.apache.org/docs/featureBehavior/02delaymessage/)。

<a id="fb02"></a>

### FB02 多副本为什么仍可能丢写或暂停服务

**优先级：P0**

**知识点详解**：复制策略、选主资格与确认条件必须一起解释。Kafka 的 acks=all 等待当前 ISR 的规定确认，min.insync.replicas 给出允许写入的最小同步副本门槛，不等于等待所有配置副本，更不等于每条都 fsync。RabbitMQ 4.0 已移除经典镜像队列；quorum queue 依赖多数成员；RocketMQ 4.x DLedger 是 Raft 日志复制部署。多数派系统只剩任意一台不能据此继续写。切换会带来错误、重试、短暂不可用和结果不确定。Kafka 的机架感知副本读取配置也意味着“消费者永远只读 leader”不成立。

**具体例子**：三副本 Kafka 设置最小 ISR 为 2，一台掉线仍可能写；仅剩一个 ISR 时应拒绝要求该门槛的写入。若放宽门槛或允许不干净选举，故障后的数据风险随之变化。

**面试答法**：我分别回答哪一步叫成功、允许丢多少已确认数据、缺哪些副本时停止写，再谈客户端重试和幂等。

**追问**：为什么三副本与三个故障域不是一回事？放在同一主机或同一电源域会共同失败。

**常见误区**：多副本等于绝不丢；主从切换对客户端完全透明；把历史经典镜像队列当作现代 RabbitMQ 的通用推荐。

**来源**：[FB-S002 Kafka 4.0 生产者配置](https://kafka.apache.org/40/configuration/producer-configs/)、[FB-S003 Kafka 4.0 Broker 配置](https://kafka.apache.org/40/configuration/broker-configs/)、[FB-S004 RabbitMQ Quorum Queues](https://www.rabbitmq.com/docs/quorum-queues)、[FB-S009 RocketMQ 4.x DLedger](https://rocketmq.apache.org/docs/4.x/bestPractice/02dledger/)、[FB-S077 RabbitMQ 经典镜像队列移除说明](https://www.rabbitmq.com/docs/3.13/ha)。

<a id="fb03"></a>

### FB03 如何把消息可靠性拆成可验证的三个交接点

**优先级：P0**

**知识点详解**：生产端必须区分尚未发送、已发送未确认、确认成功。未确认可能已经写入，重试需要稳定业务 ID。Broker 层分别核查复制确认与刷盘策略，不能从“同步发送”推断两者都同步。消费端业务完成后才确认；对数据库写入，用事务把去重记录与业务变化绑定。Kafka 提交 offset 记录消费进度，不触发逐条删除；RabbitMQ ACK 表示队列投递已完成，其数据清理模型不同。

**具体例子**：订单事件发送超时，应用保存“发布结果待确认”，用原 event_id 重发。消费者首次提交订单事务后崩溃，重放命中 event_id 唯一约束并返回已有结果。应测试四个崩溃点，而不只看正常路径。

**面试答法**：我画生产者、Broker、消费者三段，每个 ACK 都说明它承诺的是接收、复制、持久化还是业务完成。最后补重试、幂等和对账。

**追问**：确认返回成功后仍丢数据怎么办？检查该确认的故障假设、磁盘与副本相关故障，以及是否有权威业务流水可恢复。

**常见误区**：所有 MQ 都用“关闭自动提交”一句配置；同步调用就是同步落盘；消息堆积只监控条数而不监控最老消息年龄。

**来源**：[FB-S001 Kafka 4.0 设计与交付语义](https://kafka.apache.org/40/design/design/)、[FB-S002 Kafka 4.0 生产者配置](https://kafka.apache.org/40/configuration/producer-configs/)、[FB-S004 RabbitMQ Quorum Queues](https://www.rabbitmq.com/docs/quorum-queues)、[FB-S007 RocketMQ 5.x 事务消息](https://rocketmq.apache.org/docs/featureBehavior/04transactionmessage/)。

<a id="fb04"></a>

### FB04 Kafka 为什么吞吐高，什么情况下优化会失效

**优先级：P1**

**知识点详解**：把开销按存储、系统调用、网络与并行度拆开：日志追加减少随机写；页缓存利用最近数据；批量摊薄每条请求开销；压缩减少传输字节；分区分摊生产与消费。一个分区由滚动日志段及索引组成，不是一个永不切分的文件。批次越大可能越省资源，也会提高等待延迟。Kafka 4.0 官方设计说明：启用 TLS 的路径不使用该文所述 sendfile 优化，因此不能把所有部署都画成同一拷贝次数。

**具体例子**：消息从 100 B 改为 1 MB，瓶颈可能由请求数转成网卡、复制带宽与内存。应同时测 records/s、MB/s、批大小、压缩 CPU、p99 与积压。

**面试答法**：我不先报 TPS，而是解释每个机制节省什么成本，再用瓶颈指标验证它是否在当前配置生效。

**追问**：分区越多越快吗？元数据、文件句柄、恢复与重平衡成本会增长，热点键也可能仍在一个分区。

**常见误区**：顺序写完全不需要磁盘；批量没有延迟成本；零拷贝在加密路径无条件成立。

**来源**：[FB-S001 Kafka 4.0 设计与交付语义](https://kafka.apache.org/40/design/design/)、[FB-S002 Kafka 4.0 生产者配置](https://kafka.apache.org/40/configuration/producer-configs/)、[FB-S010 Linux sendfile(2)](https://man7.org/linux/man-pages/man2/sendfile.2.html)。

<a id="fb05"></a>

### FB05 按业务键有序与生产者幂等各保证到哪一层

**优先级：P0**

**知识点详解**：同一聚合键进入同一分区，才能得到该日志内的顺序。应用还要控制多生产者的先后关系、并发重试、消费者并行与重平衡。幂等生产者依靠 producer id、epoch 及分区序列识别协议范围内的重复批次，并非按业务内容去重。Kafka 4.0 的启用条件还关联 acks、retries 和 max.in.flight.requests.per.connection。事务可扩大 Kafka 内的原子范围，但外部数据库仍需自己协调。

**具体例子**：同一订单的“创建→取消”进入同一分区，消费者却把两个事件交给不同线程；取消先完成就破坏业务序。可按订单串行队列处理，或在数据库以版本号拒绝旧事件。

**面试答法**：我先定义顺序单位，再逐段证明生产、分区、消费和落库都尊重它。生产者幂等防协议重试重复，不替代订单唯一约束。

**追问**：失败事件能不能直接送死信再处理下一条？若后续事件依赖它，必须冻结该键、补偿或证明可交换，而非默认跳过。

**常见误区**：扩分区后同一键仍永远路由原分区；相同消息体必被自动合并；只设置 key 就保证数据库更新顺序。

**来源**：[FB-S001 Kafka 4.0 设计与交付语义](https://kafka.apache.org/40/design/design/)、[FB-S002 Kafka 4.0 生产者配置](https://kafka.apache.org/40/configuration/producer-configs/)。

<a id="fb06"></a>

### FB06 死信、延后重试与优先级为什么不能混为一谈

**优先级：P0**

**知识点详解**：死信是投递或处理失败后的隔离路径，优先级是正常工作调度顺序。RabbitMQ 的拒绝且不重新入队、TTL 到期、队列长度限制等可触发 dead lettering，但具体溢出行为依 queue type 和 overflow 策略，不能统一说“新消息进死信”。保留原业务 ID、失败原因、版本、次数与首次失败时间；隔离区也要限额。重放需鉴权、可审计、幂等，并阻止原队列与死信交换机循环。

**具体例子**：金额字段格式不合法，重复三千次不会恢复；隔离后修正解析器，在小批量灰度重放中检查成功率。依赖暂时超时则使用带抖动的有限重试，避免把可恢复失败都变人工工单。

**面试答法**：我分清永久错误、暂时错误和未知结果，为三类设置不同路径，并给失败消息明确所有者和处理期限。

**追问**：死信投递本身失败呢？核对队列类型支持的安全交接模式，监控源与目标，不把“配置了 DLX”当作投递绝不丢的证明。

**常见误区**：死信等于业务优先级；无限重放；只统计死信总数而不追最老未处理失败。

**来源**：[FB-S005 RabbitMQ Dead Letter Exchanges](https://www.rabbitmq.com/docs/dlx)、[FB-S006 RabbitMQ TTL](https://www.rabbitmq.com/docs/ttl)、[FB-S004 RabbitMQ Quorum Queues](https://www.rabbitmq.com/docs/quorum-queues)。

<a id="fb07"></a>

### FB07 RocketMQ 半消息回查应查询什么事实

**优先级：P1**

**知识点详解**：半消息暂不可见；生产端执行本地事务后，按实际提交结果决定 commit 或 rollback。第二阶段通知缺失时，Broker 回查生产者。回查逻辑必须查询持久业务事实，不能依赖进程内布尔变量，也不能用“刚才请求超时”推定回滚。此机制协调本地事务与消息可见性，消费端成功、跨服务强一致和外部扣款不由它自动保证。

**具体例子**：创建订单事务同时记录 transaction_id 与 COMMITTED 状态。回查按 transaction_id 读取主库或满足一致性要求的数据源；若事务仍处理中返回 Unknown 并遵守回查期限，不能立即把“未看到记录”当成确定不存在。

**面试答法**：我重点讲回查的数据源、事务状态机与超时上限，说明它是最终一致方案，消费者仍然需要幂等和补偿。

**追问**：回查请求到另一台实例怎么办？实例应能访问相同持久事务事实，不能只在最初生产者内存里保存状态。

**常见误区**：事务消息相当于跨所有服务的 ACID；示例里固定 return true 可以上线。

**来源**：[FB-S007 RocketMQ 5.x 事务消息](https://rocketmq.apache.org/docs/featureBehavior/04transactionmessage/)。

<a id="fb08"></a>

### FB08 mmap 与 sendfile 的数据路径如何解释

**优先级：P1**

**知识点详解**：传统 read 后 write 会让数据经过用户缓冲区。sendfile 将文件描述符之间的数据转移放在内核内，减少用户态往返复制；仍存在设备读写、缓存与 DMA 等数据移动。mmap 把文件区间映射到进程虚拟地址，按需缺页后可直接访问映射，但后续发送和加密仍可能复制。它既可映射小文件，也可按窗口处理大文件。两者优化不同路径，不能只背固定“几次复制几次切换”。

**具体例子**：静态文件转发且不改内容可评估 sendfile；随机读取索引页可评估 mmap。若应用需要逐字节解密再重编码，优化前必须先画出这一步在哪里执行。

**面试答法**：我画磁盘、页缓存、用户空间与网卡四处，说明减少哪次 CPU 搬运，并列出 TLS、硬件和内核版本的限制。

**追问**：sendfile 一次一定传完吗？不一定，调用方仍要处理短写、非阻塞 EAGAIN 与剩余偏移。

**常见误区**：零拷贝等于没有任何物理数据移动；mmap 自动保证修改已持久化；映射大文件必须一次占用等量物理内存。

**来源**：[FB-S010 Linux sendfile(2)](https://man7.org/linux/man-pages/man2/sendfile.2.html)、[FB-S011 Linux mmap(2)](https://man7.org/linux/man-pages/man2/mmap.2.html)。

<a id="fb09"></a>

### FB09 订单超时关闭如何使用定时消息与 TTL

**优先级：P1**

**知识点详解**：RocketMQ 4.x 常见延迟等级与 5.x 按投递时间戳的定时消息是不同版本能力。延时消息表示到某时刻后具备投递资格，不能保证业务恰在那一毫秒完成。RabbitMQ 可用 TTL 和死信路由，但单队列混合每条不同 TTL 时，过期处理受到队头位置影响；不要把它当无限精度定时器。订单是否关闭仍由数据库状态及业务截止时间决定。

**具体例子**：订单 30 分钟后收到关闭事件，消费者执行“仅当 PENDING 且已到期才变 CLOSED”的条件更新。付款已成功则不关闭；关闭成功再发幂等释放库存事件，定期扫描遗漏到期订单。

**面试答法**：我把调度触发和业务决定分开：消息负责唤醒，状态机和权威时间负责决定；重复、迟到和丢失唤醒都有兜底。

**追问**：为什么不能收到消息就退库存？它可能重复、早到或对应已支付订单。

**常见误区**：18 个延迟等级适用于所有 RocketMQ；TTL 到期等于立刻被消费者处理；插件维护状态未核验却当默认能力。

**来源**：[FB-S006 RabbitMQ TTL](https://www.rabbitmq.com/docs/ttl)、[FB-S008 RocketMQ 5.x 定时消息](https://rocketmq.apache.org/docs/featureBehavior/02delaymessage/)。
