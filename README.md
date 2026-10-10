# AI Agent 与后端实习学习讲义

从原理、例子和失败场景出发，练习能独立解释、验证和追问的技术回答。覆盖 AI Agent、Java、Go 与后端通用基础。

> 部分章节暂未发布。本版包含361道讲义详解与Hot100独立100题，保留已发布题号。另列15道算法基础外部资源题，不计入Hot100或讲义题数。题设条件与未运行集成实验均保留说明。阅读站点UI的检查另行记录。

## 先从这里开始

**在线阅读：** [打开学习讲义](https://minimoster.github.io/agent-backend-interview-handbook/)。支持全文搜索、题号与分类筛选、折叠详解、阅读字号和本机收藏；电脑与手机使用同一份内容。

**离线阅读：** 下载整个仓库后，用浏览器打开 [静态阅读页 `site/index.html`](site/index.html)，不需要联网。[打开与更新说明](site/README.md)。

1. [全主题地图与六周学习路线](docs/00-guide/expanded-map-and-study-plan.md)
2. [基线与扩展题索引](QUESTION_INDEX.md)
3. [来源、日期与证据边界](sources/catalog.md)
4. [版本与纠错记录](errata/README.md)
5. [主题范围与验证](coverage/README.md)
   - [本版验证记录](coverage/VALIDATION.md)
6. [Hot100：按17类学习100道Python题](docs/80-hot100/README.md)
7. [算法基础补充：15道代码随想录官方资源题](docs/85-algorithm-supplement/README.md)
   - [逐题资源覆盖与引用边界](sources/carl-hot100-resources.md)

P0/P1/P2 是学习优先级建议，不是统计考频。先选 Java 或 Go 作为主语言，再把 HTTP、数据库、并发和模型工具调用串成可解释的小项目。

## 内容导航

### AI Agent 与大模型应用

[查看本模块完整专题目录](docs/10-agent/README.md)，含以下基线及新增详解。

- [Agent loop、工具、状态与编排](docs/10-agent/01-agent-loop-tools-and-state.md) · 8题
- [RAG、检索与重排](docs/10-agent/02-rag-retrieval-and-reranking.md) · 10题
- [Memory 与上下文管理](docs/10-agent/03-memory-and-context.md) · 5题
- [SSE、异步任务与可靠执行](docs/10-agent/04-streaming-and-reliable-execution.md) · 7题
- [两个公开仓库的技术案例与贡献边界](docs/50-projects/public-repository-case-studies.md) · 6题

### Java

[查看本模块完整专题目录](docs/20-java/README.md)，含以下基线及新增详解。

- [集合与语言基础](docs/20-java/01-language-and-collections.md) · 8题
- [并发基础与线程池](docs/20-java/02-concurrency-and-thread-pools.md) · 14题
- [JVM 与类加载](docs/20-java/03-jvm-and-classloading.md) · 7题
- [Spring 与后端基础](docs/20-java/04-spring-and-backend.md) · 11题
- [Java 实现 AI Agent 的工程题](docs/20-java/05-agent-integration.md) · 6题

### Go

[查看本模块完整专题目录](docs/30-go/README.md)，含以下基线及新增详解。

- [并发、取消与同步](docs/30-go/01-concurrency.md) · 13题
- [容器、类型与错误](docs/30-go/02-types-containers-and-errors.md) · 9题
- [内存、GC 与性能直觉](docs/30-go/03-memory-gc-and-performance.md) · 4题
- [HTTP、SSE、gRPC 与服务治理](docs/30-go/04-http-sse-grpc.md) · 9题
- [测试与故障排查](docs/30-go/05-testing-and-debugging.md) · 5题

### 后端通用基础

[查看本模块完整专题目录](docs/40-backend/README.md)，含以下基线及新增详解。

- [网络与流式接口](docs/40-backend/01-network-and-streaming.md) · 8题
- [数据库与 SQL](docs/40-backend/02-databases-and-sql.md) · 13题
- [Redis 与缓存正确性](docs/40-backend/03-redis-and-caching.md) · 9题
- [消息队列与幂等](docs/40-backend/04-messaging-and-idempotency.md) · 5题
- [系统设计与故障处理](docs/40-backend/05-system-design-and-reliability.md) · 6题
- [Linux 与容器](docs/40-backend/06-linux-and-containers.md) · 6题
- [安全与面试练习](docs/40-backend/07-security-and-problem-solving.md) · 3题

### 实验与项目表达

- [SQL九题：边界、事务与索引](docs/70-practice/sql-nine-worked-problems.md)
- [十二类推理题与可验证构造](docs/70-practice/reasoning-twelve-puzzles.md)
- [面经算法补充：六个Python解法](docs/70-practice/interview-algorithm-supplements.md)

- [Go 小实验](docs/70-practice/go-labs.md)
- [Java 小实验](docs/70-practice/java-labs.md)
- [Agent 自测](docs/70-practice/agent-labs.md)
- [算法与 SQL 练习](docs/70-practice/algorithm-and-sql-plan.md)
- [公开仓库案例及贡献边界](docs/50-projects/public-repository-case-studies.md)

### LeetCode Hot100 · Python

- [17类课程目录与100题](docs/80-hot100/README.md)
- [解题方法与复杂度对照](docs/80-hot100/PATTERNS.md)
- [源码与运行方式](examples/hot100/README.md)
- [验证范围与测试记录](docs/80-hot100/TESTING.md)

按哈希、双指针、链表、树、图、回溯、二分、栈、堆、贪心与动态规划等分类阅读。每题包含思路、步骤、完整Python代码、复杂度、误区和练习方式；本地测试通过不等于在线判题提交通过。算法的官方难度与讲义P0/P1/P2学习优先级分别展示，不相互替代。

每题另有“代码随想录延伸阅读”，提供核验过的官网讲解、Python区和官方视频外链，作者为代码随想录（程序员Carl）。本题精确资源与相关题迁移资源分别标注；本次未找到精确匹配时保留缺口，主解法保持稳定，原创讲解可按知识核验结果修订。[资源覆盖与权利说明](sources/carl-hot100-resources.md)。

### 算法基础补充 · 15道外部资源题

[按分类打开补充题库](docs/85-algorithm-supplement/README.md)，包含组合、二分、双指针、滑动窗口、矩阵、链表、哈希、字符串、栈与队列基础题。15题独立于当前官方Hot100，均提供核验过的代码随想录官网讲解与Python区，视频区分本题配套和相关迁移。

这是外部资源练习单与自主复习提示，没有新增这些题的原创实现、本地测试或在线AC记录；外部题解与视频未复制或镜像到仓库。题号、官方难度、资源归属和核验日期见[机器映射](sources/carl-hot100-resources.json)。

### 公开面经样本

- [AI Agent](docs/60-interviews/agent.md)
- [Java](docs/60-interviews/java.md)
- [Go](docs/60-interviews/go.md)
- [后端通用](docs/60-interviews/backend.md)

面经是公开发帖者的个人自述，岗位与年份以原页证据为准。样本包含实习、秋招及跨岗位补充，不能据此推断公司统一要求、真实录用概率或全行业考频。

## 内容与来源原则

- 题解、教学情境和练习说明采用独立组织的讲解，技术结论以指定版本和一手来源为准。
- 第三方资料只保留必要的主题标识、短摘要、出处和纠错定位，不镜像课程全文、原图或受限文档导出。
- 示例中的性能、样本量和结果不代表任何学习者实际完成的工作。未经运行的示例会明确标明。
- 私人身份、登录信息、密钥、访问令牌、内部工作记录和机器路径不属于公开资料。
- 第三方资料各自的权利与许可仍适用；链接或公开可读不代表获得转载许可。

## 维护入口

[整合方案](coverage/INTEGRATION_PLAN.md) · [完成标准](coverage/ACCEPTANCE.md) · 部分章节暂未发布 · [修订方式](CONTRIBUTING.md)

最后整理日期：2026-10-10。

## 进阶主题

[跨主题进阶学习路线](docs/00-guide/advanced-study-route.md)：Spark与作业生命周期、双模型路由、推理服务、ES父子关系和跨栈工程边界。
