"""226 · 翻转二叉树：原创教学实现。"""
class Solution:
    def invertTree(self, root):
        stack = [root] if root else []
        while stack:
            node = stack.pop()
            # 同时赋值保留两边旧引用，再继续处理它们。
            node.left, node.right = node.right, node.left
            if node.left:
                stack.append(node.left)
            if node.right:
                stack.append(node.right)
        return root
