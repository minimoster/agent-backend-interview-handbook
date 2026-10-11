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

## Agent应用实验路线

1. 先用[评测与路由](../10-agent/25-agent-evaluation-and-routing.md)定义失败、成本及升级条件，再做[生产设计合同](../10-agent/26-agent-production-design-lab.md)。
2. 用[业务场景](../10-agent/27-practical-agent-scenarios.md)练状态、审批和未知结果；教学内存测试不等于真实订单或支付。
3. 对照[前沿决策](../10-agent/28-frontier-and-engineering-decisions.md)与[框架选型](../10-agent/29-framework-selection-and-integration.md)，区分候选能力、固定版本与未运行方案。
4. 从[RAG分块与合成评测](../10-agent/30-rag-data-and-chunking-lab.md)进入[工具/MCP/Skill合同](../10-agent/31-tool-mcp-and-skill-contracts.md)。现代协议解释与旧SDK实验分别记录。
5. 用[Python/FastAPI](../40-backend/40-python-fastapi-lab.md)和[AI Coding内核](../70-practice/ai-coding-exercises.md)练可复验代码，最后按[面试证据表](../90-interview/01-evidence-based-interview-preparation.md)说明自己的真实范围。

这条路线不新增编号题。[本批验证范围](../../coverage/AGENT_LABS_VALIDATION.md)。
