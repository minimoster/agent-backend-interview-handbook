# SC-B09 更新数据库再删缓存只是起点

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

**练习问题：** 数据库更新成功，删缓存失败怎么办？删成功后为什么也可能读到旧值？

**知识点详解**： 数据库与缓存通常不是同一个本地事务。删除失败会保留旧缓存；并发回填也可能把删除之前读出的旧数据写回来。这些是不同故障，不能只给一句“延迟双删”。

## 参考答案

我先声明一致性目标：允许多长的旧值窗口，哪些操作必须直接读库或验证版本。数据库更新和待失效事件可以写入同一事务的outbox，后台持续处理失败并有可观察告警。缓存对象带数据版本，回填/失效设计避免旧版本覆盖新版本。TTL可限制部分旧值寿命，但不能保证固定窗口内一定修复所有时序问题。

## 追问1：分布式锁能实现强一致吗？

锁有失效、超时和持有者暂停的边界，数据库仍应保护关键不变量。Redis异步主从故障切换可能影响互斥；即使有锁也要说明有效期和失败处理，不能一把锁涵盖全部正确性。

## 追问2：只有一个数据库事务，outbox为何有帮助？

业务修改与待发送/失效意图在同一事务提交，避免业务提交后进程崩溃造成事件完全丢失。事件处理仍可能重复，因此消费者或失效动作必须可重放。

## 常见误区

把缓存命中率高等同于一致性好；把“通常很快”写成强一致保证；没有说明事件积压与删除失败的告警。

## 练习与验收

画出读旧库值、写新库值、删缓存、旧值回填的四步交错，再设计版本策略。验收包括进程在提交后崩溃、缓存不可用和重复失效，不能只测试正常路径。

**主题来源：** P02、P04、P17。**技术依据：** [Redis锁模式与故障边界](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)、[AWS安全重试](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)。当前Redis文档含8.4专有命令，不能原样套入旧版本。

## 阅读与复验入口

公开主题线索：[P02](../../sources/public-interviews/README.md#report-p02)、[P04](../../sources/public-interviews/README.md#report-p04)、[P17](../../sources/public-interviews/README.md#report-p17)。

先读基础：

- [03-redis-and-caching](../../docs/40-backend/03-redis-and-caching.md)
- [05-system-design-and-reliability](../../docs/40-backend/05-system-design-and-reliability.md)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
