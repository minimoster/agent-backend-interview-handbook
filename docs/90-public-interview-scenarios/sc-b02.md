# SC-B02 context取消不会替你强制杀死goroutine

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

**练习问题：** HTTP请求已经超时，后台goroutine为什么还在增加？

**知识点详解**： context的取消是通知。函数和goroutine必须主动观察Done，或者调用支持context的阻塞API。它不是进程级强制终止，也不会自动回收你创建的所有任务。

## 参考答案

我会列出每个goroutine的创建点、所有阻塞点和退出条件。发送结果时同时监听ctx.Done，网络/数据库调用用支持context的接口；若底层接口无法中断，单独包装goroutine只让调用方提早返回，底层任务仍可能泄漏。调用WithCancel或WithTimeout后，保证释放对应cancel资源。关闭服务时先停新任务，通知取消，再等待工作者退出，并给等待设置上限。

## 追问1：WaitGroup能负责取消吗？

不能，它只协调等待任务完成。增加计数要发生在可能开始等待之前，每个任务完成时递减；它不保证任务不会阻塞，也不传错误。

## 追问2：GMP怎么和项目问题关联？

G是goroutine，M是执行的系统线程，P承载运行Go代码所需的调度资源；细节是运行时实现。先说明你遇到的是CPU饱和、阻塞还是任务泄漏，再用profile和goroutine栈定位，不能背完模型就认为问题解决。

## 常见误区

每次超时都再开一个goroutine重试；把“返回给客户端”当“工作已停止”；把GOMAXPROCS当允许创建goroutine的总数。

## 练习与验收

让消费者提前退出，比较无取消分支和有取消分支的生产者。等待工作者明确返回，检查重复执行后任务数不持续增长；同时运行race检测。这里只提供实验设计。

**主题来源：** P02、P03、P17。**技术依据：** [context合同](https://pkg.go.dev/context)、[Go诊断工具](https://go.dev/doc/diagnostics)。不同Go版本的调度和诊断细节要另核对。

## 阅读与复验入口

公开主题线索：[P02](../../sources/public-interviews/README.md#report-p02)、[P03](../../sources/public-interviews/README.md#report-p03)、[P17](../../sources/public-interviews/README.md#report-p17)。

先读基础：

- [01-concurrency](../../docs/30-go/01-concurrency.md)
- [05-testing-and-debugging](../../docs/30-go/05-testing-and-debugging.md)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
