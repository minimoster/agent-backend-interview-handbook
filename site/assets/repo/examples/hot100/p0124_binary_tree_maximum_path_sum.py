"""124 · 二叉树中的最大路径和：原创教学实现。"""
class Solution:
    def maxPathSum(self, root):
        if root is None:
            raise ValueError("the problem requires a non-empty tree")
        gains, best = {}, float("-inf")
        stack = [(root, False)]
        while stack:
            node, expanded = stack.pop()
            if not expanded:
                stack.append((node, True))
                if node.right:
                    stack.append((node.right, False))
                if node.left:
                    stack.append((node.left, False))
            else:
                left = max(0, gains.get(node.left, 0))
                right = max(0, gains.get(node.right, 0))
                # 完整路径能接两边，但向父亲延伸只能保留一边。
                best = max(best, node.val + left + right)
                gains[node] = node.val + max(left, right)
        return best
