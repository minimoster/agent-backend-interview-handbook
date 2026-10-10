# 215. 数组中的第K个最大元素

[官方题目](https://leetcode.cn/problems/kth-largest-element-in-an-array/) · MEDIUM · 官方分类：堆

## 题意与接口

返回数组按降序排列后的第k个元素，重复值分别占名次。`findKthLargest(nums,k)`用随机三路Quickselect；`findKthLargestHeap(nums,k)`提供堆对照。两者不修改输入，k合法。

## 从朴素方法到优化

完整排序O(n log n)计算了不需要的全部次序。方案一用大小k的小根堆保存最大的k个值，O(n log k)；方案二随机划分后只继续搜索目标所在一侧，平均O(n)。

## 核心思路

主解寻找升序下标n-k。随机选枢轴，三路划分为“小于、等于、大于”；若目标落在等值段立即返回，否则只保留一侧。堆解中根是当前保留k个大值里最小的，遇更大数才替换。

## 手推一个小例子

[7,2,7,4,9]找第2大，升序目标下标3。若枢轴7，划分为[2,4]、[7,7]、[9]，目标3处于等值段，返回7。堆解维护两个最大值，最终堆内为7与9，根也是7。

## 为什么正确

三路划分后，小值段、等值段、大值段的相对名次范围确定，目标不可能在被排除的一侧；等值段覆盖其所有重复名次。堆解归纳保持已扫描前缀最大的k个元素，结束时其中最小正是全局第k大。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0215_kth_largest_element_in_an_array.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
import heapq
import random

class Solution:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        values = nums[:]  # 不修改调用方；若允许原地，可直接使用nums
        # 第k大对应升序名次n-k，重复值照常占位。
        target = len(values) - k
        left, right = 0, len(values) - 1
        while left <= right:
            pivot = values[random.randrange(left, right + 1)]
            lower = cursor = left
            upper = right
            while cursor <= upper:
                if values[cursor] < pivot:
                    values[lower], values[cursor] = values[cursor], values[lower]
                    lower += 1
                    cursor += 1
                elif values[cursor] > pivot:
                    values[cursor], values[upper] = values[upper], values[cursor]
                    upper -= 1  # 换回的值还没检查，cursor不移动
                else:
                    cursor += 1
            if target < lower:
                right = lower - 1
            elif target > upper:
                left = upper + 1
            else:
                return pivot
        raise ValueError("k must be between 1 and len(nums)")

    def findKthLargestHeap(self, nums: list[int], k: int) -> int:
        largest = nums[:k]
        heapq.heapify(largest)
        for i in range(k, len(nums)):
            if nums[i] > largest[0]:
                heapq.heapreplace(largest, nums[i])
        return largest[0]
```

## 复杂度

Quickselect：期望O(n)、最坏O(n²)时间，因保留输入而复制数组，辅助空间O(n)；划分本身O(1)额外空间且无递归栈。堆：O(n log(k+1))时间，O(k)辅助空间；k=1时即O(n)。随机枢轴只改善期望，不构成最坏线性保证。

## 边界与易错点

- 第k大不是第k个不同值；先set会改变名次。
- 三路划分交换右侧值过来后不能立即cursor++。
- 堆是小根堆，大小维持k；用大根堆保存全部值是另一种空间复杂度。
- Quickselect的n-k是升序下标，别用k-1直接查。

## 本地测试与复习

测试k=1、k=n、全相等、负数重复；固定随机种子，两种实现与sorted(nums)[-k]对拍；同时验证输入不变。

复习：什么情况下更偏好堆的稳定时间上界与O(k)空间？为什么三路划分适合大量重复值？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/kth-largest-element-in-an-array/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0215.Kth%20Largest%20Element%20in%20an%20Array/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：明确第 k 大与排序下标的换算，比较堆和快速选择在最坏时间、平均时间及输入修改上的取舍。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
