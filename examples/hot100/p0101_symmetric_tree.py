"""101 · 对称二叉树：原创教学实现。"""
from collections import deque

class Solution:
    def isSymmetric(self, root):
        if root is None:
            return True
        queue = deque([(root.left, root.right)])
        while queue:
            a, b = queue.popleft()
            if a is None and b is None:
                continue
            if a is None or b is None or a.val != b.val:
                return False
            # 镜像比较必须交叉配对，空位置也参与结构检查。
            queue.append((a.left, b.right))
            queue.append((a.right, b.left))
        return True
