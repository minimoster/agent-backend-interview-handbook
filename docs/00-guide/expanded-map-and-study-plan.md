# 学习路线：用一个项目串起 Agent 与后端

[返回总目录](../../README.md) · [题号索引](../../QUESTION_INDEX.md)

从一个能运行的小服务开始，逐步加入数据库、并发、检索和工具调用。每学一个概念，就给项目增加一个可解释的行为，再用测试检查它。六周安排是一份节奏参考；基础较少或时间有限时，可以把一周拆成两周。

<a id="learning-main-language"></a>
## 先确定学习主线

选择 Java 或 Go 作为主语言，先掌握 HTTP、SQL、并发、错误处理和测试，再把这些能力用于 Agent 应用。另一门语言用于比较概念，需要时再深入。

- Java：语言与集合 → JUC → JVM → Spring/MyBatis → 数据库与缓存 → Agent 接口
- Go：类型与接口 → goroutine/channel/context → 同步与竞态 → HTTP 与数据库 → 可靠任务 → Agent 接口
- Agent：Transformer 基础 → 模型调用与工具循环 → RAG → 上下文与记忆 → 持久任务 → 评测与复杂编排

P0 用于打基础，P1 用于扩展常用场景，P2 用于按需要深入。先把单 Agent 的任务、状态和失败处理做清楚，再用同一组任务比较多 Agent 的收益与协调成本。

<a id="six-week-plan"></a>
## 六周安排

每周学习五天，每天约两小时。沿用同一个项目和同一份学习记录，周末做一次复盘。算法与 SQL 穿插进行：每次少量新题，重做错题，并解释复杂度与边界输入。

<a id="week-1"></a>
### 第 1 周：写出请求入口

- 读主语言的类型、集合、错误处理、接口与测试，配合[网络基础](../40-backend/01-network-and-streaming.md) B01—B08、[Linux 与进程](../40-backend/06-linux-and-containers.md) B42。
- 写健康检查和简单查询接口，加输入校验、错误码与结构化日志。画出客户端、HTTP 服务、处理函数和存储之间的调用关系。
- 用数组、哈希和双指针题练习输入输出与复杂度；给接口补空参数、无效参数和正常请求三个测试。
- 完成标准：独立运行接口，用一个具体请求解释 GET/POST、TCP 消息边界、TLS 和 SSE 各自解决什么问题。

<a id="week-2"></a>
### 第 2 周：理解数据与并发

- 读[SQL 与事务](../40-backend/02-databases-and-sql.md) B09—B21、[缓存](../40-backend/03-redis-and-caching.md) B22—B30。选定一个数据库及版本，先用订单、库存两张小表练习。
- 比较两种索引的查询计划；用两个数据库会话观察 RC/RR 下的读取变化，并执行并发扣库存。记录执行顺序、受影响行数与最终数据。
- 加旁路缓存，制造并发未命中、删除失败和旧值回填；画出 B26 的时间线，比较 TTL、请求合并、回源并发上限与版本校验。
- Java 练线程池和超时；Go 练 context、channel、mutex 与 race 检测。两条主线都要说明共享状态归谁管理，以及取消后怎样退出。
- 完成标准：解释一条慢 SQL、一个事务竞态和一个缓存竞态，给出可复现步骤与修复测试。B36、B41 用于连接锁、容量与系统可靠性。

<a id="week-3"></a>
### 第 3 周：接入检索与工具

- 读[Agent loop](../10-agent/01-agent-loop-tools-and-state.md)、[RAG](../10-agent/02-rag-retrieval-and-reranking.md)。Q/K/V 和注意力形状不熟时，先做[Transformer 前向小实验](../10-agent/05-transformer-prerequisite.md)。
- 用有权使用的小型语料建立问答接口，展示引用；接入一个范围明确的工具，校验参数、身份和权限。
- 构造检索无结果、证据不够、工具超时三类样例，分别决定拒答、补充输入和重试条件。
- 用[RAG 分块实验](../10-agent/30-rag-data-and-chunking-lab.md)比较分块与召回，用[工具/MCP/Skill](../10-agent/31-tool-mcp-and-skill-contracts.md)区分协议、技能包与执行权限。
- 完成标准：保存一次任务的输入、检索结果、工具参数和回答，解释错误发生在召回、排序、证据使用还是生成阶段。

