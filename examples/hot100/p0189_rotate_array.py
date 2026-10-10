"""189 · 轮转数组：原创教学实现。"""
class Solution:
    def rotate(self, nums: list[int], k: int) -> None:
        if not nums:
            return
        k %= len(nums)
        def reverse(left, right):
            while left < right:
                nums[left], nums[right] = nums[right], nums[left]
                left += 1
                right -= 1
        # AB -> rev(B)rev(A) -> B rev(A) -> BA。
        reverse(0, len(nums) - 1)
        reverse(0, k - 1)
        reverse(k, len(nums) - 1)
