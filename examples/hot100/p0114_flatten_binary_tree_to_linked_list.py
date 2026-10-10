"""114 · 二叉树展开为链表：原创教学实现。"""
class Solution:
    def flatten(self, root) -> None:
        cur = root
        while cur:
            if cur.left:
                predecessor = cur.left
                while predecessor.right:
                    predecessor = predecessor.right
                # 原右子树接到左子树末端，保留先序的左右相对顺序。
                predecessor.right = cur.right
                cur.right = cur.left
                cur.left = None
            cur = cur.right
