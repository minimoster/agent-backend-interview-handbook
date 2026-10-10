"""394 · 字符串解码：原创教学实现。"""
class Solution:
    def decodeString(self, s: str) -> str:
        stack = []
        parts = []
        repeat = 0
        for ch in s:
            if ch.isdigit():
                repeat = repeat * 10 + int(ch)
            # 遇到左括号，暂停并保存外层上下文。
            elif ch == '[':
                stack.append((parts, repeat))
                parts, repeat = [], 0
            elif ch == ']':
                block = ''.join(parts)
                parent, count = stack.pop()
                parent.append(block * count)
                parts = parent
            else:
                parts.append(ch)
        return ''.join(parts)
