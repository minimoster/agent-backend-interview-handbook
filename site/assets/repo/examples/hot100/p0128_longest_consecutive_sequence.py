"""128 · 最长连续序列：原创教学实现。"""
class Solution:
    def longestConsecutive(self, nums: list[int]) -> int:
        # 去重既保证段长正确，也避免重复的起点多次扫描。
        values = set(nums)
        best = 0
        for value in values:
            if value - 1 in values:
                continue  # 只在连续段最左端起跑
            end = value
            while end in values:
                end += 1
            best = max(best, end - value)
        return best
