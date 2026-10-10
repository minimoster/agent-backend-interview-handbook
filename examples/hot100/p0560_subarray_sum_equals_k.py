"""560 · 和为 K 的子数组：原创教学实现。"""
from collections import defaultdict

class Solution:
    def subarraySum(self, nums: list[int], k: int) -> int:
        frequency = defaultdict(int)
        frequency[0] = 1
        prefix = answer = 0
        for value in nums:
            prefix += value
            # 先计数再登记当前前缀，排除零长度区间。
            answer += frequency[prefix - k]
            frequency[prefix] += 1
        return answer
