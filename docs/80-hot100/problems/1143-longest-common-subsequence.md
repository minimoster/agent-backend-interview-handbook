# 1143. 最长公共子序列

[官方题目](https://leetcode.cn/problems/longest-common-subsequence/) · MEDIUM · 官方分类：多维动态规划

## 题意与接口

接口：`Solution.longestCommonSubsequence(text1: str, text2: str) -> int`。求两串最长公共子序列长度；字符可跳过，但相对顺序必须保留。官方两串长度各为 1 至 1000，均为小写字母。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/longest-common-subsequence/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

枚举一串的全部子序列再检查另一串代价指数级。用两个前缀长度作为状态：最后字符相同则共同匹配；不同则舍弃其中一端。二维表需要 O(mn) 空间，滚动一行可进一步减少。

## 核心思路

令 D(i,j) 为 text1[:i]、text2[:j] 的 LCS 长度。字符相等时取 D(i−1,j−1)+1，否则取 max(D(i−1,j),D(i,j−1))。一维 dp 保存旧行，`diagonal` 保存旧左上角；从左到右更新时 dp[j−1] 已是当前行。让短串作为列，可用 O(min(m,n)) 空间。

## 手推一个小例子

取 text1=`"axby"`、text2=`"aby"`，列前缀为 `""`、a、ab、aby：
1. 空行 `[0,0,0,0]`。
2. 读 a 后 `[0,1,1,1]`。
3. 读 x 后仍 `[0,1,1,1]`。
4. 读 b 后 `[0,1,2,2]`。
5. 读 y 后 `[0,1,2,3]`，答案 3。

## 为什么正确

若末字符不同，一个公共子序列不能同时使用这两个末字符，因此至少舍弃一边，最优值是两个较短前缀状态的最大值。若末字符相同，存在最优公共子序列以这对字符结尾：可以把最后一次使用的同字符挪到两个末尾而不破坏先前顺序；若完全未用它，则可追加并变长。删除共同末字符后得到左上状态，所以加一。空前缀为 0，滚动变量保存了全部所需旧值。

## Python 实现

[完整可导入源码](../../../examples/hot100/p1143_longest_common_subsequence.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        if len(text1) < len(text2):
            text1, text2 = text2, text1
        dp = [0] * (len(text2) + 1)
        for first in text1:
            diagonal = 0
            for column, second in enumerate(text2, 1):
                above = dp[column]  # 覆盖前先保存，供下一列作左上角。
                if first == second:
                    dp[column] = diagonal + 1
                else:
                    dp[column] = max(above, dp[column - 1])
                diagonal = above
        return dp[-1]
```

## 复杂度

时间 O(mn)，辅助空间 O(min(m,n))。只交换字符串引用，不复制字符串。

## 边界与易错点

- 求子序列而非子串，字符不相等时不能把状态清零。
- diagonal 必须在覆盖 dp[column] 前保存旧值。
- 同字符出现多次仍需保持顺序，集合交集不能解决本题。
- 官方输入非空；代码也自然支持空串，测试会把它标作扩展行为。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p1143`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：如果需要返回一个 LCS，单行长度表还够吗？最长公共子串的转移与此有何不同？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/longest-common-subsequence/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/1100-1199/1143.Longest%20Common%20Subsequence/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/1143.longest-common-subsequence.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/1143.longest-common-subsequence.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[1143. 最长公共子序列](https://www.bilibili.com/video/BV1ye4y1L7CQ)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：定义两个前缀上的 DP，比较末字符相等与不等时的转移；区分子序列与连续子串。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
