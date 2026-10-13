# SC-A07 工具调用正确的判断不能停在JSON合法

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

**练习问题：** 模型输出了合法的“删除文件”参数，是否就该执行？

**知识点详解**： Schema校验检查结构和类型；业务校验检查目标、权限、前置状态和风险。合法JSON不代表存在这个文件，更不代表用户允许删除。MCP提供工具发现/调用等协议，应用仍负责策略和执行。

## 参考答案

我把调用拆成模型提案、schema验证、业务与权限验证、执行、结果归一化和状态记录。只接受允许的工具和目标，参数限制范围，处理超时与错误。写操作可以要求预览或确认，并使用幂等键。工具说明应明确输入、返回、失败与副作用；大结果用分页/引用，避免无限上下文。

## 追问1：Function Calling、MCP和Skill是不是三种替代方案？

模型原生tool/function calling帮助模型提出结构化调用；MCP连接客户端与工具服务器；Skill通常组织任务说明和资源，具体含义由框架定义。可组合使用，不能把Skill当一个通用网络协议。

## 追问2：工具很多，如何减少描述token？

用分类、工具索引或渐进加载缩小候选，同时保证选到工具后读到完整合同。评测要覆盖近义工具误选、权限差异和加载失败，不能以token减少证明功能不变。

## 常见误区

模型工具提案与实际执行混为一谈；重试所有错误；把工具注解直接当可信安全承诺；以隐藏工具名代替服务端鉴权。

## 练习与验收

为只读查询与写入更新设计两个schema，用非法字段、越界ID、无权限用户、旧版本和重复请求测试。预期无权限及旧版本都在业务层阻止，而不只检查JSON解析。本轮没有连接真实服务。

**主题来源：** P05、P07、P08、P09、P11、P16、P17。**技术依据：** [MCP tools 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)、[MCP transports 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)。这是明确固定的协议快照，不声称是2026最新修订。

## 阅读与复验入口

公开主题线索：[P05](../../sources/public-interviews/README.md#report-p05)、[P07](../../sources/public-interviews/README.md#report-p07)、[P08](../../sources/public-interviews/README.md#report-p08)、[P09](../../sources/public-interviews/README.md#report-p09)、[P11](../../sources/public-interviews/README.md#report-p11)、[P16](../../sources/public-interviews/README.md#report-p16)、[P17](../../sources/public-interviews/README.md#report-p17)。

先读基础：

- [15-mcp-versions-and-integration](../../docs/10-agent/15-mcp-versions-and-integration.md)
- [16-skills-routing-and-governance](../../docs/10-agent/16-skills-routing-and-governance.md)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
