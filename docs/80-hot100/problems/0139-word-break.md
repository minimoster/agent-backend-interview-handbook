# 139. 单词拆分

[官方题目](https://leetcode.cn/problems/word-break/) · MEDIUM · 官方分类：动态规划

## 题意与接口

接口：`Solution.wordBreak(s: str, wordDict: list[str]) -> bool`。判断能否用词典单词依次拼出整个 s，同一个词可重复使用。官方 s 长度 1 至 300；词典非空，单词长度 1 至 20，均为小写字母。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/word-break/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

枚举切分位置会重复判断同一后缀；动态规划只需记录每个前缀能否组成。与其对每个终点尝试全部此前位置，可只尝试词典中存在的长度，减少无用切分。

## 核心思路

`possible[end]` 表示半开前缀 s[:end] 能否拆分。possible[0]=真。对词长 length，若前缀 end−length 可拆，且最后一段 s[end−length:end] 在词典，则当前前缀可拆。词长排序后遇到 length>end 即可停止。

## 手推一个小例子

取 s=`"redbluered"`、词典 `["red", "blue"]`：
1. possible[0]=真。
2. end=3 时，空前缀加 `red`，possible[3]=真。
3. end=7 时，possible[3] 加 `blue`，possible[7]=真。
4. end=10 时，possible[7] 加 `red`，possible[10]=真。中间不对应完整词边界的前缀仍可为假。

## 为什么正确

任意有效拆分的最后一个词具有词典中的某种长度，其前方也是有效拆分，因此会被转移发现。反过来，一个可拆前缀后连接词典中的完整单词一定合法。空前缀是真正的递推基底，按终点递增处理后，末状态恰好表示整个字符串是否可拆。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0139_word_break.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def wordBreak(self, s: str, wordDict: list[str]) -> bool:
        words = set(wordDict)
        lengths = sorted({len(word) for word in words})
        possible = [False] * (len(s) + 1)
        possible[0] = True
        for end in range(1, len(s) + 1):
            for length in lengths:
                if length > end:
                    break
                start = end - length
                # 一个可拆前缀加一个完整词，构成新的可拆前缀。
                if possible[start] and s[start:end] in words:
                    possible[end] = True
                    break
        return possible[-1]
```

## 复杂度

设 n 为字符串长度，S 为词典总字符数，D 为不同词长集合，d=|D|，L 为最大词长。Python 切片及新子串哈希需要 O(length)，所以期望时间上界为 O(S+d log d+n·Σ_{ℓ∈D} ℓ)，也可写作 O(S+d log d+nL²)，不能简单写成 O(nL)。辅助空间 O(n+w+d+L)，其中 w 为词数，集合只保存原词的引用，L 计入临时切片。哈希查询使用通常的期望模型。

## 边界与易错点

- 不能贪心总选最长匹配词，例如 `s="abcd"`、词典 `["abc","ab","cd"]`。
- 词可以复用，不应从词典中删除用过的词。
- 切片按字符长度分配内存，不是 O(1)。
- possible[0] 为真只是递推需要；官方字符串本身非空。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0139`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：若要输出一种切分，如何记录前驱？若词典特别大，Trie 如何减少重复比较？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/word-break/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0139.Word%20Break/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/dynamic-programming/0139-word-break.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/dynamic-programming/0139-word-break.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[139. 单词拆分](https://www.bilibili.com/video/BV1pd4y147Rh/)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：定义前缀能否被切分，检查空前缀的初值与每次匹配单词后更新的结束位置。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
