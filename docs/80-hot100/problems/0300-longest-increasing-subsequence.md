# 300. 最长递增子序列

难度：MEDIUM · 分类：动态规划

## 题意与接口

接口：`Solution.lengthOfLIS(nums: list[int]) -> int`。求严格递增子序列的最长长度；子序列允许跳过位置但不得改顺序。官方输入非空，长度至多 2500。

约束与规则于 2026-10-09 查阅官方英文题面核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

先理解 O(n²) DP：dp[i] 为以 i 结尾的最长长度，枚举所有 j<i 且 nums[j]<nums[i]，取 dp[j]+1 最大值。进一步问：长度相同的序列，尾值越小，未来越容易接上新数，因此每种长度只需保留最小尾值。

## 核心思路

`tails[k]` 表示已读前缀中长度为 k+1 的递增子序列的最小结尾值。tails 严格递增。对新数 x 二分寻找首个 ≥x 的位置：找到则替换，让同长度尾值更小；找不到则追加，最长长度增加 1。Python 的 `bisect_left` 正好实现这个边界。

## 手推一个小例子

取 `[6, 2, 5, 3, 7, 4]`：
1. 读 6：tails=[6]。
2. 读 2：替换得到 [2]。
3. 读 5：追加得到 [2,5]。
4. 读 3：替换得到 [2,3]。
5. 读 7：追加得到 [2,3,7]。
6. 读 4：替换得到 [2,3,4]，长度为 3。

## 为什么正确

设 x 应放的位置为 k。k>0 时 tails[k−1]<x，存在对应长度 k 的序列可以接上 x，故长度 k+1 的新尾值 x 可实现。比 k 更长的序列不能靠 x 新增，因为它们所需的前一尾值都至少为 x。替换只改进同长度结尾，不破坏已有可实现长度；追加则恰好创造一个更长长度。此不变量从空表保持至结束，长度就是答案。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0300_longest_increasing_subsequence.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from bisect import bisect_left


class Solution:
    def lengthOfLIS(self, nums: list[int]) -> int:
        tails = []
        for value in nums:
            # 首个 >=value 的位置，避免把相等数算作严格递增。
            position = bisect_left(tails, value)
            if position == len(tails):
                tails.append(value)
            else:
                tails[position] = value
        return len(tails)
```

## 复杂度

时间 O(n log n)，辅助空间 O(n)；更精确地以最终长度 k 表述为 O(n log(k+1)) 时间、O(k) 空间。

## 边界与易错点

- 严格递增应找首个 ≥x，重复值不能增加长度。
- tails 不一定是输入的一条真实子序列，例如 `[2,3,1]` 最终 tails 为 `[1,3]`，它们的原始顺序不对。
- 本实现仅求长度；恢复序列需要前驱及对应下标。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0300`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：为什么保存最大尾值不行？求最长非递减子序列时应该改成哪一种二分边界？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：比较二维枚举前驱的 DP 与 tails 二分；说明 tails 本身未必是最终子序列。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