<a id="week-4"></a>
### 第 4 周：让任务可以恢复

- 读[记忆与上下文](../10-agent/03-memory-and-context.md)、[流式与可靠执行](../10-agent/04-streaming-and-reliable-execution.md)、[消息与幂等](../40-backend/04-messaging-and-idempotency.md) B31—B39。
- 做异步文档处理任务，保存稳定任务身份和执行状态。重复投递同一任务，验证本地业务效果只发生一次。
- 在业务提交后、位点提交前终止消费者，观察重放；再模拟用户断线、取消和迟到结果，检查资源清理与结果查询。
- 为一条跨任务偏好设计写入、修改、删除与权限检查，说明短期上下文和长期记忆各自的作用域。
- 完成标准：用失败时间线解释重试、outbox、幂等与取消之间的关系。涉及外部副作用时，补充未知结果的对账方式。

<a id="week-5"></a>
### 第 5 周：评测、部署与排障

- 读[评测与路由](../10-agent/25-agent-evaluation-and-routing.md)、[生产设计实验](../10-agent/26-agent-production-design-lab.md)，结合 B40、B44—B48 补齐容器、配置、探针、优雅退出、指标与 trace。
- 固定一组任务，分别记录答案质量、失败率、延迟与 token 成本。比较优化前后结果时保持样本和统计方式一致。
- 注入数据库慢、模型超时、重复任务、用户断线和服务终止五种故障，为每种故障写预期行为和恢复步骤。
- 按[业务场景](../10-agent/27-practical-agent-scenarios.md)练审批与未知结果；按[框架选型](../10-agent/29-framework-selection-and-integration.md)说明框架提供了哪些能力、应用还需要补什么。
- 完成标准：别人能按 README 启动项目；每项指标附数据规模、并发数、软件版本与测量方式；能用日志或测试定位一次失败。

<a id="week-6"></a>
### 第 6 周：复盘并讲清项目

- 对照目标任务或岗位说明，把知识分为“已实践、能解释、待补齐”。优先处理影响项目正确性的缺口。
- 做三次计时练习：基础知识 30 分钟、项目追问 30 分钟、算法与 SQL 45 分钟。录下回答，修正因果关系不清的地方。
- 随机抽十道 P0，独立讲机制、举例并回答一个失败场景；给项目中的每个组件回答“为什么需要”“去掉会发生什么”。
- 整理一页项目说明：问题、设计、个人改动、测试、实际结果与下一步。面试表达可参考[项目与追问准备](../90-interview/01-evidence-based-interview-preparation.md)。
- 完成标准：连续三分钟讲清项目，并用代码、图或运行记录回答两层追问。把仍待验证的内容变成下一次实验。

<a id="daily-practice"></a>
## 每天怎样学

- 15 分钟：闭卷复述前一天的两题，标出卡住的概念
- 40 分钟：学习两到四道相关题，画数据流或执行顺序
- 45 分钟：写最小实验、补测试或定位失败
- 20 分钟：用自己的话解释结果，记下下一步

单题按“独立回答 → 读原理 → 手推例子 → 制造反例 → 再次解释”推进。能复述却解释不了反例，就回到原理；能解释却写不出来，就补最小代码；代码能运行却不清楚原因，就缩小实验，只验证一个机制。

<a id="project-workflow"></a>
## 用同一个项目连接知识

项目可以是“带引用的资料问答与任务助手”。第一版保留输入、后端接口、检索、模型回答、引用与日志；后续按六周安排加入缓存、队列、评测和权限。入门工具可以选择只读查询或可恢复的沙盒操作。

一次任务的主流程：用户输入 → 身份与输入校验 → 预算与超时 → 检索或规划 → 权限与参数检查 → 执行 → 结果与来源校验 → 回答 → 日志与评测。

