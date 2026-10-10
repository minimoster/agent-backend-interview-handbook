# 200. 岛屿数量

[官方题目](https://leetcode.cn/problems/number-of-islands/) · MEDIUM · 官方分类：图论

## 题意与接口

二维字符网格中，`"1"` 为陆地、`"0"` 为水；上下左右相邻陆地连成一个岛。返回岛屿数量。接口：`numIslands(grid)`，本实现保留输入不变。

约束核对（2026-10-09）：行列均为 1..300，元素为字符 0/1；只按上下左右连接陆地。 [官方来源](https://leetcode.com/problems/number-of-islands/)

## 从朴素方法到优化

逐格计算“能连接哪些格子”会反复搜索同一片岛。遍历所有格子，只有遇到尚未访问的陆地才启动一次洪泛搜索，每片岛只计数一次。

## 核心思路

外层扫描找新起点；找到后答案加一，用显式栈遍历其全部四邻陆地。入栈时立即标记，防止同一格被多个邻居重复加入。

## 手推一个小例子

网格 `110 / 010 / 001`：从 (0,0) 出发走到 (0,1)、(1,1)，三格为第一岛；(2,2) 只对角接触其他陆地，是第二岛，答案 2。

## 为什么正确

四邻搜索恰访问起点所在的连通分量。该分量所有格子标记后不再触发计数，任何其他分量都不可能被本次访问，因此每个岛恰计数一次。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0200_number_of_islands.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def numIslands(self, grid):
        if not grid or not grid[0]:
            return 0
        rows, cols = len(grid), len(grid[0])
        seen, answer = set(), 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != "1" or (r, c) in seen:
                    continue
                answer += 1
                seen.add((r, c))
                stack = [(r, c)]
                while stack:
                    x, y = stack.pop()
                    for nx, ny in ((x-1,y), (x+1,y), (x,y-1), (x,y+1)):
                        if (0 <= nx < rows and 0 <= ny < cols
                                and grid[nx][ny] == "1" and (nx, ny) not in seen):
                            # 入栈时就标记，避免同格被多个邻居重复加入。
                            seen.add((nx, ny))
                            stack.append((nx, ny))
        return answer
```

## 复杂度

时间 O(RC)，辅助空间 O(RC)：访问集合和最坏搜索栈。不修改网格；若允许原地改标记，可省集合但最坏栈仍 O(RC)。

## 边界与易错点

对角线不算相邻。输入是字符不是整数。先标记再压栈，避免大量重复候选。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：如果把四邻改八邻，上述例子的答案如何变化？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/number-of-islands/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0200.Number%20of%20Islands/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/other/0200-number-of-islands-bfs.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/other/0200-number-of-islands-bfs.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：用只在对角线上接触的陆地检查邻接规则；说明何时标记访问可以避免重复入栈或入队。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
