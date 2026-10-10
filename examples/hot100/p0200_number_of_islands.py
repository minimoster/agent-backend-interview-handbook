"""200 · 岛屿数量：原创教学实现。"""
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
