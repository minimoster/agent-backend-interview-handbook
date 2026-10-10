"""283 · 移动零：原创教学实现。"""
class Solution:
    def moveZeroes(self, nums: list[int]) -> None:
        # nums[:write]始终是已读区域中稳定排列的非零前缀。
        write = 0
        for value in nums:
            if value != 0:
                nums[write] = value
                write += 1
        for i in range(write, len(nums)):
            nums[i] = 0
