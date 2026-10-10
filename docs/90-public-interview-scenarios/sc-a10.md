# SC-A10 人和多个Agent同时编辑同一份内容

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

本卡是原创教学场景，编号独立于361道讲义题、Hot100的100题与15道外部资源题。原帖仅支持作者报告过相关主题，不是公司认证题库；参考答案依据正文所列技术一手来源。

**原创起手问：** Agent读取版本7的文档，人已经写出版本8，它拿旧快照整篇替换，如何避免覆盖？

**知识点详解**： 锁住本地文件不能约束云端人工修改。并发编辑的核心是让写入基于当前版本，并在冲突时停下来比较，而不是最后写入者无条件覆盖。

## 参考答案

读取时带版本号或ETag，提交时带expectedVersion/If-Match。服务端原子检查版本并更新；不匹配返回冲突，Agent重新读取并展示差异或做可审查合并。多个子Agent尽量分不同文件/区域，最终集成由一个写入者处理。追加事件可以合并，不代表任意全文修改能自动合并。

## 追问1：先查版本再UPDATE就够吗？

两条独立语句中间还有竞争窗口。版本条件必须进入同一原子更新或事务锁合同；检查受影响行数。重试也要重新理解差异，不能只换成最新版本号后覆盖。

## 追问2：数据库乐观锁适合几百人同时填表吗？

按记录/字段拆粒度减少冲突，保存每人记录而不是全表快照。对同一记录的高争用操作，可用更适合的数据结构、排队或明确锁合同；选型须结合冲突率与交互体验。

## 常见误区

在客户端判断版本后无条件写；“三个Agent互相review”替代并发写入约束；每次冲突自动覆盖人的修改。

## 练习与验收

附带原创版本文档store练习模拟两位读者。验收第一个提交成功、旧版本提交冲突、冲突不改变内容；再基于新版本明确合并并成功提交。它是内存模型，不是分布式数据库验证。

**主题来源：** P07、P08、P12、P13。**技术依据：** [RFC9110 If-Match](https://www.rfc-editor.org/rfc/rfc9110.html#name-if-match)、[Git合并冲突机制](https://git-scm.com/docs/git-merge)。练习将版本条件解释为并发合同，非所有服务都支持ETag。

## 阅读与复验入口

公开主题线索：[P07](../../sources/public-interviews/README.md#report-p07)、[P08](../../sources/public-interviews/README.md#report-p08)、[P12](../../sources/public-interviews/README.md#report-p12)、[P13](../../sources/public-interviews/README.md#report-p13)。

先读基础：

- [18-harness-runtime-and-observability](../../docs/10-agent/18-harness-runtime-and-observability.md)

可检查的练习材料：

- [interview_lab.py#VersionedDocuments](../../examples/public_interview_scenarios/interview_lab.py#VersionedDocuments)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
