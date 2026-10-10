"""230 · 二叉搜索树中第 K 小的元素：原创教学实现。"""
class Solution:
    def kthSmallest(self, root, k):
        stack, cur = [], root
        while cur or stack:
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            # 弹栈即完成下一次中序访问，排名从 1 开始。
            k -= 1
            if k == 0:
                return cur.val
            cur = cur.right
        raise ValueError("k must be within the tree size")
