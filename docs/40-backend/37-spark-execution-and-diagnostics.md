# Spark 执行机制与证据驱动诊断

[返回总目录](../../README.md) · [后端基础](README.md) · [数据工程 Agent 案例](../50-projects/data-engineering-agent-case.md)

本章覆盖批处理 Spark 的执行模型、Shuffle、Join 和诊断证据，适合已经理解 SQL、进程和网络的读者。先解释一条查询如何执行，再讨论参数调优。

技术语义限定Apache Spark 4.0.1，示例尚未在 Spark 运行，性能仍待实测。

- [执行模型与基础概念](#spark-basics)
- [Shuffle 与 Join 的成本](#spark-shuffle)
- [从日志到可解释诊断](#spark-diagnostics)
- [验证优化与练习](#spark-verification)

<a id="spark-basics"></a>

## 执行模型与基础概念

### 先分清进程 数据和调度单位

一个 Spark application 包含 driver 和它的 executors。Driver 执行应用入口、维护计算计划并调度 task；executor 是该 application 的执行进程，运行 task 并保存缓存或中间数据。集群管理器分配资源，worker node 是能够承载执行进程的机器。机器、进程、task 是三个不同层次，不能把“十台机器”直接换算成“十个分区”。

| 名称 | 教学理解 | 常见误解 |
| --- | --- | --- |
| DataFrame | 有 schema 的逻辑表，由分布式计算产生 | 所有行已经装入 driver 内存 |
| Partition | 某一计算阶段处理的数据切片 | 永久绑定某台机器，或永远等于一个文件块 |
| Task | 对一个 stage 的一个 partition 执行计算的工作单位 | 一个 task 对应整张表 |
| Stage | 可按依赖组织执行的一组 task | 一行 PySpark 代码必对应一个 stage |
| Spark job | action 触发的内部计算调度单位 | 等同平台上的一个业务任务 |

例如教学设定有 80 个分区、16 个可用 task slot。通常需要分批调度这些分区，不会因为分区数多于 CPU 就报错；其中一个分区特别大时，它可能成为最后完成的 task。Task 失败后还可能有新的 task attempt，不能把所有 attempt 数当唯一分区数。输入分区与扫描文件、切片设置及数据源有关，后续 `repartition` 或 Shuffle 又会改变分布。

### 惰性计算不意味着代码没有任何开销

`select`、`filter`、`join` 和聚合描述计算，通常先构建计划；`count`、`collect`、`show` 或写出结果等 action 才要求求值。逻辑计划描述“要什么”，优化计划重排可等价的操作，物理计划决定执行算子，调度器再组织 job、stage 和 task。计划构建、元数据查询、schema 推断仍可能发生工作；不能把惰性计算解释为所有 API 调用都零 I/O。

也不要记“一次 action 必定只显示一个 job”或“每次 join 固定增加两个 stage”。实际 SQL 执行可能有多个 job，广播、子查询、复用与 AQE 都会改变图。`explain("formatted")` 展示物理计划轮廓与节点细节，`explain("cost")` 展示计划和可用统计；运行之后还应核对 SQL UI 中的实际计划。

### 一个有明确口径的 PySpark 例子

目标是统计截至 2026-10-10 00:00 UTC 的过去七天点击次数，并保留所有用户。窗口为 `[2026-10-03 00:00, 2026-10-10 00:00)`，无点击记零，空用户 ID 丢弃。这里是固定截止点的报表，不能直接把这张表用于发生在更早时间的训练样本。

以下是经典 PySpark 本地模式的示意脚本，不是 Spark Connect 示例。输入均为合成数据，只有四行结果，因此最后可以 `collect`；生产中应按输出规模写到受控存储，不能无界拉回 driver。

```python
from datetime import datetime, timezone
from pyspark.sql import SparkSession, functions as F, types as T

def utc(text):
    return datetime.fromisoformat(text).replace(tzinfo=timezone.utc)

spark = (
    SparkSession.builder.master("local[2]")
    .appName("teaching-click-window")
    .config("spark.sql.session.timeZone", "UTC")
    .config("spark.sql.shuffle.partitions", "4")  # 教学值，不能照搬生产
    .getOrCreate()
)

try:
    event_schema = T.StructType([
        T.StructField("user_id", T.LongType(), True),
        T.StructField("action", T.StringType(), False),
        T.StructField("event_time", T.TimestampType(), False),
    ])
    user_schema = T.StructType([
        T.StructField("user_id", T.LongType(), False),
        T.StructField("region", T.StringType(), False),
    ])
    events = spark.createDataFrame([
        (1, "click", utc("2026-10-02T23:59:59")),  # 窗口外
        (1, "click", utc("2026-10-03T00:00:00")),  # 下界包含
        (1, "click", utc("2026-10-09T23:59:59")),
        (1, "click", utc("2026-10-10T00:00:00")),  # 上界排除
        (2, "view",  utc("2026-10-05T12:00:00")),
        (2, "click", utc("2026-10-06T12:00:00")),
        (2, "click", utc("2026-10-07T12:00:00")),
        (3, "view",  utc("2026-10-08T12:00:00")),
        (None, "click", utc("2026-10-08T12:00:00")),
    ], event_schema)
    users = spark.createDataFrame([
        (1, "north"), (2, "south"), (3, "north"), (4, "west"),
    ], user_schema)

    start, cutoff = utc("2026-10-03T00:00:00"), utc("2026-10-10T00:00:00")
    valid = events.filter(
        F.col("user_id").isNotNull()
        & (F.col("action") == "click")
        & (F.col("event_time") >= F.lit(start))
        & (F.col("event_time") < F.lit(cutoff))
    )
    counts = valid.groupBy("user_id").agg(F.count("*").alias("clicks_7d"))
    result = (
        users.join(counts, "user_id", "left")
        .select("user_id", "region",
                F.coalesce(F.col("clicks_7d"), F.lit(0)).cast("long").alias("clicks_7d"))
    )
    result.explain("formatted")
    rows = result.orderBy("user_id").collect()  # action；排序本身也有成本
    actual = [(r.user_id, r.region, r.clicks_7d) for r in rows]
    assert actual == [(1, "north", 2), (2, "south", 2),
                      (3, "north", 0), (4, "west", 0)]
    assert result.columns == ["user_id", "region", "clicks_7d"]
    assert result.schema["clicks_7d"].dataType == T.LongType()
finally:
    spark.stop()
```

断言给出可复核的预期，不表示本仓库已跑通该脚本。样例假定 `users.user_id` 唯一且每行日志就是一个应计数事件；真实输入还要定义重复事件、迟到事件与用户维表版本。输出顺序只在显式排序后用于断言，DataFrame 默认没有全局行序保证。Join 的业务正确性可独立核对：右表聚合后每个用户至多一行，left join 才不会因右表重复键把左表行数放大。

<a id="spark-shuffle"></a>

## Shuffle 与 Join 的成本

### 为什么按用户聚合需要交换数据

用教学数据说明：分区甲有用户 1 的一次点击和用户 2 的一次点击，分区乙又有用户 1 的一次点击。各分区的局部计数不足以产生最终用户计数，必须把同一 key 的贡献汇到对应目标分区。可结合的聚合通常能先局部合并，例如把大量相同用户事件变成局部计数后再交换；不能估算为永远搬运全部原始日志。

Shuffle 涉及分区、序列化、中间数据写入和读取，跨 executor 拉取时还用网络。在调度层，Shuffle 依赖通常形成 stage 边界；同一 stage 内可串接的 narrow 操作不要求这种重分区，但仍可能读取远程文件，不能说“filter 所在 stage 完全没有网络”。同一用户落到一个目标分区，也不等于永远固定在同一机器。

### 三种需要识别的物理计划线索

| 计划线索 | 需要追问的成本 | 可以怎样验证 |
| --- | --- | --- |
| `Exchange` | 为满足分布要求交换哪些列和多少数据 | 对照输入裁剪与实际 Shuffle 指标 |
| `SortMergeJoin` | 两侧分布是否满足要求，是否需要排序 | 看 Exchange、Sort、输出基数和热点 key |
| `BroadcastHashJoin` | 构建侧能否广播并容纳在相关进程内存中 | 看广播大小、构建侧统计和实际计划 |

Join 策略取决于连接类型、键、统计、已有分布和配置，不是所有 join 都双边 Shuffle，也不能保证永远用 sort-merge join。广播可以减少大表重分布，却仍有传输和内存成本；“压缩文件只有几 GB”不能证明广播安全。`F.broadcast(df)` 标记广播候选，hint 是否采用仍受策略适用性约束。

AQE 利用运行时统计调整部分物理计划，例如合并小 Shuffle 分区、改变适用的 Join 策略或处理部分倾斜；它不是业务语义校验器，也不能保证任意热点查询都快。比较计划时保存初始与最终计划，并记录 `spark.sql.adaptive.enabled` 等关键配置。

### 热点和 Join 膨胀要分别处理

假设某 key 在左表有 1,000 行，在右表有 20,000 行，等值多对多 Join 可能生成 2,000 万个匹配。这是业务基数放大；即使把工作均匀拆散，也不会自动减少应产生的匹配数。先确认右表是否本来应该唯一、是否能预聚合、能否用 semi join 表达“只判断存在”，再讨论倾斜优化。

Salting 是给热点 key 加额外分桶信息的设计方法。计数可先按 `(key, salt)` 算局部结果再按 key 汇总；Join 需要协调两侧分桶，可能复制较小侧。盐应由稳定事件标识等确定性规则产生，避免每次重试随机改变分布。Outer join、重复值、去重和非可结合聚合都需专项证明，不能只看到 task 变快就认为结果正确。这套分桶方案尚未运行，需结合实际 Join 与聚合语义验证。

### 报表窗口与训练特征的区别

示例的统一截止点对报表是清晰口径。若样本时间是 2026-10-07，则它的特征不能读到 10-09 的行为。应以样本的 event time 和当时可获得的数据为界限；离线记录时间早，不代表当时已经到达线上系统。快照需要选择不晚于预测点的可用版本，精确时间连接还要评估基数和成本。不要宣称“天级快照必然消除全部穿越”或虚构 AUC 影响比例。这个边界是由时间可得性推导出的数据设计要求。

<a id="spark-diagnostics"></a>

## 从日志到可解释诊断

### 保留观察粒度和指标口径

| 粒度 | 至少保留 | 原因 |
| --- | --- | --- |
| Application | application ID、可用的 application attempt、Spark 版本、来源、采集时刻 | 关联同一次外部运行并识别版本差异 |
| Stage attempt | stage ID、attempt ID、提交及结束时间、成功或失败 | 重试不能与首次执行混成一个总数 |
| Task attempt | partition/task index、attempt、executor、状态、duration、输入量、Shuffle、spill | 去重、比较长尾并解释重复工作 |
| 解析质量 | 文件片段、水位、坏行数、未知事件数、缺字段数 | 缺日志不能伪装成指标为零 |

以下 JSON 是虚构观察格式，用于讨论 schema，不是采集产物：

```json
{
  "schema_version": 1,
  "application_id": "teaching-app-01",
  "stage_id": 3,
  "stage_attempt": 0,
  "metric_scope": "successful_task_attempts",
  "task_duration_ms": {"p50": 2000, "p95": 12000, "max": 24000},
  "shuffle_read_local_bytes": 1048576,
  "shuffle_read_remote_bytes": 4194304,
  "shuffle_write_bytes": 6291456,
  "memory_bytes_spilled": 2097152,
  "disk_bytes_spilled": 524288,
  "quality": {"complete": false, "bad_lines": 1, "missing_task_events": 2}
}
```

Shuffle read 应分清 local 与 remote；只取 remote 不能叫总读取量。Memory spill 表示被溢写数据的反序列化大小，disk spill 表示落盘序列化大小，两者不能相加声称写盘字节。Stage 墙钟时长与所有 task 耗时之和不同，因为 task 会并行。Input records、SQL 算子输出行数与全链路唯一业务行数也不是同一指标。

如果目标是业务处理量，用成功完成的相关 task attempt 避免重试重复计数；如果目标是资源成本，应另保留失败和投机执行带来的开销。分位数必须附样本数和计算方法；中位数为零时，最大值/中位数比不可用。缺 completion time 应记未知或未完成，而不是构造一个“耗时为零”的完成 stage。

### 运行中与运行后的观察路径

运行中的 driver UI 可观察 job、stage 与 SQL 执行；应用结束后的观察通常依赖 event log 和 History Server。应在应用启动前启用 `spark.eventLog.enabled` 并配置可写日志目录，History Server 也要能读取对应存储。监控 REST API 的 `/api/v1` 可返回结构化信息。滚动日志和压缩需要版本适配；History Server 的日志压缩整理可能丢弃部分事件，应记录证据完整度。

采集器只读观察，不从日志中的字符串获取执行权限。模型接收经过脱敏的统计与代表性错误即可，不必整份日志都放进 prompt；但诊断应能回到 application、stage 和时间窗定位原始证据。

### 诊断步骤要把事实 假设和动作连起来

1. **确认任务与证据完整度。** 先核对运行 ID、输入版本、失败 stage、日志是否完整；超时和看不到日志都不能直接等同失败。
2. **定位慢在哪里。** 比较排队、扫描、Shuffle、计算、写出各阶段，不凭“总共用了十分钟”判断内存不足。
3. **建立有竞争假设的解释。** 单个慢 task 可能是热点、坏机器、远程拉取慢或 GC。热点通常需要 input/Shuffle 量与耗时一起集中，而不只是用户说了“倾斜”。
4. **提出最小改动。** 先裁剪列、过滤分区、校验 Join 基数或更新统计；再考虑分区、广播、盐和资源规格。
5. **注明判断强度。** 使用“已观察到”“疑似”“尚未测量”，并给出反证条件。未知不填成零，关键词提示不升级为实测结论。

教学诊断例：观察到同一 stage 的 P95 为 12 秒、最大值为 24 秒，但缺两个 task 事件。可写“已采集 task 存在长尾，证据不完整”；继续检查慢 task 的数据量、executor 与 GC，不能据此宣布“热点用户导致瓶颈”。如果下次相同 key 换 executor 后仍有同样数据集中，热点解释更可信；如果慢任务总落在同一台坏机器，应转向资源故障。

<a id="spark-verification"></a>

## 验证优化与练习

优化实验固定输入快照、业务参数、代码版本与资源预算，记录冷/热缓存条件和并发背景。先检查 schema、行数、空值、重复键、关键聚合和输出等价，再比较耗时、Shuffle、spill、失败与资源消耗。对浮点聚合明确容差；哈希比较需固定列和规范化方式，不能把文件顺序变化算成业务差异。

练习均为学习任务，不计入题库：

- 在样例中加入重复用户维表行，解释 left join 为什么放大结果，补唯一键检查
- 把固定截止点改成两个不同样本时间，指出哪些行为应被排除
- 比较两份实际计划，说明多出的 Exchange 服务于哪种分布要求；没有计划时不猜 stage 数
- 给虚构日志加入重复 TaskEnd、stage 重试和坏行，定义业务指标与资源指标各如何统计
- 为“广播一定更快”设计反例，列出需要采集的数据与能停止实验的成本上限

继续阅读 [数据工程 Agent 的任务与执行边界](../50-projects/data-engineering-agent-case.md#job-lifecycle)。业务工作流、Spark 内部 DAG 和 UI 进度有不同的状态权威。
