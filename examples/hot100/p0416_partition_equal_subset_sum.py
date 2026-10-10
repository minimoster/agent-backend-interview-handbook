"""416 · 分割等和子集：原创教学实现。"""
class Solution:
    def canPartition(self, nums: list[int]) -> bool:
        total = sum(nums)
        if total % 2:
            return False
        target = total // 2
        possible = [False] * (target + 1)
        possible[0] = True
        for value in nums:
            # 倒序保证 possible[capacity-value] 尚未使用当前元素。
            for capacity in range(target, value - 1, -1):
                possible[capacity] = (
                    possible[capacity] or possible[capacity - value]
                )
            if possible[target]:
                return True
        return possible[target]
