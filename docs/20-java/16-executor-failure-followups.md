# Java 追问诊所：排队、超时、取消与线程上下文

[Java目录](README.md) · [本轮学习路线](../00-guide/interview-followup-study-paths.md) · [源码与复验](../../examples/interview_followups/README.md)

基础先读[J15–J22](02-concurrency-and-thread-pools.md#j15)、[FJ17–FJ21](13-concurrency-details.md#fj17)。本章不再背七参数，而把参数接成故障时间线。所有情境、数值和参考回答为原创教学设计；面经只提示主题，不证明公司统一要求。本章采用 Java SE 21 API，配套源文件本地执行了19个有限合同场景，没有数据库、Spring容器、压测或真实请求链路。

## 先画四条线

一次异步请求至少有四个状态：调用者是否仍等待、Future是否完成、实际计算是否退出、外部副作用是否提交。它们不一定同时变化。超时响应不等于线程已停；线程已停不等于远端没执行；取消Future也不等于撤销业务事实。

<a id="java-queue-admission"></a>
## 1. 线程池没满，为什么请求已经超时

**起手问：** 最大线程数64，队列10000，为什么只有8个线程在跑，却积压了几千任务？

先看实际执行器类型及提交路径。ThreadPoolExecutor通常先使用核心线程，然后尝试入队，入队失败才考虑扩展到maximumPoolSize。大队列可能让“最大64”长期不起作用。[Java21 ThreadPoolExecutor](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)

**继续追问：队列该设多大？** 不用“CPU核数乘某个常数”直接下结论。画出接入、排队、执行、借连接、下游调用五段；队列占据请求总deadline，连接池和下游额度是另外两道门。教学例：剩余300ms，但前面已有一整波预计400ms工作，入队成功也不代表有业务价值。估算用于准入，执行时仍要重查deadline，且实际服务时间会波动。

**陷阱：** 把无界队列换成有界队列却没有定义拒绝后响应；把队列长度当端到端容量；只统计执行耗时，不统计等待时长。

**可复验反例：** `boundedReject`把一个worker固定在门闩，第二项入队，第三项得到拒绝；`queueExpiry`让任务排队期间逻辑时钟越过deadline，出队后不调用业务函数。这是确定性合同实验，不是QPS数据。

**面试收束：** “我先设总预算和资源上限，队列只吸收有限突发；过期任务出队时不再执行，满载时明确过载响应并计数。”

<a id="java-rejection-observation"></a>
## 2. CallerRunsPolicy是天然安全降级吗

不一定。它在相应过载情形把任务放到提交线程执行。如果提交者是HTTP工作线程，会延长它的占用；如果是事件循环，还可能阻塞整条调度链。它是一种反馈机制，不是通用的“拒绝但不影响上游”。本实验只验证调用线程身份，不构造生产延迟结论。

**追问：静默丢弃更快，能不能用于有结果任务？** `submit`包装出来的Future可能既没执行也没完成。调用方无期限等待会造成另一种挂住。`silentDiscard`确认该Future仍未完成，并在实验收尾主动取消。按业务合同选择显式拒绝、可观测降级或受控反馈；不要将丢弃任务伪装成成功。

**追问：任务异常为什么没有打日志？** `submit`的计算失败可存进Future；没有读取结果，就可能没人观察。`submitCapturesFailure`通过`get`检查ExecutionException的原因。同步、异步和拒绝三类错误都要纳入错误指标。[Future合同](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Future.html)

<a id="java-future-cancellation"></a>
## 3. Future超时之后，工作究竟停没停

按对象回答，不把相似方法当成同一机制：

| 操作 | 本地状态变化 | 仍要回答的问题 |
|---|---|---|
| Future.get带超时 | 调用者停止此次等待 | 实际任务是否继续、是否需要取消 |
| Future.cancel(true) | 请求取消，可能请求中断正在运行的任务 | 任务是否响应中断、是否已提交副作用 |
| CompletableFuture.cancel(true) | Future异常完成 | 它不直接控制产生结果的计算，不能据此保证中断supplier |
| CompletableFuture.orTimeout | 该Future超时异常完成，并返回同一Future | supplier是否还在运行、共享Future的其他观察者是否受影响 |

前三种差异分别以门闩与信号验证，`orTimeoutIdentity`检查对象身份，`lateCompletion`检查超时结果不能被迟到success改写。[CompletableFuture合同](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CompletableFuture.html)

**追问：取消后还扣了一次库存，谁的错？** 不能只看Future状态。请求可能在取消前已经到达资源端。应带稳定操作身份、定义未知结果查询、用业务事务约束和幂等重试；取消是在途控制，库存正确性由资源端保证。[存储失败窗口](../40-backend/41-storage-recovery-followups.md#storage-unknown-outcome)

**参考回答：** “我区分等待预算、协作中断、计算退出和提交事实。超时路径要清理自己拥有的资源，但不能凭超时把未知提交当作失败重做。”

<a id="java-aggregate-deadlock"></a>
## 4. allOf和anyOf能替我实现失败策略吗

`allOfWaits`中A先失败、B尚未完成，聚合Future仍未完成。它不是“任一失败立刻取消兄弟”的任务组。`anyOfErrorWins`中A先异常完成，B随后成功，也不会自动变成“第一个成功结果”。业务必须定义等待全部、首个完成、首个成功、部分可用、法定数量等不同策略。

**继续追问：外层任务再提交一个内层任务并get，为什么卡住？** 一个worker被外层占据，内层还在同池队列，外层等待内层，形成资源等待环。实验`nestedPoolStarvation`用零等待的get观察无法马上获得内层结果，随后外层返回，内层得以运行；故意不制造永久死锁。

**修复取舍：** 尽量用阶段组合避免阻塞占据同一个有限执行器；明确区分CPU工作、阻塞I/O和回调；即使拆池，也要画连接等稀缺资源的等待图。把池无限扩大只可能转移瓶颈。

<a id="java-context-boundary"></a>
## 5. 日志和事务为什么到了异步线程就变了

普通ThreadLocal是线程关联值，不是请求传播协议。实验先证明提交者的值不会自动复制，再证明同一个worker会保留上一任务未清理的值，最后验证remove。实际应用应捕获最小必要上下文，显式传递或使用框架认可的包装机制，并在finally恢复/清理worker原状态。[ThreadLocal](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ThreadLocal.html)

**追问：把所有ThreadLocal整包复制过去就行？** 不应。权限、事务连接、请求对象和大可变对象有不同生命周期，复用过期授权甚至会串租户。传播trace标识与传播数据库事务不能混为一谈。

Spring命令式事务通常绑定当前线程，新线程不自动加入旧事务；通过正确代理调用可在另一个线程开启它自己的事务。REQUIRES_NEW还可能需要额外连接，外层持着连接、内层等不到连接会放大池压力。本轮没有启动Spring做此集成实验。[事务传播](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html) · [事务注解边界](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)

<a id="java-shutdown-ownership"></a>
## 6. 服务关闭为何不能只调用shutdownNow

先停止接纳，再给在途任务有限收尾时间，然后请求协作取消，最后核对资源归还和任务最终状态。`orderlyShutdown`验证shutdown仍允许已接纳工作完成；`shutdownNowQueuedFuture`验证从队列排出的Future不会因此自动得到完成状态。调用方仍需处理被排出的任务、取消它们的结果句柄和记录恢复需求。[ExecutorService](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ExecutorService.html)

**追问：中断没有效果怎么办？** 检查是否吞掉InterruptedException、阻塞API是否支持中断、锁是否可中断获取，以及任务是否在远端。能及时退出是合作合同，不是Java强杀保证。诊断时看重复线程栈和等待依赖，而不只读一次Thread.State。

## 从这里练到能讲清

运行：`java examples/interview_followups/ExecutorFailureLab.java`。完整19场景源码可[下载](../../examples/interview_followups/ExecutorFailureLab.java)。依次解释每个断言保护什么、没有保护什么，再把小池参数改成自己的教学设定，保持门闩协调与收尾，不用sleep假装同步。

面经主题入口：[本轮公开线索](../../sources/interview-followups/README.md#java-reports)。一页纸画出队列、线程、连接、Future与提交状态的关系，再回答：“取消、异常、重复、退出分别是谁负责？”
