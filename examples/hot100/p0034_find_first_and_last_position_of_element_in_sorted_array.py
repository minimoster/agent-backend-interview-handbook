"""34 · 在排序数组中查找元素的第一个和最后一个位置：原创教学实现。"""
class Solution:
    def searchRange(self, nums: list[int], target: int) -> list[int]:
        # strict区分第一个>=target与第一个>target的位置。
        def bound(strict):
            left, right = 0, len(nums)
            while left < right:
                middle = (left + right) // 2
                if nums[middle] < target or (strict and nums[middle] == target):
                    left = middle + 1
                else:
                    right = middle
            return left
        first = bound(False)
        if first == len(nums) or nums[first] != target:
            return [-1, -1]
        return [first, bound(True) - 1]
