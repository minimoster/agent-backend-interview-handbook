# 33. 搜索旋转排序数组

[官方题目](https://leetcode.cn/problems/search-in-rotated-sorted-array/) · MEDIUM · 官方分类：二分查找

## 题意与接口

严格递增数组经过一次循环旋转，查目标并返回其下标，不存在返回-1。`search(nums,target)`不修改输入；题设元素互异。

## 从朴素方法到优化

顺序扫描O(n)。旋转后的任一区间若被中点分开，至少一半仍有序；只要识别有序半边，就能判断目标该留在哪边。

## 核心思路

闭区间二分。若nums[left]≤nums[mid]，左半有序，目标位于[nums[left],nums[mid])则保留左半，否则保留右半；另一种情况对称。

## 手推一个小例子

[8,11,14,2,5]找11：mid=2值14，左半[8,11,14]有序且11在范围内，right=1；mid=0值8，目标不等，left=1；命中11。

## 为什么正确

无重复保证当左半没有跨越旋转断点时能由端点比较识别，若左半跨断点则右半有序。目标若不在有序半边的值域内就不可能位于那半；每次只排除不含目标的候选并保留全部可能位置。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0033_search_in_rotated_sorted_array.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def search(self, nums: list[int], target: int) -> int:
        left, right = 0, len(nums) - 1
        while left <= right:
            middle = (left + right) // 2
            if nums[middle] == target:
                return middle
            # 无重复值保证至少一侧能由端点判断为有序。
            if nums[left] <= nums[middle]:
                if nums[left] <= target < nums[middle]:
                    right = middle - 1
                else:
                    left = middle + 1
            else:
                if nums[middle] < target <= nums[right]:
                    left = middle + 1
                else:
                    right = middle - 1
        return -1
```

## 复杂度

时间O(log n)，辅助空间O(1)。

## 边界与易错点

- 元素互异是此判定的前提；允许大量重复时可能无法靠端点识别有序侧。
- left==mid时左半仍有序，比较用≤。
- 目标等于mid先返回，之后两侧范围可以排除mid。

## 本地测试与复习

测试未旋转、单元素、旋转点旁命中和缺失；随机枚举旋转后与list.index对拍。

复习：为重复元素版本构造一个左右端都等于mid的反例；为何会退化到线性？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/search-in-rotated-sorted-array/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0033.Search%20in%20Rotated%20Sorted%20Array/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0033.search-in-rotated-sorted-array.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0033.search-in-rotated-sorted-array.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：每次先识别有序半边，再判断目标范围；检查中点和端点的等号归属。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
