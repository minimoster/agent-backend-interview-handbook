# 后端综合训练

[返回总目录](../../README.md) · [题目索引](../../QUESTION_INDEX.md)

## 1. 索引、事务与缓存

问题：数据库索引怎样加速查询？事务隔离保证什么？Redis数据结构、缓存异常、分布式锁与Go并发如何影响同一业务？

解析与练法：先练B09—B18、B22—B30，再沿项目请求画读写与失败路径。基础概念要能连接架构，不能只背语言语法。

## 2. 网络、消息与项目取舍

问题：HTTP、数据库隔离、回表、缓存和消息队列分别承担什么？聊天类项目消息丢失或数据增长后怎么办？

解析与练法：结合B05、B10、B14、B22、B31，解释为什么选方案、何时失效，以及如何检测、重试与恢复。

## 答案入口

[网络与流式接口](../40-backend/01-network-and-streaming.md) · [数据库与SQL](../40-backend/02-databases-and-sql.md) · [Redis与缓存](../40-backend/03-redis-and-caching.md) · [消息队列与幂等](../40-backend/04-messaging-and-idempotency.md) · [系统设计与可靠性](../40-backend/05-system-design-and-reliability.md)

结合B01—B50逐题练习机制、例子与失败处理；不以练习出现次数推断考频或录用概率。
