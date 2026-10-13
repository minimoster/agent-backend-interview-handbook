# SC-A09 保存checkpoint为什么还可能重复调用工具

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

**练习问题：** Agent保存了每一步状态，进程重启后是否就能完全从断点继续而不重复任何操作？

**知识点详解**： Checkpoint保存某个执行点的状态，恢复可能重新执行部分代码。外部副作用与状态保存之间若没有事务或幂等协议，恢复就可能重复动作。

## 参考答案

我把纯计算、读取和副作用分开，副作用使用稳定执行ID并保存结果。恢复前核对已执行状态，未知结果通过目标系统查询，不直接再做。Loop保存目标、预算、工具状态和退出理由。重复工具/参数、相同错误反复出现或无状态进展时触发重规划、澄清或人工处理。

## 追问1：多Agent互相推任务，如何让任务结束？

定义明确的任务所有者、完成条件、错误类型和交付结构。设置全任务截止时间、子任务预算和重复委派检测。多个模型输出意见不算环境中的完成证据。

## 追问2：把所有失败都交给模型再想一次行不行？

结构错误可反馈修正，权限拒绝不能当临时错误反复绕路；确定无权限或目标不支持时应停止。可恢复的超时和限流才按受控策略重试。

## 常见误区

持久化等于exactly once；循环次数越多越准确；恢复后总从最后一句自然语言摘要推测业务状态。

## 练习与验收

在“查文档→生成草案→保存草案”中标出4个崩溃位置。验收写出每处重启如何确认是否保存成功，重复恢复不得新增第二份同执行ID草案。LangGraph 故障注入实验尚未执行。

**主题来源：** P07、P10、P11、P13。**技术依据：** [LangGraph持久化](https://docs.langchain.com/oss/python/langgraph/persistence)、[LangGraph durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution)。执行语义须按实际版本测试；当前公开URL可能重定向。

## 阅读与复验入口

公开主题线索：[P07](../../sources/public-interviews/README.md#report-p07)、[P10](../../sources/public-interviews/README.md#report-p10)、[P11](../../sources/public-interviews/README.md#report-p11)、[P13](../../sources/public-interviews/README.md#report-p13)。

先读基础：

- [18-harness-runtime-and-observability](../../docs/10-agent/18-harness-runtime-and-observability.md)

可检查的练习材料：

- [interview_lab.py#IdempotentInventory](../../examples/public_interview_scenarios/interview_lab.py#IdempotentInventory)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
