# 工程追问实验：资源、提交与协议边界

[本轮路线](../../docs/00-guide/expanded-map-and-study-plan.md#topic-map)
全部为原创教学代码，不复制第三方SDK。没有凭这些模型宣称真实服务、供应商互通或性能成绩。

## Java21：19个合同场景

```bash
java examples/interview_followups/ExecutorFailureLab.java
```

[源码](ExecutorFailureLab.java)。单文件源启动器，不依赖JUnit。门闩协调、有界等待与finally收尾，分别验证拒绝、调用者执行、静默丢弃、等待超时、Future/CF取消差异、聚合Future、上下文、队列过期与退出。实验不靠sleep建立同步，不故意留下永久阻塞线程。

## Python标准库：29个存储/状态测试

```bash
python3 -B -m unittest discover -s examples/interview_followups -p test_storage_lab.py -v
```

[storage_lab.py](storage_lab.py) · [test_storage_lab.py](test_storage_lab.py)。执行SQLite本地事务、临时文件重开、重复命令、Outbox/Inbox，另有有限offset前缀、资源fence和版本floor模型。未连接MySQL、Redis或Kafka；没有真实断电/杀进程耐久验证。整数offset模型不适用于Kafka跳号，生产需要已交付序列frontier。

## Agent协议与工具流

[标准库协议实验](agent_protocol_lab.py) · [测试源码](test_agent_protocol_lab.py)。使用明确的本地事件合同，不冒充A2A wire parser或供应商SDK；详细范围见[A2A章](../../docs/10-agent/32-a2a-task-lifecycle-lab.md)与[工具流章](../../docs/10-agent/33-tool-stream-assembly-lab.md)。

```bash
python3 -B -m unittest discover -s examples/interview_followups -p test_agent_protocol_lab.py -v
```

## Go：有界生命周期

[完整模块与10个测试函数](../go/followup_lifecycle/README.md)。本地缺少Go编译器，CI以实际工具链执行race命令；确切提交结果是运行证据，go.mod语法下限不是多版本认证。
