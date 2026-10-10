"""300 · 最长递增子序列：原创教学实现。"""
from bisect import bisect_left


class Solution:
    def lengthOfLIS(self, nums: list[int]) -> int:
        tails = []
        for value in nums:
            # 首个 >=value 的位置，避免把相等数算作严格递增。
            position = bisect_left(tails, value)
            if position == len(tails):
                tails.append(value)
            else:
                tails[position] = value
        return len(tails)
