"""139 · 单词拆分：原创教学实现。"""
class Solution:
    def wordBreak(self, s: str, wordDict: list[str]) -> bool:
        words = set(wordDict)
        lengths = sorted({len(word) for word in words})
        possible = [False] * (len(s) + 1)
        possible[0] = True
        for end in range(1, len(s) + 1):
            for length in lengths:
                if length > end:
                    break
                start = end - length
                # 一个可拆前缀加一个完整词，构成新的可拆前缀。
                if possible[start] and s[start:end] in words:
                    possible[end] = True
                    break
        return possible[-1]
