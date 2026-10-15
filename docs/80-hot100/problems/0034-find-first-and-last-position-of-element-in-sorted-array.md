# 34. 在排序数组中查找元素的第一个和最后一个位置

难度：MEDIUM · 分类：二分查找

## 题意与接口

给非递减数组，返回目标出现的最左和最右下标；不存在返回[-1,-1]。`searchRange(nums,target)`不修改输入，空数组合法。

## 从朴素方法到优化

找到任意目标后左右扫描最坏仍O(n)，比如全数组相等。分别二分第一个≥target和第一个>target的位置，两次都O(log n)。

## 核心思路

实现统一边界函数bound(strict)。非strict时找≥target；strict时找>target。左边界lo确认命中后，右边界就是后一分界减1。

## 手推一个小例子

[1,4,4,4,8]找4：第一个≥4在1，第一个>4在4，所以答案[1,3]。找6时两分界都在4，但nums[4]不是6，返回[-1,-1]。

## 为什么正确

有序性使小于目标、等于目标、大于目标三段连续。两次二分分别确定等值段的左边界与右开边界；若左边界不是目标，等值段为空。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0034_find_first_and_last_position_of_element_in_sorted_array.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def searchRange(self, nums: list[int], target: int) -> list[int]:
        # strict区分第一个>=target与第一个>target的位置。
        def bound(strict):
            left, right = 0, len(nums)
            while left < right:
                middle = (left + right) // 2
                if nums[middle] < target or (strict and nums[middle] == target):
                    left = middle + 1
                else:
                    right = middle
            return left
        first = bound(False)
        if first == len(nums) or nums[first] != target:
            return [-1, -1]
        return [first, bound(True) - 1]
```

## 复杂度

时间O(log n)，辅助空间O(1)。

## 边界与易错点

- 不可只找到任意一个位置后线性扩张，否则不满足最坏对数要求。
- 空数组的first=0也等于len，短路判断避免越界。
- 找>target避免依赖target+1，在通用可比较类型上也更容易推广。

## 本地测试与复习

测试空、全相等、只出现一次、目标位于两端；随机与枚举全部命中下标对拍。

复习：为什么第二个边界要减1？比较bisect_left与bisect_right的含义。

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：用重复值分别手推左边界与右边界，检查目标缺失时不能把插入位置当作实际匹配。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
