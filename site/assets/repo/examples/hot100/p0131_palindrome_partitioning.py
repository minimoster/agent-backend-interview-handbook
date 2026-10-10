"""131 · 分割回文串：原创教学实现。"""
class Solution:
    def partition(self, s):
        n = len(s)
        pal = [[False] * n for _ in range(n)]
        # i 递减保证内区间 pal[i+1][j-1] 已求出。
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i+1][j-1])
        answer, path = [], []
        def search(start):
            if start == n:
                answer.append(path.copy())
                return
            for end in range(start, n):
                # 只沿回文片段切一刀，回文查询本身 O(1)。
                if pal[start][end]:
                    path.append(s[start:end+1])
                    search(end + 1)
                    path.pop()
        search(0)
        return answer
