# 560. 和为 K 的子数组

难度：MEDIUM · 分类：子串

## 题意与接口

统计连续子数组的元素和恰等于k的个数。`subarraySum(nums,k)` 返回数量；数组可含正数、负数和零。

## 从朴素方法到优化

每个起点向右累加是 O(n²)。设前缀和为P，区间[l,r]的和等于P[r+1]-P[l]；只需统计过去出现多少个P[l]=当前前缀和-k。

## 核心思路

字典记录前缀和出现次数，初始{0:1}表示数组开始前的空前缀。读数后先累加答案freq[prefix-k]，再把当前前缀加入频次。

## 手推一个小例子

nums=[2,-1,2]，k=3：前缀从0变2，需-1，贡献0；变1，需-2，贡献0；变3，需0，命中初始空前缀，贡献1。答案是整个数组。

## 为什么正确

每个合法子数组唯一对应一对前缀边界。处理右边界时，字典含所有更早左边界的次数，因此贡献正好是以该处结束的合法区间数；先查后存排除了长度为零的区间。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0560_subarray_sum_equals_k.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from collections import defaultdict

class Solution:
    def subarraySum(self, nums: list[int], k: int) -> int:
        frequency = defaultdict(int)
        frequency[0] = 1
        prefix = answer = 0
        for value in nums:
            prefix += value
            # 先计数再登记当前前缀，排除零长度区间。
            answer += frequency[prefix - k]
            frequency[prefix] += 1
        return answer
```

## 复杂度

平均时间 O(n)，辅助空间 O(n)。答案最大可达n(n+1)/2，Python整数不会固定32位溢出。

## 边界与易错点

- 有负数时，普通“和大就缩窗口”没有单调性。
- 初始化0前缀一次，才能统计从下标0开始的区间。
- [0,0]且k=0有3个区间，不是只有一种和。

## 本地测试与复习

测试全部零、负数、从首项开始命中；随机对拍双层累加。

复习：为什么存频次而不是只存是否存在？此处与两数之和的先查后存有什么共同点？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：用含负数和零的数组说明普通滑动窗口为何不可靠；解释前缀和频次表中初始零的意义。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
