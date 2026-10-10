"""104 · 二叉树的最大深度：原创教学实现。"""
class Solution:
    def maxDepth(self, root):
        if root is None:
            return 0
        best, stack = 0, [(root, 1)]
        while stack:
            node, depth = stack.pop()
            # 孩子携带父深度加一，不依赖 Python 递归调用栈。
            best = max(best, depth)
            if node.left:
                stack.append((node.left, depth + 1))
            if node.right:
                stack.append((node.right, depth + 1))
        return best
