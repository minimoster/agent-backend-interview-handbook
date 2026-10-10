# 239. 滑动窗口最大值

[官方题目](https://leetcode.cn/problems/sliding-window-maximum/) · HARD · 官方分类：子串

## 题意与接口

对长度为k的滑动窗口，依次返回每个窗口的最大值。`maxSlidingWindow(nums,k)` 返回数组，合法k满足1≤k≤n。

## 从朴素方法到优化

每窗调用max需 O(nk)。堆可以懒删除过期项但通常 O(n log n)；单调队列能丢弃“值更小且更早过期”的无用候选，降为线性。

## 核心思路

双端队列保存下标，对应值严格递减。新数进入前弹掉队尾不大于它的旧数；队头过期则移除。窗口满后，队头就是最大值。

## 手推一个小例子

[4,1,3,2]，k=2。读4队列[0]；读1为[0,1]，输出4；读3时0过期且1不如3，队列[2]，输出3；读2队列[2,3]，输出3。

## 为什么正确

被新元素从队尾淘汰的旧元素，数值不更大且更早离窗，此后任何包含旧元素的窗口也包含新元素，所以旧元素永不需要成为答案。有效候选按值递减，队头自然是当前最大值；下标递增保证过期项只在头部。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0239_sliding_window_maximum.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from collections import deque

class Solution:
    def maxSlidingWindow(self, nums: list[int], k: int) -> list[int]:
        if k <= 0 or k > len(nums):
            return []  # 题设外输入的本地约定
        candidates = deque()
        answer = []
        for right, value in enumerate(nums):
            while candidates and candidates[0] <= right - k:
                candidates.popleft()
            # 新值更大且更晚过期，旧的较小候选不再可能最优。
            while candidates and nums[candidates[-1]] <= value:
                candidates.pop()
            candidates.append(right)
            if right >= k - 1:
                answer.append(nums[candidates[0]])
        return answer
```

## 复杂度

时间 O(n)：每个下标入队一次、出队至多一次。辅助空间 O(k)，输出O(n-k+1)。

## 边界与易错点

- 必须存下标，才能识别相同数值中哪个已过期。
- 离窗条件为index≤right-k。
- 普通list.pop(0)是O(k)，应使用deque.popleft。

## 本地测试与复习

测试k=1、k=n、递增、递减、相等；随机与切片max对拍。

复习：从队尾删相等值为什么安全？单调递减输入为什么会让队列达到长度k？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/sliding-window-maximum/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0239.Sliding%20Window%20Maximum/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/stack-queue/0239-sliding-window-maximum.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/stack-queue/0239-sliding-window-maximum.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[239. 滑动窗口最大值](https://www.bilibili.com/video/BV1XS4y1p7qj)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：解释队列为何保存下标；分别检查过期元素、相等元素与队尾淘汰的条件。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
