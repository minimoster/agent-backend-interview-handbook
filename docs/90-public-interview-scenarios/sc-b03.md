# SC-B03 volatile可见，不代表i++原子

[返回场景卡目录](README.md)

**练习问题：** volatile计数器为什么在两个线程下仍可能少计？ConcurrentHashMap又是否让所有业务操作都原子？

**知识点详解**： Java内存模型描述跨线程读写可见性和顺序。volatile读写有相应的happens-before保证，但i++包含读取、加一和写回，两个线程可以基于同一个旧值计算。线程安全容器保护它提供的操作，不自动保护你拼出的操作序列。

## 参考答案

我先明确要保护的不变量。单个计数可用原子类或锁；“库存大于零才减一”需要把检查和修改作为一个原子操作。Map上`get`后`put`不等于原子递增，可按合同使用compute/merge，或在合适粒度加锁。多个键、多个对象及外部数据库之间的一致性还需要额外设计。

## 追问1：可见性等于立即刷新到主存吗？

这种简化说法容易误导。准确表达应使用JMM规定的读写、同步动作和happens-before；不要把某个CPU缓存实现当语言合同。

## 追问2：线程安全容器中的value对象可随便改吗？

不可以。容器对引用的并发管理不自动使可变value的字段或多个字段之间的不变量安全。

## 常见误区

将旧版ConcurrentHashMap的Segment实现作为JDK21答案；只回答“加volatile”而没有说明原子操作范围。

## 练习与验收

两线程重复递增，分别用普通int、volatile、AtomicInteger或锁。无错误的一次运行不能证明无竞争；用规范解释每种版本保障了什么，并补充value对象竞争例子。

本卡的语言边界为Java21，不描述固定容器内存布局。

## 阅读与复验入口

先读基础：

- [02-concurrency-and-thread-pools](../../docs/20-java/02-concurrency-and-thread-pools.md)
- [13-concurrency-details](../../docs/20-java/13-concurrency-details.md)

正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
