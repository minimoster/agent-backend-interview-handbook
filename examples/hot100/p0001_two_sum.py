"""1 · 两数之和：原创教学实现。"""
class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        # 表里只存已经走过的位置，避免一个元素使用两次。
        seen = {}
        for i, value in enumerate(nums):
            complement = target - value
            if complement in seen:  # 先查询，确保不能复用当前位置
                return [seen[complement], i]
            seen[value] = i
        return []  # 非题设的无解输入，方便本地复用
