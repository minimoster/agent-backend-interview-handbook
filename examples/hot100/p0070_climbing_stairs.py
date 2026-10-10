"""70 · 爬楼梯：原创教学实现。"""
class Solution:
    def climbStairs(self, n: int) -> int:
        previous, current = 1, 1  # f(0), f(1)
        for _ in range(2, n + 1):
            previous, current = current, previous + current
        return current
