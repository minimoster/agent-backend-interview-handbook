# AI Agent 与后端开发学习手册

从 Agent 应用到后端工程，系统学习核心知识、项目实践与面试方法。

用一个小项目连接 Java 或 Go、HTTP、数据库、并发与模型工具调用。每个主题配合例子、追问和练习，帮助你从“看过”走到“能解释、能实现、能验证”。

## 开始学习

1. [学习路线：用一个项目串起 Agent 与后端](docs/00-guide/expanded-map-and-study-plan.md)：六周安排、每日练法、项目任务与进阶入口
2. [题目索引](QUESTION_INDEX.md)：按题号与学习优先级找问题
3. [在线阅读](https://minimoster.github.io/agent-backend-interview-handbook/)：全文搜索、专题筛选、折叠详解、字号调整和本机收藏

离线阅读：下载仓库，用浏览器打开 [site/index.html](site/index.html)。[打开与更新说明](site/README.md)

## 核心知识

### AI Agent 与大模型应用

[完整专题目录](docs/10-agent/README.md)

- [Transformer 先修与前向小实验](docs/10-agent/05-transformer-prerequisite.md)
- [Agent loop、工具、状态与编排](docs/10-agent/01-agent-loop-tools-and-state.md)
- [RAG、检索与重排](docs/10-agent/02-rag-retrieval-and-reranking.md)
- [Memory 与上下文管理](docs/10-agent/03-memory-and-context.md)
- [SSE、异步任务与可靠执行](docs/10-agent/04-streaming-and-reliable-execution.md)
- [评测、模型路由与上下文消融](docs/10-agent/25-agent-evaluation-and-routing.md)
- [框架选型与组件集成](docs/10-agent/29-framework-selection-and-integration.md)
- [工具、MCP 与 Skill](docs/10-agent/31-tool-mcp-and-skill-contracts.md)
- [虾皮 Agent 一二面 34 题](docs/10-agent/34-shopee-agent-interview-playbook.md)：RAG、记忆、Coding Agent、PRD/TD 与会议 Skill

### Java

[完整专题目录](docs/20-java/README.md)

- [集合与语言基础](docs/20-java/01-language-and-collections.md)
- [并发基础与线程池](docs/20-java/02-concurrency-and-thread-pools.md)
- [JVM 与类加载](docs/20-java/03-jvm-and-classloading.md)
- [Spring 与后端基础](docs/20-java/04-spring-and-backend.md)
- [Agent 接口工程](docs/20-java/05-agent-integration.md)
- [执行器的排队、超时与取消](docs/20-java/16-executor-failure-followups.md)

### Go

[完整专题目录](docs/30-go/README.md)

- [并发、取消与同步](docs/30-go/01-concurrency.md)
- [容器、类型与错误](docs/30-go/02-types-containers-and-errors.md)
- [内存、GC 与性能](docs/30-go/03-memory-gc-and-performance.md)
- [HTTP、SSE、gRPC 与服务治理](docs/30-go/04-http-sse-grpc.md)
- [测试与故障排查](docs/30-go/05-testing-and-debugging.md)
- [有界任务与资源收尾](docs/30-go/07-concurrency-failure-followups.md)

### 后端通用基础

[完整专题目录](docs/40-backend/README.md)

- [网络与流式接口](docs/40-backend/01-network-and-streaming.md)
- [数据库与 SQL](docs/40-backend/02-databases-and-sql.md)
- [Redis 与缓存正确性](docs/40-backend/03-redis-and-caching.md)
- [消息队列与幂等](docs/40-backend/04-messaging-and-idempotency.md)
- [系统设计与故障处理](docs/40-backend/05-system-design-and-reliability.md)
- [Linux 与容器](docs/40-backend/06-linux-and-containers.md)
- [提交、重放与旧写保护](docs/40-backend/41-storage-recovery-followups.md)
- [Python 与 FastAPI](docs/40-backend/40-python-fastapi-lab.md)

## 动手练习

- [Agent 自测](docs/70-practice/agent-labs.md)、[Go 小实验](docs/70-practice/go-labs.md)、[Java 小实验](docs/70-practice/java-labs.md)
- [Hot100：按 17 类学习 100 道 Python 题](docs/80-hot100/README.md)、[解题方法对照](docs/80-hot100/PATTERNS.md)
- [算法基础补充：15 道题解](docs/85-algorithm-supplement/README.md)
- [算法与 SQL 练习单](docs/70-practice/algorithm-and-sql-plan.md)、[SQL 九题](docs/70-practice/sql-nine-worked-problems.md)
- [十二类推理题](docs/70-practice/reasoning-twelve-puzzles.md)、[六个算法变体解法](docs/70-practice/interview-algorithm-supplements.md)
- [AI Coding 练习与参考内核](docs/70-practice/ai-coding-exercises.md)
- [26 张场景卡](docs/90-public-interview-scenarios/README.md)：Agent 应用与后端可靠性

## 项目与面试复盘

- [公开仓库技术案例](docs/50-projects/public-repository-case-studies.md)、[数据工程 Agent 案例](docs/50-projects/data-engineering-agent-case.md)
- [技术、HR 与负责人追问准备](docs/90-interview/01-evidence-based-interview-preparation.md)
- 综合训练：[Agent](docs/60-interviews/agent.md) · [Java](docs/60-interviews/java.md) · [Go](docs/60-interviews/go.md) · [后端](docs/60-interviews/backend.md)

把训练中的问题带回知识章节，练习原理、实现与失败场景；用自己的代码和运行记录整理项目表达。

## 版本与维护

[版本与纠错](errata/README.md) · [修订方式](CONTRIBUTING.md)

具体版本、题设与实验状态在对应章节说明，构建与测试结果另列；依法需要的版权与许可声明保持不变。

最后整理日期：2026-10-16。
