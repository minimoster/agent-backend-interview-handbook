# SC-B13 TCP read边界不是消息边界

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

本卡是原创教学场景，编号独立于361道讲义题、Hot100的100题与15道外部资源题。原帖仅支持作者报告过相关主题，不是公司认证题库；参考答案依据正文所列技术一手来源。

**原创起手问：** 我一次write发送JSON，对方为什么可能需要多次read，也可能一次读到两条？

**知识点详解**： TCP提供有序字节流，不保留应用write的消息边界。接收读取大小受缓冲区和到达时机等影响；“粘包/拆包”是应用消息定界问题，不是TCP把数据随机打乱。

## 参考答案

选择长度前缀、分隔符或固定长度等明确协议。长度前缀解析要维护状态：先等完整头，再检查长度上限，再等完整payload，多条消息循环解析。字节长度不能直接用字符数量代替；文本解码应在完整帧或有状态增量解码后进行。

## 追问1：为什么要先检查长度上限？

不可信输入若声称几GB长度，程序不应直接按声明分配。限制单帧大小、缓冲累计量和等待期限，错误后明确关闭/重置策略。

## 追问2：read返回0就是空消息吗？

要按具体语言网络API理解，许多流式socket读取的0/空字节表示对端正常关闭，不等于协议层空payload。协议允许空消息时也需显式编码帧。

## 常见误区

用sleep等待“整包到齐”；每次read都直接JSON parse；用字符串长度写入以字节定义的header。

## 练习与验收

附带Python长度前缀解码器测试半个header、半个payload、多帧、UTF-8拆分、超长声明和EOF截断。它只测试应用解析，不模拟真实网络拥塞或TCP重传。

**主题来源：** P04、P17。**技术依据：** [RFC9293 TCP字节流合同](https://www.rfc-editor.org/rfc/rfc9293.html)。read/EOF按目标语言API核对；随包实现使用Python bytes。

## 阅读与复验入口

公开主题线索：[P04](../../sources/public-interviews/README.md#report-p04)、[P17](../../sources/public-interviews/README.md#report-p17)。

先读基础：

- [01-network-and-streaming](../../docs/40-backend/01-network-and-streaming.md)

可检查的练习材料：

- [interview_lab.py#FrameDecoder](../../examples/public_interview_scenarios/interview_lab.py#FrameDecoder)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
