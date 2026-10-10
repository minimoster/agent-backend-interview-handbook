"""11 · 盛最多水的容器：原创教学实现。"""
class Solution:
    def maxArea(self, height: list[int]) -> int:
        left, right, best = 0, len(height) - 1, 0
        while left < right:
            best = max(best, (right - left) * min(height[left], height[right]))
            # 固定较短边只会越缩越差，因此安全舍弃较短边。
            if height[left] <= height[right]:
                left += 1
            else:
                right -= 1
        return best
