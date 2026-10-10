# 153. 寻找旋转排序数组中的最小值

[官方题目](https://leetcode.cn/problems/find-minimum-in-rotated-sorted-array/) · MEDIUM · 官方分类：二分查找

## 题意与接口

在由严格递增数组旋转得到的非空数组中找最小值。`findMin(nums)`返回元素值，输入不修改；元素互异。

## 从朴素方法到优化

扫描为O(n)。比较mid与最右端：mid更大说明最小值一定在mid右边；否则最小值可能是mid或位于左侧。

## 核心思路

闭区间维护最小值所在位置。nums[mid]>nums[right]时left=mid+1；否则right=mid保留中点，直到两端重合。

## 手推一个小例子

[6,9,12,1,3]：mid=2值12大于右端3，left=3；mid=3值1小于右端3，right=3；返回1。

## 为什么正确

若中点大于右端，区间在中点之后必跨过唯一下降断点，最小值在右半；若中点小于等于右端，则中点到右端有序且其最小是中点，真正最小只能在左半或中点。区间始终包含最小值并严格缩短。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0153_find_minimum_in_rotated_sorted_array.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def findMin(self, nums: list[int]) -> int:
        if not nums:
            raise ValueError("nums must be nonempty")
        left, right = 0, len(nums) - 1
        while left < right:
            middle = (left + right) // 2
            # 中点高于右端，下降断点必在中点右侧。
            if nums[middle] > nums[right]:
                left = middle + 1
            else:
                right = middle  # 最小值可能恰好是middle
        return nums[left]
```

## 复杂度

时间O(log n)，辅助空间O(1)。

## 边界与易错点

- nums[mid]较小时不能right=mid-1，会删掉最小值本身。
- 不旋转也是合法情形。
- 有重复值的第154题需要额外规则，不能直接照搬。

## 本地测试与复习

测试单元素、已升序、长度2；随机旋转互异有序数组，与min对拍。

复习：为什么这里比较右端比比较左端更直接？试着手推长度2的两种排列。

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/find-minimum-in-rotated-sorted-array/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0153.Find%20Minimum%20in%20Rotated%20Sorted%20Array/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：解释为什么将中点与右端比较；用已排序数组与最小值靠近边界的旋转数组检查更新。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
