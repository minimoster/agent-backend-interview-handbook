"""153 · 寻找旋转排序数组中的最小值：原创教学实现。"""
class Solution:
    def findMin(self, nums: list[int]) -> int:
        if not nums:
            raise ValueError("nums must be nonempty")
        left, right = 0, len(nums) - 1
        while left < right:
            middle = (left + right) // 2
            # 中点高于右端，下降断点必在中点右侧。
            if nums[middle] > nums[right]:
                left = middle + 1
            else:
                right = middle  # 最小值可能恰好是middle
        return nums[left]
