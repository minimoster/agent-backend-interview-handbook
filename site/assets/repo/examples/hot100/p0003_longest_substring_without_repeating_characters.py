"""3 · 无重复字符的最长子串：原创教学实现。"""
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        last = {}
        left = best = 0
        for right, ch in enumerate(s):
            # 历史位置可能已在窗外，left绝不能倒退。
            left = max(left, last.get(ch, -1) + 1)
            last[ch] = right
            best = max(best, right - left + 1)
        return best
