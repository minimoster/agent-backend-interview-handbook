# 64. 最小路径和

[官方题目](https://leetcode.cn/problems/minimum-path-sum/) · MEDIUM · 官方分类：多维动态规划

## 题意与接口

接口：`Solution.minPathSum(grid: list[list[int]]) -> int`。网格每格有非负代价，从左上到右下仅向右或向下，求沿途格子值总和的最小值，起点和终点都计入。官方网格非空，行列各至多 200。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/minimum-path-sum/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

枚举每条路径会指数增长。到某格的最小路径只需比较上方和左方的最优路径；二维 DP 可压缩成一行。本实现额外保存这一行，不修改输入网格。

## 核心思路

dp[col] 为当前扫描位置的最小代价。初始全部为无穷大，仅 dp[0]=0，作为起点上方的虚拟来源。每格取上方旧 dp[col] 与左方新 dp[col−1] 的最小值，再加本格代价；第一列没有左方，用无穷大排除。

## 手推一个小例子

取网格 `[[2,1,4],[3,2,1]]`：
1. 初始 `[0,∞,∞]`。
2. 第一行依次成为 `[2,3,7]`。
3. 第二行第一格为 2+3=5。
4. 中间格取 min(3,5)+2=5。
5. 右下取 min(7,5)+1=6，答案 6，对应 2→1→2→1。

## 为什么正确

到每个非起点格子的路径最后一步只能来自上或左。若之前的路径不是该前驱格子的最优路径，可以替换而不改变后续移动，因而最优代价必为两前驱最优值中较小者加当前值。虚拟初值让起点恰好计入一次，行列边界排除不存在的前驱，一维更新保持正确依赖，所以最终状态正确。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0064_minimum_path_sum.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def minPathSum(self, grid: list[list[int]]) -> int:
        columns = len(grid[0])
        dp = [float('inf')] * columns
        dp[0] = 0  # 只为起点提供一个零代价的虚拟前驱。
        for row in grid:
            for column, value in enumerate(row):
                left = dp[column - 1] if column > 0 else float('inf')
                dp[column] = min(dp[column], left) + value
        return dp[-1]
```

## 复杂度

时间 O(mn)，辅助空间 O(n)，不修改 grid。所有合法位置均能到达，选中的最小前驱是整数，所以最终返回整数而非无穷大。

## 边界与易错点

- 只有一个格子时返回该格子的值。
- 起点也计入路径和。
- 第一行无真实上方、第一列无左方，必须通过初始化或分支处理。
- 将 dp 初始化为全 0 会虚构从网格中间开始的免费路径。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0064`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：为何不能每步选相邻格子中较小的那个？如何恢复一条最优路径而不只返回总和？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/minimum-path-sum/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0064.Minimum%20Path%20Sum/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：区别路径数与最小路径和的转移，检查第一行第一列只有一个前驱的边界。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
