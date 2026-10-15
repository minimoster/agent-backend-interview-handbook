# 152. 乘积最大子数组

难度：MEDIUM · 分类：动态规划

## 题意与接口

接口：`Solution.maxProduct(nums: list[int]) -> int`。求非空连续子数组的最大乘积。官方数组非空、长度至多 2×10⁴，值可正可负可为 0；所有子数组乘积保证在 32 位整数范围。

约束与规则于 2026-10-09 查阅官方英文题面核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

枚举所有起点并向右累乘需要 O(n²)。像最大子数组和那样只保存最大结尾状态却不够：乘以负数后，之前的最小乘积可能变成最大，因此需要两个极值。

## 核心思路

`largest`、`smallest` 表示恰好以当前位置结尾的最大和最小乘积。新数 x 的候选只有三种：单独 x、旧最大乘 x、旧最小乘 x。两种新状态同时从旧状态计算；全局 best 记录所有终点中最大的 largest。

## 手推一个小例子

取 `[-2, 3, -4, 0, -1]`：
1. 初始最大/最小都为 −2，全局 −2。
2. 读 3：候选 3、−6、−6，最大 3、最小 −6。
3. 读 −4：候选 −4、−12、24，最大 24、最小 −12，全局 24。
4. 读 0：两种结尾状态都为 0。
5. 读 −1：最大 0、最小 −1，全局仍为 24。

## 为什么正确

以当前数结尾的非空子数组，要么只含当前数，要么由以前一位置结尾的子数组扩展而来。乘以固定 x 时，若 x≥0，极值来自旧同向极值；若 x<0，极值来自旧反向极值，所以只检查旧最大和旧最小就足够。三种候选完整覆盖新的极值，再对全部终点取最大即可得到全局最优。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0152_maximum_product_subarray.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def maxProduct(self, nums: list[int]) -> int:
        largest = smallest = best = nums[0]
        for i in range(1, len(nums)):
            value = nums[i]
            # 两个新极值必须读取同一轮的旧状态。
            from_largest = largest * value
            from_smallest = smallest * value
            largest = max(value, from_largest, from_smallest)
            smallest = min(value, from_largest, from_smallest)
            best = max(best, largest)
        return best
```

## 复杂度

时间 O(n)，辅助空间 O(1)。官方对子数组乘积有固定整数范围保证；若推广到无限制大整数，应另计乘法成本。

## 边界与易错点

- 全局答案不能初始化为 0，因为 `[-3]` 的答案是 −3。
- 不能用更新后的 largest 计算 smallest，必须保留旧候选。
- 0 自然重置结尾积，但此前最优答案仍需保留。
- 子数组必须连续，不能跳过中间的 0。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0152`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：为什么加法题只需一个结尾极值，而乘法题需要两个？试手推三个负数连续出现的情况。

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：用负数使最大积与最小积交换角色的例子手推，并检查零如何重新开始状态。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
