"""347 · 前 K 个高频元素：原创教学实现。"""
from collections import Counter

class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        counts = Counter(nums)
        # 频率最多n；每个桶必须独立，不能用列表乘法共享。
        buckets = [[] for _ in range(len(nums) + 1)]
        for value, frequency in counts.items():
            buckets[frequency].append(value)
        answer = []
        for frequency in range(len(nums), 0, -1):
            for value in buckets[frequency]:
                answer.append(value)
                if len(answer) == k:
                    return answer
        return answer
