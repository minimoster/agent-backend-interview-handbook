# 消息队列与幂等

[返回总目录](../../README.md) · [题目索引](../../QUESTION_INDEX.md) · [版本与纠错](../../errata/README.md)

<a id="b31"></a>

### B31 为什么引入消息队列，Kafka 怎样保证顺序

**优先级：P0** 

**知识点详解**： 消息队列可把生产与处理解耦、缓冲突发流量、支持异步处理，但增加延迟、重复消费和运维复杂度。Kafka 的顺序范围是分区；不同分区之间没有通用的全局顺序承诺。同一消费组通过分区分配实现并行消费。

**具体例子**： 订单创建后异步建立搜索索引。按 order_id 选分区有助于同一订单事件保持分区顺序；消费端若再任意并发处理，仍可能把业务更新完成顺序打乱。

**面试答法**： 我先说明为什么同步处理不合适，再定义消息的顺序范围、积压上限和失败恢复。

**追问**： 消费者变多一定更快吗？还受分区数、热点键、下游容量与处理模型限制。

**常见误区**： MQ 可以无限削峰；把分区顺序等同于跨所有订单的全局顺序。

**来源**： [BS40 Kafka 4.0 核心概念](https://kafka.apache.org/40/getting-started/introduction/)。

<a id="b32"></a>

### B32 消息为什么重复，消费端如何真正幂等

**优先级：P0** 

**知识点详解**： 处理完成但确认或位点提交前崩溃，会导致再次处理。应用幂等通常需要稳定的业务操作 id，以及“是否已处理”的原子记录。只做“先查 Redis 标记，再写数据库”，检查与写入之间仍有竞态和崩溃窗口。

**具体例子**： 消费订单扣款事件，在同一个数据库事务内插入唯一 event_id 的处理记录，并修改相应业务记录。唯一冲突表示这次事件已被处理；事务失败则两者一起回滚。若副作用发生在第三方接口，还需要对方支持相同幂等键或设计对账补偿。

**面试答法**： 我把去重记录和本地业务效果放在同一原子边界，并定义幂等键的生成、作用域、参数一致性和保留期限。

**追问**： 同一幂等键却携带不同金额怎么办？应视为冲突，不能静默当成同一个操作。

**常见误区**： 用时间戳随重试重新生成 id；把“检查过一次”当成并发安全。

**来源**： [BS41 AWS 幂等 API 与安全重试](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)、[BS26 PostgreSQL 约束](https://www.postgresql.org/docs/18/ddl-constraints.html)。消费事务示例为原创设计。

<a id="b33"></a>

### B33 Kafka 的 exactly-once 保证到哪里为止

**优先级：P1** 

**知识点详解**： 幂等生产者处理其协议范围内的重试重复写入；事务进一步协调 Kafka 内的输出与消费位点。read_committed 消费者不返回已中止事务的数据。Kafka 内“读→处理→写回 Kafka”的事务语义，不自动扩展为外部数据库、发邮件或调用支付接口只发生一次。

**具体例子**： 消费者已把数据库库存减一，却在提交 Kafka 位点前崩溃；重启后同一消息仍可能重做数据库操作。仅打开 enable.idempotence 不能修复这个边界。

**面试答法**： 我会先问 exactly-once 指生产、消费处理还是端到端业务效果，再解释对应事务边界及外部系统配合。

**追问**： 业务方主动发送两次相同内容会自动合并吗？不能依赖生产者幂等替代业务去重。

**常见误区**： 把幂等生产者等同于所有消费者副作用恰好一次；不核对 acks、重试和并发请求等相关配置。

**来源**： [BS42 Kafka 4.0 交付语义与事务](https://kafka.apache.org/40/design/design/)、[BS43 Kafka 4.0 Producer Configs](https://kafka.apache.org/40/configuration/producer-configs/)。

<a id="b34"></a>

### B34 数据库写成功但消息发送失败，outbox 怎样解决

**优先级：P0** 

**知识点详解**： 数据库与 MQ 双写存在“一个成功、另一个失败”的窗口。事务 outbox 把业务行和“待发送事件”写入同一个数据库事务，再由独立发布器可靠转发。发布器可以轮询，也可用 CDC 读取数据库变更。它保证有机会继续发布，不代表发布器不会重复发送。

**具体例子**： 创建订单与插入 outbox(event_id,order_id,payload) 同时提交。发布器发出后、标记成功前崩溃，重启会再次发；因此消费端仍按 event_id 幂等。持续监控未发送事件年龄，避免静默积压。

**面试答法**： outbox 把双系统原子提交问题转成单库事务加可靠异步转发；代价是最终一致、重复处理与清理运维。

**追问**： 顺序怎么保持？需要定义聚合键和发布/分区策略，不能只靠数据库插入时间猜顺序。

**常见误区**： 把记录写入 outbox 后就认为 MQ 已收到；无限累积事件不做归档与告警。

**来源**： [BS44 AWS Transactional Outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)、[BS45 Debezium Outbox Event Router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html)。

<a id="b35"></a>

### B35 坏消息一直失败怎么办，什么时候提交位点

**优先级：P0** 

**知识点详解**： 消费前提交位点可能造成业务尚未完成就跳过；业务完成后提交能降低这种丢处理风险，但崩溃时可能重做。短暂故障适合有限重试；格式错误等永久故障应隔离，并告警、保存原因、支持受控重放。死信队列是处理失败的机制，不是扔进去就解决。

**具体例子**： 模型供应商暂时超时可退避重试；事件字段缺失连续重试没有意义，应送入受控失败通道。对要求同一订单严格顺序的流程，跳过失败事件会影响后续语义，必须先定策略。

**面试答法**： 我将可重试、不可重试与人工处理分开，明确重试次数、总时限、位点提交和重放幂等。

**追问**： 慢消费会怎样影响组协调？需核对 poll 间隔、处理时长及重平衡配置，避免长时间处理超出约束。

**常见误区**： 无限重试阻塞整个分区；认为 Kafka 与 SQS 拥有完全相同的死信内建能力。

**来源**： [BS46 Amazon SQS 死信队列](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)、[BS47 Kafka 4.0 Consumer Configs](https://kafka.apache.org/40/configuration/consumer-configs/)。死信模式用于对照，Kafka 流程需自行设计或选支持它的框架。

本节题号：B31、B32、B33、B34、B35。
