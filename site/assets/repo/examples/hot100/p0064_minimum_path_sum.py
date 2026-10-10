"""64 · 最小路径和：原创教学实现。"""
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
