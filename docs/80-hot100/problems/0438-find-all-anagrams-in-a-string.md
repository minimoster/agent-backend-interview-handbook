# 438. 找到字符串中所有字母异位词

难度：MEDIUM · 分类：滑动窗口

## 题意与接口

找出s中所有与p字符计数相同的连续子串起点。`findAnagrams(s,p)` 返回下标列表；题设两个串只含小写英文字母，p非空。

## 从朴素方法到优化

每个长度为m的窗口重新排序需要 O(nm log m)。相邻窗口只差一个移出和一个移入字符，可直接维护26维频次。

## 核心思路

窗口长度固定为m=len(p)。每轮加入s[right]，长度过大时减掉s[right-m]；当计数向量等于目标且窗口已满，记录right-m+1。

## 手推一个小例子

s="babaac"，p="aab"。窗口"bab"计数不符；"aba"匹配下标1；"baa"匹配下标2；"aac"不匹配，所以输出[1,2]。

## 为什么正确

每轮更新后计数恰好描述以right结尾、最多m个字符的窗口。两个等长串是异位词当且仅当各字符计数相同；检查每个满窗即可不重不漏枚举起点。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0438_find_all_anagrams_in_a_string.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def findAnagrams(self, s: str, p: str) -> list[int]:
        width = len(p)
        if width == 0 or width > len(s):
            return []  # 空模式是本地扩展约定，不在原题输入内
        wanted, window = [0] * 26, [0] * 26
        for ch in p:
            wanted[ord(ch) - 97] += 1
        answer = []
        for right, ch in enumerate(s):
            window[ord(ch) - 97] += 1
            # 移除左端过期字符，使窗口最多包含width个字符。
            if right >= width:
                window[ord(s[right - width]) - 97] -= 1
            if right >= width - 1 and window == wanted:
                answer.append(right - width + 1)
        return answer
```

## 复杂度

时间 O(26n+m)，固定字符表下为O(n+m)。辅助空间 O(26)，输出O(r)。比较两个26长列表不是一般意义的O(1)，是这里字母表固定后的常数。

## 边界与易错点

- 先移除过期字符再判断，避免比较m+1长窗口。
- 重复字符必须比较次数，仅比较字符集合会错。
- p比s长时没有候选窗口。

## 本地测试与复习

测试重复字母、重叠命中、模式更长；随机与逐窗口排序比较对拍。

复习：若字符表极大，如何用差值计数和“非零差种数”避免每次全表比较？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：先明确窗口长度与频次差，再检查重复字符、短输入和每次移出移入的更新顺序。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
