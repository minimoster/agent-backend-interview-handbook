"""121 · 买卖股票的最佳时机：原创教学实现。"""
class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        lowest = prices[0]
        best = 0
        for i in range(1, len(prices)):
            price = prices[i]
            # 卖出必须使用以前某一天的买入价。
            best = max(best, price - lowest)
            lowest = min(lowest, price)
        return best
