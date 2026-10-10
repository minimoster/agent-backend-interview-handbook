"""287 · 寻找重复数：原创教学实现。"""
class Solution:
    def findDuplicate(self, nums: list[int]) -> int:
        slow = fast = 0
        while True:
            slow = nums[slow]
            fast = nums[nums[fast]]
            if slow == fast:
                break
        finder = 0  # 重置到与第一阶段相同的轨迹起点。
        while finder != slow:
            finder = nums[finder]
            slow = nums[slow]
        return finder
