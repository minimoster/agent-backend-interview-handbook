# Agent 先修与学习方法

[返回 Agent 目录](README.md) · [学习路线](../00-guide/expanded-map-and-study-plan.md) · [题目索引](../../QUESTION_INDEX.md)

学习 Agent 时，把模型、工具执行器和状态存储分开观察。模型提出调用，执行器校验权限与参数，状态记录任务进展；每次练习都说明这三部分怎样协作。

如果 Q/K/V、注意力形状或 LayerNorm 还不熟，先读[Transformer 先修](05-transformer-prerequisite.md)，运行手设权重小实验，再读[推理与缓存](24-inference-and-serving-boundaries.md)。

每题先独立解释，再对照知识点和具体例子，最后用代码或时间线回答追问。项目案例结合固定提交中的代码阅读；设计题则写出输入、状态、不变量和验证步骤。

## 基础之后怎样练

- [A2A 任务生命周期](32-a2a-task-lifecycle-lab.md)：用身份、快照和终态解释交付与恢复
- [工具流组装](33-tool-stream-assembly-lab.md)：把参数片段组装成完整候选，再进行校验与执行
- [虾皮 Agent 一二面 34 题](34-shopee-agent-interview-playbook.md)：练 RAG/评测、记忆/代码定位与需求交付

统一的时间安排和进阶入口见[学习路线](../00-guide/expanded-map-and-study-plan.md#followup-route-agent)。练习中记录所用版本、测试输入、观察结果和下一步验证。
