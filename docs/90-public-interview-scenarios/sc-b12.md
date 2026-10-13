# SC-B12 CPU高与内存高先留下可解释证据

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

**练习问题：** 服务CPU100%，你登录服务器后第一步做什么？

**知识点详解**： 症状不是原因。CPU高可能是业务计算、忙循环、GC、锁竞争等；内存高也可能是合理缓存、堆外内存、泄漏或容器上限导致。无证据重启可能恢复服务，却抹掉定位线索。

## 参考答案

在已授权环境，先确认告警时间、服务/容器和资源限制，比较流量、延迟、错误率与部署变更，再采集有上限的指标、栈和profile。Java使用适配JDK的线程/堆诊断，Go用goroutine/CPU/heap profile；重点找重复出现的调用与增长对象，结合时间变化判断。dump可能含用户数据且带停顿/磁盘开销，需要遵守权限和敏感信息处理。

## 追问1：线程CPU与栈如何对应？

平台线程可借助系统线程标识关联，但虚拟线程不是一一对应的系统线程，不能把传统TID方法套给每个虚拟线程。必须选对应JDK诊断工具和输出。

## 追问2：RSS高就是Java heap泄漏吗？

不是。RSS包括堆、线程栈、直接缓冲、native等多项，Go也有自身堆及runtime行为。把进程、容器、语言堆指标分开，避免只扩大堆掩盖原因。

## 常见误区

生产上无界采集profile；把kill当唯一诊断动作；只截一张top图就宣布根因；共享未脱敏dump。

## 练习与验收

在隔离测试服务制造忙循环和未释放对象两种故障，分别选择诊断方法。验收能指出证据、定位路径、修复后的同条件对比及采集开销。本轮没有访问生产机器。

**主题来源：** P02、P03、P17。**技术依据：** [Go诊断](https://go.dev/doc/diagnostics)、[Oracle JDK21诊断工具](https://docs.oracle.com/en/java/javase/21/troubleshoot/diagnostic-tools.html)。诊断命令与权限依据实际环境，不提供生产默认执行脚本。

## 阅读与复验入口

公开主题线索：[P02](../../sources/public-interviews/README.md#report-p02)、[P03](../../sources/public-interviews/README.md#report-p03)、[P17](../../sources/public-interviews/README.md#report-p17)。

先读基础：

- [35-linux-operations-practice](../../docs/40-backend/35-linux-operations-practice.md)
- [05-testing-and-debugging](../../docs/30-go/05-testing-and-debugging.md)
- [12-jvm-operation](../../docs/20-java/12-jvm-operation.md)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
