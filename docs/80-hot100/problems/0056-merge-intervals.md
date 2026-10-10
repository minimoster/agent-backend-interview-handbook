# 56. 合并区间

[官方题目](https://leetcode.cn/problems/merge-intervals/) · MEDIUM · 官方分类：普通数组

## 题意与接口

将有交集的闭区间合并，返回互不重叠的区间集合。`merge(intervals)` 返回新列表及新子列表，不修改输入；端点相接也算重叠。

## 从朴素方法到优化

反复两两查找可合并区间会做大量重复比较。按左端排序后，只需把新区间与已合并结果的最后一个比较。

## 核心思路

若新区间左端大于最后区间右端，开始新组；否则两区间相交，右端更新为二者最大值。先复制端点，避免结果与输入子列表共享导致意外修改。

## 手推一个小例子

[[5,7],[1,3],[3,6],[9,9]]排序后为[1,3],[3,6],[5,7],[9,9]。前两段接触合成[1,6]，再合到[1,7]；最后9在7之外，得到[[1,7],[9,9]]。

## 为什么正确

处理到当前区间时，之前结果按起点有序且互不重叠。新区间起点不小于所有旧起点，只有最后区间可能与之重叠；若连最后区间都够不到，更早区间也不可能够到。合并取最远右端保持覆盖范围不变。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0056_merge_intervals.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        merged = []
        for start, end in sorted(intervals):
            # 排序后仅最后一段可能与当前区间重叠。
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)
        return merged
```

## 复杂度

时间 O(n log n)，排序副本及排序工作空间O(n)，输出O(n)。

## 边界与易错点

- 闭区间[1,3]与[3,4]要合并，分离条件是>而不是≥。
- 区间可能完全被上一段包含，右端必须max而非直接覆盖。
- 代码不修改输入；原地排序变体的副作用须另行说明。

## 本地测试与复习

测试端点相接、嵌套、乱序、单点；随机用独立反复两两合并算法对拍。

复习：如果区间是半开区间且仅相接不算重叠，判断条件怎样改？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/merge-intervals/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0056.Merge%20Intervals/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0056.merge-intervals.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0056.merge-intervals.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[56. 合并区间](https://www.bilibili.com/video/BV1wx4y157nD)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：排序后手推包含区间、接触端点和不相交区间，说明合并时右端点为何取最大值。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
