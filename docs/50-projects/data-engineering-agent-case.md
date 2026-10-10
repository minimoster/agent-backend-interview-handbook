# 数据工程 Agent 的受控执行与任务恢复

[返回总目录](../../README.md) · [项目案例](README.md) · [Spark 执行与诊断](../40-backend/37-spark-execution-and-diagnostics.md)

本篇是原创学习补充，用一个自然语言驱动的批处理任务讲清计划、提交、尝试、状态对账、取消和长任务交互。它不是新增面试题，不改变已有题号或统计，也不是读者的项目经历。

技术参照为 Apache Spark 4.0.1，核查日 2026-10-10。下文的任务、ID、状态协议、schema 和测试场景都是教学设计，没有执行 Spark 集群实验。源码路径、测试名或文章描述仅能提示应当核对哪里，不能替代亲自运行或贡献证明。

- [案例范围与请求收敛](#data-agent-scope)
- [业务任务与执行尝试](#job-lifecycle)
- [提交双写与重启对账](#job-reconciliation)
- [长任务 UI 与流式事件](#long-task-ui)
- [可组合 Skill 与有界计划](#composable-data-skills)
- [验证矩阵与讲解边界](#data-agent-verification)

<a id="data-agent-scope"></a>

## 案例范围与请求收敛

### 从一句请求得到一份可批准的计划

教学请求：“计算已登记事件表截至 2026-10-10 的过去七天用户点击数，保留用户维表中的所有用户，输出到我的分析空间。”

请求进入执行前，至少收敛这些信息：

1. **数据与语义。** 哪个租户、哪张事件表、用户维表哪个版本；点击定义；UTC 或业务时区；窗口上下界；重复、迟到和空 ID 如何处理。
2. **模式。** 本次是只生成查询、预估计划，还是已授权执行；是否允许创建输出表或文件，是否允许替换旧结果。
3. **预算。** 可读表/列、扫描分区、并发和时间上限、输出规模；预估可能不准确，还要有运行时限额与停止机制。
4. **结果契约。** 输出 schema、主键与质量断言，哪些校验通过后才能发布，谁能读取结果。

Catalog 负责提供真实表字段、可用版本和权限相关信息。模型可以提出候选，不得凭记忆补一张不存在的表。即使计划只读，后端仍要限制可用函数、外部连接、路径和相关资源；仅检查 SQL 以 `SELECT` 开头无法建立完整边界。

成功也应分层：`PLAN_VALIDATED` 说明计划合法；`COMPUTE_SUCCEEDED` 说明计算后端完成；`QUALITY_PASSED` 说明业务校验通过；`RESULT_PUBLISHED` 才说明用户可获取有效结果。一个 SQL 文件、一份执行配置或一段成功文案都不能充当最终完成证据。

### 划分状态权威

| 层 | 管理对象 | 可决定什么 |
| --- | --- | --- |
| Agent 运行 | 请求、计划、步骤依赖、授权和预算 | 下一步是否允许执行 |
| 业务 Job | 用户想完成的一次有界计算 | 本平台的成功、失败、取消和发布 |
| 外部 application | Spark driver 与 executors | 外部计算的真实运行状态 |
| Spark job/stage/task | action 触发的内部计算 | 具体调度与执行指标 |
| UI | 事件、文字和用户操作 | 展示与发送控制请求，不能凭本地标志改变后端事实 |

Spark application 与内部 job 的含义见 [官方术语](https://spark.apache.org/docs/4.0.1/cluster-overview.html#glossary)。一次业务 Job 可以对应多个 action，也可能在重试时关联新的 application；共享 application 的服务则可能用 job group 关联多个内部 job，不能要求所有 ID 一一对应。

<a id="job-lifecycle"></a>

## 业务任务与执行尝试

### 五类 ID 各自解决一个问题

以下字段属于本篇建议模型，仅用于教学设计：

| 字段 | 身份语义 | 生命周期 |
| --- | --- | --- |
| `run_id` | 一次 Agent 请求运行 | 关联多个步骤和相关任务 |
| `job_id` | 一次业务目标 | 重试时保持不变 |
| `attempt_id` | 一次业务执行尝试 | 每次真实重试新建，历史不覆盖 |
| `submission_key` | 该 attempt 的外部提交身份 | 网络重发沿用，不为超时重新生成 |
| `external_ref` | 后端、application ID 及可用的外部 attempt ID | 用于查询、取消与日志关联 |

另设幂等记录归并客户端对同一业务请求的重复投递。建议以`(tenant_id, operation, caller_idempotency_key)`作为数据库唯一身份，另存首次请求的规范化`fingerprint`，其中包含目标、输入版本及影响结果的业务参数。相同身份且fingerprint一致时返回同一业务Job或明确的进行中结果；fingerprint不同时拒绝并报告冲突。网络重发沿用客户端键，显式新业务运行使用新键。若选择按内容寻址，应说明不同内容会产生新身份，不同时承诺检测同一客户端键的参数误用。业务attempt、YARN application attempt、Spark stage attempt和task attempt是不同重试层，不能混算。[AWS幂等API设计](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)、[Stripe同键参数校验](https://docs.stripe.com/api/idempotent_requests)


### 把意图与事实分开存

建议 `JobRecord` 保存期望动作、当前观察状态、状态版本和最后对账时刻。可以用以下状态表达业务进度：

```text
CREATED -> QUEUED -> SUBMITTING -> SUBMITTED -> RUNNING
RUNNING -> VERIFYING -> SUCCEEDED
SUBMITTING/SUBMITTED/RUNNING -> RECONCILING  （外部结果不确定）
可恢复失败 -> RETRY_WAIT -> 新 attempt -> SUBMITTING
不可恢复失败或预算耗尽 -> FAILED
可取消状态 -> CANCEL_REQUESTED -> 观察与核对 -> CANCELLED
```

`RECONCILING` 是内部仍待确认的情况，不是 Spark 的状态。`CANCEL_REQUESTED` 记录用户意图，不能立刻宣称外部计算已停止。`FAILED`、`SUCCEEDED`、`CANCELLED` 是本业务版本的终态；自动重试等待应另存为 `RETRY_WAIT`，避免一会儿对用户报终态失败、一会儿又恢复运行。显式再次执行则建立新业务版本并保留关联。

状态更新使用期望版本比较，绑定当前 attempt 与执行租约 epoch。旧执行者即便晚到成功回调，也不能覆盖新 attempt 的状态。拒绝旧回调后仍可保存其审计信息，以便处理残留计算与产物。租约本身不能阻止外部计算继续，写回和结果发布都要检查有效执行身份。

### 重试先分类 再检查副作用

| 情况 | 建议策略 | 重试前的证据 |
| --- | --- | --- |
| schema 不匹配、字段不存在、权限拒绝 | 阻断并修正计划，不原样重试 | 具体校验错误与输入契约 |
| 资源临时不足、明确可恢复的连接错误 | 有上限的退避与 jitter | 外部未运行或上次已终止，剩余预算 |
| `FetchFailed` 或 executor 丢失 | 先了解 Spark 内部恢复，再决定业务重跑 | stage/application 最终状态和失败原因 |
| OOM | 查分区、数据形态和内存后再决定 | 原样运行是否必然重复，调整是否获准 |
| 提交/结果回写超时 | 先对账，不新建 attempt 盲重提 | 同 submission_key 对应的外部状态 |
| 用户请求取消 | 停止自动重试和后继步骤 | 持久化取消意图与后端反馈 |

不能把异常消息含有 “timeout” 就当作可重试证明。总预算需要覆盖应用层和 Spark 内部的重复工作，否则各层独立重试会放大负载。每次 attempt 固定输入快照、计划摘要与输出位置；换输入、扩大权限或改写发布目的地属于新计划。

### 取消贯穿执行链

取消流程是 UI 发请求、服务核对归属与版本、持久化意图、停止未启动步骤，再调用对应后端的取消能力并确认结果。关闭聊天窗口或停止 token 流，不会自动停止 Spark。

共享 SparkContext 场景可在提交 action 的线程为该 attempt 设置 job group，再对该 group 取消；注意线程相关属性和 PySpark 线程传播限制。取消当前 active jobs 不保证阻止稍后新提交的 action，因此编排器还必须检查持久取消意图。`interruptOnCancel` 有具体线程中断行为和存储兼容注意事项，不能把它当作无条件开启的“立即停止”按钮。[SparkContext job group 与取消 API](https://spark.apache.org/docs/4.0.1/api/scala/org/apache/spark/SparkContext.html)、[PySpark 并发 job 注意事项](https://spark.apache.org/docs/4.0.1/job-scheduling.html#concurrent-jobs-in-pyspark)

若是独立提交的 application，取消目标应交给所选集群后端的适配器；杀掉本地 `spark-submit` 进程并不能通用地证明集群 application 已终止。Client 与 cluster deploy mode 中 driver 所在位置不同，提交端退出语义也不能一概而论。[官方提交模式](https://spark.apache.org/docs/4.0.1/submitting-applications.html)

取消与成功竞态应在设计前明确：本篇采用“已完成且已提交发布事务的成功不会被迟到取消覆盖”。取消请求被接受后尚未发布的结果先禁止发布，由对账确认计算状态并收敛；后端不可达时保持“取消待确认”，不能向用户承诺已停止或偷偷重跑。确认取消终态时，还要确保没有后继步骤、重试和可见的半成品。

<a id="job-reconciliation"></a>

## 提交双写与重启对账

### 数据库提交不是外部计算提交

危险窗口：外部后端接受了 attempt A，服务还没保存 application ID 就崩溃。重启后看到 `SUBMITTING`，直接再提交一次可能创建第二份计算。反过来，先标内部 `RUNNING`，外部提交失败，也可能留下永久“运行中”。

本篇建议将 job、attempt 和待发送 submit intent 在短数据库事务中写入；worker 领取 intent，以稳定 `submission_key` 调用后端，保存外部引用及观察状态。需要的持久化结构至少包括：

| 记录 | 主要字段与约束 |
| --- | --- |
| Job | 租户、业务幂等键、请求摘要、计划版本、状态版本、取消意图 |
| Attempt | job_id、尝试序号、submission_key、external_ref、执行 epoch、错误分类、观察时间 |
| Submit intent | attempt_id、待发送/已接受/未知、领取者、租约、下一次处理时间 |
| Artifact | attempt_id、内容摘要、schema、输入版本、临时/已验证/已发布、可见范围 |

Outbox 使“需要提交”不会随进程内存丢失，通常仍是至少一次交付。外部系统没有幂等提交或按稳定身份查询的能力时，它不能创造跨系统 exactly-once。不能从 `save`、UUID 或 upsert 推导出“永远不会双执行”。这是本篇的恢复设计与限制说明。

### 启动与周期对账的确定分支

1. 扫描未收敛任务和过期租约，领取者用版本/epoch 抢占；不能让所有恢复进程同时决定重提。
2. 已有 `external_ref` 的 attempt，查询适配器认可的后端状态；记录查询时刻与证据来源。
3. 没有外部引用但有提交意图的 attempt，按 submission_key 查找：唯一匹配则补关联；明确未接受才重发同一意图；查询失败或有多个匹配则进入待核对。
4. 发现外部成功后进入校验与发布；失败则分类；仍运行则继续观察；取消意图始终参与决策，禁止新增后继和自动重试。
5. 外部查不到并不总是失败，可能是历史保留期、索引延迟或查询范围错误。保存“未知”及原因，按后端契约选择继续检查或人工处理，不伪造终态。

Spark 的 live UI 和 History Server 提供指标与历史证据，但不能把“History Server 暂时没有记录”当成集群作业不存在，也不能把缺结束事件当成仍然运行。[官方监控与历史记录说明](https://spark.apache.org/docs/4.0.1/monitoring.html)

### 结果发布是单独的提交边界

每个 attempt 写自己的 staging 产物，先验证完整性、schema、质量和输入版本，再提交业务结果指针。发布事务要求 job/attempt/epoch 仍有效且满足取消策略。外部算完后内部验收失败，可以显示“计算完成，结果校验失败”；不应把两个状态折叠。

对象存储、文件系统和表格式有不同提交语义。不要依赖所有平台都支持目录原子 rename；可以用该系统支持的事务提交或受控 manifest/结果指针。读者只看已发布版本，清理仅删除该 attempt 拥有的临时产物，不覆盖其他任务，也不删仍被引用的结果。重试发布同一摘要要幂等，发布不同摘要必须检测冲突。

### 一个崩溃轨迹

教学设定：job J 的 attempt A 已被后端接受，但回写失败。恢复者按 A 的 submission_key 找到唯一 application，补写关联并观察；此时不建立 attempt B。随后 A 成功，质量校验通过，发布指针提交，J 才成为 SUCCEEDED。若取消先进入持久记录，则恢复者按取消协议处理，不能因为 UI 曾显示“执行中”就无视取消。这里没有执行故障注入，轨迹用于确定实现必须测试的分支。

<a id="long-task-ui"></a>

## 长任务 UI 与流式事件

### 流式文本和运行进度分别建模


本篇建议 UI 消费有类型的事件，而不从自然语言中解析“成功”：

```json
{
  "event_id": "teaching-event-12",
  "run_id": "teaching-run-01",
  "job_id": "teaching-job-01",
  "attempt_id": "teaching-attempt-01",
  "seq": 12,
  "state_version": 5,
  "type": "JobStateObserved",
  "payload": {"status": "RUNNING", "source": "execution-adapter"}
}
```

事件类型可以包括 `TextDelta`、`StepStarted`、`StepCompleted`、`JobStateObserved`、`ArtifactValidated`、`WarningRaised` 和 `RunFinished`。TextDelta 只影响文案，JobStateObserved 携带已提交的业务状态版本，ArtifactValidated 也不自动等于 ArtifactPublished。前端的 READY 表示可以继续输入，不能暗示所有后台任务已结束。

### 重连和背压都要有协议

- 事件 ID 用于去重，单一运行流的 seq 用于发现缺口；重连使用已确认游标，缺失时取状态快照并标记快照版本
- 状态和产物事件来自可恢复记录，普通 token 可按时间合并；UI 不能以最后收到的字符串覆盖较新状态
- 采用有界队列与生产者反馈，不能把任意 `sleep` 等同背压；关键事件先持久化，再交付或重放
- UI 主线程只渲染和处理输入，阻塞模型、网络和计算工作交给 worker；跨线程更新必须遵守所用 UI 框架契约
- 多任务隔离 run/job/attempt、输出位置、队列和配额；共享 Service 对象不证明已具备多租户隔离
- 断线默认不自动取消长任务；若产品规定断线取消，需要明确期限、恢复规则与持久控制请求

队列慢时可以合并文本，但不能永久丢弃取消确认、终态和发布事实。多个 run 的 seq 无全局可比性；迟到 attempt 的进度只进入历史，不覆盖当前 attempt。显示“最近观察时间”和未知状态，会比一条永久停在 99% 的进度条更可信。

<a id="composable-data-skills"></a>

## 可组合 Skill 与有界计划

### 描述层不授予执行能力


本篇建议四道边界：描述说明输入输出，注册表记录已审核能力，planner 生成候选步骤，执行器校验能力、参数、授权与预算。Skill 文件、Catalog 文本、日志和数据行都是可能含恶意指令的输入，不能让它们动态导入代码、扩大工具集或改写用户授权。

下面是原创有界计划片段，所有资源标识均为教学值：

```json
{
  "plan_version": 1,
  "mode": "execute_authorized",
  "input_snapshot": "events-snapshot-v3",
  "max_steps": 6,
  "max_attempts_per_job": 2,
  "deadline_seconds": 600,
  "steps": [
    {"id": "query", "tool": "build_query", "depends_on": [],
     "input_schema_version": 1, "output_schema_version": 1},
    {"id": "validate", "tool": "validate_plan", "depends_on": ["query"],
     "input_schema_version": 1, "output_schema_version": 1},
    {"id": "execute", "tool": "submit_job", "depends_on": ["validate"],
     "input_schema_version": 1, "output_schema_version": 1},
    {"id": "quality", "tool": "check_result", "depends_on": ["execute"],
     "input_schema_version": 1, "output_schema_version": 1},
    {"id": "publish", "tool": "publish_result", "depends_on": ["quality"],
     "input_schema_version": 1, "output_schema_version": 1}
  ]
}
```

`execute_authorized` 是执行器核对真实授权后的内部标记，模型自行写这个值不提供授权。上限之外还要约束实际读取量、输出、执行资源与工具调用频率。只要求“生成 SQL”的请求应停在生成/校验，不应自动追加 submit_job；没有计算运行时则明确停在规划阶段，不伪造执行成功。

### 计划校验和失败传播

校验器应检查重复节点、未知工具、缺失依赖、环、参数 schema、数据权限、写入范围、预算和版本兼容。每步保存输入摘要、输出 artifact 版本和状态；“依赖列表是数组”不代表实现了拓扑调度。允许并行还需要资源配额、就绪节点领取、取消传播、失败阻断和共享资源控制。

诊断节点与发布节点可以有不同策略：执行失败后发布必阻断，只读诊断可基于已有失败日志继续，但必须明确它的输入是部分证据。修复建议不得自动改计划扩大数据范围或重跑；同范围、已有授权的有限恢复也须符合预算与错误分类。调度器应保留“部分步骤已成功”的状态。

<a id="data-agent-verification"></a>

## 验证矩阵与讲解边界

以下是建议实现时运行的测试，当前均未执行：

| 场景 | 必须成立的断言 |
| --- | --- |
| 客户端重复投递同一幂等身份 | 同一租户/操作/客户端键且指纹一致返回同一Job；同身份不同指纹被拒绝；其他租户、新操作或新键不误合并 |
| 后端接受提交后服务崩溃 | 恢复关联原 attempt；不因超时盲建新 application |
| 对账查询不可达 | 状态保持未知/待核对；不会伪造失败或无界重提 |
| 旧执行者迟到成功 | 版本或 epoch 检查阻止覆盖新 attempt 和发布 |
| 取消与成功同时到达 | 按既定发布边界收敛，UI 与持久状态一致 |
| 首次 attempt 写出半份文件 | 未验证产物不可见；新 attempt 不共用临时输出 |
| UI 断线后重连 | 去重、补缺口或取快照；不把旧终态覆盖新版本 |
| 恶意 Skill/数据文本要求执行任意代码 | 未知工具和越权参数拒绝，不能改变执行白名单 |
| Spark 环境缺失 | 返回规划/运行不可用状态，不声称计算成功 |
| 优化后更快但行数错误 | 质量失败，禁止发布，保存诊断与比较证据 |

讲解时可以说“我理解业务任务与外部执行不同，设计会保留 attempt 与对账证据”；只有亲自实现、走读和运行后，才能把某能力说成自己的工作。本文不声称完成了部署、取消恢复或性能提升。可以沿本篇选一条失败轨迹实现最小原型，再用 [Spark 诊断补充](../40-backend/37-spark-execution-and-diagnostics.md#spark-diagnostics) 定义观察证据。


可先运行[幂等身份内存反例](../../examples/agent_contracts/README.md)核对同键异参数合同。该实验没有连接Spark或数据库，不替代上表的集成验收。
