"""46 · 全排列：原创教学实现。"""
class Solution:
    def permute(self, nums):
        answer, path = [], []
        used = [False] * len(nums)
        def search():
            if len(path) == len(nums):
                # 保存快照，否则后续撤销会改动已保存的答案。
                answer.append(path.copy())
                return
            for i, value in enumerate(nums):
                if used[i]:
                    continue
                used[i] = True
                path.append(value)
                search()
                # 撤销本层选择，允许下一候选复用这些位置。
                path.pop()
                used[i] = False
        search()
        return answer