每一段写清输入、输出、失败信号与处理方式。例如，无资料时补充输入或拒答，工具超时时依据执行身份判断是否能重试，结构化输出则同时检查格式和字段含义。

保留架构图、依赖版本与启动说明、脱敏请求日志、固定测试集、改动前后对照和排障记录。架构图标出进程、存储与第三方服务；测试集覆盖正常、无资料、格式错误、超时和重复任务；排障记录写清假设、证据、修复与回归测试。

<a id="followup-route-practice"></a>
## 学习记录与复盘

| 日期 | 题号或主题 | 当前状态 | 下一次验证动作 |
|---|---|---|---|
| 待填 | B01 HTTP 方法 | 未学 / 能解释 / 能复现 / 能追问 | 写重复请求例子，观察副作用 |
| 待填 | 主语言并发 | 待填 | 写取消与退出测试 |
| 待填 | SQL 或缓存 | 待填 | 展示计划或并发时间线 |
| 待填 | Agent 工具调用 | 待填 | 制造失败输入，验证处理 |
| 待填 | 项目的一次改动 | 待填 | 保存前后结果，列下一步 |

每周选出能讲清的三点、容易混淆的两点和下周要做的一个实验。复习时依次检查：术语是否准确、不变量与所有者是谁、失败后怎样恢复、方案如何取舍、测试观察到了什么。

<a id="topic-map"></a>
## 按主题补深度

完成基础后，从当前项目的问题进入对应专题。以下是同一条学习主线的扩展入口。

<a id="followup-route-agent"></a>
### Agent：状态、检索与协作

