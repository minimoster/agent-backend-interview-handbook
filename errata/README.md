# 版本与纠错记录

纠错针对可定位的技术表述，不评价作者整体水平。每项区分官方文档核对、正文修订与实际运行验证；未完成的步骤不会写成已验证。

核验日期：2026-10-09。[返回总目录](../README.md) · [版本使用规则](../VERSIONS.md)

## E003 MCP 必须区分协议版本

**适用范围**：2026-07-28 规范与旧版协议的区别。

**修正**：2026-07-28 规范改变了原有初始化握手和协议会话设计；可选能力发现、订阅通知与旧 HTTP+SSE 的弃用都有明确版本边界。旧客户端和兼容层仍可能采用旧版流程，因此不能把某一版本的握手、传输和会话模型描述成所有实现的固定规则。协议是否有状态与业务是否保存状态也是不同问题。

**验证状态**：已对照规范发布说明及官方 SDK 版本表。新增示例必须固定 SDK 与协议版本；本记录不声称已经完成跨版本互通测试。

[MCP 2026-07-28 官方说明](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [官方 SDK 协议版本表](https://ts.sdk.modelcontextprotocol.io/v2/protocol-versions)

## E004 JDK17 的 SecurityManager 状态

**适用范围**：Java SE 17 API。

**修正**：JDK17 中仍存在 `SecurityManager`，状态是弃用并计划未来移除，不能说在17已经移除。版本特性应分别标注预览、正式、弃用、禁用和移除，不能互相替换。

**验证状态**：已核对 Java17 官方 API 标注。本条不据此推断其他 JDK 版本的具体状态。

[Oracle Java17 SecurityManager API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/SecurityManager.html)

## E005 连续登录 SQL 的嵌套窗口问题

**适用范围**：MySQL 8.0。

**修正**：MySQL 8.0 不支持嵌套窗口函数。连续登录计算应拆成多层：先按用户和日期去重，下一层计算行号与连续分组标识，再统计组长度，最后按用户取最长值。要另外约定时区、同日多次登录、日期缺口与空数据的处理。

**验证状态**：已按官方限制完成静态核对。[S02](../docs/70-practice/sql-nine-worked-problems.md#s02)已提供合成数据、完整分层查询与SQLite/Python算法核对，MySQL目标引擎仍未运行。不能用其他数据库的通过结果冒充MySQL验证。

[MySQL8.0 窗口函数限制](https://dev.mysql.com/doc/refman/8.0/en/window-function-restrictions.html)

## 分领域修订与范围澄清

- [SQL记录](sql-corrections.json)：窗口分层、聚合口径、日期边界、错误分支与索引。
- [推理题记录](reasoning-corrections.json)：沙漏、赛马上界、投票规则、找零及借瓶条件。

记录包含真正的技术错误、条件补充、版本差异和证据范围限定，记录条数不等同独立技术问题数。

## 未采用的无证据结论

没有指定项目/版本的OpenClaw或Hermes内部实现、未同条件实测的产品排名、固定且普适的检索/压缩阈值，不作为已确认事实写入。论文报告与独立复现区分，教学方案与原作者真实项目实现区分。题目缺完整条件时明确保留缺失条件，而不是虚构一个标准答案。
