# 76. 最小覆盖子串

[官方题目](https://leetcode.cn/problems/minimum-window-substring/) · HARD · 官方分类：子串

## 题意与接口

在s中找一个最短连续片段，覆盖t要求的所有字符和重复次数。`minWindow(s,t)` 返回该片段；无解返回空串，输入不修改。

## 从朴素方法到优化

枚举所有子串再核对频次十分昂贵。窗口右端扩张取得覆盖后，只要仍合法就左缩；这样每个边界只移动一次。

## 核心思路

need保存每种目标字符还缺多少，missing表示总共还缺多少个字符。加入一个仍短缺的字符才减少missing；missing为0时尝试记录并缩窗，直到移出了一个必需字符。

## 手推一个小例子

s="caxbaad"，t="aab"。右端到下标4时窗口"caxba"已覆盖；去掉c后得到"axba"，再去掉a就不足。读到下标5的a后再次覆盖，缩掉x得到更短"baa"；再删b会失效，最短答案就是"baa"。

## 为什么正确

扩张不会破坏覆盖，缩小时第一次失效前访问到以当前右端结束的最短合法窗口。所有全局最短答案都有某个右端，因此逐一保留最短候选不会漏解。负的need只是富余数量，不能被误算为欠缺。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0076_minimum_window_substring.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from collections import Counter

class Solution:
    def minWindow(self, s: str, t: str) -> str:
        if not t:
            return ""
        need = Counter(t)
        missing = len(t)
        left = best_left = 0
        best_length = len(s) + 1
        for right, ch in enumerate(s):
            # 仅当此前仍短缺该字符时，missing才真正减少。
            if need[ch] > 0:
                missing -= 1
            need[ch] -= 1
            while missing == 0:
                if right - left + 1 < best_length:
                    best_left, best_length = left, right - left + 1
                outgoing = s[left]
                need[outgoing] += 1
                if need[outgoing] > 0:
                    missing += 1
                left += 1
        if best_length > len(s):
            return ""
        return s[best_left:best_left + best_length]
```

## 复杂度

平均时间 O(n+m)，其中n=len(s)、m=len(t)，最后切片O(答案长度)。辅助字典含s与t出现字符，空间O(Σ)；输出为一个新字符串。

## 边界与易错点

- t里两个相同字母意味着必须覆盖两次，不能只算字符种类。
- 更新缺口与缩窗的先后必须一致。
- 在每次合法窗口都切片会放大复制成本；代码只保存边界并最终切片。

## 本地测试与复习

测试重复需求、无法覆盖、目标比源长；随机穷举所有子串验证最短长度和覆盖，允许多个同长最优答案。

复习：need为负是什么意思？为什么“找到第一个覆盖就返回”不能保证最短？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/minimum-window-substring/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0076.Minimum%20Window%20Substring/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0076.minimum-window-substring.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0076.minimum-window-substring.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：先定义“已满足”统计的是字符种类还是出现次数，再手推窗口刚满足和刚失效的两次更新。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
