# 739. 每日温度

[官方题目](https://leetcode.cn/problems/daily-temperatures/) · MEDIUM · 官方分类：栈

## 题意与接口

每一天给一个温度，求要等几天才会出现更高温度；没有则记0。`dailyTemperatures(temperatures)`返回等待天数列表。

## 从朴素方法到优化

每一天向后扫描最坏O(n²)。新的一天可以一次解决若干较冷旧天；尚未找到更高温的候选适合维护单调栈。

## 核心思路

栈存下标，对应温度从底到顶非递增。新温度严格更高时反复弹栈，为旧下标写入当前下标差，然后当前下标入栈。

## 手推一个小例子

[68,70,69,73]：读70时弹下标0，等待1天；69入栈；73先弹下标2，等待1天，再弹下标1，等待2天；最后答案[1,2,1,0]。

## 为什么正确

一个旧下标留在栈中说明此前尚未出现更高温度。当前温度首次把它弹出，所以当前正是最近的更高温日。栈中被更高温阻挡的较早低温项会在同一while中继续被解决，最终每项要么找到首个答案要么保持0。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0739_daily_temperatures.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
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
```

## 复杂度

时间O(n)，每个下标入栈出栈至多一次。辅助栈O(n)，输出O(n)。

## 边界与易错点

- 要求严格更高，相等温度不能弹出。
- 栈存下标才能算距离；只存温度不够。
- 结束后没被解决的下标答案应维持0。

## 本地测试与复习

测试相等、递增、递减与末天；随机与逐日向后搜索对拍。

复习：如果要求“不低于”而不是“更高”，比较符号怎样改？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/daily-temperatures/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0700-0799/0739.Daily%20Temperatures/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0739.daily-temperatures.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0739.daily-temperatures.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[739. 每日温度](https://www.bilibili.com/video/BV1my4y1Z7jj/)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：单调栈保存待求答案的下标；用相同温度检查弹出条件是否必须严格升温。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
