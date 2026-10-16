# 两个公开仓库的机制走读

[返回总目录](../../README.md) · [题目索引](../../QUESTION_INDEX.md) · [版本与纠错](../../errata/README.md)

Openresearch 现名 ResearchPilot，Saber 现名 KnowFlow；以下机制仍基于原固定提交：Openresearch 为 5f876faabba238563001151fc7a573581ddaf869，Saber 为 6d5bb13dc74dc03a7a59c74b2396c3b10e84caef。本章沿固定提交学习状态、调度、评测与投影机制；部署状态与性能仍需实际运行确认。练习时，从一个请求入口沿文件和调用栈走读。

<a id="a39"></a>

### A39 Openresearch 的状态持久化和执行租约解决什么？有什么边界？

**优先级：P0**

**知识点详解**
- 直接核对FilePlanStore可见临时文件Sync、Rename、目录Sync，注释明确面向单机部署。Scheduler确实递增ExecutionEpoch，但完成/失败路径的executionMatches检查任务状态、ExecutionID、LeaseOwner和AssignedTo，并未把epoch作为外部写入端的fencing协议。字段存在、执行身份匹配与分布式fencing保证应分别解释。
- rename着重避免读到半份替换文件，fsync涉及落盘；二者不自动提供跨文件事务，也不自动解决多个执行者同时提交。平台与文件系统语义需要明确。
- 该固定FilePlanStore先更新内存再调用persistLocked，持久化失败时没有回滚内存；目录Sync还可能在Rename完成后返回错误。因此失败响应不必然表示状态未改变。应分别在写入、文件Sync、Rename和目录Sync阶段注入错误，对比当前进程读取、磁盘快照和重启回读，再明确回滚、隔离故障状态或对账策略。这里是静态代码核对，未运行该项目故障注入。
- 完成/失败提交路径有 executionMatches 检查并处理迟到结果；仍应测试取消、恢复等组合路径。该实现的单机身份校验不能直接扩展为多个进程共享文件时的分布式互斥保证。

**具体例子** ：执行者甲超时，乙接管后，甲又返回结果；需要验证甲能否覆盖乙的新状态。这应写成故障测试，不凭字段名推断。

**30 秒答题主线** ：当前实现关注单机快照落盘和执行身份控制。我会分别解释rename/fsync、持久化失败窗口、ExecutionEpoch计数器与完成提交的身份匹配。计数器存在不代表写入端执行了分布式fencing，返回失败也不保证RAM和磁盘都没变化。

**追问** ：rename 成功但进程立即断电会怎样？旧执行者回写如何复现？

#### 参考答案

