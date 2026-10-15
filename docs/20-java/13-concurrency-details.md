# JUC 组件、执行器与锁的版本细节

[总目录](../../README.md) · [原并发题](02-concurrency-and-thread-pools.md)

以 Java 17/21/25 的公开 API 语义为主；实现源码另标版本。以下示例均未运行，容量值不构成生产建议。

<a id="fj17"></a>
### FJ17 创建任务、创建线程和选择线程池为什么是三件事

**优先级：P0。**

**知识点详解**：Runnable 定义不返回结果的任务，Callable 定义可返回结果并抛异常的任务；二者本身不创建线程。Thread 承载执行，调用 start 才启动新执行，直接 run 只是当前线程普通调用。FutureTask 将任务与完成结果连接起来，Executor/ExecutorService 决定如何调度；结果管理、线程模型和资源限制因此可以分离。

**线程生命周期**按 Java 的 Thread.State 说六种状态，不照搬操作系统五态：NEW 是尚未 start；RUNNABLE 包含 JVM 正在执行及等待 CPU 等资源；BLOCKED 专指等待进入/重入对象监视器；WAITING 是无期限等待他人动作，例如无期限 wait/join/park；TIMED_WAITING 是 sleep、带时限 wait/join/park 等；TERMINATED 是已退出。线程只能 start 一次，终止后不能再次启动同一 Thread 对象。

典型路径是 NEW → RUNNABLE → 等待态 → RUNNABLE → TERMINATED，并非每个线程必经全部六态。Object.wait 释放相应监视器，醒来还需重新竞争，期间可能成为 BLOCKED；Thread.sleep 不释放已经持有的监视器。ReentrantLock 的竞争者常通过 park 等待，不能把一切等锁都标成 BLOCKED。getState 是诊断快照，不能靠轮询状态代替 latch、join 等协作协议。

JUC 是一组工具：原子变量做特定原子更新；Lock/AQS 类协调互斥或许可；并发集合保存共享数据；latch/barrier/phaser 表达协作阶段；Executor/ForkJoinPool 组织任务。不能把所有问题都塞进一个线程池。

常见工厂要看背后资源边界：
- fixed 和 single 常用无界队列，生产过载时可能积累过多任务；single 表达顺序执行，不等于队列容量有界。
- cached 倾向复用空闲线程，不足时新建，线程上限很高；下游卡住时可能扩大线程和连接压力。
- scheduled 是延迟/周期任务调度，不是操作系统进程调度。ScheduledThreadPoolExecutor 主要按 corePoolSize 和无界延迟队列运行，调大 maximumPoolSize 没有预期扩容作用。
- work-stealing 对应 ForkJoinPool 思路，适合可拆分任务；不能认为所有执行器都继承 ThreadPoolExecutor。
- Java 21+ 虚拟线程每任务执行器按任务创建虚拟线程，不靠复用固定数量虚拟线程限流，仍要限制下游连接/配额。

