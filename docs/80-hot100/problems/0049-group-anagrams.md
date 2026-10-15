# 49. 字母异位词分组

难度：MEDIUM · 分类：哈希

## 题意与接口

把由小写英文字母组成的字符串按“字符出现次数完全相同”分组。`groupAnagrams(strs)` 返回若干字符串列表，组间及组内顺序不影响答案；输入不修改。

## 从朴素方法到优化

逐一把新字符串与已有组代表比较，会反复数相同字符。排序字符串可形成规范键，单词长 L 时 O(L log L)；固定26字符表可以直接计数到 O(L)。

## 核心思路

用26位计数元组作哈希键。字符顺序被消除，字符种类与次数保留；同键的原字符串放入同一列表。

## 手推一个小例子

输入["ab", "cab", "ba", "abc"]。"ab"与"ba"的键都是(a:1,b:1)，进入同组；"cab"与"abc"的键都是(a:1,b:1,c:1)，进入另一组。

## 为什么正确

两个字符串是异位词，当且仅当每个字母的计数相等。元组键精确表达这个条件，因此既不会把不匹配字符串合并，也不会把匹配字符串拆散。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0049_group_anagrams.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from collections import defaultdict

class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        # 26维计数保留重复次数，同时消除字母顺序。
        groups = defaultdict(list)
        for word in strs:
            counts = [0] * 26
            for ch in word:
                counts[ord(ch) - ord('a')] += 1
            groups[tuple(counts)].append(word)  # list 不能作字典键
        return list(groups.values())
```

## 复杂度

设 N 为单词数，S 为总字符数，G 为组数。时间 O(S+26N)，哈希键辅助空间 O(26G)，输出保存 N 个字符串引用。计数数组每次 O(26)。

## 边界与易错点

- 空字符串使用全零键，应正常成组。
- 本实现依赖题设小写英文字母；通用Unicode需改用排序或字典计数。
- 不要把集合当键："a"和"aa"的集合相同、计数不同。

## 本地测试与复习

测试空串、重复词、不同长度；把各组内部及组之间排序后，与独立排序键分组结果对拍。

复习：排序键与计数键何时各自更合适？如何测试输出顺序不固定的题？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：说明分组键怎样表达字符的多重集合；若字符范围扩大，计数元组和排序字符串各有什么代价？

[算法基础补充题库](../../85-algorithm-supplement/README.md)
