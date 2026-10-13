# Go 追问诊所：有界任务、取消竞争与资源收尾

[Go目录](README.md) · [主学习路线](../00-guide/expanded-map-and-study-plan.md#topic-map) · [完整worker pool](../../examples/go/followup_lifecycle/pool.go)

先读[G03–G10](01-concurrency.md#g03)、[G27–G34](04-http-sse-grpc.md#g27)与[G39–G40](05-testing-and-debugging.md#g39)。本章要求画出失败后每个 goroutine、队列和连接的去向。实验使用标准库，语法下限为 Go 1.23；编译与 race 的验证记录见[实验说明](../../examples/go/followup_lifecycle/README.md)。

<a id="go-owner-join"></a>
## 1. context都传了，为什么goroutine还在增长

**起手问：** 请求取消后，下游调用返回了，可goroutine数量仍每轮增加，怎么办？

不要只找`context.WithCancel`。沿任务生命周期列出每个可能阻塞点：等待准入、读取jobs、等待下游、发送结果、写客户端、等待子任务退出。一个函数接受ctx，并不证明它在这些地方使用了取消信号。生产者若发送到已经没人读的结果channel，业务调用已经结束也会泄漏。

**最小所有权表：** 调用者拥有取消函数；发送协调者在全部发送结束后拥有jobs的close；每个worker负责归还自己的许可与连接；顶层协调者负责join所有它创建的goroutine。不能只join计算worker，却漏掉feed goroutine。[Go官方pipeline取消](https://go.dev/blog/pipelines)

配套`Map`使用无缓冲jobs、至多64个worker、至多4096个整数输入。结果按索引写入，每个索引只有一个writer；错误时返回nil，不把部分结果伪装成完整答案。协调者连feed一起等待结束。它的**前提**是回调响应ctx且不panic；忽视取消或永久阻塞的回调会让join一直等，本示例没有强杀机制。

**追问：加缓冲不就不会卡住了？** 只可能把阻塞推迟。若未来发送数量不受控，有限缓冲终会满；若完全按输入规模缓冲，要说明内存上限和对象引用保留。修复应该建立“消费者退出→生产者可感知→停止发送→归还资源”的协议，而不只改一个数字。

<a id="go-cancel-race"></a>
## 2. ctx.Done放在select第一行，能优先取消吗

不能靠代码顺序获得优先级。多个分支同时就绪时，select会按规范选择一个可执行分支。因此取消发生后仍可能取到一个jobs。示例在取出jobs后再检查ctx，避免明知已取消还开始回调，但检查与实际副作用之间仍有竞争窗口。[Go规范select](https://go.dev/ref/spec#Select_statements)

**继续追问：那能保证取消后绝不写数据库吗？** 单靠本地ctx不能。写入是否获准应由数据库条件版本、权威任务状态或资源端fencing等原子边界决定。要求“取消确认后旧执行者绝不提交”时，要定义取消确认的线性化点，并让提交与它竞争同一权威状态。一次读取`ctx.Err()==nil`不能构成这种证明。

**反例时间线：** A检查未取消→B记录取消→A完成远端写。进一步回答：A用哪个operation_id？B取消的是等待还是业务任务？客户端拿到了什么确认？远端实际提交是否可查询？[未知结果与重试](../40-backend/41-storage-recovery-followups.md#storage-unknown-outcome)

<a id="go-budget-backpressure"></a>
## 3. 限流、并发上限、队列和deadline怎么一起设计

四者分别限制到达速率、同时占用、等待数量和等待时长。一个令牌桶可能限制平均速率，却允许突发；一个Semaphore限制同时调用，却不自动限制等它的goroutine；一个worker pool限制worker，也不自动限制外部HTTP请求或提交者数量。

**教学推导：** 下游允许20个并发，服务时间从50ms变成500ms，同样到达流量会显著增加等待。扩大本地队列不会让下游恢复。总deadline应从请求接纳开始计算，准入等待、连接获取和下游重试共用预算，不在每一层重新给完整2秒。

**追问：每个重试都开新goroutine？** 必须在统一准入和总预算下重试，并区分可重试错误与未知副作用。退避不应阻止ctx取消；多个层各重试三次可能乘出调用放大。缓存或singleflight用于合并相同读工作时，还要明确key的租户/权限范围，不能合并不同授权用户的数据。

**排错顺序：** 先看接纳率、排队等待、在途数、下游延迟和被拒数，确定哪道门变窄，再决定限流、隔离或降级。不能把“G数多”直接归因于调度器。

<a id="go-http-body-lifecycle"></a>
## 4. HTTP调用结束，为何连接仍不能复用

HTTP Client应复用，响应Body由调用方按合同读取并关闭。读尽响应有助于连接复用，但不能为了读尽无限响应而耗尽预算；应给体积和时间上限，超界后关闭并接受这次连接可能无法复用。请求context可以控制相应请求生命周期，不意味着你自己启动的所有旁路任务都已收尾。[net/http Client与Response](https://pkg.go.dev/net/http#Client) · [context](https://pkg.go.dev/context)

**追问：defer Close放在循环最外层安全吗？** defer在当前函数返回时执行，不是每轮结束都执行。长期循环可能同时保留许多Body和资源。把一次请求放进单独函数，或每轮明确关闭；遇到早返回、解析错误、体积超限也走同一清理责任。

**SSE继续追问：** Flush成功不代表客户端已经消费，更不代表业务提交成功。慢客户端会占连接和缓冲，用户断连后要取消上游并join子任务。事件拼接、工具调用参数和业务结果是不同边界。[工具流组装诊所](../10-agent/33-tool-stream-assembly-lab.md)

<a id="go-shutdown-diagnostics"></a>
## 5. 优雅退出遇到长连接，怎样交代最后一分钟

先让实例不再接纳新工作，再给在途请求有限排空窗口，最后取消超期任务并join。net/http的Shutdown不替你处理所有升级/劫持连接，例如WebSocket；应用需要知道这些连接由谁持有、如何通知以及何时关闭。长SSE也可能耗尽排空预算。[Server.Shutdown](https://pkg.go.dev/net/http#Server.Shutdown)

**追问：数量回落一次就证明没泄漏？** 不够。固定负载、重复取消/错误/正常三种路径，检查相似阻塞栈是否积累、活对象是否增长、是否仍保留Body与结果缓冲。先看goroutine和heap/allocs，再按需要启用block/mutex profile或trace；诊断采样范围和开销要受控，不把pprof直接暴露到公网。[Go Diagnostics](https://go.dev/doc/diagnostics)

**参考答法：** “我会列所有者、阻塞点、退出信号和join证据。若任务不响应取消，我先定位它卡在哪个资源合同，不把cancel函数当强杀。”

<a id="go-lab-reproduction"></a>
## 6. 从口述到验收

完整[源码](../../examples/go/followup_lifecycle/pool.go)、[10个测试函数](../../examples/go/followup_lifecycle/pool_test.go)与[运行说明](../../examples/go/followup_lifecycle/README.md)。测试覆盖非法资源参数、输入上限、完整顺序结果、空输入、预取消不启动、在途取消后join、错误不返回部分结果、实际活跃上限、200轮成功/失败重复路径。循环中的子场景不重复计为新的测试函数。

```bash
cd examples/go/followup_lifecycle
go test -race -count=1 -timeout=60s ./...
```

这是有限标准库任务模型，不是HTTP服务器、数据库、调度器兼容性或性能验证。race只检查实际执行路径；一次未报错不能证明全部并发行为正确。

面经线索：[宇99的Go秋招回顾](../../sources/interview-followups/README.md#go-report)。练习把同一实现按“正常完成、父请求取消、回调失败、回调不合作”分别画时间线，最后一类诚实保留前提缺口。
