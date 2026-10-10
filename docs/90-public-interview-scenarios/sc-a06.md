# SC-A06 上下文压缩怎样保住任务约束

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

本卡是原创教学场景，编号独立于361道讲义题、Hot100的100题与15道外部资源题。原帖仅支持作者报告过相关主题，不是公司认证题库；参考答案依据正文所列技术一手来源。

**原创起手问：** 聊天太长，需要压缩。如何避免压掉“只能编辑这个目录”之类的重要约束？

**知识点详解**： Context是本次模型能看到的信息；持久化历史不等于每次都进入context。Memory是跨轮次或跨会话保留并选择性取回的信息。两者可能共享存储，但职责不同。

## 参考答案

我把目标、用户明确约束、授权范围、关键事实与证据链接、完成状态、待决问题分结构保存；再对可重建的历史做摘要。压缩阈值考虑输入token、输出预留和工具返回预算。原始记录仍保存供核验，但避免把全部历史再次塞回模型。记忆必须有来源、时间、租户和删除/失效机制。

## 追问1：小模型摘要便宜，能直接替代大模型吗？

成本更低不代表保真。使用固定约束字段、摘要前后断言和含否定/例外的样本评测；失败时降级或保留原片段。不能把摘要模型自己的推断变成用户明确要求。

## 追问2：长期记忆什么时候过期？

地址、项目状态和授权等可能变化，应记录时间与作用域，优先最新可信来源。用户纠正后要处理旧记忆和相关缓存，不能继续把旧内容当事实。

## 常见误区

单纯保留最近N轮可能丢掉很早的重要条件；把长期记忆当“越多越好”的日志库；记忆检索跨租户混用。

## 练习与验收

写8轮虚构任务历史，第一轮设目录限制，第六轮撤销一项动作。压缩后验收目标、限制和撤销均保留；引用可回到原记录。不是实际框架持久化测试。

**主题来源：** P05、P07、P09、P11、P13。**技术依据：** [LangChain短期记忆](https://docs.langchain.com/oss/python/langchain/short-term-memory)、[LangChain长期记忆](https://docs.langchain.com/oss/python/langchain/long-term-memory)。具体状态结构与API按实际版本固定。

## 阅读与复验入口

公开主题线索：[P05](../../sources/public-interviews/README.md#report-p05)、[P07](../../sources/public-interviews/README.md#report-p07)、[P09](../../sources/public-interviews/README.md#report-p09)、[P11](../../sources/public-interviews/README.md#report-p11)、[P13](../../sources/public-interviews/README.md#report-p13)。

先读基础：

- [03-memory-and-context](../../docs/10-agent/03-memory-and-context.md)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
