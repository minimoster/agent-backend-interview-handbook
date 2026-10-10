"""45 · 跳跃游戏 II：原创教学实现。"""
class Solution:
    def jump(self, nums: list[int]) -> int:
        steps = 0
        end = 0
        farthest = 0
        for i in range(len(nums) - 1):
            farthest = max(farthest, i + nums[i])
            if i == end:
                # 本层全部处理完，才用一跳进入下一层。
                steps += 1
                end = farthest
                if end >= len(nums) - 1:
                    break
        return steps
