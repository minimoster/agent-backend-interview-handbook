"""55 · 跳跃游戏：原创教学实现。"""
class Solution:
    def canJump(self, nums: list[int]) -> bool:
        farthest = 0  # 已扫描的可达位置共同覆盖的最右下标。
        for i, jump in enumerate(nums):
            if i > farthest:
                return False
            farthest = max(farthest, i + jump)
            if farthest >= len(nums) - 1:
                return True
        return False
