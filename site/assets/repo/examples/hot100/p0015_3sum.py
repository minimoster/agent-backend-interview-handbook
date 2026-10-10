"""15 · 三数之和：原创教学实现。"""
class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        values = sorted(nums)
        answer = []
        for i in range(len(values) - 2):
            if i and values[i] == values[i - 1]:
                continue
            if values[i] > 0:
                break
            # 固定最小值后，剩余二元组可借有序性单调移动。
            left, right = i + 1, len(values) - 1
            while left < right:
                total = values[i] + values[left] + values[right]
                if total < 0:
                    left += 1
                elif total > 0:
                    right -= 1
                else:
                    answer.append([values[i], values[left], values[right]])
                    low, high = values[left], values[right]
                    while left < right and values[left] == low:
                        left += 1
                    while left < right and values[right] == high:
                        right -= 1
        return answer
