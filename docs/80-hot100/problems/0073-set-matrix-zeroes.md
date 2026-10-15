# 73. 矩阵置零

难度：MEDIUM · 分类：矩阵

## 题意与接口

矩阵中原先为0的格子，会让它所在整行与整列都变成0。`setZeroes(matrix)` 原地修改并返回None；只以原始零的位置为依据。

## 从朴素方法到优化

发现零就立即清整行列会制造新零并错误传播。先保存零行/列集合是 O(m+n)空间；用矩阵首行首列作标记可降到常数额外空间。

## 核心思路

先独立记住首行、首列本来是否有零。扫描内部格，遇零就在对应首行/首列打标；第二轮依标记清内部；最后再决定是否清首行、首列。

## 手推一个小例子

[[1,2,3],[4,0,6],[7,8,9]]：中心零使matrix[1][0]与matrix[0][1]成为0；据此清第1行与第1列，得到[[1,0,3],[0,0,0],[7,0,9]]。

## 为什么正确

扫描内部时只写首行首列，不会改变其他待检查内部格，所以标记恰好描述原始内部零。提前保存的两个布尔量补充了首行首列原始信息。根据这些标记同时清零，等价于原始所有零行列的并集。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0073_set_matrix_zeroes.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def setZeroes(self, matrix: list[list[int]]) -> None:
        if not matrix or not matrix[0]:
            return
        rows, cols = len(matrix), len(matrix[0])
        # 首行和首列稍后会充当标记，先保存它们的原始状态。
        first_row_zero = any(matrix[0][j] == 0 for j in range(cols))
        first_col_zero = any(matrix[i][0] == 0 for i in range(rows))
        for i in range(1, rows):
            for j in range(1, cols):
                if matrix[i][j] == 0:
                    matrix[i][0] = matrix[0][j] = 0
        for i in range(1, rows):
            for j in range(1, cols):
                if matrix[i][0] == 0 or matrix[0][j] == 0:
                    matrix[i][j] = 0
        if first_row_zero:
            for j in range(cols):
                matrix[0][j] = 0
        if first_col_zero:
            for i in range(rows):
                matrix[i][0] = 0
```

## 复杂度

时间 O(mn)，辅助空间 O(1)。any使用生成器，没有构造一整列的列表。

## 边界与易错点

- matrix[0][0]不能单独同时表达首行、首列两个独立状态。
- 最后再清首行首列，避免破坏标记。
- 单行单列与首格为零是高价值测试。

## 本地测试与复习

测试首行、首列、首格、单行单列；随机与“先收集所有原始零行列”的参考法对拍。

复习：只用一个额外布尔量也能做，另一个状态放在哪里？实现是否因此更容易出错？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：第一行和第一列同时充当标记区时，哪些原始信息需要单独保存？检查清零执行顺序。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
