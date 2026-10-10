# SC-B06 ThreadLocal把变量绑定到线程，不是绑定到请求

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

本卡是原创教学场景，编号独立于361道讲义题、Hot100的100题与15道外部资源题。原帖仅支持作者报告过相关主题，不是公司认证题库；参考答案依据正文所列技术一手来源。

**原创起手问：** 为什么线程池第二个请求读到了上一个用户的上下文？

**知识点详解**： ThreadLocal让每个线程拥有自己的值。线程池会复用线程，而请求有独立生命周期，两者不能天然对应。ThreadLocal不自动跨异步线程传播，也不是授权检查本身。

## 参考答案

如果确实用它传递请求上下文，我会在明确入口设置，在finally中remove，并在执行实际业务前核验身份。异步任务优先显式传递必要上下文，或使用框架提供且已核对语义的传播方案。不能把整个请求和大对象无期限留在线程中。

## 追问1：InheritableThreadLocal能解决线程池传播吗？

它关注线程创建时的继承，不是每次任务提交时传播。池线程通常早已创建，因此不能靠它保证每个任务拿到新请求的值。

## 追问2：key是弱引用，为什么仍可能保留value？

线程内部映射中的value不会仅因为key失去强引用就立即同步释放；长期存活线程可能暂时保留条目。弱引用不替代明确清理，也不能把所有内存问题都归因于它。

## 常见误区

在catch中清理但正常返回忘清理；把“同线程可访问”当“线程安全认证”；为虚拟线程大量缓存昂贵对象而忽略数量。

## 练习与验收

单线程执行器依次处理两个不同用户任务，并让第一个任务抛异常。验收第二个任务不能读到第一个用户；使用finally后的正常与异常路径都通过。本轮未运行Java实验。

**主题来源：** P09、P17。**技术依据：** [JDK21 ThreadLocal](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ThreadLocal.html)、[JDK21虚拟线程](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html)。具体上下文框架的自动传播行为须单独核对。

## 阅读与复验入口

公开主题线索：[P09](../../sources/public-interviews/README.md#report-p09)、[P17](../../sources/public-interviews/README.md#report-p17)。

先读基础：

- [13-concurrency-details](../../docs/20-java/13-concurrency-details.md)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
