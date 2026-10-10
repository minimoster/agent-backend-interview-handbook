"""4 · 寻找两个正序数组的中位数：原创教学实现。"""
class Solution:
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        a, b = nums1, nums2
        if len(a) > len(b):
            a, b = b, a
        m, n = len(a), len(b)
        if m + n == 0:
            raise ValueError("at least one array must be nonempty")
        left_size = (m + n + 1) // 2
        low, high = 0, m
        while low <= high:
            i = (low + high) // 2
            # 固定左右两半的人数，只调整两数组各自贡献。
            j = left_size - i
            a_left = a[i - 1] if i else float('-inf')
            a_right = a[i] if i < m else float('inf')
            b_left = b[j - 1] if j else float('-inf')
            b_right = b[j] if j < n else float('inf')
            if a_left > b_right:
                high = i - 1
            elif b_left > a_right:
                low = i + 1
            else:
                if (m + n) % 2:
                    return float(max(a_left, b_left))
                return (max(a_left, b_left) + min(a_right, b_right)) / 2
        raise ValueError("arrays must be sorted")
