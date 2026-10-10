"""78 · 子集：原创教学实现。"""
class Solution:
    def subsets(self, nums):
        answer, path = [], []
        def search(start):
            answer.append(path.copy())
            for i in range(start, len(nums)):
                path.append(nums[i])
                # 下标严格递增，避免把同一子集的不同顺序重复输出。
                search(i + 1)
                path.pop()
        search(0)
        return answer
