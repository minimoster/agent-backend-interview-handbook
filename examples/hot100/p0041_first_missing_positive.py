"""41 · 缺失的第一个正数：原创教学实现。"""
class Solution:
    def firstMissingPositive(self, nums: list[int]) -> int:
        n = len(nums)
        # 合法值x的登记位置是x-1；每次交换至少归位一个值。
        for i in range(n):
            while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                target = nums[i] - 1  # 先存目标，避免交换后再读nums[i]
                nums[i], nums[target] = nums[target], nums[i]
        for i, value in enumerate(nums):
            if value != i + 1:
                return i + 1
        return n + 1
