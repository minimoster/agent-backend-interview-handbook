"""1143 · 最长公共子序列：原创教学实现。"""
class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        if len(text1) < len(text2):
            text1, text2 = text2, text1
        dp = [0] * (len(text2) + 1)
        for first in text1:
            diagonal = 0
            for column, second in enumerate(text2, 1):
                above = dp[column]  # 覆盖前先保存，供下一列作左上角。
                if first == second:
                    dp[column] = diagonal + 1
                else:
                    dp[column] = max(above, dp[column - 1])
                diagonal = above
        return dp[-1]
