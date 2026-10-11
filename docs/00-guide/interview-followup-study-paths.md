# 面经补充学习路线：基础、追问、设计与排障

[总目录](../../README.md) · [题号索引](../../QUESTION_INDEX.md) · [公开线索与权利边界](../../sources/interview-followups/README.md) · [验证记录](../../coverage/INTERVIEW_FOLLOWUPS_VALIDATION.md)

本轮围绕当前内容的实际缺口补充六篇深读专题与这一篇路线，而不是再复制基础题。新专题不新增编号题，不改变原361道讲义题、100道Hot100、15道外部资源练习、26张原创场景卡的口径。原有17份公开场景自报集合保持原样；本轮发现/重核线索单独说明，不把不同来源类型混成“又验证了若干真人面试”。

P0/P1是学习建议，不是统计考频。公开面经属于便利样本；同一作者多轮、多公司不能当多个独立候选人。GitHub题单、牛客自报、知乎二手整理、小红书未获可读原帖分别标注。没有任何一批能保证覆盖所有可能问题或押中面试。

<a id="followup-route-agent"></a>
## Agent线：先分层，再解释失败

1. **基础：** [Agent loop与工具](../10-agent/01-agent-loop-tools-and-state.md)、[RAG](../10-agent/02-rag-retrieval-and-reranking.md)、[上下文](../10-agent/03-memory-and-context.md)、[Transformer先修](../10-agent/05-transformer-prerequisite.md)
2. **项目问法：** [评测与路由](../10-agent/25-agent-evaluation-and-routing.md)、[生产设计](../10-agent/26-agent-production-design-lab.md)、[工具/MCP/Skill合同](../10-agent/31-tool-mcp-and-skill-contracts.md)
3. **新增追问：** [A2A任务生命周期](../10-agent/32-a2a-task-lifecycle-lab.md) → Message/Task → 身份范围 → 输入/授权中断 → 取消竞争 → 重连与终态
4. **新增追问：** [工具流组装](../10-agent/33-tool-stream-assembly-lab.md) → 帧/事件边界 → 多调用交错 → 部分JSON → 完整候选 → 参数/业务/授权检查 → 执行身份
5. **设计与排障：** 用同一个工具调用回答“断连后是否能执行”“重复done怎么办”“取消后副作用未知怎么办”，不要只回答再重试一次

**练习产物：** 一张状态/身份表、一条失败时间线和一个能拒绝坏输入的本地测试。模型性能、A2A服务器和供应商互通仍是另一层实验，不能拿标准库模型替代。

<a id="followup-route-java"></a>
## Java线：从执行器参数到真实等待图

1. **基础：** [集合](../20-java/01-language-and-collections.md)、[JMM/线程池](../20-java/02-concurrency-and-thread-pools.md)、[JVM](../20-java/03-jvm-and-classloading.md)
2. **框架：** [Spring基础](../20-java/04-spring-and-backend.md)、[机制与事务边界](../20-java/14-spring-mechanisms.md)
3. **新增深读：** [执行器故障诊所](../20-java/16-executor-failure-followups.md) → 队列先于扩池 → 拒绝如何被观察 → get超时与取消 → allOf/anyOf → 线程上下文 → 有限退出
4. **系统连线：** 画HTTP线程、异步池、数据库连接、下游额度四种资源的持有/等待；解释为什么拆池或扩大池仍可能堵塞
5. **验收：** 运行19个Java合同场景，讲清每个反例依赖的JDK API和业务合同；没有Spring容器就不说事务集成已通过

<a id="followup-route-go"></a>
## Go线：每个goroutine都要有结束故事

1. **基础：** [GMP与同步](../30-go/01-concurrency.md)、[slice/map/error](../30-go/02-types-containers-and-errors.md)、[版本边界](../30-go/06-version-boundaries.md)
2. **服务：** [HTTP/SSE/退出](../30-go/04-http-sse-grpc.md)、[测试与诊断](../30-go/05-testing-and-debugging.md)
3. **新增深读：** [生命周期诊所](../30-go/07-concurrency-failure-followups.md) → feed/worker所有权 → select取消竞争 → 限流/并发/排队/预算 → Body与长连接 → join证据
4. **验收：** 逐步解释标准库Map，指出回调不合作时没有强杀保证。10个Go测试函数与race在同提交CI运行；本地没有Go编译工具的事实另行保留

<a id="followup-route-storage"></a>
## 后端线：先写不变量，再选中间件

1. **基础：** [网络](../40-backend/01-network-and-streaming.md)、[SQL](../40-backend/02-databases-and-sql.md)、[缓存](../40-backend/03-redis-and-caching.md)、[消息](../40-backend/04-messaging-and-idempotency.md)
2. **新增深读：** [提交与恢复诊所](../40-backend/41-storage-recovery-followups.md) → 未知结果 → 稳定身份 → Outbox/Inbox → 安全frontier → 资源端fencing → 缓存floor → 死锁重试范围
3. **新增设计：** [系统设计与排障诊所](../40-backend/42-system-design-debugging-clinic.md) → 尾延迟与队列 → SQL证据 → 在线迁移水位 → 任务API → 事故假设
4. **验收：** 运行29个SQLite/状态模型测试，补上真实MySQL、Redis、Kafka环境还应测什么。特别指出Kafka实际offset可能跳号，连续整数模型不能直接当生产消费者

<a id="followup-route-practice"></a>
## 每次复习用同一个五层模板

| 层次 | 要交代的内容 | 自检反例 |
|---|---|---|
| 基础 | 术语和边界 | 是否把两个不同API当同一机制 |
| 原理 | 不变量、所有者、资源 | 谁close、谁join、谁提交 |
| 追问 | 失败、重复、竞争 | 回复丢失、旧worker恢复、迟到事件 |
| 设计 | 权衡、恢复、预算 | 队列满、无法补偿、版本跨重启 |
| 证据 | 实际运行与未测范围 | 本地模型是否被夸大成生产事实 |

先用自己的话讲60秒，再画时间线，再运行对应小实验。参考回答不是个人经历：没做过就说明“如果实现，我会……”；没有真实QPS、GPU、模型或线上事故证据，不补写成简历成绩。

算法继续沿用[Hot100](../80-hot100/README.md)、[SQL九题](../70-practice/sql-nine-worked-problems.md)、[面经算法补充](../70-practice/interview-algorithm-supplements.md)，这轮不重复发布现有题解。
