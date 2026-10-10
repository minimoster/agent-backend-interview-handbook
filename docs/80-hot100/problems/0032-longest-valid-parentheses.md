# 32. 最长有效括号

[官方题目](https://leetcode.cn/problems/longest-valid-parentheses/) · HARD · 官方分类：动态规划

## 题意与接口

接口：`Solution.longestValidParentheses(s: str) -> int`。s 只含左右圆括号，求最长的连续、完整匹配括号片段的长度。官方允许空串，长度至多 3×10⁴。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/longest-valid-parentheses/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

枚举全部子串并逐一检查合法性最坏 O(n³)。改为固定右端，记录“恰在该位置结束”的最长合法长度，便可跳过已经匹配的一整段，直接寻找当前右括号的配对位置。

## 核心思路

令 dp[i] 为以 i 结尾的最长合法长度。左括号处一定为 0。若 s[i] 为右括号，先跨过紧邻前方的合法段 dp[i−1]，候选配对位置为 j=i−dp[i−1]−1。若 j≥0 且 s[j] 是左括号，就得到 dp[i−1]+2，并可再连接 j 左侧的 dp[j−1]。

## 手推一个小例子

取 `s="()(())"`：
1. i=1，j=0，匹配成 `()`，dp[1]=2。
2. i=2、3 都是左括号，状态为 0。
3. i=4，j=3，得到内部 `()`，dp[4]=2。
4. i=5，跨过前面的长度 2，j=2；本对包住内部串得到 4，再接 dp[1]=2，最终 dp[5]=6。

## 为什么正确

任何以右括号 i 结尾的合法串，其配对左括号 j 与 i 之间必须是合法串。前一位置的最长合法后缀可整体跨过；若它左边存在左括号，就能把这段包裹成更长合法串，再与 j−1 结尾的最长合法串拼接。若候选左侧越界或为右括号，则无法构造以 i 结尾的合法串。递推按右端递增，每个依赖已经正确；取所有终点最大值即为答案。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0032_longest_valid_parentheses.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def longestValidParentheses(self, s: str) -> int:
        dp = [0] * len(s)
        best = 0
        for i in range(1, len(s)):
            if s[i] != ')':
                continue
            # 跨过紧邻的完整合法段，再寻找能够包住它的左括号。
            opening = i - dp[i - 1] - 1
            if opening >= 0 and s[opening] == '(':
                dp[i] = dp[i - 1] + 2
                if opening > 0:
                    dp[i] += dp[opening - 1]
                best = max(best, dp[i])
        return best
```

## 复杂度

时间 O(n)，辅助空间 O(n)。也可用带哨兵的下标栈；双向计数扫描可进一步做到 O(1) 辅助空间，但需要分别解释未匹配左右括号的处理。

## 边界与易错点

- 空串和单个括号返回 0。
- j 必须先检查非负，Python 负下标不会自动报错，反而会取到尾部。
- 不要漏掉连接 j 左侧的合法段，否则 `()()` 只能算到 2。
- 目标是子串，不能删除中间无效括号把两段凑起来。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0032`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：在 `()(())` 中，只写 dp[i−1]+2 为什么不够？试手推 `())(())`。

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/longest-valid-parentheses/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0032.Longest%20Valid%20Parentheses/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：用嵌套、连续有效段和开头多余右括号检查状态或哨兵，说明答案为何要求连续。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
