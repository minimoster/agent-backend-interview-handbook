"""62 · 不同路径：原创教学实现。"""
class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        dp = [1] * n
        for _ in range(1, m):
            for column in range(1, n):
                # dp[column] 来自上一行，dp[column-1] 来自当前行。
                dp[column] += dp[column - 1]
        return dp[-1]
