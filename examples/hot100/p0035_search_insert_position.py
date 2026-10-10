"""35 · 搜索插入位置：原创教学实现。"""
class Solution:
    def searchInsert(self, nums: list[int], target: int) -> int:
        # 半开区间[left,right)，答案允许是尾后位置n。
        left, right = 0, len(nums)
        while left < right:
            middle = (left + right) // 2
            if nums[middle] < target:
                left = middle + 1
            else:
                right = middle  # middle仍可能是第一个满足条件的位置
        return left
