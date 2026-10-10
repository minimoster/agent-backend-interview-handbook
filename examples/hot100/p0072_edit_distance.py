"""72 · 编辑距离：原创教学实现。"""
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        # 插入和删除代价相同，交换两串不改变距离，短串作列。
        if len(word1) < len(word2):
            word1, word2 = word2, word1
        dp = list(range(len(word2) + 1))
        for row, first in enumerate(word1, 1):
            diagonal = dp[0]
            dp[0] = row
            for column, second in enumerate(word2, 1):
                above = dp[column]
                if first == second:
                    dp[column] = diagonal
                else:
                    dp[column] = 1 + min(above, dp[column - 1], diagonal)
                diagonal = above
        return dp[-1]
