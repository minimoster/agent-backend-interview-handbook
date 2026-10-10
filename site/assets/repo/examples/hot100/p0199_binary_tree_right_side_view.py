"""199 · 二叉树的右视图：原创教学实现。"""
from collections import deque

class Solution:
    def rightSideView(self, root):
        if root is None:
            return []
        answer, queue = [], deque([root])
        while queue:
            width = len(queue)
            for i in range(width):
                node = queue.popleft()
                # 左孩子先入队，因此本层最后一项就是最右侧。
                if i == width - 1:
                    answer.append(node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
        return answer
