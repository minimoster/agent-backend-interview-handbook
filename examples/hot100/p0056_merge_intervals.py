"""56 · 合并区间：原创教学实现。"""
class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        merged = []
        for start, end in sorted(intervals):
            # 排序后仅最后一段可能与当前区间重叠。
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)
        return merged
