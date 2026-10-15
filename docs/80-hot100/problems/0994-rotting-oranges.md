# 994. 腐烂的橘子

难度：MEDIUM · 分类：图论

## 题意与接口

网格 0 为空格、1 为新鲜橘子、2 为腐烂橘子。每分钟所有腐烂橘子同时感染四邻新鲜橘子；求全部腐烂的最短分钟数，不可能则 -1。接口：`orangesRotting(grid)`，会修改网格。

约束核对（2026-10-09）：行列均为 1..10，元素为整数 0/1/2；所有腐烂源每分钟同时四向传播。

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

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：从所有初始腐烂橘子同时开始 BFS，检查没有新鲜橘子与新鲜橘子不可达两种结束情况。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
