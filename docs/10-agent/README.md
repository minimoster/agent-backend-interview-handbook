# AI Agent 与大模型应用

[返回总目录](../../README.md) · [题号索引](../../QUESTION_INDEX.md)

- [怎样使用这份资料](00-reading-guide.md)
- [Transformer先修 从向量到一个可计算的注意力块](05-transformer-prerequisite.md) · 算例与 CPU 前向实验
- [Agent loop、工具、状态与编排](01-agent-loop-tools-and-state.md) · 8题
- [RAG、检索与重排](02-rag-retrieval-and-reranking.md) · 10题
- [Memory 与上下文管理](03-memory-and-context.md) · 5题
- [SSE、异步任务与可靠执行](04-streaming-and-reliable-execution.md) · 7题
- [受控自改进与反馈治理](14-controlled-improvement.md) · 5题
- [MCP版本边界与安全集成](15-mcp-versions-and-integration.md) · 5题
- [Skill结构路由与生命周期](16-skills-routing-and-governance.md) · 4题
- [RAG索引表示与证据治理](17-rag-indexes-and-evidence.md) · 5题
- [Harness执行治理与观测](18-harness-runtime-and-observability.md) · 3题
- [Chroma持久化与嵌入集成](22-chroma-persistence-and-embedding.md) · 1题

### 推理与检索进阶

- [采样、KV缓存与推理服务边界](24-inference-and-serving-boundaries.md)
- [动态Top-K与图谱消融](17-rag-indexes-and-evidence.md#dynamic-top-k-and-graph-ablation)

### 应用实验与选型

- [Agent评测、模型路由与上下文消融](25-agent-evaluation-and-routing.md)
- [Agent生产设计与故障实验](26-agent-production-design-lab.md)
- [实际业务场景与状态契约](27-practical-agent-scenarios.md)
- [前沿模型与工程决策](28-frontier-and-engineering-decisions.md)
- [框架选型与组件集成](29-framework-selection-and-integration.md)
- [RAG数据工程与分块实验](30-rag-data-and-chunking-lab.md)
- [工具、MCP与Skill契约](31-tool-mcp-and-skill-contracts.md)

另见[Python/FastAPI附录](../40-backend/40-python-fastapi-lab.md)、[AI Coding练习](../70-practice/ai-coding-exercises.md)与[面试证据准备](../90-interview/01-evidence-based-interview-preparation.md)。

[实验复现与验证范围](../../coverage/AGENT_LABS_VALIDATION.md)。

## 协议交付与工具流追问

- [A2A身份、终态与断线恢复](32-a2a-task-lifecycle-lab.md)
- [多工具增量参数组装与验证](33-tool-stream-assembly-lab.md)

沿着[学习路线](../00-guide/expanded-map-and-study-plan.md#followup-route-agent)练习任务交付与流式参数组装。

## 虾皮 Agent 一二面专项学习

- [34题学习与追问](34-shopee-agent-interview-playbook.md)：独立SP-R1/SP-R2编号，每轮17题；基础答案与新追问交叉阅读
- [练习安排与技术参考](../../sources/shopee-agent-interview-supplement.md) · [验证范围](../../coverage/SHOPEE_AGENT_VALIDATION.md)

## 检索手算与算法练习

- [同例手算检索指标、分母与配对回归](35-retrieval-evaluation-worked-example.md)
- [稳定 Top-K、堆与 RRF](../70-practice/retrieval-ranking-algorithms.md)
- [两篇公开自述逐项答案、项目对应与四道深入练习](../60-interviews/agent-followups-20261015.md)
