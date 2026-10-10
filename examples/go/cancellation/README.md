# Go 取消与假 SSE 的最小实验

原创合成输入，仅用标准库。模块最低版本为 Go 1.20（`http.ResponseController` 与写 deadline）；采用 Add/Done 以兼容该版本，不用于演示 Go 1.25 的 WaitGroup.Go。

## 执行状态

2026-10-10：已补源文件和断言，当前环境未找到 Go 编译器，**未编译、未运行 go test、未运行 -race，也未验证真实 HTTP 网络行为**。下面是目标环境的复验命令，不是通过记录。没有启动 MySQL、Redis、外部模型或独立服务。唯一使用套接字的测试由 httptest 在本机临时启动并关闭 HTTP 服务。

```sh
cd examples/go/cancellation
go version
go env GOOS GOARCH CGO_ENABLED
gofmt -w pipeline.go sse.go cancellation_test.go
gofmt -l pipeline.go sse.go cancellation_test.go
go vet ./...
go test -v -count=1 -timeout=30s ./...
# -race 需要支持的 GOOS/GOARCH、启用 cgo 和兼容的 C 工具链。
go test -race -v -count=10 -timeout=60s ./...
```

逐条记录退出码、实际 Go 版本和完整输出；gofmt 的输出应为空。普通测试通过不能替代 -race 通过，工具链不支持 race 时记录未运行原因。不要把日期或 PASS 写进结果，除非实际执行得到它。

## 机器断言

- 流水线：100 个整数经四 worker 平方；结果无重复且完整。正常与慢消费者均返回，回调进入/退出计数一致。
- 提前退出：消费者收到首个结果后返回 ErrStop；零缓冲与两格缓冲均取消 producer/worker 的阻塞发送，并等待全部任务结束。
- 失败：worker 在输入 7 返回固定错误；驱动返回该错误并 join。外部取消发生在已启动 worker 内，检查 context.Canceled 与进入/退出计数。
- SSE：正常数据与 flush、成功 flush 后清除写 deadline、第二段前的模型失败、写端断连、模拟慢读者导致的写 deadline、首段 deadline、deadline 不受支持的 writer 都有明确断言。
- 临时 HTTP：客户端读取首段后关闭响应体；观察期间没有其他客户端 timeout 或显式 cancel 来代替断连原因，handler 的请求 context 应取消，长时间等待下一段应在两秒清理界内返回。

测试对异步结果设置两秒断言/观察窗口，整个测试进程另有 timeout。观察超时会让测试失败，但不会强制杀掉被测函数；HTTP 测试清理会取消请求、关闭连接，再等待服务器退出，若实现不响应取消，最终由测试进程 timeout 判失败。正常返回即意味着本流水线已等 producer 与 worker 退出；不拿全进程 goroutine 数精确相等作证，因为 runtime、HTTP 和测试框架也会创建任务。race 仅覆盖实际执行的路径，有限测试不是所有调度的证明。

## 必须保留的边界

回调若忽略 context、永远阻塞或 panic，流水线不能强制修复；此合同与有界队列同样重要。并行 worker 的结果不承诺输入顺序。测试的“慢读者”用可控 writer 模拟阻塞，只覆盖 deadline 传播，不证明任意代理、HTTP/2、TLS 或真实客户端网络均可靠收尾。真实断连仅用本机 httptest HTTP；生产还需验证代理缓冲、空闲超时、全任务时限、响应体关闭及供应商协议。

本例负责设置并在成功 flush 后清除响应写 deadline，避免等待下一段时旧 deadline 到期；不要与其他层并发改同一 deadline。本例失败时直接结束流，不约定业务级 error/done 事件、重连、Last-Event-ID 或消息持久化。没有吞吐或性能基准。

来源：[Go 官方流水线与取消](https://go.dev/blog/pipelines)、[ResponseController](https://pkg.go.dev/net/http#ResponseController)、[testing](https://pkg.go.dev/testing)、[Go race detector](https://go.dev/doc/articles/race_detector)。实现与测试组织为原创。
