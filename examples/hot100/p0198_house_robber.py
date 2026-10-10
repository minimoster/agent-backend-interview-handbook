"""198 · 打家劫舍：原创教学实现。"""
class Solution:
    def rob(self, nums: list[int]) -> int:
        previous = current = 0
        for value in nums:
            # 右侧读取的都是更新前的两个前缀状态。
            previous, current = current, max(current, previous + value)
        return current
