"""49 · 字母异位词分组：原创教学实现。"""
from collections import defaultdict

class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        # 26维计数保留重复次数，同时消除字母顺序。
        groups = defaultdict(list)
        for word in strs:
            counts = [0] * 26
            for ch in word:
                counts[ord(ch) - ord('a')] += 1
            groups[tuple(counts)].append(word)  # list 不能作字典键
        return list(groups.values())
