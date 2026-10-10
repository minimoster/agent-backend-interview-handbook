"""105 · 从前序与中序遍历序列构造二叉树：原创教学实现。"""
from examples.hot100.structures import TreeNode

class Solution:
    def buildTree(self, preorder, inorder):
        if not preorder:
            return None
        root = TreeNode(preorder[0])
        stack, index = [root], 0
        for offset in range(1, len(preorder)):
            value = preorder[offset]
            parent = stack[-1]
            child = TreeNode(value)
            # 中序尚未轮到栈顶：它的左子树还未完成。
            if parent.val != inorder[index]:
                parent.left = child
            else:
                # 连续弹出已完成中序访问的祖先，找到右分支的父亲。
                while stack and stack[-1].val == inorder[index]:
                    parent = stack.pop()
                    index += 1
                parent.right = child
            stack.append(child)
        return root
