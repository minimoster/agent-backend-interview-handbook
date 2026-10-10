"""739 · 每日温度：原创教学实现。"""
class Solution:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:
        answer = [0] * len(temperatures)
        pending = []
        for day, value in enumerate(temperatures):
            # 第一次遇到更高温才弹出；相等温度继续等待。
            while pending and temperatures[pending[-1]] < value:
                earlier = pending.pop()
                answer[earlier] = day - earlier
            pending.append(day)
        return answer
