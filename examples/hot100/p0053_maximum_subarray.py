"""53 · 最大子数组和：原创教学实现。"""
class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        if not nums:
            raise ValueError("nums must be nonempty")
        ending = best = nums[0]
        for i in range(1, len(nums)):
            # 延长前缀不划算时，从当前位置重新开始。
            ending = max(nums[i], ending + nums[i])
            best = max(best, ending)
        return best
