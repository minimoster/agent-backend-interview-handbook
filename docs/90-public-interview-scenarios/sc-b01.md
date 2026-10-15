# SC-B01 Go的nil与closed不能混成一种状态

[返回场景卡目录](README.md)

**练习问题：** 为什么同样没初始化，map读起来没事，写入却崩；channel收发又一直不返回？

**知识点详解**： nil map可读取，得到元素类型的零值，`ok`为false；向nil map写元素会panic。nil channel的收发会阻塞，放在select中的相应分支不会就绪。closed channel是另一种状态：缓冲区先被读完，然后接收返回零值和false；向已关闭channel发送、再次关闭它以及关闭nil channel都会panic。

## 参考答案

我会先区分“没有创建”“正在使用”“生产者结束”三种状态。接收端用逗号ok区分真实零值与结束；关闭责任应有唯一、明确的协调者。多个生产者共享channel时，不能让任意生产者在自己结束时关闭，否则其他生产者仍可能发送。map需要并发访问时，初始化只解决nil，不解决数据竞争。

## 追问1：`range ch`何时退出？

channel被关闭且已有值都消费完时退出；nil channel永远等。不能依靠给channel变量赋nil来通知另一个goroutine，变量本身的共享修改还需要同步。

## 追问2：为什么select里会把channel设为nil？

可以在当前goroutine里禁用一个分支，例如某个输入结束后继续监听另一个输入。这是有意的局部状态管理，不是关闭通道的替代品。

## 常见误区

“关闭channel就是释放内存”“channel一定不需要任何同步设计”“加recover就解决并发关闭”都不成立。

## 练习与验收

写出nil map读取/写入、nil channel select默认分支、closed channel缓冲排空四个小例子。每个先预测再运行，核对值、ok、是否panic。故意阻塞的例子应设置超时，避免测试挂住。

按实际Go版本记录结果；运行时map布局不能当成跨版本合同。

## 阅读与复验入口

先读基础：

- [02-types-containers-and-errors](../../docs/30-go/02-types-containers-and-errors.md)
- [01-concurrency](../../docs/30-go/01-concurrency.md)

正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
