"""152 · 乘积最大子数组：原创教学实现。"""
class Solution:
    def maxProduct(self, nums: list[int]) -> int:
        largest = smallest = best = nums[0]
        for i in range(1, len(nums)):
            value = nums[i]
            # 两个新极值必须读取同一轮的旧状态。
            from_largest = largest * value
            from_smallest = smallest * value
            largest = max(value, from_largest, from_smallest)
            smallest = min(value, from_largest, from_smallest)
            best = max(best, largest)
        return best
