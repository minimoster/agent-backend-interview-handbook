# 763. 划分字母区间

[官方题目](https://leetcode.cn/problems/partition-labels/) · MEDIUM · 官方分类：贪心算法

## 题意与接口

接口：`Solution.partitionLabels(s: str) -> list[int]`。把字符串切为尽可能多的连续段，每种字母只能出现在一段中，返回各段长度。输入由小写英文字母构成，长度 1 至 500。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/partition-labels/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

枚举所有切法有指数种可能。一个字符一旦进入某段，它的最后一次出现也必须被包含；预先记录最后位置，扫描中不断合并这些“必须覆盖”的范围。

## 核心思路

用字典 `last` 保存各字符最后下标。当前段从 `start` 开始，右端 `end` 是扫描过的字符最后位置的最大值。当扫描位置刚好达到 `end`，本段所有字母都已完整包含，立刻切开，给后面留下最大分段自由。

## 手推一个小例子

取 `s="abacddce"`：最后位置 a=2、b=1、c=6、d=5、e=7。
1. 从 0 扫到 2，右端一直为 2，切出 `aba`，长度 3。
2. 从 3 读到 c，右端变 6；中间 d 的最后位置 5 不超过它，切出 `cddc`，长度 4。
3. 最后的 e 自成一段，结果 `[3, 4, 1]`。

## 为什么正确

在到达 end 之前切开，至少有一个已出现字符仍在右侧，必然违反条件；到达 end 时，所有已读字符都没有剩余出现，所以这里切开合法。选择最早合法边界不会减少后缀可切的段数：任何更晚的第一段都可在此拆开而仍合法。对剩余后缀重复此论证，得到最多段数。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0763_partition_labels.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def partitionLabels(self, s: str) -> list[int]:
        last = {char: i for i, char in enumerate(s)}
        lengths = []
        start = end = 0
        for i, char in enumerate(s):
            # 本段必须覆盖已读字符的所有后续出现。
            end = max(end, last[char])
            if i == end:
                lengths.append(end - start + 1)
                start = i + 1
        return lengths
```

## 复杂度

时间 O(n)，辅助字典 O(σ)，结果 O(k)，σ 是不同字符数、k 是段数。官方只有 26 个小写字母，所以 σ、k 都至多 26。

## 边界与易错点

- 区间是闭区间，长度需要加 1。
- 必须取最后位置，首次出现的位置无法保证字符不跨段。
- 切分目标是最多段，整个字符串虽然合法，但通常不是答案。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0763`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：为什么安全时立即切割不影响后续？若字符集不限，空间如何描述？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/partition-labels/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0700-0799/0763.Partition%20Labels/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/greedy/0763-partition-labels.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/greedy/0763-partition-labels.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[763. 划分字母区间](https://www.bilibili.com/video/BV18G4y1K7d5)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：扫描时把段末更新为已见字符的最远末次位置，解释何时才能安全切开一个分段。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
