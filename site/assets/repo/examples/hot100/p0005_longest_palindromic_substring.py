"""5 · 最长回文子串：原创教学实现。"""
class Solution:
    def longestPalindrome(self, s: str) -> str:
        best_start = 0
        best_length = 0
        for center in range(len(s)):
            for left, right in ((center, center), (center, center + 1)):
                while left >= 0 and right < len(s) and s[left] == s[right]:
                    left -= 1
                    right += 1
                # 停止时两指针恰在合法回文区间之外。
                length = right - left - 1
                if length > best_length:
                    best_start = left + 1
                    best_length = length
        return s[best_start:best_start + best_length]
