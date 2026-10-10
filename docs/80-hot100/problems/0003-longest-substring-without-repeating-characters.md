# 3. 无重复字符的最长子串

[官方题目](https://leetcode.cn/problems/longest-substring-without-repeating-characters/) · MEDIUM · 官方分类：滑动窗口

## 题意与接口

求字符串中没有重复字符的最长连续片段长度。`lengthOfLongestSubstring(s)` 返回长度；这里按Python字符处理，字符串不修改。

## 从朴素方法到优化

枚举每个起点再扩张，最坏 O(n²)。滑动窗口遇到重复时，重复字符上一次出现的位置可以直接告诉我们左端至少应移动到哪里。

## 核心思路

last记录字符最近下标；窗口左端left只向右移动。读到字符ch时，把left更新为max(left,last[ch]+1)，再记录当前下标并计算窗口长度。

## 手推一个小例子

"dvdf"：窗口依次为"d"、"dv"；第二个d在下标2，left跳到1，窗口变"vd"；读f得到"vdf"，最大长度3。

## 为什么正确

更新left后，当前字符在窗口内没有旧副本；其余字符在上一个合法窗口中已互异，缩短窗口不会引入重复。left取满足条件的最小可用位置，所以当前窗口是以当前右端结束的最长合法窗口。遍历全部右端即可得到全局最优。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0003_longest_substring_without_repeating_characters.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        last = {}
        left = best = 0
        for right, ch in enumerate(s):
            # 历史位置可能已在窗外，left绝不能倒退。
            left = max(left, last.get(ch, -1) + 1)
            last[ch] = right
            best = max(best, right - left + 1)
        return best
```

## 复杂度

平均时间 O(n)，辅助空间 O(min(n,Σ))，Σ为可能出现的字符种数。

## 边界与易错点

- "abba"读最后a时，left不能从2退回1；max不可省。
- 求连续子串，不是可跳过字符的子序列。
- 空串返回0，空格也属于普通字符。

## 本地测试与复习

测试空串、"abba"、全同字符、Unicode；随机与逐起点集合扩张对拍。

复习：写出窗口无重复这个不变量；为什么不必从字典删除窗口外字符？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/longest-substring-without-repeating-characters/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0003.Longest%20Substring%20Without%20Repeating%20Characters/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0003.longest-substring-without-repeating-characters.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0003.longest-substring-without-repeating-characters.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：重复字符出现在窗口外时，左边界为什么不能退回去？手推最近位置表与左边界的更新。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
