# 84. 柱状图中最大的矩形

难度：HARD · 分类：栈

## 题意与接口

柱状图每根柱宽1，求完全包含在柱形区域中的最大矩形面积。`largestRectangleArea(heights)`返回整数，不修改输入。

## 从朴素方法到优化

对每个高度向两边寻找更低边界需O(n²)。单调栈能在第一次遇到右侧更低柱时，同时确定一些高度的最远跨度。

## 核心思路

栈存(start,height)，高度严格递增。读到更低或相等高度，弹出旧柱，用当前下标减start结算面积，并把旧start传给当前柱；末尾虚拟高度0让剩余柱全部结算。

## 手推一个小例子

[2,4,3]：2从0入栈，4从1入栈；遇3弹4，面积4×1=4，3继承start=1；结尾0弹3得3×2=6，再弹2得2×3=6，最大6。

## 为什么正确

栈中某高度的start是它能向左覆盖的最早位置。更低柱到来时，该高度无法向右继续，当前结算覆盖其全部合法跨度。相等高度合并保留更早start不会丢掉更优矩形。任何最优矩形都可取其覆盖柱中的最低高度，因此必被某次结算包含。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0084_largest_rectangle_in_histogram.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def largestRectangleArea(self, heights: list[int]) -> int:
        increasing = []
        best = 0
        for right in range(len(heights) + 1):
            value = heights[right] if right < len(heights) else 0
            start = right
            # 当前柱限制右边界，较矮新柱继承弹出柱的最早起点。
            while increasing and increasing[-1][1] >= value:
                start, old_height = increasing.pop()
                best = max(best, old_height * (right - start))
            increasing.append((start, value))
        return best
```

## 复杂度

时间O(n)，辅助空间O(n)。没有heights+[0]的额外复制，末尾哨兵通过逻辑下标产生。

## 边界与易错点

- 弹栈后的start要传递给当前更矮柱，不然会遗漏向左延展。
- 最后必须结算尚在栈中的柱，单调递增输入尤其容易漏。
- 高度为0会切断正高度矩形，重复高度合并要保留最早起点。

## 本地测试与复习

测试零、全同、单调、峰谷；随机枚举所有区间的最小高度×长度对拍。

复习：与“栈存下标+左边更低边界”的写法如何对应？为什么面积宽度不加1？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：在弹栈时指出左右更矮边界，检查相等高度与末尾剩余栈如何处理。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
