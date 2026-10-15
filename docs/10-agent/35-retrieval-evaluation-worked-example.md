# 检索评测手算：从一条问题到可解释的回归结果

[返回 Agent 目录](README.md) · [RAG 基础](02-rag-retrieval-and-reranking.md) · [评测与模型路由](25-agent-evaluation-and-routing.md) · [Python 检索算法练习](../70-practice/retrieval-ranking-algorithms.md)

本章接着已有的 RAG 与评测章节，把“看召回率、MRR、nDCG”拆成可以手算、写代码和解释的步骤。先回答三个问题：哪些材料算正确证据？模型实际看到了哪些材料？这两者的差距在哪一层产生？

## 1. 先把评测对象变成一张小卡片

假设用户问：“任务取消后，已经开始的工具调用会不会继续执行？”我们准备四段材料：

|证据 ID|内容|人工相关性等级|
|---|---|---|
|A|当前版本的取消语义，明确正在执行的调用如何收尾|3：直接解决核心问题|
|B|当前版本的超时与取消说明，提供部分答案|2：较强相关|
|C|任务状态图，提供背景信息|1：辅助相关|
|X|旧版本的启动接口说明|0：与当前问题不相关|

等级表示这次人工标注的相关性，不是模型自报置信度。这个例子把 1、2、3 都作为二值“相关”，用来算 Precision 与 Recall；排序评测再保留等级差异。

一条评测记录至少保存：问题、语料快照、适用身份与权限、证据 ID 及等级、关键答案要点、任务类别。若评测时文档已更新，仍拿旧标注评分，就可能把正确新版答案判错。ID 可包含文档版本与块号，便于回到对应材料。

**先做一个判断：** A 与 B 都提到“取消”，不代表二者能够互换。B 可能缺少“已提交的调用无法回滚”这类关键条件。相关性是第一层；能否支撑完整答案要继续检查。

## 2. 同一排序，算清 Precision、Recall、Hit 与 RR

系统返回前三项 `[B, X, A]`，设 K=3。全部已标注的相关材料是 `{A, B, C}`。

### Precision@3：交给下游的材料有多少是相关的

三项里 B、A 相关，X 不相关，所以 `Precision@3 = 2/3`。这里固定以 3 个名额为分母；如果只返回 A 一个结果，Precision@3 为 `1/3`。

也有人另外报告“返回结果准确率”，分母用实际返回条数。只返回 A 时它会是 1。这两个数字回答不同问题，应分别命名。固定 K 的口径避免系统只交一条结果就掩盖候选不足。

### Recall@3：应当找出的相关材料找到了多少

一共三份相关材料，找到了两份，所以 `Recall@3 = 2/3`。分母来自相关性标注，而不是本次返回条数。若知识库有九份相关材料，只命中一份，则 Recall 是 `1/9`，不是 1。

Precision 关心返回集合里的噪声，Recall 关心相关集合里的遗漏；公式可参见 [Stanford《信息检索导论》的集合评测](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-unranked-retrieval-sets-1.html)。在固定排序上扩大 K，Recall 不会下降，但 Precision 并不保证单调下降或上升，取决于新加入的材料。

### Hit@3：至少命中一份了吗

本题命中了相关材料，所以 Hit 为 1。对多条问题求平均得到 HitRate@3。它适合观察“完全没找着”的比例，但无法区别找齐三份和只找着一份。因此不要把 HitRate 写成 Recall。

### RR@3：第一份相关材料出现在第几名

第一名 B 已相关，`RR@3 = 1/1 = 1`。若返回 `[X, B, A]`，第一份相关材料在第 2 名，RR 是 `1/2`。前三名都不相关时，RR@3 为 0。

对多条问题的 RR 求平均才叫 MRR。RR 只看第一份相关材料，所以 `[B, X, X2]` 与 `[B, A, C]` 都可以得到 1；需要多份证据的 RAG 不能仅靠 MRR 验收。[Microsoft Research 的定义](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-2008-179.pdf)把 RR 与支持多级相关性的 nDCG 区分开来。

## 3. nDCG：重要证据是不是排得够靠前

仍看 `[B, X, A]`，相关性等级依次为 `[2, 0, 3]`。本章明确采用指数增益：`gain(g)=2^g-1`；第 r 名用 `log2(r+1)` 折扣，名次从 1 开始。

按位置算：

- B 在第 1 名：`(2²−1)/log2(2) = 3`。
- X 在第 2 名：`(2⁰−1)/log2(3) = 0`。
- A 在第 3 名：`(2³−1)/log2(4) = 7/2 = 3.5`。
- 因此 `DCG@3 = 6.5`。

