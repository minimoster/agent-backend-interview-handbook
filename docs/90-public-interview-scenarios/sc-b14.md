# SC-B14 没有线上业务也能讲清自己的项目

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

**练习问题：** “性能提升40%”具体测了什么？这个指标真的由你的修改带来吗？

**知识点详解**： 面试项目追问关心问题、取舍、本人工作与证据。初次实习项目可以是实验或课程项目，诚实的离线数据比杜撰线上用户、QPS和规模更有价值。

## 参考答案

我会按问题→原方案→修改→实验→边界讲一条完整链。先解释输入规模、设备/版本、负载、测量窗口和指标分母；给修改前后同条件比较，必要时做消融。明确我负责的模块、复用了哪些组件、没做过哪些生产要求，并拿一条失败样本说明下一步。

## 追问1：平均延迟降了，用户体验一定更好？

可能尾延迟变差，或错误请求被快速拒绝拉低平均。一起看成功/失败、p50/p95/p99、吞吐及资源，比较相同负载下的结果。

## 追问2：如何说明框架选型不是跟风？

给出具体需求和替代方案，例如可恢复状态、简单流式接口、团队语言栈或现有组件；承认未验证的能力。不必为了看起来高级临时加入多Agent、分布式锁或微服务。

## 常见误区

把公开面经作者的项目和数据改成自己的经历；把运行一次截图当稳定实验；只讲反问薪资而无法解释一段自己写的代码。

## 练习与验收

做一页“项目证据表”：一项真实问题、一项本人修改、一条失败、一组有分母的对比和一条限制。用3分钟讲完，再接受5个为什么。随包评测模板可以填写，但没有替用户生成虚构成绩。

**主题来源：** P07、P09、P12、P13、P16、P17。**技术依据：** [Anthropic Agent评测设计](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)、[Go性能诊断](https://go.dev/doc/diagnostics)。这是原创表达结构，不是任何公司的评分表。

## 阅读与复验入口

公开主题线索：[P07](../../sources/public-interviews/README.md#report-p07)、[P09](../../sources/public-interviews/README.md#report-p09)、[P12](../../sources/public-interviews/README.md#report-p12)、[P13](../../sources/public-interviews/README.md#report-p13)、[P16](../../sources/public-interviews/README.md#report-p16)、[P17](../../sources/public-interviews/README.md#report-p17)。

先读基础：

- [README](../../docs/50-projects/README.md)
- [backend-self-check](../../docs/70-practice/backend-self-check.md)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
