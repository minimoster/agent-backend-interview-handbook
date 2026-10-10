"""76 · 最小覆盖子串：原创教学实现。"""
from collections import Counter

class Solution:
    def minWindow(self, s: str, t: str) -> str:
        if not t:
            return ""
        need = Counter(t)
        missing = len(t)
        left = best_left = 0
        best_length = len(s) + 1
        for right, ch in enumerate(s):
            # 仅当此前仍短缺该字符时，missing才真正减少。
            if need[ch] > 0:
                missing -= 1
            need[ch] -= 1
            while missing == 0:
                if right - left + 1 < best_length:
                    best_left, best_length = left, right - left + 1
                outgoing = s[left]
                need[outgoing] += 1
                if need[outgoing] > 0:
                    missing += 1
                left += 1
        if best_length > len(s):
            return ""
        return s[best_left:best_left + best_length]
