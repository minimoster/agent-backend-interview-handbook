"""437 · 路径总和 III：原创教学实现。"""
class Solution:
    def pathSum(self, root, targetSum):
        freq, answer = {0: 1}, 0
        stack = [(root, 0, False)] if root else []
        while stack:
            node, total, exiting = stack.pop()
            # 离开时撤销前缀，保证频次表只描述当前祖先路径。
            if exiting:
                freq[total] -= 1
                if freq[total] == 0:
                    del freq[total]
                continue
            total += node.val
            # 先查后加入，避免 target=0 时统计空路径。
            answer += freq.get(total - targetSum, 0)
            freq[total] = freq.get(total, 0) + 1
            stack.append((node, total, True))
            if node.right:
                stack.append((node.right, total, False))
            if node.left:
                stack.append((node.left, total, False))
        return answer
