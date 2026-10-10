# 994. 腐烂的橘子

[官方题目](https://leetcode.cn/problems/rotting-oranges/) · MEDIUM · 官方分类：图论

## 题意与接口

网格 0 为空格、1 为新鲜橘子、2 为腐烂橘子。每分钟所有腐烂橘子同时感染四邻新鲜橘子；求全部腐烂的最短分钟数，不可能则 -1。接口：`orangesRotting(grid)`，会修改网格。

约束核对（2026-10-09）：行列均为 1..10，元素为整数 0/1/2；所有腐烂源每分钟同时四向传播。 [官方来源](https://leetcode.com/problems/rotting-oranges/)

## 从朴素方法到优化

逐分钟扫描整张网格可能 O(RC×分钟数)，且直接边扫描边改会在一分钟内传播多层。将所有初始腐烂点同时入队，用多源 BFS 精确模拟同一时间层。

## 核心思路

先统计 fresh 并收集全部腐烂格。只要尚有 fresh 且队列不空，每轮处理当前队列长度，一轮就是一分钟。新感染格立即置为 2、fresh 减一并入队。

## 手推一个小例子

一行 `[2,1,1,1,2]`：第 1 分钟两端同时感染位置 1、3；第 2 分钟感染位置 2，全部腐烂，返回 2。单源搜索会错误忽略另一端带来的加速。

## 为什么正确

BFS 第 t 层恰是距最近初始腐烂点 t 步的可达橘子；首次感染最早，因此最后一个新鲜橘子的层数就是总耗时。队列耗尽仍有 fresh 表示不存在可传播路径。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0994_rotting_oranges.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from collections import deque

class Solution:
    def orangesRotting(self, grid):
        if not grid or not grid[0]:
            return 0
        rows, cols = len(grid), len(grid[0])
        queue, fresh = deque(), 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 2:
                    queue.append((r, c))
                elif grid[r][c] == 1:
                    fresh += 1
        minutes = 0
        while queue and fresh:
            # 一轮只处理当前时间层，新增感染点下一分钟再传播。
            for _ in range(len(queue)):
                r, c = queue.popleft()
                for nr, nc in ((r-1,c), (r+1,c), (r,c-1), (r,c+1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                        grid[nr][nc] = 2
                        fresh -= 1
                        queue.append((nr, nc))
            minutes += 1
        return minutes if fresh == 0 else -1
```

## 复杂度

时间 O(RC)，辅助队列 O(RC)。原地把新鲜格改为腐烂格。

## 边界与易错点

一开始没有新鲜橘子就返回 0。有新鲜但无腐烂源返回 -1。同一分钟新增节点只能下一轮传播。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为什么从每个腐烂点各跑一次 BFS 再取最小距离虽然可行却更慢？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/rotting-oranges/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0900-0999/0994.Rotting%20Oranges/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：从所有初始腐烂橘子同时开始 BFS，检查没有新鲜橘子与新鲜橘子不可达两种结束情况。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
