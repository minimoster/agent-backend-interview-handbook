# Agent 检索算法实练：稳定 Top-K、堆与 RRF

[返回练习目录](README.md) · [RRF 基础](../10-agent/02-rag-retrieval-and-reranking.md#a13) · [检索评测手算](../10-agent/35-retrieval-evaluation-worked-example.md) · [Hot100 解题方法](../80-hot100/PATTERNS.md)

算法学习最有用的连接点，是把一道抽象题放回真实数据流。本章处理一条常见链路：两路检索返回候选榜单，按文档身份汇总 RRF 分数，再从大量候选里选出最高的 K 个。先理解每个变量保存什么，再解释为何能丢掉其余候选。

完整原创代码与测试：[内核](../../examples/retrieval_worked_examples/retrieval_worked_examples.py) · [测试](../../examples/retrieval_worked_examples/test_retrieval_worked_examples.py)。本章使用 Python 3.10+ 标准库。

## 1. 先把 Top-K 题设说完整

输入是一串 `(证据 ID, 分数)`，可能只能从头到尾读取一次。证据 ID 已经唯一，分数越大越好；输出最高的 K 项，按分数降序，相同分数按输入先后排序。K=0 返回空；K 大于输入数量就返回全部。分数必须有限，NaN 和正负无穷不进入排序。

例如输入 `[(A,0.2),(B,0.9),(C,0.5),(D,0.9)]`、K=2，结果应为 `[(B,0.9),(D,0.9)]`，不能随机改变 B、D 的顺序。

这几个条件决定实现：

- 要完整有序结果，最后还需要把保留的 K 项排序。
- 要稳定并列，不能只保存分数。
- 输入是流，不能假定能反复扫描。
- 已按 ID 唯一，Top-K 函数不额外建立所有历史 ID 的集合，否则“仅 O(K) 空间”就不成立。

## 2. 朴素法为什么可用，又在哪儿浪费

最直接的办法是 `sorted(items, key=lambda item: item[1], reverse=True)[:K]`。Python 排序是稳定的，容易验证；n 项数据通常需要 O(n log n) 时间，且要把流收集起来。

当 n 很小，或者 K 接近 n，直接排序往往是很好的工程选择。只有 K 远小于 n、希望限制保留内存时，维护固定大小的堆才更有吸引力。面试不要只背“Top-K 一定用堆”，应先说明数据量与输出要求。

## 3. 要最大的 K 个，为什么维护最小堆

想象手上已有 K 个暂时最好的候选。新候选到来时，要比较的是“它比当前最差的入选者更好吗”，所以应当能立刻看到入选集合里最小的那个。

最小堆让堆顶是最小元素；它不保证整个数组已经排序。Python 的堆可用列表表示：下标 i 的孩子在 `2*i+1`、`2*i+2`，父节点不大于孩子。本节按Python 3.12的heapq操作语义推导。

K=2 时手推四个分数：

1. 读 A=0.2：集合不足 2 项，加入。
2. 读 B=0.9：继续加入，此时最差的是 A=0.2。
3. 读 C=0.5：比最差的 A 好，替换 A。保留 B、C。
4. 读 D=0.9：比最差的 C 好，替换 C。保留 B、D。

堆顶只负责快速找到淘汰对象，最后才按要求降序输出。

## 4. 正确性：一句不变量比十个样例更有力

不变量：处理完前 i 个输入后，堆里恰好保存这些输入中按既定总顺序最好的 `min(i,K)` 项。

- 初始没有元素，不变量成立。
- 堆未满时加入新元素，所有已见项都保留，仍成立。
- 堆满时，若新项不优于堆顶，它不会超过任何入选项，丢弃安全。
- 若新项优于堆顶，原堆顶是 K 个入选者里最差的，替换后得到新的最佳 K 项。
- 所有输入处理完，不变量给出所需集合；最后排序只改变顺序，不改变入选元素。

这里的“总顺序”包含并列规则。只证明分数、不证明并列处理，仍可能得到与接口要求不同的结果。

## 5. 稳定并列：为什么存 `(score, -order, id)`

`order` 是从 0 开始的输入序号。分数相同时，越早出现越好，所以把 `-order` 放在第二项。序号越小，负数越大，排序时就更优。

例如 B 在序号 1、D 在序号 3，比较键分别是 `(0.9,-1,...)` 与 `(0.9,-3,...)`，B 更大；如果必须从同分者里淘汰一个，D 会先被淘汰。由于每个序号唯一，比较不会走到第三项 ID，避免把 ID 的字典序误当作业务优先级。

下面是完整实现。`heapreplace` 会无条件替换堆顶，所以调用前必须判断新项是否更优；不要拿一个更差的新项换掉好候选。

```python
from collections.abc import Iterable
import heapq
import math


def top_k(items: Iterable[tuple[str, float]], k: int) -> list[tuple[str, float]]:
    """Score descending, ties earlier arrival first. IDs must already be unique.

    Keeps at most k records. Finite float-compatible scores only.
    k=0 returns immediately without consuming the input iterator.
    """
    if type(k) is not int or k < 0:
        raise ValueError("k must be a nonnegative integer")
    if k == 0:
        return []
    heap: list[tuple[float, int, str]] = []
    for order, (doc_id, raw_score) in enumerate(items):
        score = float(raw_score)
        if not math.isfinite(score):
            raise ValueError("scores must be finite")
        item = (score, -order, doc_id)
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)
    heap.sort(reverse=True)
    return [(doc_id, score) for score, _neg_order, doc_id in heap]

```

若输入共有 n 项，实际保留 `s=min(n,K)` 项，K>0：扫描与维护为 O(n log(s+1)) 上界，最后排序 O(s log s)，额外空间 O(s)。对通常的 `1≤K≤n` 可写 O(n log(K+1)+K log K) 时间、O(K) 空间。用 `log(K+1)` 能自然覆盖 K=1 的线性扫描；K=0 在本接口里直接返回，不消耗输入迭代器。

**四个常见错误：** 用最大堆却不断删除最大项；把 heap 数组直接当已排序结果；同分时不定义顺序；偷偷保存全部历史候选却仍宣称 O(K) 内存。

## 6. RRF：先按身份累加，再选 Top-K

RRF 的输入不是任意分数，而是多个有序榜单。对文档 d，每路榜单贡献 `1/(c+rank(d))`，没有出现在该路里则贡献 0；名次从 1 开始。c 是平滑常数，和要输出多少项的 K 不是同一个量。

RRF的c可取60等正值，但没有对所有语料都最优的固定常数；应在冻结的开发集上选取。本节为了方便手算使用 c=10。

两路输入为：

- 关键词榜单：`[A,B,C]`
- 向量榜单：`[B,D,A]`

逐个累加：

|候选|关键词贡献|向量贡献|总分|
|---|---|---|---|
|A|1/11|1/13|0.167832|
|B|1/12|1/11|0.174242|
|C|1/13|0|0.076923|
|D|0|1/12|0.083333|

所以融合顺序为 B、A、D、C，Top-2 是 B、A。B 没在关键词榜单里排第一，却因为两路都靠前，综合超过 A。

字典 `scores[id]` 存的是该身份目前累计得到的分数，不能存“最后一次出现的分数”；这是一次聚合，不是覆盖。两个榜单中同一个 A 应累加，两份不同版本的 A 则应先按应用版本规则确定身份，不能仅凭相同标题合并。

## 7. 同一路重复与候选窗口怎么处理

跨路重复代表多路都支持这个候选；同一路 `[A,A,B]` 则是重复返回，不能让 A 吃两次贡献。本实现只取该路第一次出现的物理名次，因此 A 用第 1 名、B 保持第 3 名，不把 B 悄悄前移成第 2 名。正常输入应尽量在检索器侧提供唯一 ID。

也可以选择先去重再连续编号，但那是另一份合同，分数会不同。重要的是代码、手算和测试用同一个定义。

候选窗口也会改变结果。假如第二路只取前两名 `[B,D]`，A 就失去第二路的 1/13 贡献；融合不能使用它没看到的名次。工程上分别配置每路召回窗口、融合保留条数、重排输入条数及最终上下文条数，别全都叫 top_k。排名常数、候选窗口与最终返回数量是不同的配置。

在进入这些榜单前完成适用的权限与版本过滤。RRF 分数不表示访问许可，也不等于答案可信概率。

```python
def rrf_scores(rankings: Iterable[Iterable[str]], c: float = 60.0) -> dict[str, float]:
    """Fuse finite ranked lists. A duplicate within one list counts only once.

    The first physical rank is kept; later entries are not renumbered.
    The dictionary insertion order supplies deterministic tie handling to top_k.
    """
    c = float(c)
    if not math.isfinite(c) or c <= 0:
        raise ValueError("c must be finite and positive")
    scores: dict[str, float] = {}
    for ranking in rankings:
        seen: set[str] = set()
        for rank, doc_id in enumerate(ranking, 1):
            if not isinstance(doc_id, str) or not doc_id:
                raise ValueError("evidence IDs must be nonempty strings")
            if doc_id in seen:
                continue
            seen.add(doc_id)
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (c + rank)
    return scores


def rrf(rankings: Iterable[Iterable[str]], k: int, c: float = 60.0) -> list[tuple[str, float]]:
    return top_k(rrf_scores(rankings, c).items(), k)

```

设所有榜单合计出现 N 项，合并后 U 个不同 ID，每路最长 L 项。字典累加在通常哈希模型下期望 O(N) 时间；全局分数占 O(U) 空间，该路去重集合最多 O(L)，且 L 的不同 ID 数不超过 U。随后选 K 项需要 O(U log(min(U,K)+1)) 的上界时间，再排序保留项。总体额外空间 O(U)，不是 O(K)：RRF 必须先保存每个候选的累计分数。

## 8. 为什么不能边融合边永久丢弃低分候选

Top-K 算法处理的是“每项的最终分数”。RRF 还在读取后续榜单时，候选分数可能继续增加。一个当前落后的 A，下一路可能排第一并反超。

因此本实现分两阶段：先完成全部榜单的累计，再把最终分数交给 Top-K。若想提前剪枝，需要能证明未读榜单对某候选的最大贡献上界，而且正确维护候选的动态键；不能把“当前不在前 K”当作永远无缘前 K 的证据。

这是一类可迁移的面试思路：安全丢弃元素，需要一个与后续数据兼容的不变量。找不到这个证明，就先使用正确的全量方案。

## 9. RRF、语义重排与多样性选择各解决什么

- RRF 只读取名次，融合多个检索器的候选，不重新阅读文本。
- 语义重排读取查询和候选内容，判断相关性，可能消耗模型推理资源。
- 多样性或去重选择限制高度重复的证据占满上下文，它优化的目标又不同。

例如十个块都重复同一退款条件，而遗漏例外条款；它们可能都相关，Top-K 的分数排序也完全正确，但答案仍缺条件。可在评测里加入要点覆盖，发现需要多样性选择或父子块扩展，而不是指责堆算法“算错了”。

## 10. 原创模拟面试题与追问

**题 1：一百万个打分候选，只保留最好的 20 个，怎样做？**

“如果每个候选分数已最终确定且输入 ID 唯一，我会用容量 20 的最小堆，堆顶保存入选者里最差的。新项更好才替换，最后把 20 项排序。说明并列规则后，用已处理前缀的最佳 K 项不变量证明。时间约 O(n log K)，额外保留 O(K) 项；若还要全局去重，去重存储要另算。”

**题 2：为什么选最大的 K 项却用最小堆？** 比较对象是入选边界，快速淘汰当前入选者中最差的。若问题变成反复取全部候选中的最大项，可以选择最大堆或把比较方向反过来。

**题 3：相同文档在两路都出现，要去掉一路吗？** 不能。合并输出身份，但累加两路排名贡献。同一路重复才按约定处理，否则改变了融合意义。

**题 4：RRF 不可直接流式 Top-K，那 Top-K 算法还有用吗？** 有用，应用在聚合完成的 U 个最终分数上，避免把 U 项全部排序。问题在于分数是否仍会更新，不是 heapq 不能处理流。

**题 5：不用自己写堆，直接 nlargest 行不行？** 工程上可按 Python 文档使用库函数，并核对稳定性和输入合同。学习时应能解释不变量与复杂度，面试时先确认是否允许直接使用高层 API。不能把库名当作推理过程。

## 11. 练习：修改一个条件，再判断算法是否仍成立

1. K=1，输入全为负数。能否用初始分数 0 代表当前最优？说明反例。
2. 把同分规则改为 ID 字典序更小优先。你会如何修改比较键，并验证边界？
3. 将 RRF 两路次序交换。没有并列时结果如何？精确并列时，本章的“第一次遇到先”规则会如何？
4. 对两路 `[A,B,C]` 与 `[B,D,A]`，把每路窗口缩成 1，再手算 Top-2。为什么结果不能用于证明窗口 3 的检索质量？
5. 分数会不断上调，需要随时查询 Top-K。静态函数应怎样扩展？先讨论可更新堆、惰性删除或周期重建，再说明旧项失效与内存清理，不要直接改 heap 数组中的某一格。

核对答案：

1. 不能。输入 `[(A,-5),(B,-2)]` 的最大值为 -2，初始 0 并不是输入元素。使用空堆或首个合法候选，不引入虚构的零分候选。
2. 定义“分数大、ID 字典序小”更优。完整排序的键可直接用 `(-score, id)`；有界最小堆必须反转 ID 的比较方向，让同分时字典序最大的 ID 位于淘汰边界，可用自定义比较对象，不能简单用 `(score,id)`。对 `[(B,1),(A,1),(C,1)]`、K=2 应保留 A、B；交换输入顺序仍应相同，并与完整排序对拍。字符串没有通用的数值取负操作。
3. 非并列的数学分数不变，但浮点加法顺序和精确并列排序要固定合同。本实现精确同分按第一次遇到顺序，交换榜单可能改变并列项顺序；若需要与榜单次序无关，应规定稳定 ID 等独立键，并测试浮点近似相等规则。
4. 只剩 A、B 各得 1/11，按先见 A 再 B 输出，与窗口 3 的 B、A 不同。窗口 1 没有观察到后续排名，不能用其结果替窗口 3 的质量作证。
5. 按 ID 维护当前分数/版本，每次更新向堆加入新版本，读取时丢弃过期版本；设置重建阈值，避免惰性删除让堆无限增长。也可实现带 ID 到位置索引的可更新堆。若还必须保证未入选候选能在旧入选者下降或删除后补位，需要保存全部有效候选或另一个候选结构，不能继续无条件声称只用 O(K) 空间。用逐次全量排序作更新序列的参考答案。

## 12. 怎样验证实现而不是只跑一个示例

先用可人工计算的小输入核对分数，再用独立方法对拍：Top-K 对比完整稳定排序；RRF 小例用 `Fraction` 有理数求和，避免把同一份浮点实现复制成“参考答案”。边界包含空输入、K=0、K>n、负数、并列、非法分数、单路重复及候选窗口变化。

仓库根目录可运行：

```sh
python -B -m unittest discover -s examples/retrieval_worked_examples -p 'test_*.py' -v
```

教学内核于 2026-10-15 在 Python 3.12.14 通过 11 个测试入口，整合时在 Python 3.14.6 复跑通过，包含 250 组 Top-K 与独立稳定排序对拍，以及 RRF 有理数对照。它验证的是本章数据合同与算法，不涉及真实检索服务效果。

## 13. 对应 Saber 源码时，哪些能说、哪些不能说？

固定项目为 agi-saber 6d5bb13dc74dc03a7a59c74b2396c3b10e84caef。internal/domain/rag/hybrid.go 的 `searchHybrid` 按 PG ID 累加多路排名贡献，`SearchMulti` 再跨查询融合；后者实际以子块文本字符串为键，不是内容哈希。该实现用 `sort.Slice` 对候选排序，**没有使用本章 Python 有界堆，也没有本章输入次序稳定并列保证**。Go map 遍历顺序不能作为稳定业务顺序。

**口述版：**“我的项目案例可以从 Saber 的混合检索讲起：单查询按 PG ID 累加 RRF，跨查询还要再次合并，之后做 LLM 重排。固定源码当前是全量排序；本章有界堆是我用来理解最终分数 Top-K 的独立教学实现，不把它说成已经替换上线。若优化，我会先固定候选身份和同分规则，再与原排序逐项对拍，最后测内存、时延和质量。”

原理上的对应点是“先完成聚合，再选最终 Top-K”；差异是语言、身份策略、排序方式与稳定合同。源码能支持机制描述，不能证明个人负责范围、百万级规模或性能收益。
