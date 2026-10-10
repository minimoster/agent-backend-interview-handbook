# 322. 零钱兑换

[官方题目](https://leetcode.cn/problems/coin-change/) · MEDIUM · 官方分类：动态规划

## 题意与接口

接口：`Solution.coinChange(coins: list[int], amount: int) -> int`。面额为正，每种硬币可无限使用，求凑出 amount 的最少硬币数；无法恰好凑出返回 −1。金额允许 0，至多 10⁴，面额列表非空且至多 12 项。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/coin-change/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

逐个尝试硬币的搜索有大量相同剩余金额。只保存每个金额的最少硬币数，每个状态枚举最后一枚硬币即可。不能假设大面额优先的贪心总正确。

## 核心思路

dp[0]=0；其余先设为 amount+1，作为不可能的数量。对于每个金额 value，枚举不超过它的 coin，用 dp[value−coin]+1 更新。所有硬币都至少为 1，所以合法方案至多用 amount 枚，哨兵不会与合法答案混淆。

## 手推一个小例子

取 coins=`[1, 3, 4]`、amount=6：
1. dp[1]=1，dp[2]=2。
2. dp[3]=1，dp[4]=1。
3. dp[5]=2。
4. dp[6]=min(dp[5]+1,dp[3]+1,dp[2]+1)=2，即 3+3。
若贪心先选 4，则还要两个 1，共 3 枚。

## 为什么正确

最优方案的最后一枚硬币必是某个 coin，前面的硬币要最优地凑出 value−coin，否则能减少总数量。因此枚举最后硬币覆盖所有最优候选；从可达前驱加一也一定产生合法方案。正面额保证前驱已计算，归纳得到最少数量。最终仍为哨兵说明不存在合法构造。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0322_coin_change.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def coinChange(self, coins: list[int], amount: int) -> int:
        unreachable = amount + 1
        dp = [0] + [unreachable] * amount
        for value in range(1, amount + 1):
            for coin in coins:
                if coin <= value:
                    # 正面额让前驱金额更小，可反复使用同一面额。
                    dp[value] = min(dp[value], dp[value - coin] + 1)
        return -1 if dp[amount] == unreachable else dp[amount]
```

## 复杂度

设 A 为 amount、k 为面额数，时间 O(Ak)，辅助空间 O(A)。这是关于数值 A 的伪多项式算法，不是关于 A 的二进制位数的多项式算法。

## 边界与易错点

- amount=0 返回 0，不能返回 −1。
- 面额可能大于目标金额，应跳过而不是负下标访问。
- 本实现不接受 0 或负面额，那会破坏官方契约和递推顺序。
- 不可达前驱加一不会小于哨兵，无需专门分支。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0322`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：为什么这里可以无限复用面额，而第 416 题必须防止复用同一个元素？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/coin-change/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0300-0399/0322.Coin%20Change/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0322.coin-change.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0322.coin-change.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[322. 零钱兑换](https://www.bilibili.com/video/BV14K411R7yv/)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：区分求最小硬币数与求组合数，检查目标为零和无法凑出的金额。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
