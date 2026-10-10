"""295 · 数据流的中位数：原创教学实现。"""
import heapq

class MedianFinder:
    def __init__(self):
        self.lower = []  # 存负数，根的相反数为左半最大值
        self.upper = []

    def addNum(self, num: int) -> None:
        # 先修复两堆数值顺序，再修复人数差。
        heapq.heappush(self.lower, -num)
        heapq.heappush(self.upper, -heapq.heappop(self.lower))
        if len(self.upper) > len(self.lower):
            heapq.heappush(self.lower, -heapq.heappop(self.upper))

    def findMedian(self) -> float:
        if not self.lower:
            raise ValueError("no values added")
        if len(self.lower) > len(self.upper):
            return float(-self.lower[0])
        return (-self.lower[0] + self.upper[0]) / 2
