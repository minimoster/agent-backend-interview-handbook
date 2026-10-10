# 题目索引

[返回总目录](README.md) · [完整学习路线](docs/00-guide/expanded-map-and-study-plan.md) · [覆盖状态](coverage/README.md)

已发布题目的题号保持不变。扩展题使用FA/FJ/FB、SQL用S、推理用R；重复来源可合并到同一题，题数不是面经命中率。

本版详解题：361道，另附Hot100独立100题。源文缺失与验证边界见覆盖状态和验证记录。

独立练习入口：[15道算法基础外部资源题](docs/85-algorithm-supplement/README.md)，按题号、分类与官方难度检索；不增加上述361/100计数，不提供新增原创实现。[代码随想录资源归属与覆盖](sources/carl-hot100-resources.md)。

## Agent基线 · 36题

- [A01 什么是 Agent？与聊天机器人、Workflow 有什么区别？](docs/10-agent/01-agent-loop-tools-and-state.md#a01) · P0
- [A02 ReAct 如何工作？为什么不能只让模型一直“想”？](docs/10-agent/01-agent-loop-tools-and-state.md#a02) · P0
- [A03 一次 Function Calling 到底是谁执行函数？如何设计工具？](docs/10-agent/01-agent-loop-tools-and-state.md#a03) · P0
- [A04 JSON Schema 能解决什么？为什么解析成功还不安全？](docs/10-agent/01-agent-loop-tools-and-state.md#a04) · P0
- [A05 Agent 的 state 应保存什么？为什么不能只存聊天记录？](docs/10-agent/01-agent-loop-tools-and-state.md#a05) · P0
- [A06 ReAct 与 Plan–Execute 如何取舍？怎么防止无限循环？](docs/10-agent/01-agent-loop-tools-and-state.md#a06) · P1
- [A07 多 Agent 真比单 Agent 好吗？怎么协作？](docs/10-agent/01-agent-loop-tools-and-state.md#a07) · P1
- [A08 MCP、Function Calling、Tool 和 Skill 是一回事吗？](docs/10-agent/01-agent-loop-tools-and-state.md#a08) · P1
- [A09 RAG 从文档到答案的完整流程是什么？](docs/10-agent/02-rag-retrieval-and-reranking.md#a09) · P0
- [A10 chunk 大小、overlap、父子块怎么选？](docs/10-agent/02-rag-retrieval-and-reranking.md#a10) · P0
- [A11 Embedding 是什么？余弦、点积、欧氏距离有什么区别？](docs/10-agent/02-rag-retrieval-and-reranking.md#a11) · P0
- [A12 BM25 和向量检索为什么要混合？](docs/10-agent/02-rag-retrieval-and-reranking.md#a12) · P0
- [A13 RRF 怎么算？为什么不直接加 BM25 和向量分数？](docs/10-agent/02-rag-retrieval-and-reranking.md#a13) · P0
- [A14 Rerank 做什么？Cross-Encoder 与 LLM rerank 有何不同？](docs/10-agent/02-rag-retrieval-and-reranking.md#a14) · P0
- [A15 Query rewrite、多 query、HyDE 为什么可能有用，也可能有害？](docs/10-agent/02-rag-retrieval-and-reranking.md#a15) · P1
- [A16 RAG 答错了，按什么顺序排查？](docs/10-agent/02-rag-retrieval-and-reranking.md#a16) · P0
- [A17 Recall@k、MRR、NDCG 分别衡量什么？](docs/10-agent/02-rag-retrieval-and-reranking.md#a17) · P0
- [A18 RAG、微调、LoRA 应怎么选？](docs/10-agent/02-rag-retrieval-and-reranking.md#a18) · P1
- [A19 短期记忆、长期记忆、RAG 的关系是什么？](docs/10-agent/03-memory-and-context.md#a19) · P0
- [A20 上下文太长怎么压缩？怎样验证没压坏？](docs/10-agent/03-memory-and-context.md#a20) · P0
- [A21 “三层记忆”应该怎样解释，才能不是背架构词？](docs/10-agent/03-memory-and-context.md#a21) · P1
- [A22 长期记忆不断增长、相互矛盾或过期怎么办？](docs/10-agent/03-memory-and-context.md#a22) · P1
- [A23 模型支持长上下文，还需要检索和压缩吗？](docs/10-agent/03-memory-and-context.md#a23) · P1
- [A24 SSE 与普通 HTTP、WebSocket 的区别是什么？](docs/10-agent/04-streaming-and-reliable-execution.md#a24) · P0
- [A25 SSE 断线重连，如何避免漏事件或重复展示？](docs/10-agent/04-streaming-and-reliable-execution.md#a25) · P0
- [A26 后端在逐条写 SSE，为什么前端还是最后一起显示？](docs/10-agent/04-streaming-and-reliable-execution.md#a26) · P0
- [A27 长任务为什么要和 HTTP 连接解耦？恢复时从哪里继续？](docs/10-agent/04-streaming-and-reliable-execution.md#a27) · P0
- [A28 Go 中如何取消 Agent、限制并发和避免 goroutine 泄漏？](docs/10-agent/04-streaming-and-reliable-execution.md#a28) · P0
- [A29 模型或工具超时，怎么重试才不会越重试越糟？](docs/10-agent/04-streaming-and-reliable-execution.md#a29) · P0
- [A30 Agent 工具副作用如何做到幂等？Exactly-once 能随口承诺吗？](docs/10-agent/04-streaming-and-reliable-execution.md#a30) · P0
- [A39 Openresearch 的状态持久化和执行租约解决什么？有什么边界？](docs/50-projects/public-repository-case-studies.md#a39) · P0
- [A40 Openresearch 的 DAG、Agent routing 与 Eino 各负责什么？](docs/50-projects/public-repository-case-studies.md#a40) · P0
- [A41 Openresearch 有评测和修复循环，为什么还不能说“效果已被充分证明”？](docs/50-projects/public-repository-case-studies.md#a41) · P0
- [A42 Saber 到底解决什么问题？如何讲清完整架构而不是报组件名单？](docs/50-projects/public-repository-case-studies.md#a42) · P0
- [A43 Saber 检索的并行边界和重排实现，最容易说错什么？](docs/50-projects/public-repository-case-studies.md#a43) · P0
- [A44 Saber 长期记忆的 outbox、版本 hash 与 reconcile 为什么不是强一致？](docs/50-projects/public-repository-case-studies.md#a44) · P0

## 后端基线 · 50题

- [B01 HTTP 的安全性、幂等性与状态码分别解决什么问题](docs/40-backend/01-network-and-streaming.md#b01) · P0
- [B02 HTTP 缓存里的 no-cache、no-store 和协商缓存有什么区别](docs/40-backend/01-network-and-streaming.md#b02) · P1
- [B03 TCP 为什么可靠，又为什么会出现所谓粘包](docs/40-backend/01-network-and-streaming.md#b03) · P0
- [B04 三次握手、连接关闭与 TIME_WAIT 如何联系起来](docs/40-backend/01-network-and-streaming.md#b04) · P0
- [B05 HTTP 1.1、2、3 的主要差别是什么](docs/40-backend/01-network-and-streaming.md#b05) · P0
- [B06 HTTPS 中 TLS 到底保护了什么](docs/40-backend/01-network-and-streaming.md#b06) · P0
- [B07 AI 输出流为什么常用 SSE，断线如何恢复](docs/40-backend/01-network-and-streaming.md#b07) · P0
- [B08 WebSocket 与 SSE 怎么选择](docs/40-backend/01-network-and-streaming.md#b08) · P1
- [B09 索引为什么加速查询，B 树结构适合什么查询](docs/40-backend/02-databases-and-sql.md#b09) · P0
- [B10 聚簇索引、二级索引、回表和覆盖索引是什么](docs/40-backend/02-databases-and-sql.md#b10) · P0
- [B11 联合索引的最左前缀应该怎样理解](docs/40-backend/02-databases-and-sql.md#b11) · P0
- [B12 慢 SQL 怎样用 EXPLAIN 排查](docs/40-backend/02-databases-and-sql.md#b12) · P0
- [B13 ACID 是什么，为什么开了事务仍会写错业务](docs/40-backend/02-databases-and-sql.md#b13) · P0
- [B14 四个隔离级别怎样区分，MySQL 与 PostgreSQL 哪里不同](docs/40-backend/02-databases-and-sql.md#b14) · P0
- [B15 MVCC 怎样让读写并行，快照是什么](docs/40-backend/02-databases-and-sql.md#b15) · P0
- [B16 快照读、锁定读、记录锁和间隙锁有什么关系](docs/40-backend/02-databases-and-sql.md#b16) · P0
- [B17 死锁为什么发生，应用应该怎么处理](docs/40-backend/02-databases-and-sql.md#b17) · P0
- [B18 两个请求同时抢最后一件商品，怎样避免超卖](docs/40-backend/02-databases-and-sql.md#b18) · P0
- [B19 深分页为什么慢，游标分页怎样设计](docs/40-backend/02-databases-and-sql.md#b19) · P1
- [B20 LEFT JOIN 为什么有时写着写着变成了 INNER JOIN](docs/40-backend/02-databases-and-sql.md#b20) · P0
- [B21 每个用户取最近三条订单，窗口函数怎么用](docs/40-backend/02-databases-and-sql.md#b21) · P0
- [B22 Redis 常见数据结构怎样对应业务需求](docs/40-backend/03-redis-and-caching.md#b22) · P0
- [B23 Redis 为什么仍可能很慢，KEYS 与 SCAN 怎么选](docs/40-backend/03-redis-and-caching.md#b23) · P0
- [B24 RDB 和 AOF 怎样选择，持久化是否等于绝不丢数据](docs/40-backend/03-redis-and-caching.md#b24) · P1
- [B25 TTL 过期与内存淘汰有什么区别](docs/40-backend/03-redis-and-caching.md#b25) · P0
- [B26 先更新数据库再删除缓存，为什么仍不是强一致](docs/40-backend/03-redis-and-caching.md#b26) · P0
- [B27 缓存击穿与雪崩怎样区分，如何保护数据库](docs/40-backend/03-redis-and-caching.md#b27) · P0
- [B28 缓存穿透与布隆过滤器是怎么回事](docs/40-backend/03-redis-and-caching.md#b28) · P0
- [B29 Redis 分布式锁的最小正确实现需要什么](docs/40-backend/03-redis-and-caching.md#b29) · P0
- [B30 有 Redis 主从复制，为什么故障切换后仍可能丢写入](docs/40-backend/03-redis-and-caching.md#b30) · P1
- [B31 为什么引入消息队列，Kafka 怎样保证顺序](docs/40-backend/04-messaging-and-idempotency.md#b31) · P0
- [B32 消息为什么重复，消费端如何真正幂等](docs/40-backend/04-messaging-and-idempotency.md#b32) · P0
- [B33 Kafka 的 exactly-once 保证到哪里为止](docs/40-backend/04-messaging-and-idempotency.md#b33) · P1
- [B34 数据库写成功但消息发送失败，outbox 怎样解决](docs/40-backend/04-messaging-and-idempotency.md#b34) · P0
- [B35 坏消息一直失败怎么办，什么时候提交位点](docs/40-backend/04-messaging-and-idempotency.md#b35) · P0
- [B36 固定窗口、滑动窗口和令牌桶怎样选择](docs/40-backend/05-system-design-and-reliability.md#b36) · P0
- [B37 超时、deadline 和取消是什么关系](docs/40-backend/05-system-design-and-reliability.md#b37) · P0
- [B38 重试为什么可能把故障放大，怎样设计退避](docs/40-backend/05-system-design-and-reliability.md#b38) · P0
- [B39 限流、熔断和隔离分别防什么问题](docs/40-backend/05-system-design-and-reliability.md#b39) · P0
- [B40 日志、指标、链路追踪分别怎么看问题](docs/40-backend/05-system-design-and-reliability.md#b40) · P0
- [B41 什么是背压，为什么不能给每个任务无限开协程](docs/40-backend/05-system-design-and-reliability.md#b41) · P0
- [B42 进程、线程与协程有什么区别](docs/40-backend/06-linux-and-containers.md#b42) · P0
- [B43 epoll 的 I/O 多路复用为什么有用](docs/40-backend/06-linux-and-containers.md#b43) · P1
- [B44 容器与虚拟机怎么区分，namespace 和 cgroup 分别做什么](docs/40-backend/06-linux-and-containers.md#b44) · P0
- [B45 镜像构建和健康检查，实习生要懂到什么程度](docs/40-backend/06-linux-and-containers.md#b45) · P1
- [B46 优雅退出怎样避免发布时丢请求](docs/40-backend/06-linux-and-containers.md#b46) · P0
- [B47 服务突然变慢，如何从 Linux 走到应用定位](docs/40-backend/06-linux-and-containers.md#b47) · P0
- [B48 SQL 注入为什么发生，参数化查询解决了什么](docs/40-backend/07-security-and-problem-solving.md#b48) · P0
- [B49 算法题怎样从会背答案变成能现场写](docs/40-backend/07-security-and-problem-solving.md#b49) · P0
- [B50 SQL 手写应该练哪些能力，如何自测正确性](docs/40-backend/07-security-and-problem-solving.md#b50) · P0

## Go基线 · 40题

- [G01 什么是 GMP？为什么 goroutine 比线程轻量？](docs/30-go/01-concurrency.md#g01) · P0
- [G02 网络 I/O、系统调用、CPU 密集任务如何影响调度？](docs/30-go/01-concurrency.md#g02) · P1
- [G03 什么是 goroutine 泄漏？如何保证每个任务退出？](docs/30-go/01-concurrency.md#g03) · P0
- [G04 无缓冲与有缓冲 channel 有什么区别？](docs/30-go/01-concurrency.md#g04) · P0
- [G05 nil、关闭、空的 channel 分别会怎样？谁负责 close？](docs/30-go/01-concurrency.md#g05) · P0
- [G06 select 如何工作？为什么 default 可能把 CPU 跑满？](docs/30-go/01-concurrency.md#g06) · P0
- [G07 context 到底传递什么？cancel 会杀掉 goroutine 吗？](docs/30-go/01-concurrency.md#g07) · P0
- [G08 一个请求要调用多个下游，超时预算怎样分配？](docs/30-go/01-concurrency.md#g08) · P0
- [G09 WaitGroup 与 errgroup 如何选择？](docs/30-go/01-concurrency.md#g09) · P0
- [G10 如何设计一个有界 worker pool？](docs/30-go/01-concurrency.md#g10) · P0
- [G11 什么是 data race？加 sleep 为什么不能同步？](docs/30-go/01-concurrency.md#g11) · P0
- [G12 Mutex、RWMutex 如何选择？锁住什么才正确？](docs/30-go/01-concurrency.md#g12) · P0
- [G13 atomic、Once 能替代锁吗？](docs/30-go/01-concurrency.md#g13) · P1
- [G14 map 使用有哪些必知边界？sync.Map 适合所有场景吗？](docs/30-go/02-types-containers-and-errors.md#g14) · P0
- [G15 Go map 底层还是“8 个桶元素＋溢出桶”吗？](docs/30-go/02-types-containers-and-errors.md#g15) · P1
- [G16 slice 的 len、cap、append、共享底层数组怎么理解？](docs/30-go/02-types-containers-and-errors.md#g16) · P0
- [G17 只保留一个小切片，为何可能占用很多内存？](docs/30-go/02-types-containers-and-errors.md#g17) · P1
- [G18 make、new、零值有什么区别？](docs/30-go/02-types-containers-and-errors.md#g18) · P0
- [G19 为什么 interface 里放了 nil，比较却不等于 nil？](docs/30-go/02-types-containers-and-errors.md#g19) · P0
- [G20 errors.Is、errors.As、%w 如何配合？](docs/30-go/02-types-containers-and-errors.md#g20) · P0
- [G21 defer、panic、recover 的执行顺序是什么？](docs/30-go/02-types-containers-and-errors.md#g21) · P0
- [G22 for 循环启动 goroutine 时，变量捕获还有坑吗？](docs/30-go/02-types-containers-and-errors.md#g22) · P1
- [G23 什么是逃逸分析？返回局部变量指针安全吗？](docs/30-go/03-memory-gc-and-performance.md#g23) · P0
- [G24 Go GC 如何判断垃圾？三色、写屏障、STW 分别解决什么？](docs/30-go/03-memory-gc-and-performance.md#g24) · P0
- [G25 GOGC、GOMEMLIMIT 怎样影响延迟和内存？](docs/30-go/03-memory-gc-and-performance.md#g25) · P1
- [G26 sync.Pool 适合缓存数据库连接或任务结果吗？](docs/30-go/03-memory-gc-and-performance.md#g26) · P1
- [G27 HTTP Client 为什么要复用？响应 Body 怎么处理？](docs/30-go/04-http-sse-grpc.md#g27) · P0
- [G28 HTTP 服务端和客户端各有哪些超时？](docs/30-go/04-http-sse-grpc.md#g28) · P0
- [G29 SSE 为什么适合大模型输出？与 WebSocket 有何区别？](docs/30-go/04-http-sse-grpc.md#g29) · P0
- [G30 Go 写 SSE 时，如何处理 Flush、慢客户端和用户断连？](docs/30-go/04-http-sse-grpc.md#g30) · P0
- [G31 gRPC 的价值、deadline 与流控是什么？](docs/30-go/04-http-sse-grpc.md#g31) · P1
- [G32 下游失败要不要重试？怎样避免重复执行和雪崩？](docs/30-go/04-http-sse-grpc.md#g32) · P0
- [G33 限流与并发限制的区别？令牌桶如何工作？](docs/30-go/04-http-sse-grpc.md#g33) · P0
- [G34 Go HTTP 服务如何优雅退出？](docs/30-go/04-http-sse-grpc.md#g34) · P0
- [G35 Go HTTP 中间件怎样组织？Agent 接口额外防什么？](docs/30-go/04-http-sse-grpc.md#g35) · P1
- [G36 Go 后端怎样写有价值的测试？](docs/30-go/05-testing-and-debugging.md#g36) · P0
- [G37 race 检测、fuzz、普通测试分别能发现什么？](docs/30-go/05-testing-and-debugging.md#g37) · P1
- [G38 Benchmark 怎么写才不自欺欺人？](docs/30-go/05-testing-and-debugging.md#g38) · P1
- [G39 线上 CPU 突然变高，怎样用 pprof 排查？](docs/30-go/05-testing-and-debugging.md#g39) · P0
- [G40 内存、goroutine、延迟问题分别怎么看？](docs/30-go/05-testing-and-debugging.md#g40) · P0

## Java基线 · 46题

- [J01 为什么重写 equals 时通常也必须重写 hashCode](docs/20-java/01-language-and-collections.md#j01) · P0
- [J02 ArrayList 和 LinkedList 怎么选](docs/20-java/01-language-and-collections.md#j02) · P0
- [J03 HashMap 的 put 和 get 到底做了什么](docs/20-java/01-language-and-collections.md#j03) · P0
- [J04 HashMap 扩容和树化阈值怎么正确回答](docs/20-java/01-language-and-collections.md#j04) · P0
- [J05 ConcurrentHashMap 安全意味着什么](docs/20-java/01-language-and-collections.md#j05) · P0
- [J06 fail fast 是什么 能拿它保证线程安全吗](docs/20-java/01-language-and-collections.md#j06) · P1
- [J07 Java 泛型的类型擦除是什么意思](docs/20-java/01-language-and-collections.md#j07) · P0
- [J08 extends 和 super 通配符怎么理解](docs/20-java/01-language-and-collections.md#j08) · P1
- [J09 JMM 和 JVM 内存区域是一回事吗](docs/20-java/02-concurrency-and-thread-pools.md#j09) · P0
- [J10 happens before 和 volatile 如何保证可见性](docs/20-java/02-concurrency-and-thread-pools.md#j10) · P0
- [J11 synchronized 锁住了什么](docs/20-java/02-concurrency-and-thread-pools.md#j11) · P0
- [J12 synchronized 和 ReentrantLock 如何选择](docs/20-java/02-concurrency-and-thread-pools.md#j12) · P0
- [J13 CAS 是什么 为什么还有 ABA 问题](docs/20-java/02-concurrency-and-thread-pools.md#j13) · P0
- [J14 AQS 是一把锁吗](docs/20-java/02-concurrency-and-thread-pools.md#j14) · P1
- [J15 线程池七个参数和任务提交顺序是什么](docs/20-java/02-concurrency-and-thread-pools.md#j15) · P0
- [J16 怎么给 LLM 调用配置线程池和拒绝策略](docs/20-java/02-concurrency-and-thread-pools.md#j16) · P0
- [J17 CompletableFuture 能解决什么 不能解决什么](docs/20-java/02-concurrency-and-thread-pools.md#j17) · P1
- [J18 ThreadLocal 为什么会泄漏和串用户](docs/20-java/02-concurrency-and-thread-pools.md#j18) · P0
- [J19 wait 和 sleep 有何区别 怎么防死锁](docs/20-java/02-concurrency-and-thread-pools.md#j19) · P1
- [J20 CountDownLatch Semaphore 和队列如何分工](docs/20-java/02-concurrency-and-thread-pools.md#j20) · P1
- [J21 虚拟线程适合 AI 后端吗](docs/20-java/02-concurrency-and-thread-pools.md#j21) · P1
- [J22 中断和取消应该如何处理](docs/20-java/02-concurrency-and-thread-pools.md#j22) · P1
- [J23 JVM 运行时内存区域怎么讲](docs/20-java/03-jvm-and-classloading.md#j23) · P0
- [J24 GC 如何判断对象可以回收](docs/20-java/03-jvm-and-classloading.md#j24) · P0
- [J25 标记清除 复制 标记整理有什么取舍](docs/20-java/03-jvm-and-classloading.md#j25) · P1
- [J26 G1 和 ZGC 怎么选](docs/20-java/03-jvm-and-classloading.md#j26) · P1
- [J27 内存泄漏和 OOM 是一回事吗 怎么排查](docs/20-java/03-jvm-and-classloading.md#j27) · P0
- [J28 类加载的加载 连接 初始化分别做什么](docs/20-java/03-jvm-and-classloading.md#j28) · P0
- [J29 双亲委派是什么 现代类加载器如何回答](docs/20-java/03-jvm-and-classloading.md#j29) · P1
- [J30 IoC 和依赖注入为什么有用](docs/20-java/04-spring-and-backend.md#j30) · P0
- [J31 Bean 生命周期要掌握到什么程度](docs/20-java/04-spring-and-backend.md#j31) · P1
- [J32 Spring 单例 Bean 线程安全吗](docs/20-java/04-spring-and-backend.md#j32) · P0
- [J33 Spring AOP 和两种代理如何工作](docs/20-java/04-spring-and-backend.md#j33) · P0
- [J34 为什么同类调用会让事务失效](docs/20-java/04-spring-and-backend.md#j34) · P0
- [J35 除了自调用 事务还会在哪些地方不符合预期](docs/20-java/04-spring-and-backend.md#j35) · P0
- [J36 REQUIRED REQUIRES_NEW NESTED 怎么区别](docs/20-java/04-spring-and-backend.md#j36) · P1
- [J37 一次 Spring MVC 请求怎么到 Controller](docs/20-java/04-spring-and-backend.md#j37) · P0
- [J38 参数校验和统一异常处理为什么都需要](docs/20-java/04-spring-and-backend.md#j38) · P0
- [J39 Spring Boot 自动配置怎么排查](docs/20-java/04-spring-and-backend.md#j39) · P0
- [J40 认证 授权 CSRF CORS 分别是什么](docs/20-java/04-spring-and-backend.md#j40) · P0
- [J41 为什么流式回答常用 SSE 后端要处理什么](docs/20-java/05-agent-integration.md#j41) · P0
- [J42 HTTP 客户端为什么不能只设一个超时](docs/20-java/05-agent-integration.md#j42) · P0
- [J43 怎么让模型安全调用 Java 工具](docs/20-java/05-agent-integration.md#j43) · P0
- [J44 为什么不要用一个数据库事务包住整段 Agent 运行](docs/20-java/05-agent-integration.md#j44) · P0
- [J45 Agent 后端要怎么测试和监控](docs/20-java/05-agent-integration.md#j45) · P0
- [J46 AI Agent 和 Java javaagent 有什么区别](docs/20-java/05-agent-integration.md#j46) · P2

## Agent补充 · 63题

- [FA22 一次反思怎样成为可复用的改进 而不是把错误永久记住？](docs/10-agent/14-controlled-improvement.md#fa22) · P1
- [FA23 受控自改进的执行评估更新发布闭环怎样设计？](docs/10-agent/14-controlled-improvement.md#fa23) · P1
- [FA24 奖励信号怎样避免诱导Agent投机？](docs/10-agent/14-controlled-improvement.md#fa24) · P2
- [FA25 允许Agent改自己的技能时 安全边界应放在哪里？](docs/10-agent/14-controlled-improvement.md#fa25) · P1
- [FA26 MCP为什么是接入协议 与HTTP函数调用和Skill是什么关系？](docs/10-agent/15-mcp-versions-and-integration.md#fa26) · P0
- [FA27 MCP 2026-07-28和旧版生命周期 传输有何关键区别？](docs/10-agent/15-mcp-versions-and-integration.md#fa27) · P0
- [FA28 MCP工具目录怎样发现 缓存和感知变化？](docs/10-agent/15-mcp-versions-and-integration.md#fa28) · P1
- [FA29 多个MCP服务怎样编排 谁负责失败预算和业务状态？](docs/10-agent/15-mcp-versions-and-integration.md#fa29) · P0
- [FA30 MCP部署时为什么仍需要鉴权 沙箱和审计？](docs/10-agent/15-mcp-versions-and-integration.md#fa30) · P0
- [FA31 通用Agent Skill是什么包 自研技能服务和它相同吗？](docs/10-agent/16-skills-routing-and-governance.md#fa31) · P0
- [FA32 从用户意图到Skill执行 应该经过哪些路由和校验？](docs/10-agent/16-skills-routing-and-governance.md#fa32) · P0
- [FA33 Skill怎样组合 多轮追问和中断状态放在哪里？](docs/10-agent/16-skills-routing-and-governance.md#fa33) · P1
- [FA34 多个Agent共享Skill怎样管理版本 权限与淘汰？](docs/10-agent/16-skills-routing-and-governance.md#fa34) · P1
- [FA35 向量索引为什么能加速 HNSW IVF与精确搜索怎样取舍？](docs/10-agent/17-rag-indexes-and-evidence.md#fa35) · P1
- [FA36 稠密稀疏向量与维数是什么关系 维度成本真是指数增长吗？](docs/10-agent/17-rag-indexes-and-evidence.md#fa36) · P1
- [FA37 检索结果怎样变成可靠证据 怎样控制噪声和隐私？](docs/10-agent/17-rag-indexes-and-evidence.md#fa37) · P0
- [FA38 固定长度 结构切片和语义切片怎样选？](docs/10-agent/17-rag-indexes-and-evidence.md#fa38) · P0
- [FA39 Harness到底包含什么 与Prompt和Context工程怎样配合？](docs/10-agent/18-harness-runtime-and-observability.md#fa39) · P0
- [FA40 长任务的状态重置 持久恢复和控制流怎样一起设计？](docs/10-agent/18-harness-runtime-and-observability.md#fa40) · P0
- [FA41 Harness怎样治理工具生命周期 并把Trace变成可用评测？](docs/10-agent/18-harness-runtime-and-observability.md#fa41) · P0
- [FA42 MUSE-Autoskill案例能说明什么 怎样阅读自改进论文的数字？](docs/10-agent/14-controlled-improvement.md#fa42) · P2
- [FA43 多模态RAG怎样检索图片表格和页面 需要Diffusion吗？](docs/10-agent/17-rag-indexes-and-evidence.md#fa43) · P2
- [FA63 Chroma怎样持久化 文本是谁转成Embedding的？](docs/10-agent/22-chroma-persistence-and-embedding.md#fa63) · P1

## Java与数据库补充 · 46题

- [FJ01 JDK 8 到 25 的特性怎样回答才不会把预览当正式](docs/20-java/10-language-foundations.md#fj01) · P1
- [FJ02 JVM、JRE、JDK 是什么，为什么现代 JDK 没有传统 jre 目录](docs/20-java/10-language-foundations.md#fj02) · P0
- [FJ03 基本类型、装箱和拆箱有哪些隐藏边界](docs/20-java/10-language-foundations.md#fj03) · P0
- [FJ04 String 不可变意味着什么，StringBuffer 就能保证整段业务安全吗](docs/20-java/10-language-foundations.md#fj04) · P0
- [FJ05 封装、继承、多态、重载和重写怎样放进同一个例子](docs/20-java/10-language-foundations.md#fj05) · P0
- [FJ06 身份相等、值相等、浅拷贝和深拷贝怎样区分](docs/20-java/10-language-foundations.md#fj06) · P0
- [FJ07 反射能做什么，为什么 setAccessible 不是万能钥匙](docs/20-java/10-language-foundations.md#fj07) · P1
- [FJ08 受检异常、RuntimeException 和 Error 应该怎样处理](docs/20-java/10-language-foundations.md#fj08) · P0
- [FJ09 Collection 与 Map 如何选，ArrayList 究竟怎样增长](docs/20-java/11-collections-and-io.md#fj09) · P0
- [FJ10 HashMap 与 ConcurrentHashMap 的树化、扩容、同步到底哪些能背](docs/20-java/11-collections-and-io.md#fj10) · P1
- [FJ11 BIO、NIO、AIO 是三个互斥包名吗](docs/20-java/11-collections-and-io.md#fj11) · P0
- [FJ12 并发容器怎样选，弱一致遍历与快照迭代有何不同](docs/20-java/11-collections-and-io.md#fj12) · P0
- [FJ13 一个对象从创建到回收会经历什么，GC Roots 为什么不能死背](docs/20-java/12-jvm-operation.md#fj13) · P0
- [FJ14 分代、CMS、G1 与 Full GC 的名词怎样连起来](docs/20-java/12-jvm-operation.md#fj14) · P1
- [FJ15 频繁 Full GC、OOM、栈溢出该按什么顺序查](docs/20-java/12-jvm-operation.md#fj15) · P0
- [FJ16 自定义类加载器为什么不能只写一段“先自己加载”](docs/20-java/12-jvm-operation.md#fj16) · P1
- [FJ17 创建任务、创建线程和选择线程池为什么是三件事](docs/20-java/13-concurrency-details.md#fj17) · P0
- [FJ18 AQS 怎样实现可重入锁，公平锁为什么仍可能插队](docs/20-java/13-concurrency-details.md#fj18) · P1
- [FJ19 “偏向锁升级到重量锁”为什么不是现代 JDK 的通用答案](docs/20-java/13-concurrency-details.md#fj19) · P1
- [FJ20 CAS 与乐观、悲观并发控制怎样选择](docs/20-java/13-concurrency-details.md#fj20) · P0
- [FJ21 ThreadLocal 的弱键为什么仍会保留值，static 能解决吗](docs/20-java/13-concurrency-details.md#fj21) · P0
- [FJ22 Bean 作用域和生命周期怎样一起决定状态与资源归属](docs/20-java/14-spring-mechanisms.md#fj22) · P0
- [FJ23 Autowired、Resource 和循环依赖的“三级缓存”各解决什么](docs/20-java/14-spring-mechanisms.md#fj23) · P0
- [FJ24 Starter、自动配置与 Boot 启动怎样串起来，Cloud 又负责什么](docs/20-java/14-spring-mechanisms.md#fj24) · P1
- [FJ25 Spring 的 isolation 设置什么时候生效，怎样区分“没事务”和“没回滚”](docs/20-java/14-spring-mechanisms.md#fj25) · P0
- [FJ26 MySQL 慢 SQL 怎样定位，EXPLAIN 应看哪些字段](docs/40-backend/20-mysql-mechanisms.md#fj26) · P0
- [FJ27 索引有哪些分类，“索引失效”为什么常常说得太粗](docs/40-backend/20-mysql-mechanisms.md#fj27) · P0
- [FJ28 B+ 树、聚簇索引与覆盖查询怎样影响真正的页访问](docs/40-backend/20-mysql-mechanisms.md#fj28) · P0
- [FJ29 索引 (A,B,C) 跳过 B、出现多个范围时，到底用了哪些列](docs/40-backend/20-mysql-mechanisms.md#fj29) · P0
- [FJ30 隔离级别如何影响读异常，InnoDB RR 到底怎么处理幻读](docs/40-backend/20-mysql-mechanisms.md#fj30) · P0
- [FJ31 undo、redo、binlog 与 Read View 怎样共同支撑事务](docs/40-backend/20-mysql-mechanisms.md#fj31) · P0
- [FJ32 什么时候分库分表，单表“最大多少行”怎样回答](docs/40-backend/20-mysql-mechanisms.md#fj32) · P1
- [FJ33 MySQL 复制如何工作，读写分离为什么会读不到刚写的数据](docs/40-backend/20-mysql-mechanisms.md#fj33) · P1
- [FJ34 MySQL 与 Redis 应怎样分工，为什么不能只比较“毫秒与微秒”](docs/40-backend/20-mysql-mechanisms.md#fj34) · P0
- [FJ35 UNION 与 UNION ALL 去重什么，结果有默认顺序吗](docs/40-backend/20-mysql-mechanisms.md#fj35) · P0
- [FJ36 Mapper、XML、注解与参数绑定是什么关系，如何防止 SQL 注入](docs/40-backend/21-mybatis.md#fj36) · P0
- [FJ37 Redis 逻辑类型与内部编码有什么区别，如何映射业务](docs/40-backend/22-redis-mechanisms.md#fj37) · P0
- [FJ38 Redis 为什么快，单线程与 I/O 多路复用怎样准确表述](docs/40-backend/22-redis-mechanisms.md#fj38) · P0
- [FJ39 RDB、AOF、复制与备份分别怎样帮助故障恢复](docs/40-backend/22-redis-mechanisms.md#fj39) · P0
- [FJ40 键到期一定马上释放内存吗，淘汰策略有哪些](docs/40-backend/22-redis-mechanisms.md#fj40) · P0
- [FJ41 看门狗续租能保证分布式锁永远安全吗](docs/40-backend/22-redis-mechanisms.md#fj41) · P0
- [FJ42 两级缓存如何失效，删缓存失败和旧读回填为什么是两类问题](docs/40-backend/22-redis-mechanisms.md#fj42) · P0
- [FJ43 大键与热键怎样识别，为什么“超过10KB”不是统一标准](docs/40-backend/22-redis-mechanisms.md#fj43) · P0
- [FJ44 Redis 全量复制、部分重同步与复制积压缓冲怎样配合](docs/40-backend/22-redis-mechanisms.md#fj44) · P1
- [FJ45 Sentinel、Cluster 和持久化如何组合，怎样说明高可用边界](docs/40-backend/22-redis-mechanisms.md#fj45) · P0
- [FJ46 三个线程如何按 ABC 顺序循环输出，并在中断时全部退出](docs/20-java/15-thread-ordering-lab.md#fj46) · P0

## 后端与项目补充 · 93题

- [FB01 如何比较 Kafka、RocketMQ 和 RabbitMQ，而不背吞吐排行榜](docs/40-backend/30-message-queue-details.md#fb01) · P0
- [FB02 多副本为什么仍可能丢写或暂停服务](docs/40-backend/30-message-queue-details.md#fb02) · P0
- [FB03 如何把消息可靠性拆成可验证的三个交接点](docs/40-backend/30-message-queue-details.md#fb03) · P0
- [FB04 Kafka 为什么吞吐高，什么情况下优化会失效](docs/40-backend/30-message-queue-details.md#fb04) · P1
- [FB05 按业务键有序与生产者幂等各保证到哪一层](docs/40-backend/30-message-queue-details.md#fb05) · P0
- [FB06 死信、延后重试与优先级为什么不能混为一谈](docs/40-backend/30-message-queue-details.md#fb06) · P0
- [FB07 RocketMQ 半消息回查应查询什么事实](docs/40-backend/30-message-queue-details.md#fb07) · P1
- [FB08 mmap 与 sendfile 的数据路径如何解释](docs/40-backend/30-message-queue-details.md#fb08) · P1
- [FB09 订单超时关闭如何使用定时消息与 TTL](docs/40-backend/30-message-queue-details.md#fb09) · P1
- [FB10 怎样识别创建型、结构型、行为型模式和 Spring 工厂抽象](docs/40-backend/31-design-patterns-in-practice.md#fb10) · P1
- [FB11 如何手写安全的延迟单例，DCL 为什么必须关注发布](docs/40-backend/31-design-patterns-in-practice.md#fb11) · P0
- [FB12 代理和适配器怎样在真实 API 中区分](docs/40-backend/31-design-patterns-in-practice.md#fb12) · P1
- [FB13 拒绝策略为什么是策略模式，也是业务过载语义](docs/40-backend/31-design-patterns-in-practice.md#fb13) · P0
- [FB14 模板方法与模板加回调的扩展方式有什么不同](docs/40-backend/31-design-patterns-in-practice.md#fb14) · P1
- [FB15 从分层模型讲到 URL 请求与页面渲染](docs/40-backend/32-network-protocol-details.md#fb15) · P0
- [FB16 TCP 与 UDP 的服务模型如何影响应用设计](docs/40-backend/32-network-protocol-details.md#fb16) · P0
- [FB17 握手、半关闭和 TIME_WAIT 应怎样连起来](docs/40-backend/32-network-protocol-details.md#fb17) · P0
- [FB18 ARP 查询的是最终服务器还是下一跳](docs/40-backend/32-network-protocol-details.md#fb18) · P1
- [FB19 可靠传输、流量控制与拥塞控制分别保护什么](docs/40-backend/32-network-protocol-details.md#fb19) · P0
- [FB20 如何解释慢启动，而不把 Reno 当作所有 TCP](docs/40-backend/32-network-protocol-details.md#fb20) · P1
- [FB21 如何设计不会被拆包、粘连和超长输入破坏的分帧](docs/40-backend/32-network-protocol-details.md#fb21) · P0
- [FB22 HTTP/1.1、HTTP/2、HTTP/3 的阻塞分别在哪里](docs/40-backend/32-network-protocol-details.md#fb22) · P0
- [FB23 TLS 1.3 如何完成认证与密钥建立](docs/40-backend/32-network-protocol-details.md#fb23) · P0
- [FB24 DNS 递归、迭代和缓存如何影响排障](docs/40-backend/32-network-protocol-details.md#fb24) · P1
- [FB25 进程、线程和状态转换如何共同解释并发](docs/40-backend/33-operating-system-details.md#fb25) · P0
- [FB26 死锁四条件与预防、避免、检测怎样区分](docs/40-backend/33-operating-system-details.md#fb26) · P0
- [FB27 虚拟内存为什么不等于把磁盘当内存](docs/40-backend/33-operating-system-details.md#fb27) · P0
- [FB28 内存对齐与大小端是同一个问题吗](docs/40-backend/33-operating-system-details.md#fb28) · P1
- [FB29 哈希表加双向链表怎样实现 LRU 并验证边界](docs/40-backend/33-operating-system-details.md#fb29) · P0
- [FB30 用户态进入内核意味着什么，何时发生切换](docs/40-backend/33-operating-system-details.md#fb30) · P1
- [FB31 删除文件名后空间为什么还在，软链接怎样解析](docs/40-backend/33-operating-system-details.md#fb31) · P0
- [FB32 调度算法如何在吞吐、响应、公平之间取舍](docs/40-backend/33-operating-system-details.md#fb32) · P1
- [FB33 布隆过滤器怎样选参数并跟上实体增删](docs/50-projects/teaching-case-review-and-seckill.md#fb33) · P0
- [FB34 请求上下文怎样避免 ThreadLocal 泄漏和串用户](docs/50-projects/teaching-case-review-and-seckill.md#fb34) · P0
- [FB35 项目难点、规模与架构怎样讲出证据而不编经历](docs/50-projects/teaching-case-review-and-seckill.md#fb35) · P0
- [FB36 附近商户的距离、评分与营业条件怎样组合查询](docs/50-projects/teaching-case-review-and-seckill.md#fb36) · P1
- [FB37 突发流量如何变成容量模型和分层保护](docs/50-projects/teaching-case-review-and-seckill.md#fb37) · P0
- [FB38 Lua 怎样原子校验库存与一人一单，代码缺什么就不能声称防超卖](docs/50-projects/teaching-case-review-and-seckill.md#fb38) · P0
- [FB39 两级缓存失效失败、乱序与旧值回填如何恢复](docs/50-projects/teaching-case-review-and-seckill.md#fb39) · P0
- [FB40 怎样把详情、库存、会话和对话的缓存边界分开](docs/50-projects/teaching-case-review-and-seckill.md#fb40) · P0
- [FB41 秒杀防刷怎样分层并控制误伤](docs/50-projects/teaching-case-review-and-seckill.md#fb41) · P0
- [FB42 穿透、击穿、雪崩与预热怎样形成闭环](docs/50-projects/teaching-case-review-and-seckill.md#fb42) · P0
- [FB43 Sentinel 的故障判定、授权与选副本为何是三件事](docs/50-projects/teaching-case-review-and-seckill.md#fb43) · P0
- [FB44 看门狗、异步复制和库存账本的安全边界是什么](docs/50-projects/teaching-case-review-and-seckill.md#fb44) · P0
- [FB45 关键依赖故障如何降级而不把故障扩大](docs/50-projects/teaching-case-review-and-seckill.md#fb45) · P0
- [FB46 异步订单怎样处理 Lua 成功、消息失败和落库重复](docs/50-projects/teaching-case-review-and-seckill.md#fb46) · P0
- [FB47 Caffeine 如何用准入和淘汰抵抗一次性扫描](docs/50-projects/teaching-case-review-and-seckill.md#fb47) · P1
- [FB48 何时分库分表，路由、查询与扩容怎样一起设计](docs/50-projects/teaching-case-review-and-seckill.md#fb48) · P1
- [FB49 JWT 刷新、注销和共享会话如何设计](docs/50-projects/teaching-case-review-and-seckill.md#fb49) · P0
- [FB50 异步下单受理以后如何反馈真实结果](docs/50-projects/teaching-case-review-and-seckill.md#fb50) · P0
- [FB51 防超卖为什么应优先证明数据库不变量](docs/50-projects/teaching-case-review-and-seckill.md#fb51) · P0
- [FB52 客服工具与会话存储怎样明确权限、顺序和副作用](docs/50-projects/teaching-case-review-and-seckill.md#fb52) · P0
- [FB53 CAP 的 C 和 A 应怎样按故障模型理解](docs/40-backend/34-distributed-systems-details.md#fb53) · P1
- [FB54 分布式锁怎样实现所有权、重入和过期写保护](docs/40-backend/34-distributed-systems-details.md#fb54) · P0
- [FB55 Redlock 的多数租约需要哪些假设](docs/40-backend/34-distributed-systems-details.md#fb55) · P1
- [FB56 2PC、TCC、Saga、Outbox 怎样围绕不变量选择](docs/40-backend/34-distributed-systems-details.md#fb56) · P1
- [FB57 唯一标识怎样在顺序、可用性和恢复之间取舍](docs/40-backend/34-distributed-systems-details.md#fb57) · P0
- [FB58 RPC 和 HTTP 为什么不是同一层次的替代品](docs/40-backend/34-distributed-systems-details.md#fb58) · P0
- [FB59 Dubbo 注册中心和调用路径怎样分工](docs/40-backend/34-distributed-systems-details.md#fb59) · P1
- [FB60 消息积压怎样扩容才会真正追上](docs/40-backend/34-distributed-systems-details.md#fb60) · P0
- [FB61 一致性哈希和虚拟节点解决了什么，没解决什么](docs/40-backend/34-distributed-systems-details.md#fb61) · P1
- [FB62 复制、Sentinel、Cluster 的职责怎样区别](docs/40-backend/34-distributed-systems-details.md#fb62) · P0
- [FB63 Quartz、XXL-JOB、ElasticJob 如何按任务语义选择](docs/40-backend/34-distributed-systems-details.md#fb63) · P1
- [FB64 常用文件命令怎样操作才不把排障变成事故](docs/40-backend/35-linux-operations-practice.md#fb64) · P0
- [FB65 怎样定位进程并优雅终止，何时才用 KILL](docs/40-backend/35-linux-operations-practice.md#fb65) · P0
- [FB66 top、free、vmstat、df、du 各能证明什么](docs/40-backend/35-linux-operations-practice.md#fb66) · P0
- [FB67 只有十件库存，怎样让大量无效抢购早停](docs/70-practice/scenario-backend-worked-answers.md#fb67) · P0
- [FB68 面试中的 QPS、并行流与扩容收益怎样证明](docs/70-practice/scenario-backend-worked-answers.md#fb68) · P0
- [FB69 订单接口突然超时，按什么证据缩小范围](docs/70-practice/scenario-backend-worked-answers.md#fb69) · P0
- [FB70 深分页怎样降低回表，又怎样真正避开大 OFFSET](docs/70-practice/scenario-backend-worked-answers.md#fb70) · P0
- [FB71 秒杀和突增事故如何按不变量与应急顺序回答](docs/70-practice/scenario-backend-worked-answers.md#fb71) · P0
- [FB72 高 CPU 与 OOM 怎样留下能解释原因的证据](docs/70-practice/scenario-backend-worked-answers.md#fb72) · P0
- [FB73 下单幂等为什么需要结果状态，而不只是 SET NX](docs/70-practice/scenario-backend-worked-answers.md#fb73) · P0
- [FB74 短链从创建到跳转有哪些必须解释的边界](docs/70-practice/scenario-backend-worked-answers.md#fb74) · P1
- [FB75 支付超时与重复请求如何避免重复扣款](docs/70-practice/scenario-backend-worked-answers.md#fb75) · P0
- [FB76 慢 HTTP 依赖怎样隔离，CompletableFuture 为何不够](docs/70-practice/scenario-backend-worked-answers.md#fb76) · P0
- [FB77 唯一索引写入成本为什么不能一句“普通索引更快”](docs/70-practice/scenario-backend-worked-answers.md#fb77) · P1
- [FB78 令牌桶、漏桶与分布式全局限额怎样取舍](docs/70-practice/scenario-backend-worked-answers.md#fb78) · P0
- [FB79 Spring AI、Flux 和多人流式会话各负责哪一层](docs/40-backend/36-interview-followup-topics.md#fb79) · P0
- [FB80 关注、粉丝、点赞与会员系统怎样设计可验证的数据模型](docs/40-backend/36-interview-followup-topics.md#fb80) · P1
- [FB81 通知和并发文件导出怎样定义成功及恢复](docs/40-backend/36-interview-followup-topics.md#fb81) · P0
- [FB82 Git 分支和 CI/CD 怎样支持并行开发并保留回退](docs/40-backend/36-interview-followup-topics.md#fb82) · P0
- [FB83 Tomcat 线程池与数据库连接池为何要一起算预算](docs/40-backend/36-interview-followup-topics.md#fb83) · P0
- [FB84 Docker 与 Kubernetes 基础如何与发布可靠性相连](docs/40-backend/36-interview-followup-topics.md#fb84) · P1
- [FB85 认证、RBAC、对象级权限与 Secret 如何贯穿工具链](docs/40-backend/36-interview-followup-topics.md#fb85) · P0
- [FB86 IP 和 TCP 报文头哪些字段与排障真正相关](docs/40-backend/36-interview-followup-topics.md#fb86) · P1
- [FB87 Redis 消息、广播与备份恢复怎样避免能力混淆](docs/40-backend/36-interview-followup-topics.md#fb87) · P1
- [FB88 红黑树、跳表与 B+ 树为什么有不同的性能目标](docs/40-backend/36-interview-followup-topics.md#fb88) · P1
- [FB89 排序题如何从不变量推导快速排序的平均与最坏复杂度](docs/40-backend/36-interview-followup-topics.md#fb89) · P1
- [FB90 列表尾删、按值查找和哈希碰撞如何按实际操作计算成本](docs/40-backend/36-interview-followup-topics.md#fb90) · P1
- [FB91 强一致、最终一致、读己之写和几秒延迟如何区分](docs/40-backend/36-interview-followup-topics.md#fb91) · P0
- [FB92 知识库增量更新怎样处理修改、删除与 ACL 变化](docs/40-backend/36-interview-followup-topics.md#fb92) · P1
- [FB93 点评与订单教学案例的数据表如何按职责设计](docs/40-backend/36-interview-followup-topics.md#fb93) · P1

## SQL详解 · 9题

- [S01 怎样生成稳定的行号，又不改变并列名次？](docs/70-practice/sql-nine-worked-problems.md#s01) · P0
- [S02 怎样求每个用户最长连续登录天数？](docs/70-practice/sql-nine-worked-problems.md#s02) · P0
- [S03 过滤后分页，为什么必须把排序条件补完整？](docs/70-practice/sql-nine-worked-problems.md#s03) · P0
- [S04 统计所有部门的人数、平均工资，空部门怎么办？](docs/70-practice/sql-nine-worked-problems.md#s04) · P0
- [S05 统计一整年的用户消费，WHERE和HAVING怎么分？](docs/70-practice/sql-nine-worked-problems.md#s05) · P0
- [S06 怎样真实构造并解释两个事务的死锁？](docs/70-practice/sql-nine-worked-problems.md#s06) · P1
- [S07 库存扣减一定要先FOR UPDATE吗？](docs/70-practice/sql-nine-worked-problems.md#s07) · P0
- [S08 写“异常时ROLLBACK”就算完整转账了吗？](docs/70-practice/sql-nine-worked-problems.md#s08) · P0
- [S09 怎样解释覆盖索引，而不是把SELECT列全部加进索引？](docs/70-practice/sql-nine-worked-problems.md#s09) · P1

## 推理练习 · 12题

- [R01 1000个候选中一个异常，二值测试需要多少位？](docs/70-practice/reasoning-twelve-puzzles.md#r01) · P2
- [R02 5升和6升容器，怎样量出3升？](docs/70-practice/reasoning-twelve-puzzles.md#r02) · P2
- [R03 10、7、3升容器，怎样把10升分成5和5？](docs/70-practice/reasoning-twelve-puzzles.md#r03) · P2
- [R04 7升和11升容器，怎样量2升，并把它写成通用算法？](docs/70-practice/reasoning-twelve-puzzles.md#r04) · P2
- [R05 4分钟和7分钟沙漏，怎样从开始时刻量9分钟？](docs/70-practice/reasoning-twelve-puzzles.md#r05) · P2
- [R06 每根燃尽一小时的不均匀绳子，怎样计75分钟？](docs/70-practice/reasoning-twelve-puzzles.md#r06) · P2
- [R07 25匹马、5赛道，怎样确定有序前三，并说明为什么6场不够？](docs/70-practice/reasoning-twelve-puzzles.md#r07) · P2
- [R08 64匹马、8赛道找前四，“11场最少”能直接相信吗？](docs/70-practice/reasoning-twelve-puzzles.md#r08) · P2
- [R09 海盗分100枚金币，为什么97和98都可能出现？](docs/70-practice/reasoning-twelve-puzzles.md#r09) · P2
- [R10 七天工资用金条支付，为什么1、2、4需要允许找零？](docs/70-practice/reasoning-twelve-puzzles.md#r10) · P2
- [R11 五人顺序取100颗豆，最多和最少者淘汰，谁最安全？](docs/70-practice/reasoning-twelve-puzzles.md#r11) · P2
- [R12 20元汽水、2空瓶换1瓶，到底39还是40瓶？](docs/70-practice/reasoning-twelve-puzzles.md#r12) · P2

## 面经算法补充 · 6题

- [X01 原地反转句中单词，Python字符串可以直接改吗？](docs/70-practice/interview-algorithm-supplements.md#x01) · P1
- [X02 奇数位递增、偶数位递减的链表，如何线性排序？](docs/70-practice/interview-algorithm-supplements.md#x02) · P1
- [X03 不用大整数转换，怎样把两个十进制字符串相加？](docs/70-practice/interview-algorithm-supplements.md#x03) · P0
- [X04 怎样构造小于N的最大整数，原题少条件时怎么办？](docs/70-practice/interview-algorithm-supplements.md#x04) · P1
- [X05 删除排序链表里所有重复值，和保留一个重复值有什么区别？](docs/70-practice/interview-algorithm-supplements.md#x05) · P0
- [X06 判断两个字符串是不是字母异位词，字符范围为什么重要？](docs/70-practice/interview-algorithm-supplements.md#x06) · P0

## LeetCode Hot100 · 100道Python题

官方题号与上述讲义题号分开；算法难度不等于学习优先级。

### 哈希

- [LC1 两数之和](docs/80-hot100/problems/0001-two-sum.md) · 简单
- [LC49 字母异位词分组](docs/80-hot100/problems/0049-group-anagrams.md) · 中等
- [LC128 最长连续序列](docs/80-hot100/problems/0128-longest-consecutive-sequence.md) · 中等

### 双指针

- [LC283 移动零](docs/80-hot100/problems/0283-move-zeroes.md) · 简单
- [LC11 盛最多水的容器](docs/80-hot100/problems/0011-container-with-most-water.md) · 中等
- [LC15 三数之和](docs/80-hot100/problems/0015-3sum.md) · 中等
- [LC42 接雨水](docs/80-hot100/problems/0042-trapping-rain-water.md) · 困难

### 滑动窗口

- [LC3 无重复字符的最长子串](docs/80-hot100/problems/0003-longest-substring-without-repeating-characters.md) · 中等
- [LC438 找到字符串中所有字母异位词](docs/80-hot100/problems/0438-find-all-anagrams-in-a-string.md) · 中等

### 子串

- [LC560 和为 K 的子数组](docs/80-hot100/problems/0560-subarray-sum-equals-k.md) · 中等
- [LC239 滑动窗口最大值](docs/80-hot100/problems/0239-sliding-window-maximum.md) · 困难
- [LC76 最小覆盖子串](docs/80-hot100/problems/0076-minimum-window-substring.md) · 困难

### 普通数组

- [LC53 最大子数组和](docs/80-hot100/problems/0053-maximum-subarray.md) · 中等
- [LC56 合并区间](docs/80-hot100/problems/0056-merge-intervals.md) · 中等
- [LC189 轮转数组](docs/80-hot100/problems/0189-rotate-array.md) · 中等
- [LC238 除了自身以外数组的乘积](docs/80-hot100/problems/0238-product-of-array-except-self.md) · 中等
- [LC41 缺失的第一个正数](docs/80-hot100/problems/0041-first-missing-positive.md) · 困难

### 矩阵

- [LC73 矩阵置零](docs/80-hot100/problems/0073-set-matrix-zeroes.md) · 中等
- [LC54 螺旋矩阵](docs/80-hot100/problems/0054-spiral-matrix.md) · 中等
- [LC48 旋转图像](docs/80-hot100/problems/0048-rotate-image.md) · 中等
- [LC240 搜索二维矩阵 II](docs/80-hot100/problems/0240-search-a-2d-matrix-ii.md) · 中等

### 链表

- [LC160 相交链表](docs/80-hot100/problems/0160-intersection-of-two-linked-lists.md) · 简单
- [LC206 反转链表](docs/80-hot100/problems/0206-reverse-linked-list.md) · 简单
- [LC234 回文链表](docs/80-hot100/problems/0234-palindrome-linked-list.md) · 简单
- [LC141 环形链表](docs/80-hot100/problems/0141-linked-list-cycle.md) · 简单
- [LC142 环形链表 II](docs/80-hot100/problems/0142-linked-list-cycle-ii.md) · 中等
- [LC21 合并两个有序链表](docs/80-hot100/problems/0021-merge-two-sorted-lists.md) · 简单
- [LC2 两数相加](docs/80-hot100/problems/0002-add-two-numbers.md) · 中等
- [LC19 删除链表的倒数第 N 个结点](docs/80-hot100/problems/0019-remove-nth-node-from-end-of-list.md) · 中等
- [LC24 两两交换链表中的节点](docs/80-hot100/problems/0024-swap-nodes-in-pairs.md) · 中等
- [LC25 K 个一组翻转链表](docs/80-hot100/problems/0025-reverse-nodes-in-k-group.md) · 困难
- [LC138 随机链表的复制](docs/80-hot100/problems/0138-copy-list-with-random-pointer.md) · 中等
- [LC148 排序链表](docs/80-hot100/problems/0148-sort-list.md) · 中等
- [LC23 合并 K 个升序链表](docs/80-hot100/problems/0023-merge-k-sorted-lists.md) · 困难
- [LC146 LRU 缓存](docs/80-hot100/problems/0146-lru-cache.md) · 中等

### 二叉树

- [LC94 二叉树的中序遍历](docs/80-hot100/problems/0094-binary-tree-inorder-traversal.md) · 简单
- [LC104 二叉树的最大深度](docs/80-hot100/problems/0104-maximum-depth-of-binary-tree.md) · 简单
- [LC226 翻转二叉树](docs/80-hot100/problems/0226-invert-binary-tree.md) · 简单
- [LC101 对称二叉树](docs/80-hot100/problems/0101-symmetric-tree.md) · 简单
- [LC543 二叉树的直径](docs/80-hot100/problems/0543-diameter-of-binary-tree.md) · 简单
- [LC102 二叉树的层序遍历](docs/80-hot100/problems/0102-binary-tree-level-order-traversal.md) · 中等
- [LC108 将有序数组转换为二叉搜索树](docs/80-hot100/problems/0108-convert-sorted-array-to-binary-search-tree.md) · 简单
- [LC98 验证二叉搜索树](docs/80-hot100/problems/0098-validate-binary-search-tree.md) · 中等
- [LC230 二叉搜索树中第 K 小的元素](docs/80-hot100/problems/0230-kth-smallest-element-in-a-bst.md) · 中等
- [LC199 二叉树的右视图](docs/80-hot100/problems/0199-binary-tree-right-side-view.md) · 中等
- [LC114 二叉树展开为链表](docs/80-hot100/problems/0114-flatten-binary-tree-to-linked-list.md) · 中等
- [LC105 从前序与中序遍历序列构造二叉树](docs/80-hot100/problems/0105-construct-binary-tree-from-preorder-and-inorder-traversal.md) · 中等
- [LC437 路径总和 III](docs/80-hot100/problems/0437-path-sum-iii.md) · 中等
- [LC236 二叉树的最近公共祖先](docs/80-hot100/problems/0236-lowest-common-ancestor-of-a-binary-tree.md) · 中等
- [LC124 二叉树中的最大路径和](docs/80-hot100/problems/0124-binary-tree-maximum-path-sum.md) · 困难

### 图论

- [LC200 岛屿数量](docs/80-hot100/problems/0200-number-of-islands.md) · 中等
- [LC994 腐烂的橘子](docs/80-hot100/problems/0994-rotting-oranges.md) · 中等
- [LC207 课程表](docs/80-hot100/problems/0207-course-schedule.md) · 中等
- [LC208 实现 Trie (前缀树)](docs/80-hot100/problems/0208-implement-trie-prefix-tree.md) · 中等

### 回溯

- [LC46 全排列](docs/80-hot100/problems/0046-permutations.md) · 中等
- [LC78 子集](docs/80-hot100/problems/0078-subsets.md) · 中等
- [LC17 电话号码的字母组合](docs/80-hot100/problems/0017-letter-combinations-of-a-phone-number.md) · 中等
- [LC39 组合总和](docs/80-hot100/problems/0039-combination-sum.md) · 中等
- [LC22 括号生成](docs/80-hot100/problems/0022-generate-parentheses.md) · 中等
- [LC79 单词搜索](docs/80-hot100/problems/0079-word-search.md) · 中等
- [LC131 分割回文串](docs/80-hot100/problems/0131-palindrome-partitioning.md) · 中等
- [LC51 N 皇后](docs/80-hot100/problems/0051-n-queens.md) · 困难

### 二分查找

- [LC35 搜索插入位置](docs/80-hot100/problems/0035-search-insert-position.md) · 简单
- [LC74 搜索二维矩阵](docs/80-hot100/problems/0074-search-a-2d-matrix.md) · 中等
- [LC34 在排序数组中查找元素的第一个和最后一个位置](docs/80-hot100/problems/0034-find-first-and-last-position-of-element-in-sorted-array.md) · 中等
- [LC33 搜索旋转排序数组](docs/80-hot100/problems/0033-search-in-rotated-sorted-array.md) · 中等
- [LC153 寻找旋转排序数组中的最小值](docs/80-hot100/problems/0153-find-minimum-in-rotated-sorted-array.md) · 中等
- [LC4 寻找两个正序数组的中位数](docs/80-hot100/problems/0004-median-of-two-sorted-arrays.md) · 困难

### 栈

- [LC20 有效的括号](docs/80-hot100/problems/0020-valid-parentheses.md) · 简单
- [LC155 最小栈](docs/80-hot100/problems/0155-min-stack.md) · 中等
- [LC394 字符串解码](docs/80-hot100/problems/0394-decode-string.md) · 中等
- [LC739 每日温度](docs/80-hot100/problems/0739-daily-temperatures.md) · 中等
- [LC84 柱状图中最大的矩形](docs/80-hot100/problems/0084-largest-rectangle-in-histogram.md) · 困难

### 堆

- [LC215 数组中的第K个最大元素](docs/80-hot100/problems/0215-kth-largest-element-in-an-array.md) · 中等
- [LC347 前 K 个高频元素](docs/80-hot100/problems/0347-top-k-frequent-elements.md) · 中等
- [LC295 数据流的中位数](docs/80-hot100/problems/0295-find-median-from-data-stream.md) · 困难

### 贪心算法

- [LC121 买卖股票的最佳时机](docs/80-hot100/problems/0121-best-time-to-buy-and-sell-stock.md) · 简单
- [LC55 跳跃游戏](docs/80-hot100/problems/0055-jump-game.md) · 中等
- [LC45 跳跃游戏 II](docs/80-hot100/problems/0045-jump-game-ii.md) · 中等
- [LC763 划分字母区间](docs/80-hot100/problems/0763-partition-labels.md) · 中等

### 动态规划

- [LC70 爬楼梯](docs/80-hot100/problems/0070-climbing-stairs.md) · 简单
- [LC118 杨辉三角](docs/80-hot100/problems/0118-pascals-triangle.md) · 简单
- [LC198 打家劫舍](docs/80-hot100/problems/0198-house-robber.md) · 中等
- [LC279 完全平方数](docs/80-hot100/problems/0279-perfect-squares.md) · 中等
- [LC322 零钱兑换](docs/80-hot100/problems/0322-coin-change.md) · 中等
- [LC139 单词拆分](docs/80-hot100/problems/0139-word-break.md) · 中等
- [LC300 最长递增子序列](docs/80-hot100/problems/0300-longest-increasing-subsequence.md) · 中等
- [LC152 乘积最大子数组](docs/80-hot100/problems/0152-maximum-product-subarray.md) · 中等
- [LC416 分割等和子集](docs/80-hot100/problems/0416-partition-equal-subset-sum.md) · 中等
- [LC32 最长有效括号](docs/80-hot100/problems/0032-longest-valid-parentheses.md) · 困难

### 多维动态规划

- [LC62 不同路径](docs/80-hot100/problems/0062-unique-paths.md) · 中等
- [LC64 最小路径和](docs/80-hot100/problems/0064-minimum-path-sum.md) · 中等
- [LC5 最长回文子串](docs/80-hot100/problems/0005-longest-palindromic-substring.md) · 中等
- [LC1143 最长公共子序列](docs/80-hot100/problems/1143-longest-common-subsequence.md) · 中等
- [LC72 编辑距离](docs/80-hot100/problems/0072-edit-distance.md) · 中等

### 技巧

- [LC136 只出现一次的数字](docs/80-hot100/problems/0136-single-number.md) · 简单
- [LC169 多数元素](docs/80-hot100/problems/0169-majority-element.md) · 简单
- [LC75 颜色分类](docs/80-hot100/problems/0075-sort-colors.md) · 中等
- [LC31 下一个排列](docs/80-hot100/problems/0031-next-permutation.md) · 中等
- [LC287 寻找重复数](docs/80-hot100/problems/0287-find-the-duplicate-number.md) · 中等


## 算法基础补充 · 15道外部资源题（不计入Hot100）

来自代码随想录（程序员Carl）的官方讲解、Python区和本题/相关视频外链；只有资源与自主复习提示，没有新增原创实现或AC记录。

- [77. 组合](docs/85-algorithm-supplement/README.md#problem-77) · 回溯 · 中等 · 外部资源
- [704. 二分查找](docs/85-algorithm-supplement/README.md#problem-704) · 二分查找 · 简单 · 外部资源
- [27. 移除元素](docs/85-algorithm-supplement/README.md#problem-27) · 双指针 · 简单 · 外部资源
- [977. 有序数组的平方](docs/85-algorithm-supplement/README.md#problem-977) · 双指针 · 简单 · 外部资源
- [209. 长度最小的子数组](docs/85-algorithm-supplement/README.md#problem-209) · 滑动窗口 · 中等 · 外部资源
- [59. 螺旋矩阵II](docs/85-algorithm-supplement/README.md#problem-59) · 矩阵 · 中等 · 外部资源
- [203. 移除链表元素](docs/85-algorithm-supplement/README.md#problem-203) · 链表 · 简单 · 外部资源
- [707. 设计链表](docs/85-algorithm-supplement/README.md#problem-707) · 链表 · 中等 · 外部资源
- [242. 有效的字母异位词](docs/85-algorithm-supplement/README.md#problem-242) · 哈希 · 简单 · 外部资源
- [349. 两个数组的交集](docs/85-algorithm-supplement/README.md#problem-349) · 哈希 · 简单 · 外部资源
- [202. 快乐数](docs/85-algorithm-supplement/README.md#problem-202) · 哈希 · 简单 · 外部资源
- [344. 反转字符串](docs/85-algorithm-supplement/README.md#problem-344) · 字符串 · 简单 · 外部资源
- [151. 翻转字符串里的单词](docs/85-algorithm-supplement/README.md#problem-151) · 字符串 · 中等 · 外部资源
- [232. 用栈实现队列](docs/85-algorithm-supplement/README.md#problem-232) · 栈与队列 · 简单 · 外部资源
- [225. 用队列实现栈](docs/85-algorithm-supplement/README.md#problem-225) · 栈与队列 · 简单 · 外部资源
