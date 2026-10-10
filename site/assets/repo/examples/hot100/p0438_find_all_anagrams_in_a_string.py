"""438 · 找到字符串中所有字母异位词：原创教学实现。"""
class Solution:
    def findAnagrams(self, s: str, p: str) -> list[int]:
        width = len(p)
        if width == 0 or width > len(s):
            return []  # 空模式是本地扩展约定，不在原题输入内
        wanted, window = [0] * 26, [0] * 26
        for ch in p:
            wanted[ord(ch) - 97] += 1
        answer = []
        for right, ch in enumerate(s):
            window[ord(ch) - 97] += 1
            # 移除左端过期字符，使窗口最多包含width个字符。
            if right >= width:
                window[ord(s[right - width]) - 97] -= 1
            if right >= width - 1 and window == wanted:
                answer.append(right - width + 1)
        return answer
