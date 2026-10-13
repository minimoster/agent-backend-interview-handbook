# SC-B04 虚拟线程提升的通常是阻塞任务吞吐

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

**练习问题：** 换JDK21虚拟线程，CPU计算会变快吗？是否就不用连接池和限流？

**知识点详解**： 虚拟线程让大量并发任务用较轻量的线程表示，阻塞时通常能释放承载线程给其他任务。它没有让CPU执行同一条指令更快，也没有增加数据库连接、外部API额度或机器核心数。

## 参考答案

我会先看业务是否有大量可等待的I/O以及足够并发需求。虚拟线程适合保持简单的每任务一线程风格，但下游仍要做连接上限、超时、限流和过载处理。CPU密集型任务主要受计算资源限制。比较之前记录JDK版本、并发量、吞吐、p95延迟、内存和下游利用率，避免只看线程数量。

## 追问1：synchronized会导致pinning吗？

版本必须先说清。JDK21中在synchronized区域阻塞可固定承载线程；JDK24改变了监视器相关实现，不能沿用“所有版本都应把synchronized改成锁”的建议。仍需核对native/FFM调用等边界。

## 追问2：可以给虚拟线程建个固定线程池吗？

不应为了复用廉价虚拟线程而池化它们。限制稀缺资源可使用信号量等明确机制；为任务建立虚拟线程不代表下游有无限承载能力。

## 常见误区

“一个虚拟线程就是一个系统线程”“所有阻塞都一定卸载”“不用池化线程就不用资源池”。

## 练习与验收

分开设计等待型和CPU型两组工作负载，固定输入及资源限制，报告吞吐和尾延迟。不要把Thread.sleep实验推广为数据库真实性能。本轮没有运行JDK基准。

**主题来源：** P08、P16。**技术依据：** [Oracle JDK21虚拟线程](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html)、[Oracle JDK24虚拟线程](https://docs.oracle.com/en/java/javase/24/core/virtual-threads.html)、[JDK24监视器pinning变化](https://docs.oracle.com/en/java/javase/24/migrate/significant-changes-jdk-24.html)。这是明确的21/24边界，不承诺所有JDK版本一致。

## 阅读与复验入口

公开主题线索：[P08](../../sources/public-interviews/README.md#report-p08)、[P16](../../sources/public-interviews/README.md#report-p16)。

先读基础：

- [02-concurrency-and-thread-pools](../../docs/20-java/02-concurrency-and-thread-pools.md)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
