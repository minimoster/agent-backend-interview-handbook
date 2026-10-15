# Go有界生命周期实验

[对应追问章](../../../docs/30-go/07-concurrency-failure-followups.md)
[go.mod](go.mod)、[pool.go](pool.go)与[pool_test.go](pool_test.go)为原创标准库代码；go.mod使用1.23语法下限，不据此声称验证过所有工具链。Map最多64个worker、4096个整数；每个索引独占写入，feed和worker都join，失败无部分可信结果。

回调必须响应context且不panic。本模型没有强杀、持久队列、HTTP/数据库连接或生产性能结论。取消检查不能保证跨网络副作用不存在；资源端仍需业务身份和条件提交。

```bash
go test -race -count=1 -timeout=60s ./...
```

10个测试函数；其中一项执行200轮正常和失败回归，不把循环次数另计为测试数。本地云环境缺少Go编译工具，因此本地未执行此命令；仓库CI将执行同一命令，是否通过以确切提交的Actions结果为准。