- [评测与路由](../10-agent/25-agent-evaluation-and-routing.md)：定义失败、成本与升级条件
- [A2A 任务生命周期](../10-agent/32-a2a-task-lifecycle-lab.md)：Message/Task、身份、输入与授权中断、取消竞争、重连与终态
- [工具流组装](../10-agent/33-tool-stream-assembly-lab.md)：事件边界、多调用交错、部分 JSON、完整参数校验与执行身份
- [动态 Top-K 与图谱消融](../10-agent/17-rag-indexes-and-evidence.md#dynamic-top-k-and-graph-ablation)：比较检索方案
- [推理、KV 缓存与批处理](../10-agent/24-inference-and-serving-boundaries.md)：生成参数、延迟预算与容量
- [前沿能力与工程决策](../10-agent/28-frontier-and-engineering-decisions.md)：用任务和评测选择能力
- [虾皮 Agent 34 题](../10-agent/34-shopee-agent-interview-playbook.md)：综合练习 RAG、评测、记忆、Coding Agent 与需求交付

练习：给同一个工具调用画状态与身份表，解释断连、重复 done、取消后的未知副作用。分别测试本地状态逻辑、协议互通和模型效果。

<a id="followup-route-java"></a>
### Java：语言、执行器与框架

从[集合](../20-java/01-language-and-collections.md)、[JMM 与线程池](../20-java/02-concurrency-and-thread-pools.md)、[JVM](../20-java/03-jvm-and-classloading.md)进入[Spring 基础](../20-java/04-spring-and-backend.md)、[事务机制](../20-java/14-spring-mechanisms.md)和[MyBatis 参数映射](../40-backend/21-mybatis.md)。

[执行器故障实验](../20-java/16-executor-failure-followups.md)用于练队列、扩池、拒绝、get 超时与取消、allOf/anyOf、线程上下文和退出。画出 HTTP 线程、异步池、数据库连接和下游额度的持有/等待关系，再运行 19 个 Java 场景；Spring 事务另用容器集成实验验证。

<a id="followup-route-go"></a>
### Go：所有权、取消与退出

从[GMP 与同步](../30-go/01-concurrency.md)、[类型与错误](../30-go/02-types-containers-and-errors.md)、[版本变化](../30-go/06-version-boundaries.md)进入[HTTP/SSE](../30-go/04-http-sse-grpc.md)和[测试与诊断](../30-go/05-testing-and-debugging.md)。

[并发生命周期实验](../30-go/07-concurrency-failure-followups.md)用于练 feed/worker 所有权、select 的取消竞争、排队与预算、Body 与长连接、join 证据。运行测试与 race 检测，解释每个 goroutine 的退出条件。回调需要合作响应取消，Go 没有安全强杀任意 goroutine 的机制。

<a id="followup-route-storage"></a>
### 后端：提交、恢复与排障

[提交与恢复实验](../40-backend/41-storage-recovery-followups.md)连接稳定身份、未知结果、Outbox/Inbox、安全 frontier、资源端 fencing、缓存 floor 和死锁重试范围。[系统设计与排障](../40-backend/42-system-design-debugging-clinic.md)连接尾延迟、队列、SQL 证据、迁移水位和任务 API。

先运行 29 个 SQLite/状态模型测试，再为所用 MySQL、Redis、Kafka 补集成测试。Kafka 实际 offset 可能跳号，消费进度要按实际已处理记录推导，不能直接套用连续整数示例。

<a id="advanced-topics"></a>
### 数据工程与跨栈实践

- [Spark 分区、Stage 与 Shuffle](../40-backend/37-spark-execution-and-diagnostics.md) → [Agent 数据工程案例](../50-projects/data-engineering-agent-case.md)：业务 Job/Attempt、提交对账、取消竞争与长任务事件
- [ES 父子 Join](../40-backend/38-search-parent-child-joins.md#es-parent-join)：和 RAG 父子 chunk 对照数据关系与查询方式
- [投影一致性案例](../50-projects/public-repository-case-studies.md#a44)：读数据写入与索引更新路径，再设计验证
- [跨栈专题](../40-backend/39-cross-stack-interview-boundaries.md)：Mongo 原子写、Python 事件循环、在线迁移、共享 token 与密码哈希
- [Python/FastAPI](../40-backend/40-python-fastapi-lab.md) → [AI Coding 练习](../70-practice/ai-coding-exercises.md)：对象语义、接口与可测试内核
- [LC395 两种解法](../70-practice/interview-algorithm-supplements.md#lc395)：比较分治与窗口方法，阅读 32,800 组有限穷举对照

### 算法、SQL 与推理

[Hot100](../80-hot100/README.md)按模式练习；[算法与 SQL 练习单](../70-practice/algorithm-and-sql-plan.md)保留八项建表与查询任务；[SQL 九题](../70-practice/sql-nine-worked-problems.md)练结果、事务与索引；[十二类推理题](../70-practice/reasoning-twelve-puzzles.md)练题设、构造与证明；[设计模式](../40-backend/31-design-patterns-in-practice.md)练需求、结构与实现的对应关系。

<a id="resume-to-questions"></a>
## 把项目描述变成问题清单

以“实现知识问答缓存，降低重复请求成本”为练习句子，逐层追问：

1. 范围：缓存答案、检索结果还是嵌入？键包含哪些参数？
2. 机制：命中、失效和并发回源怎样工作？权限与租户怎样隔离？
3. 测量：基线、样本、命中率、成本与正确性怎样记录？
4. 失败：文档改动、权限撤回、模型更新、缓存故障时怎样处理？
5. 改动：自己实现或修改了什么？如何审查框架和 AI 生成代码？

用实际产物回答；尚待验证的问题进入学习记录。阅读、复现、改造和独立设计可以分别说明对应工作与结果。

<a id="cache-interview-ladder"></a>
## 缓存项目的递进练习

- 正常路径：用具体 ID 解释构造键、查缓存、回源与写回
- 更新一致性：画数据库提交、删缓存失败、旧读请求回填的并发时间线
- 压力与故障：比较请求合并、过期抖动、限流、降级和负缓存的适用条件
- 锁的失效：区分随机 token 安全解锁与 fencing token；解释资源端怎样拒绝过期持有者
- 测量与取舍：指定负载、延迟分位、错误率与一致性检查，解释测量范围

每次只加一个故障，用两分钟画图、一分钟解释、一分钟说下一步验证。参考[缓存基础](../40-backend/03-redis-and-caching.md)、[系统可靠性](../40-backend/05-system-design-and-reliability.md)与[项目案例](../50-projects/public-repository-case-studies.md)。
