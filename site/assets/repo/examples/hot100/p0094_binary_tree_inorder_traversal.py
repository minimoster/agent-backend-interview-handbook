"""94 · 二叉树的中序遍历：原创教学实现。"""
class Solution:
    def inorderTraversal(self, root):
        answer, stack, cur = [], [], root
        while cur or stack:
            # 保存返回路径，等左子树处理完才访问当前节点。
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            answer.append(cur.val)
            cur = cur.right
        return answer
