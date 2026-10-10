"""763 · 划分字母区间：原创教学实现。"""
class Solution:
    def partitionLabels(self, s: str) -> list[int]:
        last = {char: i for i, char in enumerate(s)}
        lengths = []
        start = end = 0
        for i, char in enumerate(s):
            # 本段必须覆盖已读字符的所有后续出现。
            end = max(end, last[char])
            if i == end:
                lengths.append(end - start + 1)
                start = i + 1
        return lengths
