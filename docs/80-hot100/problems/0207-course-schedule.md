# 207. 课程表

[官方题目](https://leetcode.cn/problems/course-schedule/) · MEDIUM · 官方分类：图论

## 题意与接口

有 numCourses 门课；每对 `[a,b]` 表示学 a 前必须学 b。判断能否完成全部课程。接口：`canFinish(numCourses, prerequisites)`。

约束核对（2026-10-09）：课程数 1..2000，先修对最多 5000 且不重复；[a,b] 表示 b 是 a 的先修。 [官方来源](https://leetcode.com/problems/course-schedule/)

## 从朴素方法到优化

逐个尝试所有课程排列代价阶乘。先修关系构成有向图，能完成等价于无有向环；拓扑排序通过反复删除入度为 0 的点判断。

## 核心思路

建边 b→a，统计每门课的入度。初始所有零入度课程入队；弹出一课后令所有后续课程入度减一，新变成 0 的入队。最终处理数等于课程总数才成功。

## 手推一个小例子

4 门课，依赖 `[1,0],[2,0],[3,1],[3,2]`。开始仅 0 可学；学完后 1、2 可学；两者都完成后 3 入度变 0，共处理 4 门，返回 True。若加 `[0,3]` 则形成环，无起点。

## 为什么正确

每次删除的零入度节点没有未完成前置课，可以安全学习。若剩余图无零入度点，沿前驱不断走必在有限图中重复节点，即存在环；反之有环时环内课程不会先变为零入度，无法全部处理。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0207_course_schedule.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
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
```

## 复杂度

时间 O(V+E)，辅助空间 O(V+E)，V 为课程数，E 为先修关系数。

## 边界与易错点

边方向是先修课指向后续课。无依赖的孤立课程也要入队并计数。自环一定失败；互相依赖也是环。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为何删除零入度点不会制造新的环？如果要输出学习顺序，在哪一步记录？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/course-schedule/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0207.Course%20Schedule/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/other/0207-course-schedule.html)
- 官方Python：本次读取的匹配题页未发现Python实现区；本页原有Python答案仍可独立使用。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。
- 匹配说明：官方补充页是简短的拓扑排序BFS说明，Python区和视频直链在本次读取中均未找到。

自主复习提示：逐条解释先修关系的边方向、入度更新和出队计数，再用一个有环图检查判定条件。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
