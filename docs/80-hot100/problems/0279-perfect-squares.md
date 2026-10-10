# 279. 完全平方数

[官方题目](https://leetcode.cn/problems/perfect-squares/) · MEDIUM · 官方分类：动态规划

## 题意与接口

接口：`Solution.numSquares(n: int) -> int`。把正整数 n 写成若干正完全平方数的和，平方数可重复，求最少项数。官方 n 为 1 至 10⁴。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/perfect-squares/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

搜索所有平方数拆分会大量重复求相同余数。令每个整数的最少拆分数成为一个状态，从小到大填表；正平方数总使前驱更小，因此计算次序清楚。

## 核心思路

`dp[value]` 表示总和为 value 的最少项数。最后一项可以是任意不超过 value 的平方数 q，于是 `dp[value] = min(dp[value-q]+1)`。设 dp[0]=0；预生成递增的平方数表，q 过大就停止枚举。

## 手推一个小例子

取 n=8：
1. 可用平方数为 1、4。
2. dp[1..3] 为 1、2、3。
3. dp[4]=1，因为能直接选 4。
4. dp[5]=2，dp[6]=3，dp[7]=4。
5. dp[8]=min(dp[7]+1,dp[4]+1)=2，对应 4+4。

## 为什么正确

任一和为 value 的方案，都有一个最后平方数 q；删除它后剩余 value−q。若剩余部分不是该值的最优拆分，就能替换并减少总项数，因此最优解必在转移候选中。反过来每个候选都能构造合法拆分。取最小得到正确状态，按 value 递增完成归纳。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0279_perfect_squares.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from math import isqrt


class Solution:
    def numSquares(self, n: int) -> int:
        squares = [root * root for root in range(1, isqrt(n) + 1)]
        dp = [0] + [n + 1] * n
        for value in range(1, n + 1):
            for square in squares:
                if square > value:
                    break
                # 枚举最后一项；较小金额的最优值已经确定。
                dp[value] = min(dp[value], dp[value - square] + 1)
        return dp[n]
```

## 复杂度

时间 O(n√n)，dp 空间 O(n)，平方数表 O(√n)，总体辅助空间 O(n)。`isqrt` 避免浮点开平方的取整误差。

## 边界与易错点

- 平方数可重复，不是 0/1 背包。
- 0 只是递推基底，不作为一个有用的平方数候选。
- 每次选尽量大的平方数会失败，例如 12 先选 9 后要三个 1，而三个 4 更优。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0279`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：为何平方数必须为正才使本计算顺序无环？把平方数换成任意正面额会得到哪道题？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/perfect-squares/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0279.Perfect%20Squares/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/dynamic-programming/0279-perfect-squares.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/dynamic-programming/0279-perfect-squares.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[279. 完全平方数](https://www.bilibili.com/video/BV12P411T7Br/)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：说明每个平方数可重复使用，检查最小次数的初始状态与不可达状态设置。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
