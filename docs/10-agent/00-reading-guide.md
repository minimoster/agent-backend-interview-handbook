# 怎样使用这份资料

[返回总目录](../../README.md) · [题目索引](../../QUESTION_INDEX.md) · [版本与纠错](../../errata/README.md)

- P0：先学会，能脱离稿件讲清，并在自己的代码中定位。P1：完成 P0 后补齐。P2：进阶了解，不要为背术语挤占基础和项目时间。
- 每题依次读“知识点详解 → 具体例子 → 30 秒答题主线”，最后用追问自测。30 秒段落是开场，不是让你一次背完全部细节。
- 示例数字、任务状态与测试方案是教学用的假设，不代表你的项目已有指标或生产流量。项目专属事实锁定在 [AG-P01](../../sources/catalog.md#ag-p01)、[AG-P02](../../sources/catalog.md#ag-p02) 对应提交；“建议改进”不能说成“我已完成”。
- 技术答案只依官方文档、官方工程文章、原始规范/论文，再加明确标记的工程推演；面经仅说明有人报告被问过这些主题，不用来证明技术答案正确。
- 本章源码涉及 Go，通用概念也适用于 Python。LangGraph 的例子用来解释状态编排，不表示你的 Go 项目使用了 LangGraph。

如果Q/K/V、注意力形状或LayerNorm还不熟，先读[Transformer先修](05-transformer-prerequisite.md)并运行一个手设权重小实验，再读[推理与缓存](24-inference-and-serving-boundaries.md)。这条先修路线不要求先训练模型。

## 接住协议与流式故障追问

基础之后读[A2A任务生命周期](32-a2a-task-lifecycle-lab.md)与[工具流组装](33-tool-stream-assembly-lab.md)。用身份、快照、终态和执行条件解释失败，不把部分JSON直接交给工具。[跨栈复习路线](../00-guide/interview-followup-study-paths.md)。

## 用34题检验能否回答工程追问

读完基础后进入[虾皮Agent一二面专项](34-shopee-agent-interview-playbook.md)，依次练RAG/评测、记忆/代码定位和需求到交付。先说明事实与设计的边界，再回答状态、预算、指标与失败处理。复用基础原章，不用同时背两套相同定义。
