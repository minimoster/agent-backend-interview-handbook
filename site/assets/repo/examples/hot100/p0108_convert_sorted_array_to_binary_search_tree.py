"""108 · 将有序数组转换为二叉搜索树：原创教学实现。"""
from examples.hot100.structures import TreeNode

class Solution:
    def sortedArrayToBST(self, nums):
        def build(lo, hi):
            if lo >= hi:
                return None
            # 用半开下标区间而非数组切片，左右规模尽量相等。
            mid = (lo + hi) // 2
            node = TreeNode(nums[mid])
            node.left = build(lo, mid)
            node.right = build(mid + 1, hi)
            return node
        return build(0, len(nums))
