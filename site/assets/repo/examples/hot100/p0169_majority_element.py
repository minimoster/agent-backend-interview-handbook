"""169 · 多数元素：原创教学实现。"""
class Solution:
    def majorityElement(self, nums: list[int]) -> int:
        candidate = nums[0]
        votes = 0
        for value in nums:
            if votes == 0:
                # 之前的票已成对抵消，从当前值建立新候选。
                candidate = value
            votes += 1 if value == candidate else -1
        return candidate
