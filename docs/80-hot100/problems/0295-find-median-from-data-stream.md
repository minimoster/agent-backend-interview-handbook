# 295. 数据流的中位数

[官方题目](https://leetcode.cn/problems/find-median-from-data-stream/) · HARD · 官方分类：堆

## 题意与接口

数据流持续加入整数，随时查询当前中位数。类`MedianFinder`提供`addNum(num)`和`findMedian()`；题设查询前至少加入一个数。

## 从朴素方法到优化

每次加入后重新排序代价高；有序数组插入仍O(n)。只需要最大左半和最小右半，两个堆足以维护分界。

## 核心思路

lower用负数模拟大根堆，upper用小根堆。先把新值压入lower，再把lower最大值送到upper，最后若upper人数更多就移回其最小值。保证lower比upper多0或1个且左值≤右值。

## 手推一个小例子

加入6：lower={6},upper={}，中位数6。加入2：lower={2},upper={6}，中位数4。加入9：lower={2,6},upper={9}，中位数6。

## 为什么正确

把lower最大值送到upper修复两堆顺序；若upper过大，再把upper最小值移回lower不会打破顺序。平衡后奇数时lower多一个，根就是中位数；偶数时两根是中央两项。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0295_find_median_from_data_stream.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lower = []  # 存负数，根的相反数为左半最大值
        self.upper = []

    def addNum(self, num: int) -> None:
        # 先修复两堆数值顺序，再修复人数差。
        heapq.heappush(self.lower, -num)
        heapq.heappush(self.upper, -heapq.heappop(self.lower))
        if len(self.upper) > len(self.lower):
            heapq.heappush(self.lower, -heapq.heappop(self.upper))

    def findMedian(self) -> float:
        if not self.lower:
            raise ValueError("no values added")
        if len(self.lower) > len(self.upper):
            return float(-self.lower[0])
        return (-self.lower[0] + self.upper[0]) / 2
```

## 复杂度

加入O(log n)，查询O(1)，存储n个数共O(n)空间。没有假定堆内所有元素有序。

## 边界与易错点

- 左堆存负数，跨堆移动必须变号。
- 两堆大小只能相等或左多1个，奇偶中位数规则与此约定绑定。
- 重复值、负数都按普通数值处理，不能用集合保存。

## 本地测试与复习

测试奇偶、负数、重复；随机每次add后与statistics.median比较，并检查两堆大小与边界顺序。

复习：若还要求删除任意旧元素，为什么标准堆不能直接维持同样简单接口？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/find-median-from-data-stream/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0295.Find%20Median%20from%20Data%20Stream/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：在每次插入后检查堆的大小差和跨堆顺序，手推奇数与偶数数量时的中位数。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