rename 的原子可见性不等于断电后的目录项持久性；在写入、文件 Sync、Rename 和目录 Sync 分阶段做故障测试，分别检查 RAM、磁盘和重启结果。固定实现先改内存再持久化，失败时不能默认没有变化。旧执行者测试应先领取身份1，再重新领取身份2，最后提交身份1结果，检查被拒绝。[固定 FilePlanStore](https://github.com/minimoster/agi-openresearch/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/store/file_plan_store.go)、[固定身份校验](https://github.com/minimoster/agi-openresearch/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/scheduler/scheduler.go#L703-L708)

**验收点：** 分别假设Rename前失败与Rename后目录Sync失败，列出RAM、磁盘与重启可见状态，不把返回错误当作全未生效。

**常见错误** ：原子文件替换被说成分布式强一致；看到租约字段就宣称绝无双执行。

故障注入仍待执行。

<a id="a40"></a>

### A40 Openresearch 的 DAG、Agent routing 与 Eino 各负责什么？

**优先级：P0**

**知识点详解**
- 当前项目使用 Go/Gin、Eino、React/TypeScript、Docker 和 SSE，并具有 DAG 与 typed agent routing。HTTP 接入、任务编排、模型/工具执行、容器执行和展示是不同层。
- DAG 描述任务依赖，只有依赖满足的节点才能就绪；Agent routing 决定由哪类执行逻辑处理节点；Eino 提供模型、工具、编排等组件能力，业务正确性仍由应用负责。
- 已核对 coder/general 共用 Coder，但不能推广成“所有分支都运行同一条 chain”。应按实际类型分支解释，而非用一个通用 Agent 词概括所有实现。

**具体例子** ：检索产物成为写作节点输入，是数据依赖；代码任务进入执行环境，是能力路由。这两件事不要混讲。

**30 秒答题主线** ：我会按请求入口、DAG 调度、类型路由、模型工具执行和结果展示拆解。框架提供组件与编排，项目负责业务状态与边界。然后沿一个真实请求讲到具体执行分支，不把所有 agent 类型描述成相同实现。

**追问** ：节点失败后哪些后继不能执行？如何检查环、缺失依赖和错误类型？

#### 参考答案

必须成功的依赖失败后，其后继不得执行发布；可选诊断分支须显式允许失败证据。执行前按 ID/依赖图校验环和缺失节点，再检查类型/产物合同，不能从“有依赖数组”推断实现了这些检查。案例回答应区分建议验收与已读到的代码。

**验收点：** 必要依赖失败时发布节点不得启动；缺依赖和环在执行前给出明确错误。

**常见错误** ：把前端进度图当实际 DAG 调度；把 Eino 当成提供所有可靠性保证的黑盒。

图校验是应核对项目是否覆盖的追问。

<a id="a41"></a>

### A41 Openresearch 的预检、正式评测与修复如何配合？

**优先级：P0**

**知识点详解**
- 预检 preflight 最多8条样本，用于检查适配器；总尝试次数限制1–3，所以最多2次修复。正式 benchmark 独立配置：默认 min(数据行数,1000)，参数可至100000并受实际行数约束。不能把预检规模当整个评测规模。
- Accuracy 是正确样本比例；F1 综合 precision 与 recall；MAE 平均绝对误差，MSE 平均平方误差且更惩罚大误差。分类和回归指标不能随意混用。
- 代码包含 claimRubric 的规范化/哈希验证；benchmark execute 阶段按 adapter 输出的 predictions.jsonl 中 prediction/target 两列逐样本重算，检查指标与输出记录一致性。这些验证函数没有按样本 ID 重新读取可信原始标签，dataset hash 匹配不等于标签独立可信。最终 benchmark_validate 另检查 manifest、hash、样本数范围与有限数，不重新读取 predictions。详见 [A46](#a46)。支持大样本运行不等于已经完成大样本验证。

**具体例子** ：预检8条全通过，只能说明这批输入下接口可运行；正式500条中正确450条才是这次运行的90% accuracy，仍须说明数据来源与划分。数字均为教学假设。

**30 秒答题主线** ：我会把适配器预检和正式 benchmark 分开。前者最多8条、最多3次尝试；后者按配置运行并重算指标。效果评估还需检查实际数据划分、日志与逐样本结果，并记录尚未运行的检查。

**追问** ：谁生成标签？评测规则能被待评模型改动吗？多分类 F1 是哪种平均方式？

#### 参考答案

参考标签、数据划分和判分规则应由独立可信评测侧冻结；待评模型可以生成候选代码，不能重定义标签或成功标准。多分类 F1 必须声明 micro、macro 或按真实样本数加权的 weighted，并说明无样本类、无正预测及解析失败的处理；不能只报一个“F1”。报告重复试验、失败样本和成本，8条预检不代表总体效果。

**验收点：** 同一多分类混淆矩阵分别算micro、macro和weighted F1，报告权重、缺类及无预测处理。

**常见错误** ：把模型给出的分数直接当指标；不写样本数；把同组反复修复叫独立测试。

<a id="a42"></a>

### A42 Saber 怎样连接研究、文档生成与知识索引？

**优先级：P0**

**知识点详解**
- 当前实现包含 Go/chi、Vue、PostgreSQL、Milvus、Elasticsearch，Neo4j 为可选；研究、写作、审阅后形成文档，再保存和建立索引。
- 讲架构要沿数据生命周期：请求怎样进入、任务如何组织、证据怎样检索、文档怎样生成、主数据和派生索引怎样维护。
- PostgreSQL、向量库和全文索引解决的需求不同；分别说明各组件是否必需、故障时如何降级，以及维护代价。

**具体例子** ：想比较向量和关键词召回效果，要保留同一文档/块标识，才能融合和追溯；若各系统 ID 不一致，问题首先是数据契约。

**30 秒答题主线** ：Saber 是围绕研究到文档沉淀的应用链路。我会先说明输入与最终产物，再讲角色流程、检索和持久化。组件各有职责，Neo4j 是可选能力，不会把可选依赖说成每次请求必经。

**追问** ：去掉 Neo4j 能否运行？哪个系统是主数据源？为什么需要两种索引？

#### 参考答案

固定 Saber 的知识检索可以在 Neo4j 不可用时降级，但这是能力受限而非完全等价运行。PostgreSQL 保存主记录，向量/关键词/图索引承担不同召回路径；需要讲清索引更新、权限过滤和降级结果，不能只报组件名单。[固定架构说明](https://github.com/minimoster/agi-saber/blob/6d5bb13dc74dc03a7a59c74b2396c3b10e84caef/README.md)

**验收点：** 去掉可选图能力时列出剩余可用路径与失去的结果，不声称功能完全相同。

**常见错误** ：只背 PostgreSQL/Milvus/ES；把可选服务说成全部已在生产使用。

具体入口与部署状态仍需你走读、实际运行确认。

<a id="a43"></a>

### A43 Saber 检索的并行边界和重排实现，最容易说错什么？

**优先级：P0**

**知识点详解**
- 代码核对：rewrite 后多 query 并行，每个 query 内顺序执行召回并做 RRF，跨 query 再融合与 LLM rerank；最终结果优先使用父块。父块内容在召回查 PG 时已读入，并非重排后才查库。
- “多 query 并行”和“BM25/向量检索并行”是不同层级的结论；若没读启动 goroutine 的位置，不能把整个检索栈说成全面并行。
- LLM rerank读取子块内容preview，不是Cross-Encoder。跨query融合实际以子块全文字符串作为map键，没有计算内容哈希；同一query的融合用PG ID。相同文本但来源或父块不同的候选可能合并，应保留这一身份与证据追溯边界。最终使用父块会增加token，应检查父块去重和上下文预算。

**具体例子** ：3个 query 同时开始，各自先查一个索引再查另一个；总延迟不同于6个检索请求全部同时启动。

**30 秒答题主线** ：我会准确说明并发发生在哪层。Saber 对多 query 并行，单个 query 中的召回按现有代码顺序执行，之后进行 RRF 和 LLM 重排，最终优先使用随召回结果取得的父块。如果要把召回并行化，需要先验证依赖、限流和效果。

**追问** ：单路检索失败能否保留另一条结果？父块回补会不会重复？

#### 参考答案

单路失败是否保留另一条，取决于实际错误策略，应分别注入超时和空结果核对。固定实现多个 query 可以并发，单 query 的向量与关键词路径按代码顺序执行；跨 query 用原始子块文本去重，回补父块仍须独立去重和计入 token 预算。[固定 hybrid.go](https://github.com/minimoster/agi-saber/blob/6d5bb13dc74dc03a7a59c74b2396c3b10e84caef/internal/domain/rag/hybrid.go)

**验收点：** 不同来源的两个候选有相同子块文本，按固定实现会合并；父块/出处身份的丢失必须能指出。

**常见错误** ：把“混合”自动解释成“并行”；把 LLM 排序讲成自己训练过重排模型。

概念对照见 A13、A14。

<a id="a44"></a>

### A44 Saber 长期记忆的 outbox、版本 hash 与 reconcile 为什么不是强一致？

**优先级：P0**

**知识点详解**
- 直接读取 memorytx 可见长期记忆变更与 memory_outbox 在同一 PG 事务提交，目标为 Milvus 向量与 Neo4j 图投影。不能据此宣称文档 RAG 的 ES 索引也走同一机制。
- 投影更新仍有时间窗口，消息可能重复或乱序；Version/ContentHash 参与差异判断，reconcile 为缺失或陈旧状态入队修复，但不让各库瞬时同步，也需检查其扫描覆盖范围。
- 面试应讲清用户可见语义：记忆已更正但向量投影未更新怎么办？什么时候重试、何时告警、删除如何传播，都需有明确策略；不要从长期记忆推断所有业务链路的保证。

**具体例子** ：用户偏好记忆 v2 已在主库，向量投影仍是 v1；读取时应考虑陈旧版本，待投影更新并对账。这个问题与文档知识库的索引更新要分别分析。

**30 秒答题主线** ：当前核对的是长期记忆的 PG 事务加 Milvus/Neo4j 异步投影。Outbox让更新意图可恢复，版本/hash与reconcile帮助幂等和修复，但不等于跨库强一致，也不能扩大成所有 RAG 索引都拥有相同保证。

**追问** ：先收到 v3，再收到 v2 怎么办？失败任务一直重试会怎样？

#### 参考答案

消费 v2 前核对主记录当前版本/摘要，不能在已投影 v3 后无条件覆盖。重复失败要有次数/时间预算、退避、dead-letter 或 dead 状态及告警；修复后可重放并对账。事务 outbox 只保证主记录与待发送事件一起提交，不能消除投影延迟和消费者故障。[固定投影 worker](https://github.com/minimoster/agi-saber/blob/6d5bb13dc74dc03a7a59c74b2396c3b10e84caef/internal/application/memoryprojection/worker.go)

**验收点：** 先投影v3再收到v2，核对主记录与版本；过期消息不能让索引退回v2，失败处理有预算和告警。

**常见错误** ：把 outbox 说成自动 exactly-once；把“定期对账”说成“任何时刻都没有不一致”。

<a id="a45"></a>

### A45 ResearchPilot 的任务 Completed，为什么不等于主张 verified？

**优先级：P0**

**知识点详解**

`executeClaimEvidenceBuild` 有三层语义：Task 的 Completed 表示评审报告成功产出；graph 的 assessed/degraded 表示评审过程是否完整满足合同；各项 criterion 的 verified/unverifiable 等才表达证据判定。assessed 也不保证全部 verified。证据引用覆盖率只统计有 EvidenceIDs 的准则比例，与主张 verified 比例不是同一指标。

缺少评审模型、模型调用失败、JSON 无效或 verdict 合同不完整时，代码构建 degraded 图，保留“不能确认”的结论，仍可成功生成报告并 Completed。rubric 校验失败或图序列化失败走失败分支，不能概括为所有异常都 Completed。

**具体例子**：rubric 有两项准则，模型只给第一项 verified。`buildClaimEvidenceResults(requireComplete=true)` 发现缺项返回错误；上层丢弃已有 proposal，以空 proposal 重建两项，全部为 unverifiable、confidence=0，graph 为 degraded。报告成功产出时 Task 仍为 Completed。固定测试也检查不完整评审不会残留 verified verdict。

| 条件 | Task（报告成功时） | graph | 准则含义 |
| --- | --- | --- | --- |
| 模型缺失或调用/JSON失败 | Completed | degraded | 全部 unverifiable |
| 两项准则只返回一项 | Completed | degraded | 丢弃已有判断，全部 unverifiable |
| 完整合法判断，仅 repo_manifest 却声称 verified | Completed | assessed | 对应准则降为 unverifiable，confidence ≤ 0.25 |
| 完整合法判断且引用执行派生证据 | Completed | assessed | 仍逐项看 verdict，不保证全 verified |
| rubric 无效或图序列化失败 | 失败分支 | 无成功报告保证 | 不得套用 Completed |

引用执行派生证据是有关判定的必要检查之一，不能从“有引用”推导真实性、独立复现或语义正确。

**30 秒答题主线**：Completed 是工作流产物状态，verified 是主张的证据状态。我会同时看 Task、graph 和 criterion。评审失败可以产出诚实的 degraded 报告；不完整 verdict 会整体回退为 unverifiable。即使 graph assessed，也要逐项看证据和判断。

**追问**：100% 准则有引用就能写“已验证”吗？两项只评一项时保留第一项 verified 合适吗？

#### 参考答案

不能。引用覆盖只回答有没有证据关联，不能回答证据是否足以支持结论。固定实现对不完整 proposal 整体回退，避免把不完整评审包装成完成判定。仅 repo_manifest 不构成执行派生证据，相关 verified 判定会降级。建议发布侧把“已验证”措辞绑定到所声明范围的准则 verdict、证据适用性和完整性，而不是 Task Completed；这是教学改进建议，并非当前已实现的发布门禁。普通不确定性报告可以发布，只需忠实标注 degraded/unverifiable，不能把任何未验证结果都说成不允许发布。

代码定位：[报告与任务状态](https://github.com/minimoster/ResearchPilot/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/agent/claim_evidence.go#L112-L173)、[合同与降级](https://github.com/minimoster/ResearchPilot/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/agent/claim_evidence.go#L331-L435)、[覆盖率](https://github.com/minimoster/ResearchPilot/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/agent/claim_evidence.go#L463-L489)、[缺项测试](https://github.com/minimoster/ResearchPilot/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/agent/claim_evidence_test.go#L101-L141)。本题为固定代码静态走读，未运行 ResearchPilot。

**验收点：** 对照矩阵分别解释 Completed/degraded、assessed/unverifiable 如何同时成立；不能把引用覆盖率当验证通过率。

**常见错误**：看到绿色 Completed 就宣称论文主张已复现；把 confidence 当统计置信区间；把建议门禁说成当前功能。

<a id="a46"></a>

### A46 hash 匹配、逐行重算分数，为什么仍不等于独立可信评测？

**优先级：P0**

**知识点详解**

固定代码的 `ResearchCodingAgent.ExecuteTask` 分别路由 benchmark_execute 与 benchmark_validate。逐行重算位于 execute → runBenchmarkHarness → validateBenchmarkOutputDirectory；最终 validate 节点只声明 dataset_manifest、benchmark_run_metrics、benchmark_run_manifest 输入，没有传 predictions。

execute 前后对数据集与 adapter 文件做 hash 检查，有助于发现受检查字节被修改；输出 manifest 的 dataset hash 也须匹配。hash 比较要求可信预期摘要，并不证明标签权威性、任务定义正确或覆盖了冻结样本计划。输出校验要求 count > 0 且不超过 limit/RowCount，预测行数等于自报 count；这不等于所有计划样本恰好出现一次。

`readBenchmarkPredictionLines` 只保留 adapter 输出行的 prediction 和 target，忽略 JSON 中的 index/sample_id；分类或回归指标据这两列重算。这些验证函数未把输出行逐一绑定到可信原始标签或已冻结样本集合。最终 executeBenchmarkValidation 校验 manifest 状态/hash/count 范围与指标有限数，不进行独立标签评分。这里描述静态代码合同边界，未复现攻击，也不宣称整个系统必然存在漏洞或已修复。

**具体例子**：教学计划固定 s1→cat、s2→dog、s3→cat，adapter 乱序输出 s3→cat、s1→cat、s2→cat。可信评分为 2/3；不能使用 adapter 自填的 target 或它宣称的 100%。若少交 s2，应拒绝整次评测，而不是把分母缩成 2 后报满分。示例数字不是项目实测。

**30 秒答题主线**：我区分字节一致、输出自洽、样本覆盖和独立金标评分。固定实现的 hash 与重算能检查一部分一致性，但重算 target 来自 adapter 输出。我会由可信评分侧冻结版本、样本 ID 和 gold，以固定分母判分，对缺失、重复、未知 ID 和解析失败明确处理。

**追问**：行数正确是否足够？adapter 写入 target 和 accuracy 时能否直接采信？

#### 参考答案

行数正确仍可能重复一个样本并遗漏另一个。可信评分侧应独立保存数据集版本、sample_id→gold、样本计划与解析失败策略；adapter 只能交预测，不能重定义标签或分母。版本标识还应绑定实际可信内容，不能只采信 adapter 自报版本。建议隔离评分计划、阻止待评程序修改，并记录覆盖与评分器版本；这些属于教学改进设计，不是对 ResearchPilot 的补丁。

本仓库的[标准库评分器](../../examples/trusted_evaluation/scorer.py)只演示字符串分类 accuracy，可信 plan 为非空 JSON 对象，预测每行严格仅有 sample_id/prediction。拒绝空计划、重复/未知/缺失 ID、非法 schema、空字符串、数值/布尔等边界类型及 target/自报分数字段；JSON 重复键、NaN、坏行和空行也拒绝，失败不输出部分分数。未知类别字符串按错误预测计分，不自动改标签。

```python
# gold 在评分侧冻结，预测不能携带 target；遍历时检查 ID 唯一且已知
correct += prediction == gold[sample_id]
# 只有 seen == gold.keys() 才允许产出分数
accuracy = correct / len(gold)
```

仓库根目录运行，无模型、数据库或 GPU：

```bash
python -B examples/trusted_evaluation/scorer.py examples/trusted_evaluation/plan.json examples/trusted_evaluation/predictions.jsonl
python -B -m unittest discover -s examples/trusted_evaluation -p 'test_*.py' -v
```

[教学计划](../../examples/trusted_evaluation/plan.json)、[乱序预测](../../examples/trusted_evaluation/predictions.jsonl)输出 correct=2、sample_count=3、accuracy=2/3。[测试](../../examples/trusted_evaluation/test_scorer.py)覆盖全对、部分错、全错、覆盖和伪造字段。算法期望 O(n) 时间、O(n) 空间；仅使用 CPU。它不提供进程隔离、计划签名、标签质量保证、版本注册、F1/回归或统计显著性；命令行接收的 plan 必须由可信调用者保护，不能让 adapter 指定或改写。

代码定位：[任务路由](https://github.com/minimoster/ResearchPilot/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/agent/research_coding_agent.go#L35-L50)、[planner 输入](https://github.com/minimoster/ResearchPilot/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/planner/planner.go#L417-L448)、[执行与最终校验](https://github.com/minimoster/ResearchPilot/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/agent/benchmark_harness.go#L187-L308)、[输出合同](https://github.com/minimoster/ResearchPilot/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/agent/benchmark_harness.go#L332-L376)、[预测解析与重算](https://github.com/minimoster/ResearchPilot/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/agent/benchmark_harness.go#L420-L509)。

**验收点：** 保持行数不变，把一个 ID 重复并漏掉另一个，评分器必须拒绝；插入 target 字段同样拒绝。乱序不改分，错误预测不能通过自报分数抬高结果。

**常见错误**：hash 一致就等于数据权威；逐行重算就等于独立 gold 校验；忽略解析失败样本却继续缩小分母报分。

<a id="agentscope-pr-attribution"></a>

## 补充案例：AgentScope 的 Docker/E2B 与 Daytona 沙箱后端

Docker/E2B与Daytona是不同工作区后端，适配时应分别检查路径、权限和输出契约。

对照这两个后端，练习的问题是：同一个Read/Bash工具能否在宿主机与沙箱保持接口一致，同时让路径、工作目录、权限和输出契约落在对应backend？调用工具时显式携带工作区身份，适配层把操作发给获准执行环境；不能只改prompt中的“你在沙箱里”，却仍用宿主机文件API。测试应覆盖工作区外路径、软链接、取消、输出超限和不支持功能，且不把mock通过当云沙箱端到端通过。Docker、E2B、Daytona 及这两个第三方 PR 的测试尚未运行。
