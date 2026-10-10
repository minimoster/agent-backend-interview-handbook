# SC-B05 线程池参数要回答排队与过载

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

本卡是原创教学场景，编号独立于361道讲义题、Hot100的100题与15道外部资源题。原帖仅支持作者报告过相关主题，不是公司认证题库；参考答案依据正文所列技术一手来源。

**原创起手问：** 核心线程10、最大100、无界队列，为什么最大100几乎不发挥作用？

**知识点详解**： ThreadPoolExecutor的提交路径通常是先尝试增加核心线程，再入队；队列不能接收任务时才尝试增加到最大线程，最终拒绝。无界队列通常不会因满而触发后面的扩容步骤，却可能积累大量延迟和内存。

## 参考答案

我会根据任务等待/计算比例和下游容量设置有界队列，明确排队最长时间、任务deadline及拒绝策略。核心/最大值是容量假设，要通过代表性负载验证。CallerRuns可能提供反馈，但会在提交线程执行任务；若提交线程是事件循环或承载其他关键职责，可能产生新阻塞。

## 追问1：拒绝时直接重试安全吗？

无上限立即重试会放大过载。根据业务选择快速失败、退避、降级或可靠持久化，必须限制重试预算；有副作用的任务还需幂等设计。

## 追问2：怎么判断该加线程？

同时看CPU、队列年龄、执行时间、等待资源和下游延迟。数据库已饱和时加线程可能只把等待从线程池搬到连接池。

## 常见误区

把CPU核数乘某个常数当通用答案；只监控队列长度，忽略最老任务已超时；无视线程池shutdown后仍运行任务的状态。

## 练习与验收

对固定小队列提交超过容量的慢任务，记录任务被执行/排队/拒绝的事件。验收说明每个任务的最终状态，关闭时无静默丢失。没有替用户跑线程池测试。

**主题来源：** P16、P17。**技术依据：** [JDK21 ThreadPoolExecutor](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)、[AWS超时和退避](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)。参数值为题设，不是推荐配置。

## 阅读与复验入口

公开主题线索：[P16](../../sources/public-interviews/README.md#report-p16)、[P17](../../sources/public-interviews/README.md#report-p17)。

先读基础：

- [02-concurrency-and-thread-pools](../../docs/20-java/02-concurrency-and-thread-pools.md)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
