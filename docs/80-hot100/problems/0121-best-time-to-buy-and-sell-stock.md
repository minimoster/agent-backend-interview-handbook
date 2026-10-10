# 121. 买卖股票的最佳时机

[官方题目](https://leetcode.cn/problems/best-time-to-buy-and-sell-stock/) · EASY · 官方分类：贪心算法

## 题意与接口

接口：`Solution.maxProfit(prices: list[int]) -> int`。价格按日期排列，只能先买后卖，最多完成一次交易，求最大利润；没有赚钱机会可不交易并返回 0。官方输入非空，长度至多 10⁵，价格非负。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

枚举每个买入日与之后的卖出日需要 O(n²)。反过来固定卖出日：之前所有买入方案中，只需知道最低买入价。将这个最小值随扫描维护，便不必重看历史。

## 核心思路

用 `lowest` 保存当前日之前的最低价格，`best` 保存已处理卖出日的最优利润。先用当前价格计算卖出利润，再更新最低价；这样代码顺序直接表达“先买后卖”。只有一个价格时循环不执行，答案自然为 0。

## 手推一个小例子

取 `[8, 3, 6, 2, 7]`：
1. 初始最低价 8，利润 0。
2. 价格 3：卖出无收益，最低价改为 3。
3. 价格 6：利润变为 3。
4. 价格 2：利润仍为 3，最低价改为 2。
5. 价格 7：利润变为 5，最终选择价格 2 买入、7 卖出。

## 为什么正确

处理第 i 天前，`lowest` 是第 0 至 i−1 天的最小价格。因此 `prices[i] - lowest` 是所有“第 i 天卖出”的交易中最大利润。把它与此前最优值取最大，就覆盖了卖出日不晚于 i 的所有合法交易。归纳到最后一天，再与初值 0 比较，得到允许不交易时的最优解。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0121_best_time_to_buy_and_sell_stock.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        lowest = prices[0]
        best = 0
        for i in range(1, len(prices)):
            price = prices[i]
            # 卖出必须使用以前某一天的买入价。
            best = max(best, price - lowest)
            lowest = min(lowest, price)
        return best
```

## 复杂度

时间 O(n)，辅助空间 O(1)。按索引访问，没有 `prices[1:]` 隐藏的 O(n) 切片。

## 边界与易错点

- 递减价格返回 0，不能强制做一笔亏损交易。
- 不能用全局最大值减全局最小值；它们的日期可能颠倒。
- 本实现依赖官方非空约束；没有把空列表伪装成官方测试情况。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0121`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：为什么过去的最高价格不重要？如果允许多次交易，当前状态还足够吗？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/best-time-to-buy-and-sell-stock/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0121.Best%20Time%20to%20Buy%20and%20Sell%20Stock/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/dynamic-programming/0121-best-time-to-buy-and-sell-stock.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/dynamic-programming/0121-best-time-to-buy-and-sell-stock.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[121. 买卖股票的最佳时机](https://www.bilibili.com/video/BV1Xe4y1u77q)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：最低价格必须来自卖出之前；用持续下降价格检查“不交易”对应的零收益。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
