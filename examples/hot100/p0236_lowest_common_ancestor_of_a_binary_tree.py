"""236 · 二叉树的最近公共祖先：原创教学实现。"""
class Solution:
    def lowestCommonAncestor(self, root, p, q):
        if root is None:
            return None
        parent, stack = {root: None}, [root]
        while p not in parent or q not in parent:
            node = stack.pop()
            for child in (node.left, node.right):
                if child:
                    parent[child] = node
                    stack.append(child)
        ancestors = set()
        while p is not None:
            ancestors.add(p)
            p = parent[p]
        # 从 q 由深到浅找，首次命中即最深的公共祖先。
        while q not in ancestors:
            q = parent[q]
        return q
