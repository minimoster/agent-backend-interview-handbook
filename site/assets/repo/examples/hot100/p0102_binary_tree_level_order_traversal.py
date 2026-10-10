"""102 · 二叉树的层序遍历：原创教学实现。"""
from collections import deque

class Solution:
    def levelOrder(self, root):
        if root is None:
            return []
        answer, queue = [], deque([root])
        while queue:
            level = []
            # range 在本层开始时冻结长度，新孩子留给下一层。
            for _ in range(len(queue)):
                node = queue.popleft()
                level.append(node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            answer.append(level)
        return answer
