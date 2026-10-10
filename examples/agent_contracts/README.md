# Agent合同的最小反例实验

[可靠执行](../../docs/10-agent/04-streaming-and-reliable-execution.md) · [数据工程任务身份](../../docs/50-projects/data-engineering-agent-case.md#job-lifecycle) · [固定提交案例](../../docs/50-projects/public-repository-case-studies.md#a39)

这里是独立编写的内存教学模型，不调用模型、数据库、外部计算或案例仓库。运行：

```sh
python3 -B examples/agent_contracts/test_contracts.py
```

[模型源码](contracts.py)与[测试](test_contracts.py)验证同一租户/操作/客户端键的重复身份、请求指纹冲突、进行中与完成结果、本地并发重复投递，以及总尝试次数和额外重试次数的不同上界。JSON排序只规范对象键顺序；数字、Unicode、日期、单位、缺字段与null是否等价必须由真实API的schema定义。

持久化反例把“先修改RAM，后尝试写盘”以及Rename前后错误分开：返回错误时内存仍可能是新值，Rename后错误时可见磁盘也可能是新值。它没有实际执行fsync、断电或Openresearch故障注入，不能证明文件系统持久性。示例锁只串行化一个进程中的内存记录，不提供持久幂等、过期策略、数据库事务、跨进程互斥或外部副作用exactly-once。

真实集成还须检验唯一约束、幂等记录与本地副作用的原子边界、保留期后重用、超时结果未知、旧执行者回写和多进程竞争。案例仓库原实现未被这里的教学模型修改。
