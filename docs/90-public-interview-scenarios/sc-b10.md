# SC-B10 发出消息、broker确认、业务完成是三件事

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

**练习问题：** 生产者拿到了confirm，能保证订单处理一次且已成功吗？

**知识点详解**： 发布确认关注生产者到broker的接收；消费者确认关注broker到消费者的处理进度，两种确认不是同一条合同。消息可能重复投递，应用副作用仍要按业务ID去重。

## 参考答案

数据库业务和消息发布之间用本地outbox记录意图。发布器在确认并核对路由结果后推进已发送状态；RabbitMQ不可路由消息也可能得到confirm，需按场景处理mandatory/returned消息。队列持久、消息持久和队列类型共同限定重启/故障保证，不能只开confirm。确认丢失时可能重发。消费者把去重记录和业务数据修改放入同一可原子提交边界，成功提交后ack；崩溃在提交与ack之间会再次消费，但不能再次扣库存。外部服务副作用不在本地事务内时，需外部幂等键、查询结果或补偿，不能声称本地事务保证它只发生一次。

## 追问1：用Redis set标记消费过够吗？

标记与数据库修改如果分开，就有“标记成功业务失败”和相反的崩溃窗口。先明确原子边界，不能用一次存在性检查代替事务性去重。

## 追问2：先ack再处理能提高性能吗？

可以减少等待但会丢失重投递的恢复机会。若后续处理失败或进程崩溃，broker可能已经认为完成；选择必须与业务丢失容忍度匹配。

## 常见误区

“MQ支持exactly-once，所以任何数据库/HTTP副作用都exactly-once”；“消息发出去就是可靠”；无限重试毒消息。

## 练习与验收

附带SQLite练习展示同数据库事务内的幂等效果；再手画提交成功但ack丢失的重放。它不是RabbitMQ测试，不能证明外部效果仅执行一次。

**主题来源：** P04、P08、P09、P17。**技术依据：** [RabbitMQ发布与消费确认](https://www.rabbitmq.com/docs/confirms)、[AWS幂等API设计](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)。按实际消息系统确认持久性和投递合同。

## 阅读与复验入口

公开主题线索：[P04](../../sources/public-interviews/README.md#report-p04)、[P08](../../sources/public-interviews/README.md#report-p08)、[P09](../../sources/public-interviews/README.md#report-p09)、[P17](../../sources/public-interviews/README.md#report-p17)。

先读基础：

- [04-messaging-and-idempotency](../../docs/40-backend/04-messaging-and-idempotency.md)
- [30-message-queue-details](../../docs/40-backend/30-message-queue-details.md)

可检查的练习材料：

- [interview_lab.py#IdempotentInventory](../../examples/public_interview_scenarios/interview_lab.py#IdempotentInventory)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
