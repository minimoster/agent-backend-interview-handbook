# 51. N 皇后

难度：HARD · 分类：回溯

## 题意与接口

在 n×n 棋盘放 n 个皇后，使任意两者不同行、不同列、不共斜线，返回所有棋盘。接口：`solveNQueens(n)`。本题约定 `1 <= n <= 9`。

约束核对（2026-10-09）：n 为 1..9；输出互不攻击的皇后棋盘，解顺序不限。

## 从朴素方法到优化

枚举棋盘所有 n 个位置组合再检查太大。每行恰放一个皇后，只需在 n 列中选择，同时用集合即时排除列与两条斜线冲突。

## 核心思路

当前行 r，候选列 c；占用键为 c、r-c、r+c。可放时加入三集合、记录列，递归下一行；返回时全部撤销。满 n 行后构造 Q 和点组成的字符串棋盘。

## 手推一个小例子

n=4，尝试列序 `[1,3,0,2]`：行 0 放列 1；行 1 放列 3；行 2 放列 0；行 3 放列 2。列互异，r-c 和 r+c 也各不相同，因此输出一个解；回溯继续得到另一解。

## 为什么正确

同行通过一行一皇后保证，列集合排除同列，两类斜线的格子分别具有固定 r-c 或 r+c。每一步都保持无冲突，满行就是合法解；任意合法棋盘按行对应唯一选择序列，必被搜索覆盖。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0051_n_queens.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def solveNQueens(self, n):
        answer, placement = [], []
        columns, falling, rising = set(), set(), set()
        def search(row):
            if row == n:
                answer.append(["." * col + "Q" + "." * (n-col-1)
                               for col in placement])
                return
            for col in range(n):
                # 两族斜线分别具有固定的行列差、行列和。
                down, up = row - col, row + col
                if col in columns or down in falling or up in rising:
                    continue
                columns.add(col)
                falling.add(down)
                rising.add(up)
                placement.append(col)
                search(row + 1)
                # 撤销全部四处状态，下一候选从同一棋盘前缀出发。
                placement.pop()
                columns.remove(col)
                falling.remove(down)
                rising.remove(up)
        search(0)
        return answer
```

## 复杂度

设 Q 为解数。每层扫描 n 列，忽略斜线剪枝时递归状态总数 O(n!)，故保守时间 O(n·n! + Q·n²)，含构造所有棋盘；辅助空间 O(n)，输出 O(Q·n²)。不要遗漏每解的 n² 个字符。

## 边界与易错点

n=1 有一个解，n=2、3 无解。撤销三类占用和 placement 要成对完整。r-c 可负，不应直接当非负数组下标。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为何 r-c 相同等价于共一条斜线？位运算版本可优化什么常数，而不改变输出下界？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：解释两个对角线标识的计算方式，验证回溯撤销后不会影响同一行的下一个选择。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
