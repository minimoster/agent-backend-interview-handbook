"""994 · 腐烂的橘子：原创教学实现。"""
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
