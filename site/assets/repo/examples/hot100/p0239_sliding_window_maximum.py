"""239 · 滑动窗口最大值：原创教学实现。"""
from collections import deque

class Solution:
    def maxSlidingWindow(self, nums: list[int], k: int) -> list[int]:
        if k <= 0 or k > len(nums):
            return []  # 题设外输入的本地约定
        candidates = deque()
        answer = []
        for right, value in enumerate(nums):
            while candidates and candidates[0] <= right - k:
                candidates.popleft()
            # 新值更大且更晚过期，旧的较小候选不再可能最优。
            while candidates and nums[candidates[-1]] <= value:
                candidates.pop()
            candidates.append(right)
            if right >= k - 1:
                answer.append(nums[candidates[0]])
        return answer
