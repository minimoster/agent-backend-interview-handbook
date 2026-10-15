# 54. 螺旋矩阵

难度：MEDIUM · 分类：矩阵

## 题意与接口

按从左上角开始顺时针绕圈的顺序，返回矩阵全部元素。`spiralOrder(matrix)` 返回新列表，不修改矩阵。

## 从朴素方法到优化

模拟每步方向并用访问集合避开走过位置，需要 O(mn)额外标记。未访问区域始终是一个矩形，四条边界足以描述它。

## 核心思路

依次读上边、右边、下边、左边，每读完一边缩进相应边界。下边与左边执行前重新检查区域是否还存在，防止中心单行或单列重复。

## 手推一个小例子

[[1,2,3],[4,5,6]]：上边取1,2,3；右边取6；下边倒取5,4；此时区域已空，不再读左边，结果[1,2,3,6,5,4]。

## 为什么正确

循环开始时，所有未读元素恰在四条边界围成的闭矩形内。按四边遍历把外圈每格读一次，更新边界后剩余区域仍为矩形。判断空区域避免细长内圈重复访问，最终每格恰输出一次。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0054_spiral_matrix.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def spiralOrder(self, matrix: list[list[int]]) -> list[int]:
        if not matrix or not matrix[0]:
            return []
        top, bottom = 0, len(matrix) - 1
        left, right = 0, len(matrix[0]) - 1
        answer = []
        while top <= bottom and left <= right:
            for col in range(left, right + 1):
                answer.append(matrix[top][col])
            top += 1
            for row in range(top, bottom + 1):
                answer.append(matrix[row][right])
            right -= 1
            # 最内层可能已没有下边，不能重复读取剩余单行。
            if top <= bottom:
                for col in range(right, left - 1, -1):
                    answer.append(matrix[bottom][col])
                bottom -= 1
            if left <= right:
                for row in range(bottom, top - 1, -1):
                    answer.append(matrix[row][left])
                left += 1
        return answer
```

## 复杂度

时间 O(mn)，除输出外辅助空间 O(1)，输出 O(mn)。

## 边界与易错点

- 最内圈可能只剩一行或一列，不能无条件遍历四边。
- range倒序终点不包含，常需left-1或top-1。
- 不需要修改原矩阵做已访问标记。

## 本地测试与复习

测试所有1..5行、1..5列矩阵，与独立方向移动+visited模拟对拍。

复习：给3×1和1×3矩阵，逐行手推边界变化；哪里避免了重复输出？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：用单行、单列和奇数边长矩阵检查收缩边界，避免最后一圈重复访问。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