ThreadPoolExecutor 的核心线程默认按需创建，预启动有专门 API；allowCoreThreadTimeOut 允许核心线程满足条件时超时。提交顺序与七参数见 [J15](02-concurrency-and-thread-pools.md#j15)，拒绝策略见 [J16](02-concurrency-and-thread-pools.md#j16)。

**具体例子**（未运行）：文档服务允许 8 个外部请求并发，但瞬间到来 1000 个任务。使用虚拟线程减少线程成本，并不等于 1000 个外部调用都获准。需用有界准入、超时和 Semaphore 控制实际调用；若传统线程池队列满，应明确返回过载而不是静默丢失。

**面试答法**：任务描述做什么，线程执行它，执行器决定调度；选池时检查线程上限、队列容量、调度语义和拒绝，不简单禁用或盲用所有 Executors 工厂。

**追问**：周期任务跑得比间隔慢会重叠执行吗？同一个周期任务的相邻执行在 ScheduledThreadPoolExecutor 中不重叠，但延迟和异常仍需处理。shutdown 后任务都立即停止吗？不是，需区分有序关闭、取消和协作中断。

**误区**：实现 Callable 就创建线程；把 maximumPoolSize 当所有池的有效扩展旋钮；核心线程一定启动就全部创建。

<a id="fj18"></a>
### FJ18 AQS 怎样实现可重入锁，公平锁为什么仍可能插队

**优先级：P1。**

**知识点详解**：AQS 提供可原子修改的 state、等待队列及获取失败后的阻塞/唤醒框架，子类定义“状态是什么意思、何时可以获取”。独占模式一次由一个所有者推进，共享模式可允许多个获得许可；Condition 的条件队列与竞争锁的同步队列职责不同。实现采用 CLH 思路的变体，并不等于教科书原版自旋 CLH，节点结构也会随 JDK 变化。

ReentrantLock 中 state 用作重入计数，所有者线程标识谁持锁：空闲时竞争建立所有权；同一所有者再次获取就增加计数；每次 unlock 对应递减，减到零才完整释放并允许后继竞争。可重入并不是任何线程都可进来，也不能避免不同锁形成死锁。Condition.await 会按协议释放再重新获得锁；醒来后仍应循环检查业务条件。

公平策略主要尊重已排队的竞争者，通常减少等待时间波动但可能损失吞吐。它不控制操作系统何时调度某线程。ReentrantLock 无参 tryLock 不遵守公平设置，锁可用时可抢到；持有者重入也不是重新排队。需要按所用 API 的合同解释公平，而非把构造参数当全局时间顺序保证。

synchronized 等待进入监视器本身不能通过 interrupt 取消；进入后执行的可中断阻塞操作另论。ReentrantLock 的 lockInterruptibly 与限时 tryLock 提供相应能力，但成功获取后必须 finally 释放。同步代码块通常有 monitorenter/monitorexit，同步方法通过 ACC_SYNCHRONIZED 标志表达，不能说源码每个 synchronized 都编译成同一字节码序列。

**具体例子**（未运行）：线程 T 两次 lock，第一次 unlock 后仍持锁，第二次才释放。采用 `if (lock.tryLock()) { try { ... } finally { lock.unlock(); } }`，失败时绝不能 unlock。需要等待可取消的用户请求时，显式中断获取比无界等待更容易表达需求。

**面试答法**：AQS 把状态与排队机制复用；可重入锁增加所有者与计数；公平是获取策略，既不等于调度公平，也有 tryLock 等 API 例外。

**追问**：AQS 有 FIFO 队列为何还可非公平？排队结构与获取时是否先尝试抢占不同。为何条件等待用 while？条件可能变化或虚假唤醒。

**误区**：AQS 是一把纯 CAS 自旋锁；重入无需相同次数释放；中断一定让 synchronized 入锁等待抛异常。

<a id="fj19"></a>
### FJ19 “偏向锁升级到重量锁”为什么不是现代 JDK 的通用答案

**优先级：P1。**

**知识点详解**：语言层只要求监视器互斥、可重入和对应可见性关系，并不要求某套对象头布局或升级流水线。传统 HotSpot 曾用偏向锁优化同一线程反复获得锁的路径；遇到竞争时需撤销偏向。轻量快速路径和监视器膨胀则在不同竞争/等待情形下权衡原子操作、阻塞与元数据成本。

JEP 374 在 JDK 15 默认禁用并弃用偏向锁，JDK 18 移除了其实现。现代 HotSpot 使用新的轻量锁实现，并存在对空闲监视器的消胀机制；所以“只能升级、永不降级”“所有对象必经无锁→偏向→轻量→重量”都不应作为跨版本保证。锁消除、粗化等 JIT 优化也取决于编译器证明和负载，不能靠源码某一行推定最终机器执行路径。

JDK 24 的 JEP 491 改善了虚拟线程在 synchronized 中阻塞时无法卸载的限制。Java 21 的 pinning 建议不能原样套到 24/25；native/foreign 调用等情况仍需另查。学习源码时记录 JDK 版本、LockingMode、构建及平台；面试先讲正确性，再谈性能实现。

**具体例子**：同样的短 synchronized 临界区在两个 JDK 上表现不同，先用同负载对比锁竞争、线程停顿和 CPU，而不是先将所有锁改成 ReentrantLock。即使某次测得更快，也只对测试条件成立。

**面试答法**：锁升级是某些历史 HotSpot 实现的教学模型；Java 15 默认禁用偏向，现代轻量锁与消胀不同。选锁先看功能，性能靠目标版本测量。

**追问**：没有偏向锁，synchronized 还可重入吗？可重入是语义，不依赖偏向优化。无竞争就绝无成本吗？不能这样保证。

**误区**：把旧对象头图当 JVM 规范；锁膨胀后进程生命周期内永不消胀；JDK 24+ 仍因旧 pinning 结论机械替换全部监视器。

<a id="fj20"></a>
### FJ20 CAS 与乐观、悲观并发控制怎样选择

**优先级：P0。**

**知识点详解**：悲观控制先取得排他权，再读取/修改受保护状态；乐观控制先计算或读取，提交时验证期间状态未变化，冲突则失败或重试。CAS 是“当前值等于预期值才原子替换”的原语，不等于完整乐观事务。Java 可使用 AtomicInteger/AtomicReference 和标准 VarHandle 能力，不应把非标准 Unsafe 作为业务默认入口。

ABA 是值从 A 变 B 又回 A，单纯比较值看不见历史；当历史影响正确性时，把版本号或标记纳入同一次比较。乐观算法需要计算可重试、结果尚未外部发布、竞争不会导致无限浪费等条件。读多写少只是线索：一次冲突重新做十秒外部调用可能比排队更贵；高热点写入也可通过分片、单写者或数据库条件更新降低冲突。

**具体例子**（伪代码，未运行）：`old = balance.get(); next = old - amount; compareAndSet(old,next)` 只保护这一个内存状态；扣款前的权限、余额非负判断、持久化流水和重复请求仍需要完整协议。重试函数内发送短信会因 CAS 失败被重复执行，应将不可重试副作用移出重试计算。

**面试答法**：低冲突、可重试的单状态更新适合 CAS；多状态不变量或重试成本高时更关注锁、事务和数据模型。用版本解决特定 ABA，不把原子变量说成完整业务原子性。

**追问**：lock-free 等于每个线程都很快成功吗？不等于，个体仍可能长期重试。LongAdder 能原子抢最后一个名额吗？不适合用聚合快照做原子准入。

**误区**：CAS 永远比锁快；“写少”自动证明方案正确；把随机标记与单调版本的语义混淆。

<a id="fj21"></a>
### FJ21 ThreadLocal 的弱键为什么仍会保留值，static 能解决吗

**优先级：P0。**

**知识点详解**：ThreadLocal 表达“每个线程关联自己的值”，不是“每个请求自动一份”。OpenJDK ThreadLocalMap 的键是 ThreadLocal 的弱引用，值仍被条目强引用。当 ThreadLocal 失去其他强引用，键可被 GC 清除，但存活线程的 map 仍可能留着值。部分 get/set/remove 清理路径会顺便扫除过期条目，不能依赖它何时恰好发生。

static final ThreadLocal 常用于稳定访问入口，避免反复创建键，但不是语言要求，更不是清理方案。静态键长期可达时，值仍然可能因没有 remove 而保留；线程池还会把上一个请求状态交给下一任务。请求结束、线程结束和 ThreadLocal 实例消失是三个不同生命周期。

**具体例子**（未运行）：
```java
context.set(requestContext);
try {
    handleRequest();
} finally {
    context.remove();
}
```
这个简单模式假设当前层拥有整个线程局部作用域；若在已有上下文中嵌套临时覆盖，应保存旧值并按作用域恢复，避免内层 remove 破坏外层状态。异步执行不能自动继承正确请求身份；显式传递可信上下文更容易审计。

**面试答法**：弱键只控制键的可达性，不会把 value 一起变弱；线程池任务必须按作用域清理，static 不替代 remove，异步传播另行设计。

**追问**：set(null) 与 remove 相同吗？后者删除关联，并允许未来 get 重新初始化。所有局部上下文都适合 InheritableThreadLocal 吗？线程创建继承语义不等于线程池每次提交时传播。

**误区**：键弱引用所以绝无泄漏；ThreadLocal 必须 static；一次线程切换就能自动读取正确用户身份。
