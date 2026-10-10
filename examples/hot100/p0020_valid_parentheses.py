"""20 · 有效的括号：原创教学实现。"""
class Solution:
    def isValid(self, s: str) -> bool:
        matching = {')': '(', ']': '[', '}': '{'}
        # 栈顶是最近一个尚未闭合的左括号。
        stack = []
        for ch in s:
            if ch in '([{':
                stack.append(ch)
            elif ch not in matching or not stack or stack.pop() != matching[ch]:
                return False
        return not stack
