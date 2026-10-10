"""215 · 数组中的第K个最大元素：原创教学实现。"""
import heapq
import random

class Solution:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        values = nums[:]  # 不修改调用方；若允许原地，可直接使用nums
        # 第k大对应升序名次n-k，重复值照常占位。
        target = len(values) - k
        left, right = 0, len(values) - 1
        while left <= right:
            pivot = values[random.randrange(left, right + 1)]
            lower = cursor = left
            upper = right
            while cursor <= upper:
                if values[cursor] < pivot:
                    values[lower], values[cursor] = values[cursor], values[lower]
                    lower += 1
                    cursor += 1
                elif values[cursor] > pivot:
                    values[cursor], values[upper] = values[upper], values[cursor]
                    upper -= 1  # 换回的值还没检查，cursor不移动
                else:
                    cursor += 1
            if target < lower:
                right = lower - 1
            elif target > upper:
                left = upper + 1
            else:
                return pivot
        raise ValueError("k must be between 1 and len(nums)")

    def findKthLargestHeap(self, nums: list[int], k: int) -> int:
        largest = nums[:k]
        heapq.heapify(largest)
        for i in range(k, len(nums)):
            if nums[i] > largest[0]:
                heapq.heapreplace(largest, nums[i])
        return largest[0]
