# 四个小实验：把答案变成自己的理解

[返回总目录](../../README.md) · [题目索引](../../QUESTION_INDEX.md) · [版本与纠错](../../errata/README.md)

- **取消实验**：producer/worker/consumer 使用固定 worker 与有界队列；consumer 提前结束时取消投递、处理和结果发送，并等待全部任务退出。最小源文件见[Go 取消实验](../../examples/go/cancellation/README.md)。断言正常与慢消费者的输出完整、提前退出不阻塞、下游失败保留原因、外部取消后回调进入/退出计数一致。
- **切片实验**：改变初始 cap，分别观察 append 前后两个 slice 是否共享；画出长度、容量与底层数组。记录 Go 版本、最小输入和实际结果，区分指定 cap 的语义与具体扩容策略；本题暂未提供已执行 fixture。
- **流式实验**：使用[假 SSE handler](../../examples/go/cancellation/sse.go)逐段返回，测试正常、首段 deadline、第二段前失败、用户断连和慢读者。测试用请求 context 取消与每次写 deadline 分别约束模型等待和阻塞写，断言 handler 在有界时间返回。真实断连测试由 httptest 临时开本机 HTTP，模拟慢读者仅验证可控 writer；代理、TLS、HTTP/2 和供应商协议需另测。
- **性能实验**：对同一 handler 保存基线，再做一个有依据的改动，测成功率、吞吐、P95/P99、B/op/allocs/op。固定版本、硬件、输入规模/分布、并发、deadline、预热与持续时间，保留至少多次独立样本及全部错误，不能挑最好看的一次。本题未运行 benchmark，也没有生产容量数字。

## 复验命令与状态

**2026-10-10：Go fixture 已补源文件与测试断言，当前环境没有找到 Go 编译器；编译、测试、race 与网络行为全部待验证。** 在具备 Go 1.20+、支持 race 的系统与 C 工具链时执行：

```sh
cd examples/go/cancellation
go version
go env GOOS GOARCH CGO_ENABLED
gofmt -w pipeline.go sse.go cancellation_test.go
go vet ./...
go test -v -count=1 -timeout=30s ./...
go test -race -v -count=10 -timeout=60s ./...
```

记录实际版本、命令、退出码、完整输出与未覆盖项；正常测试通过不能写成 race 已通过。测试通过也只说明执行过的输入与调度符合断言。完整输入、任务所有权、两秒断言/观察窗口与限制见[实验说明](../../examples/go/cancellation/README.md)。工作函数和 consumer 必须响应取消、不 panic；忽略 context 的永久阻塞不能由 WaitGroup 或队列自动修复。

验收标准：每题先用 30–60 秒讲主线，再接受 2–3 分钟追问；遇到未验证的版本细节能说“我会查该版本源码/文档”，比把旧口诀讲得很确定更可靠。服务相关故障演练另外按[MySQL 两连接步骤](../../examples/sql/README.md#mysql-concurrency-fixture)与[提交/消息重放实验](../50-projects/teaching-case-review-and-seckill.md#crash-replay-fixture)执行，SQLite 关系式通过不能替代它们。

实验实现与组织为原创。
