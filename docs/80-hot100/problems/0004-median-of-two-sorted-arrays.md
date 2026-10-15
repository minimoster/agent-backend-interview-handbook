# 4. 寻找两个正序数组的中位数

难度：HARD · 分类：二分查找

## 题意与接口

给两个升序数组，其中至少一个非空，返回合并后数据的中位数。`findMedianSortedArrays(nums1,nums2)`返回float，不真正合并也不修改输入。

## 从朴素方法到优化

合并后取中位数需O(m+n)时间。中位数只由左右两半的边界决定，可以在较短数组上二分分割位置，使左半人数正确且所有左值不大于右值。

## 核心思路

在较短数组A切i个，B切j=(m+n+1)//2-i个。缺失边界用±∞。若A左边界>B右边界，i太大；若B左>A右，i太小；两条件都不违背时分割合法。

## 手推一个小例子

A=[2,8]，B=[1,5,9]，左半需3个。i=1,j=2，边界为A左2/A右8，B左5/B右9，两侧有序；总长奇数，中位数max(2,5)=5。

## 为什么正确

分割左右部分各自在内部有序，只需两条跨数组边界不交叉，就能保证左半所有值≤右半所有值。人数固定后，奇数中位数是左半最大，偶数则是左半最大与右半最小的平均。违反边界时的方向由有序性保证，二分不会删掉合法分割。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0004_median_of_two_sorted_arrays.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        a, b = nums1, nums2
        if len(a) > len(b):
            a, b = b, a
        m, n = len(a), len(b)
        if m + n == 0:
            raise ValueError("at least one array must be nonempty")
        left_size = (m + n + 1) // 2
        low, high = 0, m
        while low <= high:
            i = (low + high) // 2
            # 固定左右两半的人数，只调整两数组各自贡献。
            j = left_size - i
            a_left = a[i - 1] if i else float('-inf')
            a_right = a[i] if i < m else float('inf')
            b_left = b[j - 1] if j else float('-inf')
            b_right = b[j] if j < n else float('inf')
            if a_left > b_right:
                high = i - 1
            elif b_left > a_right:
                low = i + 1
            else:
                if (m + n) % 2:
                    return float(max(a_left, b_left))
                return (max(a_left, b_left) + min(a_right, b_right)) / 2
        raise ValueError("arrays must be sorted")
```

## 复杂度

时间O(1+log(min(m,n)+1))，辅助空间O(1)。外层的1计入较短数组为空时仍需的一次常数处理。

## 边界与易错点

- 必须在较短数组二分，才能保证由i推导的j始终在合法范围。
- 奇数时左半多一个；偶数结果使用真除法/，不能整除。
- 分割位置范围是0..m，包含空左段与空右段，不是元素下标0..m-1。

## 本地测试与复习

测试一侧为空、长短悬殊、负数重复、奇偶总长；随机与排序合并+statistics.median对拍。

复习：解释四个哨兵分别解决什么边界；如果总长偶数，为什么不能只取左半最大值？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：在较短数组上二分切分位置，检查奇偶总长度、空的一边以及切分落在端点时的边界值。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
