# 35. 搜索插入位置

[官方题目](https://leetcode.cn/problems/search-insert-position/) · EASY · 官方分类：二分查找

## 题意与接口

在严格递增数组中查目标的位置；目标不存在时，返回保持升序的插入下标。`searchInsert(nums,target)`返回整数，不修改数组。

## 从朴素方法到优化

从左往右找第一个不小于目标的位置需O(n)。判断“nums[i]≥target”在有序数组上先假后真，可用二分找分界。

## 核心思路

采用半开区间[left,right)，始终让答案在闭范围[left,right]内。mid值小于目标时丢弃mid及其左边，否则保留mid并令right=mid。

## 手推一个小例子

[2,5,9,12]找7：left=0,right=4，mid=2的9偏大，right=2；mid=1的5偏小，left=2。收敛到2，插在9前。

## 为什么正确

所有下标小于left的值都小于目标；所有下标不小于right的值都不小于目标。每次更新维持这个划分并严格缩短区间，最后left=right就是第一个不小于目标的位置，可能为n。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0035_search_insert_position.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def searchInsert(self, nums: list[int], target: int) -> int:
        # 半开区间[left,right)，答案允许是尾后位置n。
        left, right = 0, len(nums)
        while left < right:
            middle = (left + right) // 2
            if nums[middle] < target:
                left = middle + 1
            else:
                right = middle  # middle仍可能是第一个满足条件的位置
        return left
```

## 复杂度

时间O(log n)，辅助空间O(1)。

## 边界与易错点

- right初值是n，与while left<right配套，不能随意换成闭区间更新。
- 目标大于全部元素时应返回n。
- 虽然题设无重复，算法也能返回有重复时的最左插入点。

## 本地测试与复习

测试首尾插入、正好命中与单元素；随机与标准库bisect_left对拍。

复习：把“≥target”换成“>target”时，应该改哪一行判断？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/search-insert-position/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0035.Search%20Insert%20Position/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/other/0035-search-insert-position.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/other/0035-search-insert-position.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：定义半开区间内仍可能存在答案的位置，检查空区间结束时返回值为何就是插入点。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
