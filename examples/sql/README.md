# SQL练习验证记录

这些是本仓库自主设计的合成数据，不包含真实用户或业务库内容。

## 已运行

2026-10-09，Python 3.12.14、SQLite 3.53.1，执行：

```sh
python3 examples/sql/check-relational-examples.py
```

10组断言通过，覆盖重复登录、闰日、断点、跨年、零记录、单条记录、排名并列、各部门第二档工资并列及缺失、空部门与NULL工资、年度半开边界、总额阈值、六字段输出且至少两笔订单的完整变体以及静态数据下的游标分页。输出见[验证结果](validation-result.json)。连续登录另与Python日期参考算法对比。

这是SQLite等价表达式和算法验证，**没有运行MySQL**。无法据此证明MySQL解析、执行计划、InnoDB锁、死锁选择、超时回滚范围或并发转账实现已通过测试。

## 待在MySQL中复验

具备已授权、隔离、可丢弃的MySQL 8.0/8.4练习库时，记录 `SELECT VERSION(), @@transaction_isolation, @@autocommit;`。不要使用业务库。`streak-fixture.sql`会创建练习表，须在新的空练习库中运行，重复运行会遇到表已存在。

```sh
# exercise_db应是自己准备好的隔离练习库；用户名按自己的环境填写。
# -p交互输入密码，避免把密码写入命令或仓库。
mysql -u EXERCISE_USER -p exercise_db < examples/sql/streak-fixture.sql
```

预期连续登录结果：用户1→3，2→2，3→0，4→2，5→1。再按[SQL九题](../../docs/70-practice/sql-nine-worked-problems.md)分别核对：

1. 排名：95/95/88产生行号1/2/3、名次1/1/3、密集名次1/1/2。
2. 分页：相同时间用唯一键保持确定顺序；另外测试新增/删除/更新时间时的一致性约定。
3. 聚合：空部门人数0，均值NULL；未知工资员工计人数但不计入已知工资均值。
4. 年度：包含年末最后微秒，排除次年零时；600+500入选，总额1000不入选。
5. 两连接按给定顺序交错锁行，记录死锁检测配置、报错与回滚结果，再结束两边事务。
6. 并发扣库存后检查不为负；重复请求不再次扣减；失败释放锁。
7. 转账需要实际应用实现后，注入扣款后失败、入账失败、死锁、提交后响应丢失；核验同币种总余额、流水与幂等记录一致。
8. 覆盖索引在代表性数据上比较EXPLAIN与实际耗时，不把小表计划当生产结论。

教学伪代码没有自动具备可运行实现。上述待验证项如被用于真实工程，应先补实现和对应环境测试。

<a id="mysql-concurrency-fixture"></a>

## 两连接锁与库存：可逐步复验的最小输入

**状态：2026-10-10 未运行。** 以下命令仅供自己已经准备好的空隔离练习库使用；不创建服务器、不改全局配置。目标为 MySQL 8.4，其他版本须独立记录。先在两个终端各打开同一练习库：

```sh
mysql --show-warnings -u EXERCISE_USER -p exercise_db
```

每个连接记录下列输出，确认两边 `DATABASE()` 相同、`CONNECTION_ID()` 不同。死锁实验要求 `innodb_deadlock_detect=1`；若不是，记录条件不满足，不能把锁等待超时当作死锁检测通过。

```sql
SELECT VERSION(), DATABASE(), CONNECTION_ID(), @@transaction_isolation,
       @@autocommit, @@innodb_deadlock_detect,
       @@innodb_lock_wait_timeout, @@innodb_rollback_on_timeout;
```

在连接 A 只初始化一次；遇到表已存在说明这不是空练习库，应换新的练习库，不要在原库盲目删表：

```sql
CREATE TABLE bl_locks (
  id INT PRIMARY KEY, value INT NOT NULL
) ENGINE=InnoDB;
INSERT INTO bl_locks VALUES (1,0),(2,0);
CREATE TABLE bl_inventory (
  activity_id INT PRIMARY KEY,
  available INT NOT NULL CHECK (available >= 0)
) ENGINE=InnoDB;
INSERT INTO bl_inventory VALUES (1,1);
CREATE TABLE bl_orders (
  request_key VARBINARY(64) PRIMARY KEY,
  activity_id INT NOT NULL,
  user_id BIGINT NOT NULL,
  UNIQUE KEY uq_activity_user (activity_id,user_id)
) ENGINE=InnoDB;
```

### 1. 死锁与完整事务回滚

必须按下面顺序逐条执行，不能把整段同时粘贴到两个终端：

1. A：`START TRANSACTION; UPDATE bl_locks SET value=value+10 WHERE id=1;`
2. B：`START TRANSACTION; UPDATE bl_locks SET value=value+20 WHERE id=2;`
3. A：`UPDATE bl_locks SET value=value+10 WHERE id=2;`，保持等待。
4. B：`UPDATE bl_locks SET value=value+20 WHERE id=1;`，形成环。
5. 保存两个终端的实际错误码与输出。预期一个事务收到 1213，被整笔回滚；不要预定 A 或 B 必为受害者。存活方的等待应结束，在其终端执行 COMMIT；受害者终端执行 ROLLBACK 明确结束。

