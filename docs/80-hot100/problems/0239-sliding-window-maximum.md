# 239. 滑动窗口最大值

难度：HARD · 分类：子串

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

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：解释队列为何保存下标；分别检查过期元素、相等元素与队尾淘汰的条件。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
