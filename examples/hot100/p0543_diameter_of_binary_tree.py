"""543 · 二叉树的直径：原创教学实现。"""
class Solution:
    def diameterOfBinaryTree(self, root):
        if root is None:
            return 0
        heights, best = {}, 0
        stack = [(root, False)]
        while stack:
            node, expanded = stack.pop()
            if not expanded:
                # 压入退出状态；左右孩子会先于它被弹出。
                stack.append((node, True))
                if node.right:
                    stack.append((node.right, False))
                if node.left:
                    stack.append((node.left, False))
            else:
                left = heights.get(node.left, 0)
                right = heights.get(node.right, 0)
                # 高度按节点数计，两侧高度之和恰是路径边数。
                best = max(best, left + right)
                heights[node] = 1 + max(left, right)
        return best