两个连接都结束后，用任一连接断言下列输出为 1。两行都为 10 或都为 20，说明仅存活事务生效；不能出现一行 10、一行 20。

```sql
SELECT IF(COUNT(*)=2 AND MIN(value)=MAX(value)
          AND MIN(value) IN (10,20),1,0) AS deadlock_invariant
FROM bl_locks;
```

受害者若要重试，应从 START TRANSACTION 重跑整笔业务，不能只重跑最后一个 UPDATE。本实验只验证指定交错与两行，不证明所有索引、范围锁或负载下没有死锁。

### 2. 锁等待超时与语句/事务回滚范围

确认上一实验的事务已全部结束，然后在 A 执行 `UPDATE bl_locks SET value=0; COMMIT;`。

1. A：`START TRANSACTION; UPDATE bl_locks SET value=10 WHERE id=1;`，保持未提交。
2. B：`SET SESSION innodb_lock_wait_timeout=2; START TRANSACTION; UPDATE bl_locks SET value=20 WHERE id=2;`
3. B：`UPDATE bl_locks SET value=20 WHERE id=1;`，预期等待后报 1205。
4. B：`SELECT id,value FROM bl_locks WHERE id=2;`。`innodb_rollback_on_timeout=0` 时，先前对行 2 的修改仍在当前事务，应读到 20；为 1 时整笔事务已回滚，应读到 0。记录实际值和变量，不靠错误码猜回滚范围。
5. B 执行 ROLLBACK，A 也执行 ROLLBACK。

断言 `SELECT IF(COUNT(*)=2 AND MIN(value)=0 AND MAX(value)=0,1,0) FROM bl_locks;` 为 1。这里只改 B 的会话等待时间，结束连接即可丢弃该设置；不要求修改服务器全局配置。等待时间是教学故障注入参数，实际调度可能令观察时长略长，不把两秒当严格墙钟性能保证。

### 3. 最后一件库存、幂等键重放

使用初始化时的 `available=1`，按顺序执行：

1. A：START TRANSACTION，插入 req-A，再条件扣库存；影响行数为 1 后先不提交。
2. B：START TRANSACTION，插入 req-B，再条件扣库存；这条 UPDATE 会等待 A。
3. A：COMMIT。B 的 UPDATE 应完成且影响行数为 0；B 必须 ROLLBACK，不能提交其已插入的订单。

连接 A 的 SQL：

```sql
START TRANSACTION;
INSERT INTO bl_orders VALUES ('req-A',1,101);
UPDATE bl_inventory SET available=available-1
WHERE activity_id=1 AND available>=1;
SELECT ROW_COUNT() AS changed_rows; -- 必须为 1 才允许下面 COMMIT
-- 先切到连接 B 执行它的三条语句，再回到 A：
COMMIT;
```

连接 B 的 SQL：

```sql
START TRANSACTION;
INSERT INTO bl_orders VALUES ('req-B',1,102);
UPDATE bl_inventory SET available=available-1
WHERE activity_id=1 AND available>=1;
SELECT ROW_COUNT() AS changed_rows; -- A 提交后为 0
ROLLBACK;
```

重复 req-A 时，在新事务执行 `INSERT INTO bl_orders VALUES ('req-A',1,101);`，预期 1062；立即 ROLLBACK，读取已有 req-A 结果并核对参数一致，**不要继续执行扣库存**。MySQL 唯一冲突通常只回滚失败语句，并不自动替应用决定整笔事务。相同键却不同用户/活动应拒绝，不能冒用已有结果。

```sql
SELECT IF((SELECT available FROM bl_inventory WHERE activity_id=1)=0
 AND (SELECT COUNT(*) FROM bl_orders)=1
 AND (SELECT COUNT(*) FROM bl_orders
      WHERE request_key='req-A' AND activity_id=1 AND user_id=101)=1,
 1,0) AS stock_and_replay_invariant;
SELECT IF(COUNT(*)=0,1,0) AS unique_user_invariant FROM (
 SELECT activity_id,user_id FROM bl_orders
 GROUP BY activity_id,user_id HAVING COUNT(*)>1
) AS duplicates;
```

两条应输出 1。自动化时可用客户端 batch 模式取得该列，并在测试程序断言整数等于 1、预期错误码出现；不能只断言 HTTP 200。保存版本、两终端完整步骤、提交/回滚分支与实际输出。当前没有执行这些命令，未生成 MySQL 通过记录。

依据：[InnoDB 死锁处理](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks-handling.html)、[InnoDB 错误与回滚范围](https://dev.mysql.com/doc/refman/8.4/en/innodb-error-handling.html)。表、输入、交错与断言为原创教学设计。
