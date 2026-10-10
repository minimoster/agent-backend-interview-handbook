"""322 · 零钱兑换：原创教学实现。"""
class Solution:
    def coinChange(self, coins: list[int], amount: int) -> int:
        unreachable = amount + 1
        dp = [0] + [unreachable] * amount
        for value in range(1, amount + 1):
            for coin in coins:
                if coin <= value:
                    # 正面额让前驱金额更小，可反复使用同一面额。
                    dp[value] = min(dp[value], dp[value - coin] + 1)
        return -1 if dp[amount] == unreachable else dp[amount]
