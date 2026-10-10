"""32 · 最长有效括号：原创教学实现。"""
class Solution:
    def longestValidParentheses(self, s: str) -> int:
        dp = [0] * len(s)
        best = 0
        for i in range(1, len(s)):
            if s[i] != ')':
                continue
            # 跨过紧邻的完整合法段，再寻找能够包住它的左括号。
            opening = i - dp[i - 1] - 1
            if opening >= 0 and s[opening] == '(':
                dp[i] = dp[i - 1] + 2
                if opening > 0:
                    dp[i] += dp[opening - 1]
                best = max(best, dp[i])
        return best