仅看 6.5 很难知道好坏，于是用“同一问题的理想排序”作分母。完整标注里最优前三项是 `[A, B, C]`，等级为 `[3,2,1]`，得到：

`IDCG@3 = 7 + 3/log2(3) + 1/log2(4) ≈ 9.39279`

`nDCG@3 = DCG@3 / IDCG@3 ≈ 0.69202`

直觉是：A 最重要却排第三，系统要被扣分；B 提前不能完全抵消 A 的延后。理想分母必须来自完整候选标注，不能只把已召回的 B、X、A 排序。后一种做法会忽略遗漏的 C，使结果偏乐观。[排序评测教材](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)解释了累计增益与理想归一化。

**用库时再核对一次定义。** nDCG 实现可能使用线性增益 `g` 或指数增益 `2^g−1`，还可能对并列分数取平均。scikit-learn 的 [ndcg_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html)直接使用输入的真实分数并有 ties 选项。若要与本章指数增益对齐，应传递相应增益值，并保持候选全集、K 和并列处理一致，不能只因为函数名一样就比较数值。

## 4. 文档都相关，为什么答案仍然不完整

把答案拆成两个必要要点：

- 要点 1：取消请求如何改变任务状态，可由 A 或 B 支撑。
- 要点 2：已产生副作用的调用如何核对与收尾，必须由 A 支撑。

如果只拿到 B，文档相关性可以为正，但要点覆盖仅为 `1/2`。这时不能把“至少一个相关块”当作完整回答。若某个要点需要两份材料联合证明，应把它标成一个 AND 证据组合；若两份材料任一即可证明，则是 OR 关系。把所有块简单计数会混淆两者。

可保存一份小型标注：`claim_1: alternatives=[{A},{B}]`，`claim_2: alternatives=[{A}]`。检查每个要点是否至少有一个完整证据组合已进入最终上下文。此处是本章的教学设计，不是要求采用某个库格式。

沿同一条请求，在四处分别记录 ID：初始候选、融合/重排后、实际送入模型的上下文、最终引用。若 A 在初始候选里，重排后消失，先检查排序；若重排里有 A、上下文没有，先查预算和截断。这样才知道该改哪一层。

## 5. 四类容易悄悄算错的输入

### 重复块

同一个 A 出现两次，不能算命中两份证据。先明确评测单位是文档、块还是证据要点，再使用稳定 ID。本文代码直接拒绝重复 ID，促使调用方检查去重；不悄悄改变被测系统的排序。

### 没有正确答案的问题

