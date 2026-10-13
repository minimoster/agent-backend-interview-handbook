# SC-A01 为什么这个任务需要Agent

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

**练习问题：** 一个企业问答系统现在能检索文档并回答。你准备加Agent循环，具体要解决什么新问题？

**知识点详解**： 模型生成文本，应用程序负责把模型提出的工具调用真正执行。固定工作流的下一步由代码预先决定；Agent允许模型根据当前结果选择下一步。两者可以混合，边界没有所有团队统一认可的唯一叫法。

## 参考答案

我先看任务是否能写成固定步骤。查一份制度并回答，通常先做检索和一次生成即可。如果用户目标需要反复查信息、比较方案、补缺信息，且步骤数难预先确定，才引入受控循环。系统至少需要任务状态、工具入口、结果检查、退出条件和权限控制。选择框架是为了持久化、追踪或流程表达等具体能力，要能指出实际用了哪项。

## 追问1：框架换了，效果为什么会更好？

框架本身不能保证任务质量。我会保持模型、评测集与工具不变，比较任务成功率、错误工具调用、延迟与成本；再判断差异来自状态恢复、工具接口还是提示组织。

## 追问2：ReAct和先计划再执行如何选？

ReAct常在观察结果后逐步选择动作；显式计划把目标拆成可检查子任务，但计划会过期，需要校验和重规划。固定流程可以限制高风险步骤，两种模式都必须有预算和终止条件。

## 常见误区

“有memory就是Agent”“多Agent一定更先进”都不是可靠判据。工具调用和推理能力也不能证明工具执行已经成功。

## 练习与验收

给“查报销规则”和“比较三条采购方案”各画一条状态流。要求每个动作说明输入、输出、失败出口；找出至少一个无需模型决策的固定步骤。

**主题来源：** P06、P11、P13、P14。**技术依据：** [Anthropic模式定义](https://www.anthropic.com/engineering/building-effective-agents)、[LangGraph工作流与Agent](https://docs.langchain.com/oss/python/langgraph/workflows-agents)。仅讨论设计模式，不保证特定框架版本的API。

## 阅读与复验入口

公开主题线索：[P06](../../sources/public-interviews/README.md#report-p06)、[P11](../../sources/public-interviews/README.md#report-p11)、[P13](../../sources/public-interviews/README.md#report-p13)、[P14](../../sources/public-interviews/README.md#report-p14)。

先读基础：

- [01-agent-loop-tools-and-state](../../docs/10-agent/01-agent-loop-tools-and-state.md)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
