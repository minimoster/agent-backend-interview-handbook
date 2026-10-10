"""31 · 下一个排列：原创教学实现。"""
class Solution:
    def nextPermutation(self, nums: list[int]) -> None:
        pivot = len(nums) - 2
        while pivot >= 0 and nums[pivot] >= nums[pivot + 1]:
            pivot -= 1
        if pivot >= 0:
            successor = len(nums) - 1
            while nums[successor] <= nums[pivot]:
                successor -= 1
            nums[pivot], nums[successor] = nums[successor], nums[pivot]
        # 后缀仍非递增，用交换反转，避免切片的线性额外内存。
        left, right = pivot + 1, len(nums) - 1
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1