如果金标没有任何正例，Recall 与 nDCG 没有适用分母。本文返回 `None`，将这类问题放入“无答案”切片，另测系统是否正确识别缺证据、是否编造断言。不可把 None 当零后与可回答问题混成一个均值。相关性库对此也有不同处理规则，见 [Microsoft rankerEval 的缺定义值说明](https://github.com/microsoft/rankerEval/blob/main/docs/source/metrics.rst)。

### 尚未人工评过的材料

未标注不等于确认不相关。本文为可复现计算，暂把未标注返回项按零贡献处理，同时输出 `unjudged_returned`。若新检索器找到了以前没被标注的好材料，应补充盲审、更新同一套标签，再对所有系统重算，不能只给新系统单独加分。

### 平均方式

假设问题 Q1 一共 1 个正例，命中 1 个；Q2 一共 9 个正例，也只命中 1 个。

- 宏平均 Recall：`(1/1 + 1/9)/2 = 5/9 ≈ 0.5556`，每个问题同权。
- 汇总计数式 Recall：`(1+1)/(1+9) = 0.2`，正例多的问题权重更大。

两个数字都能算，但不能把一个版本的宏平均与另一版本的汇总值比较。报告里写明计算单位、权重、被排除问题数及理由。

## 6. 一个能运行的指标内核

输入是已按顺序排列的唯一证据 ID、完整相关性等级表和 K。代码使用 Python 3.10+ 标准库，无模型调用。完整文件见 [指标与排序内核](../../examples/retrieval_worked_examples/retrieval_worked_examples.py)，测试见 [测试文件](../../examples/retrieval_worked_examples/test_retrieval_worked_examples.py)。

```python
from collections.abc import Mapping, Sequence
import math


def score_query(ranking: Sequence[str], grades: Mapping[str, int], k: int) -> dict:
    """Unique IDs, grades 0..3, positive grades are relevant, fixed-k precision.

    Unjudged returned IDs contribute zero under this explicit evaluation policy.
    Recall/RR/nDCG are None for queries with no judged positive evidence.
    """
    if type(k) is not int or k < 1:
        raise ValueError("k must be a positive integer")
    if len(set(ranking)) != len(ranking):
        raise ValueError("ranking must contain unique evidence IDs")
    if any(type(g) is not int or not 0 <= g <= 3 for g in grades.values()):
        raise ValueError("grades must be integers in 0..3")
    top = ranking[:k]
    relevant_total = sum(g > 0 for g in grades.values())
    gains = [grades.get(doc_id, 0) for doc_id in top]
    hits = sum(g > 0 for g in gains)
    first = next((rank for rank, g in enumerate(gains, 1) if g > 0), None)
    dcg = sum((2 ** g - 1) / math.log2(rank + 1)
              for rank, g in enumerate(gains, 1))
    ideal_grades = sorted(grades.values(), reverse=True)[:k]
    idcg = sum((2 ** g - 1) / math.log2(rank + 1)
               for rank, g in enumerate(ideal_grades, 1))
    return {
        "precision_at_k": hits / k,
        "recall_at_k": hits / relevant_total if relevant_total else None,
        "rr_at_k": (1 / first if first else 0.0) if relevant_total else None,
        "ndcg_at_k": dcg / idcg if idcg else None,
        "hit_at_k": int(hits > 0),
        "unjudged_returned": sum(doc_id not in grades for doc_id in top),
        "returned": len(top),
        "relevant_total": relevant_total,
    }

```

读代码时盯住四个变量：`relevant_total` 是标注里全部正例；`gains` 是实际前 K 名的等级；`first` 是第一份正例的位置；`ideal_grades` 来自全部标注的理想排序。最后一个变量最容易被错误地写成“只排序已经取回的结果”。

设返回列表长度为 n、标注证据数为 m。当前清晰版实现校验重复需 O(n) 时间和 O(n) 空间，读取标注需 O(m)，构建理想顺序需 O(m log m) 时间和 O(m) 空间；实际算前 K 项是 O(min(n,K))。总时间可写为 O(n+m log m)，额外空间 O(n+m)。同一问题多次评不同系统时可以预计算正例数和 IDCG，减少重复工作。

## 7. 从“涨了 10 个点”走到可信的版本比较

设同一批 100 个问题，旧版 A 成功 70 个，新版 B 成功 80 个。再按问题配对，发现：两版都成功 60 个、仅 A 成功 10 个、仅 B 成功 20 个、都失败 10 个。

这张表多告诉了两件事：B 修好了 20 个问题，但又破坏了 10 个问题；总体净提升 10 个百分点掩盖了回归。先检查这 10 个回归是否集中在关键类型，再讨论是否上线，而不是只庆祝均值上升。

一次实用实验按下面顺序做：

1. 固定问题、语料快照、身份权限、模型版本、提示、工具返回和预算；只改变要比较的组件。
2. 用开发集选择参数，最终留出集只用于评估。分块或改写出来的近重复问题按文档/模板分组，避免随机拆分后两边都出现同一事实。预处理和阈值选择也可能泄漏，参见 [scikit-learn 的数据泄漏说明](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)。
3. 保存每条问题 A/B 的结果，而不仅是两个总分；对有随机性的 Agent 重复运行，保留问题与试验之间的层级。
4. 同报总体、关键切片、回归列表、样本量、时延和失败成本。需要不确定性估计时，可按问题配对重采样；同一用户或文档的高度相关问题按组重采样。

配对 bootstrap 的基本动作是每次抽取一批问题下标，让 A、B 同时使用这批下标，再计算差值，而不是独立抽两份数据。SciPy 的 [`bootstrap(..., paired=True)`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)支持这种索引配对。置信区间取决于抽样假设与方法，不能把 100 个高度相似问题当作 100 次独立证据。

## 8. 面试口述与原创模拟追问

**30 秒回答“怎样评价一个 RAG 检索器？”**

“我会先固定语料版本和带证据标注的问题集，明确评测单位。候选层看 Recall@K，排序层看 RR/MRR 与 nDCG，最终上下文看关键要点覆盖，再单独评答案是否被证据支持。比较两版时按相同问题配对，保留回归样本、关键切片及成本时延；无答案和未标注材料分别处理，不用一个总分包办。”

以下是根据本章原创设计的模拟追问：

- **Recall@20 涨了，最终答案反而变差，怎么查？** 先核对更多噪声是否挤掉关键条件，再看重排、上下文预算与位置变化。分别比较相同证据输入下的生成，以及相同生成配置下的上下文，定位改变。
- **MRR 是 1，能不能说检索完美？** 只能说明每个被计入的问题第一名有正例；它没评价其余必要证据、证据强弱或引用正确性。
- **A/B 各随机抽 100 条问题比较公平吗？** 两批难度可能不同。离线优先使用同一批冻结问题配对；线上随机分流还要考虑用户/会话分组及观察窗口。
- **无答案题返回空列表，Recall 应该给 1 吗？** 先按评测合同定义，不把它伪装成有正例的检索成功。本章把它从 Recall 均值分离，用缺证据识别及无支持断言指标评价。

## 9. 练习与核对答案

1. 将返回结果换成 `[X,A,C]`，K=3。先算 Precision、Recall、RR，再算 nDCG。
2. 保持原排序 `[B,X,A]`，把 K 改为 1。哪些指标变化，为什么？
3. 对只有 `{A:3}` 的金标返回 `[A,A]`。你会在入库、召回还是评测层发现重复？为什么代码不应该偷偷算成两个命中？
4. 自己写一个反例：两个系统 MRR 完全一样，但关键要点覆盖明显不同。

核对答案：

1. Precision=2/3，Recall=2/3，RR=1/2；DCG=`7/log2(3)+1/2 ≈ 4.916508`，除以 IDCG≈9.392789，nDCG≈0.523434。
2. Precision=1，Recall=1/3，RR=1，nDCG=3/7。只保留第一项 B，因此首次命中不变，但 A、C 均未覆盖，最高等级证据 A 也未排第一。
3. 入库用稳定身份及适当的唯一约束阻止同一版本/块被重复创建；召回与融合按相同身份合并多路结果；评测遇到重复 ID 明确拒绝，防止一个 A 被算两次。三层都应检查，但职责不同，不能让评测偷偷修正系统输出而掩盖问题。
4. `[B,X,X2]` 与 `[B,A,C]` 的首项都是相关 B，RR=1；若每个系统仅有这一道题，MRR也都是1。按第4节要点定义，前者只覆盖要点1，覆盖率1/2；后者有A，覆盖两个要点，覆盖率2/2。首次命中相同不代表完整性相同。

## 10. 用两个项目回答“你会在哪里采集评测证据？”

**固定源码。** Saber 使用 [6d5bb13dc74dc03a7a59c74b2396c3b10e84caef](https://github.com/minimoster/agi-saber/tree/6d5bb13dc74dc03a7a59c74b2396c3b10e84caef)，Openresearch 使用 [5f876faabba238563001151fc7a573581ddaf869](https://github.com/minimoster/agi-openresearch/tree/5f876faabba238563001151fc7a573581ddaf869)。

- Saber 的 [internal/domain/rag/hybrid.go](https://github.com/minimoster/agi-saber/blob/6d5bb13dc74dc03a7a59c74b2396c3b10e84caef/internal/domain/rag/hybrid.go) 可定位 `searchHybrid` 的单查询候选与RRF、`SearchMulti` 的跨查询融合和 `finalize`；[reranker.go](https://github.com/minimoster/agi-saber/blob/6d5bb13dc74dc03a7a59c74b2396c3b10e84caef/internal/domain/rag/reranker.go) 可定位 LLM listwise 重排及解析失败回退；[rag.go](https://github.com/minimoster/agi-saber/blob/6d5bb13dc74dc03a7a59c74b2396c3b10e84caef/internal/domain/rag/rag.go) 的 `QueryWithHistory` 优先把父块放入生成上下文。可以分别在这些边界采集候选、重排与实际上下文，**这是建议加入的评测记录点，不是声称固定源码已经记录本章全部指标**。
- Openresearch 的 [scholar-agent/backend/internal/agent/benchmark_harness.go](https://github.com/minimoster/agi-openresearch/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/agent/benchmark_harness.go) 有数据/适配器hash核对、逐样本预测和指标重算；[claim_evidence.go](https://github.com/minimoster/agi-openresearch/blob/5f876faabba238563001151fc7a573581ddaf869/scholar-agent/backend/internal/agent/claim_evidence.go) 有rubric规范化、哈希和证据关联。它们可用于解释“结果须能回到样本与证据”的原则，但当前分类/回归 benchmark 不是本章RAG Recall/nDCG实现，也不能据此宣称有独立防泄漏数据集。

**口述版。**“我会沿 Saber 的候选融合、LLM重排、父块上下文三个边界保存同一问题的证据身份，避免只看最终回答。评测可借鉴 Openresearch 的冻结规则和逐样本重算思路，但需要另建带证据金标的问题集。本章 Python 指标是可手算的教学内核，没有冒充项目线上指标；没有实际运行报告时，我只讲源码机制和验证计划。”

核查日期：2026-10-15。数字、问题、代码及练习均为本章原创教学例子；技术定义的一手来源随对应段落给出。
