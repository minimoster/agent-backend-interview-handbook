"""98 · 验证二叉搜索树：原创教学实现。"""
class Solution:
    def isValidBST(self, root):
        stack, cur, prev = [], root, None
        while cur or stack:
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            # BST 中序必须严格递增，重复值也应拒绝。
            if prev is not None and cur.val <= prev:
                return False
            prev = cur.val
            cur = cur.right
        return True
