# 198. 打家劫舍

[官方题目](https://leetcode.cn/problems/house-robber/) · MEDIUM · 官方分类：动态规划

## 题意与接口

接口：`Solution.rob(nums: list[int]) -> int`。从一排非负数中选择若干项，相邻位置不能同时选择，返回可取得的最大和。官方数组长度 1 至 100。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/house-robber/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

枚举每个位置选或不选会产生指数分支。观察前 i 个位置的最优答案：最后一项要么不选，要么选且跳过前一项，于是只需保存两个较短前缀的答案。

## 核心思路

令 f(i) 为前 i 个位置的最大收益。读到当前 value 时，不选它得到 f(i−1)；选它得到 f(i−2)+value，取两者最大。`previous`、`current` 分别保存这两个前缀状态。

## 手推一个小例子

取 `[4, 1, 2, 7, 3]`，前缀答案依次为：
1. 读 4：max(0,0+4)=4。
2. 读 1：max(4,0+1)=4。
3. 读 2：max(4,4+2)=6。
4. 读 7：max(6,4+7)=11。
5. 读 3：max(11,6+3)=11。最优选择第 1、4 项。

## 为什么正确

任何最优方案都属于“选最后一项”或“不选最后一项”，两类覆盖全部可能。前者余下只能来自前 i−2 项的最优方案，否则替换成更优前缀会提高总收益；后者等于前 i−1 项的最优答案。这给出递推式。空前缀收益为 0，滚动计算保持递推所需状态，所以最终答案正确。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0198_house_robber.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def rob(self, nums: list[int]) -> int:
        previous = current = 0
        for value in nums:
            # 右侧读取的都是更新前的两个前缀状态。
            previous, current = current, max(current, previous + value)
        return current
```

## 复杂度

时间 O(n)，辅助空间 O(1)，不修改输入。

## 边界与易错点

- “分别求奇数位和、偶数位和取最大”不对，最优位置可以跨越这两组。
- 两个相邻值相等时无需特殊处理。
- 全为 0 的数组返回 0。环形排列是另一个问题，不能直接套用此接口。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0198`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：若还要返回具体选择的下标，应该记录什么？为什么当前收益最大的房子不一定要选？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/house-robber/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0198.House%20Robber/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0198.house-robber.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0198.house-robber.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[198. 打家劫舍](https://www.bilibili.com/video/BV1Te411N7SX)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：比较偷当前与跳过当前两种转移，用单个房屋、相邻高值和交替高值检查状态含义。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
