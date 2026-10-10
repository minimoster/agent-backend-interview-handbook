"""22 · 括号生成：原创教学实现。"""
class Solution:
    def generateParenthesis(self, n):
        answer, path = [], []
        def search(left, right):
            if len(path) == 2 * n:
                answer.append("".join(path))
                return
            if left < n:
                path.append("(")
                search(left + 1, right)
                path.pop()
            # 右括号只能关闭尚未配对的左括号。
            if right < left:
                path.append(")")
                search(left, right + 1)
                path.pop()
        search(0, 0)
        return answer
