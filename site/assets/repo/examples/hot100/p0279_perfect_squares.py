"""279 · 完全平方数：原创教学实现。"""
from math import isqrt


class Solution:
    def numSquares(self, n: int) -> int:
        squares = [root * root for root in range(1, isqrt(n) + 1)]
        dp = [0] + [n + 1] * n
        for value in range(1, n + 1):
            for square in squares:
                if square > value:
                    break
                # 枚举最后一项；较小金额的最优值已经确定。
                dp[value] = min(dp[value], dp[value - square] + 1)
        return dp[n]
