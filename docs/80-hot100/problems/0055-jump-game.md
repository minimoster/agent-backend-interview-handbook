# 55. 跳跃游戏

[官方题目](https://leetcode.cn/problems/jump-game/) · MEDIUM · 官方分类：贪心算法

## 题意与接口

接口：`Solution.canJump(nums: list[int]) -> bool`。从下标 0 出发，当前位置的值是最多可向右跳的距离，判断能否到达末尾。长度 1 至 10⁴，元素非负。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/jump-game/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

朴素搜索尝试每个下一跳，会重复访问同一位置；用可达数组也可能枚举 O(n²) 条跳跃边。所有可达位置构成从 0 开始的连续区间，因此只需保存区间右端。

## 核心思路

`farthest` 表示已处理的可达位置所能覆盖的最远下标。遇到 `i > farthest`，说明当前位置已经越过整个可达前缀，后面也不可能救回来。否则把右端更新为 `max(farthest, i + nums[i])`。

## 手推一个小例子

取 `[2, 0, 2, 0, 1]`：
1. 在下标 0，把最远下标扩至 2。
2. 下标 1 可达，但值 0 不扩展范围。
3. 下标 2 可达，把最远下标扩至 4，已经覆盖终点，返回真。
对 `[1, 0, 2]`，扫描到下标 2 时最远仍是 1，返回假。

## 为什么正确

从任何可达位置可以选择不超过最大步长的任意距离，新增可达位置不会在已有前缀后制造空洞。若 i 未超出右端，它确实可达，扩展合法；若 i 超出右端，所有更早的可达位置均无法跨过这一缺口，之后的位置不可能被首次到达。因而失败判定和覆盖终点时的成功判定都可靠。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0055_jump_game.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def canJump(self, nums: list[int]) -> bool:
        farthest = 0  # 已扫描的可达位置共同覆盖的最右下标。
        for i, jump in enumerate(nums):
            if i > farthest:
                return False
            farthest = max(farthest, i + jump)
            if farthest >= len(nums) - 1:
                return True
        return False
```

## 复杂度

最坏时间 O(n)，辅助空间 O(1)。

## 边界与易错点

- `[0]` 已经在终点，返回真。
- 看见 0 不应立即失败，可能从前面直接跨过它。
- 只有可达位置的跳跃能力可以扩展 `farthest`，顺序不可颠倒。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0055`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：可达集合为什么没有空洞？若每次必须恰好跳 nums[i] 步，这个证明哪里失效？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/jump-game/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0055.Jump%20Game/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/greedy/0055-jump-game.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/greedy/0055-jump-game.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[55. 跳跃游戏](https://www.bilibili.com/video/BV1VG4y1X7kB)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：扫描每个位置前先检查它是否可达，用含零的数组验证最远可达位置的更新。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
