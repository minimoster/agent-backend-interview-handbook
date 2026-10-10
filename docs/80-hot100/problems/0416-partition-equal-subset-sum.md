# 416. 分割等和子集

[官方题目](https://leetcode.cn/problems/partition-equal-subset-sum/) · MEDIUM · 官方分类：动态规划

## 题意与接口

接口：`Solution.canPartition(nums: list[int]) -> bool`。将所有正整数分成两个和相等的子集，每个元素恰好归属一边，判断是否可行。官方长度 1 至 200，元素 1 至 100。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/partition-equal-subset-sum/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

枚举所有子集要 O(2ⁿ)。设总和为 total；若 total 为奇数必定失败，否则只需判断有没有子集和等于 total/2。把目标值作为背包容量，用布尔表记录可达和。

## 核心思路

`possible[value]` 表示已处理元素能否组成 value。初始只有和 0 可达。读到 x 时，对 value 从 target 倒序到 x 更新：新状态等于原状态，或原本能组成 value−x 再选 x。倒序保证一次循环不会重复使用当前元素。

## 手推一个小例子

取 `[2, 3, 7, 8]`，目标为 10：
1. 初始可达和 `{0}`。
2. 加 2 后为 `{0,2}`；加 3 后为 `{0,2,3,5}`。
3. 加 7 时，旧和 3 加 7 得到 10，因此可分成 `{3,7}` 与 `{2,8}`。
集合只展示不超过目标的和；实现使用固定长度布尔数组。

## 为什么正确

对已处理的元素数量归纳。一个和为 value 的子集要么不包含当前 x，保留旧状态；要么包含 x，删除它后恰好对应旧元素中和为 value−x 的子集。倒序更新使所读较小下标仍属于旧一轮，保证“旧元素”的前提成立。最终目标可达时，未选元素和也为目标，反之任何等分都提供这样的子集。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0416_partition_equal_subset_sum.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def canPartition(self, nums: list[int]) -> bool:
        total = sum(nums)
        if total % 2:
            return False
        target = total // 2
        possible = [False] * (target + 1)
        possible[0] = True
        for value in nums:
            # 倒序保证 possible[capacity-value] 尚未使用当前元素。
            for capacity in range(target, value - 1, -1):
                possible[capacity] = (
                    possible[capacity] or possible[capacity - value]
                )
            if possible[target]:
                return True
        return possible[target]
```

## 复杂度

设 T=总和/2，时间 O(nT)，辅助空间 O(T)；这是依赖数值总和的伪多项式算法。奇数总和在求和后 O(n) 时间返回。

## 边界与易错点

- 正序更新会把 0/1 背包误写成无限复用的完全背包。
- 例如 `[1,2,5]` 目标为 4，正序可能用同一个 1 四次，误报真。
- 总和为偶数只是必要条件，不是充分条件。
- 相同数值但不同下标是不同元素，各可选一次。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0416`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：为什么发现目标可达后可以立即返回？若允许负数，固定 0..target 的数组会漏掉什么？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/partition-equal-subset-sum/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0400-0499/0416.Partition%20Equal%20Subset%20Sum/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/dynamic-programming/0416-partition-equal-subset-sum.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/dynamic-programming/0416-partition-equal-subset-sum.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[416. 分割等和子集](https://www.bilibili.com/video/BV1rt4y1N7jE/)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：总和奇数时先排除；用一个数检查容量倒序更新为何防止同一个数被重复使用。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
