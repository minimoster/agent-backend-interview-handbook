"""39 · 组合总和：原创教学实现。"""
class Solution:
    def combinationSum(self, candidates, target):
        values = sorted(candidates)
        answer, path = [], []
        def search(start, remain):
            if remain == 0:
                answer.append(path.copy())
                return
            for i in range(start, len(values)):
                value = values[i]
                # 排序后本项过大，后面的项也一定过大。
                if value > remain:
                    break
                path.append(value)
                # 仍传 i 允许重用当前数，同时保持下标非递减。
                search(i, remain - value)
                path.pop()
        search(0, target)
        return answer
