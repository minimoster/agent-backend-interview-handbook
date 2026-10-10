"""84 · 柱状图中最大的矩形：原创教学实现。"""
class Solution:
    def largestRectangleArea(self, heights: list[int]) -> int:
        increasing = []
        best = 0
        for right in range(len(heights) + 1):
            value = heights[right] if right < len(heights) else 0
            start = right
            # 当前柱限制右边界，较矮新柱继承弹出柱的最早起点。
            while increasing and increasing[-1][1] >= value:
                start, old_height = increasing.pop()
                best = max(best, old_height * (right - start))
            increasing.append((start, value))
        return best
