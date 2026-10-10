"""207 · 课程表：原创教学实现。"""
from collections import deque

class Solution:
    def canFinish(self, numCourses, prerequisites):
        graph = [[] for _ in range(numCourses)]
        indegree = [0] * numCourses
        for course, before in prerequisites:
            # 边从先修课程指向后续课程。
            graph[before].append(course)
            indegree[course] += 1
        queue = deque(i for i, degree in enumerate(indegree) if degree == 0)
        completed = 0
        while queue:
            before = queue.popleft()
            completed += 1
            for course in graph[before]:
                indegree[course] -= 1
                # 只在最后一个前置条件消失时入队。
                if indegree[course] == 0:
                    queue.append(course)
        return completed == numCourses
