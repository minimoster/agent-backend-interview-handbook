"""136 · 只出现一次的数字：原创教学实现。"""
class Solution:
    def singleNumber(self, nums: list[int]) -> int:
        answer = 0
        for value in nums:
            answer ^= value  # 成对相等值会在累计异或中抵消。
        return answer
