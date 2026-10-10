# 跨主题进阶学习路线

[返回总目录](../../README.md) · [全主题学习地图](expanded-map-and-study-plan.md)

本版361道讲义题、Hot100 100题与15道外部资源题独立计数。部分章节暂未发布，下面只指向当前可读内容。

## 先复用基础，再看工程边界

1. 从[Agent循环与工具](../10-agent/01-agent-loop-tools-and-state.md)进入[流式接口与可靠执行](../10-agent/04-streaming-and-reliable-execution.md)，练习区分请求、执行状态与最终结果。
2. RAG先读[检索基础](../10-agent/02-rag-retrieval-and-reranking.md)，再看[动态Top-K与图谱消融](../10-agent/17-rag-indexes-and-evidence.md#dynamic-top-k-and-graph-ablation)。[ES父子Join](../40-backend/38-search-parent-child-joins.md#es-parent-join)与RAG父子chunk分别讨论。
3. 记忆先读[Memory与上下文管理](../10-agent/03-memory-and-context.md)。投影一致性按[A44固定代码案例](../50-projects/public-repository-case-studies.md#a44)解释，阅读代码与实际运行的证据分别记录。
4. 推理服务读[采样、KV缓存与批处理](../10-agent/24-inference-and-serving-boundaries.md)，区分生成参数、延迟预算和实际验证。
5. 数据工程从[Spark分区、Stage与Shuffle](../40-backend/37-spark-execution-and-diagnostics.md)进入[Agent作业案例](../50-projects/data-engineering-agent-case.md)。重点解释业务Job与Attempt、提交对账、取消竞争和长任务事件。
6. [跨栈追问](../40-backend/39-cross-stack-interview-boundaries.md)讨论Mongo原子写、Python事件循环、在线迁移、共享Token和密码哈希约束。[LC395](../70-practice/interview-algorithm-supplements.md#lc395)独立于LC3和Hot100，用两种原创实现对照32,800组有限穷举输入。

## 阅读与验证分开

阅读页支持题号、标题与正文检索，各专题指向规范知识章节。已发布题号和本机阅读记录保持稳定。

当前已运行确定性构建、22组阅读与搜索检查、Hot100单元测试及有限穷举、LC395对照测试。Spark、GPU训练、第三方框架与云沙箱仅提供示例和验证方案，不声称已完成端到端实验。验证方法和边界见[本版验证记录](../../coverage/VALIDATION.md)。
