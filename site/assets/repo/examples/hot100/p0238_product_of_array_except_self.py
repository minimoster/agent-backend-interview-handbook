"""238 · 除了自身以外数组的乘积：原创教学实现。"""
class Solution:
    def productExceptSelf(self, nums: list[int]) -> list[int]:
        answer = [1] * len(nums)
        prefix = 1
        for i, value in enumerate(nums):
            # 先写再乘，answer[i]因此不含nums[i]。
            answer[i] = prefix
            prefix *= value
        suffix = 1
        for i in range(len(nums) - 1, -1, -1):
            answer[i] *= suffix
            suffix *= nums[i]
        return answer
