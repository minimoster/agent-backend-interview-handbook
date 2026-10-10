"""75 · 颜色分类：原创教学实现。"""
class Solution:
    def sortColors(self, nums: list[int]) -> None:
        left = scan = 0
        right = len(nums) - 1
        while scan <= right:
            if nums[scan] == 0:
                nums[left], nums[scan] = nums[scan], nums[left]
                left += 1
                scan += 1
            elif nums[scan] == 1:
                scan += 1
            else:
                nums[scan], nums[right] = nums[right], nums[scan]
                right -= 1
                # 新换到 scan 的值尚未分类，不能跳过。
