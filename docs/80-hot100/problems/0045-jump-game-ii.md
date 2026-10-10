# 45. 跳跃游戏 II

[官方题目](https://leetcode.cn/problems/jump-game-ii/) · MEDIUM · 官方分类：贪心算法

## 题意与接口

接口：`Solution.jump(nums: list[int]) -> int`。跳跃规则同第 55 题，求到达末尾的最少跳跃次数。官方保证终点可达；长度 1 至 10⁴，最大步长非负。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/jump-game-ii/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

把位置视为图节点，向每个能跳到的位置连边，BFS 可求最少边数，但显式枚举边最坏 O(n²)。每层 BFS 的可达位置仍是连续范围，可以只记当前层边界和下一层最远边界。

## 核心思路

`end` 表示使用当前 `steps` 次跳跃可覆盖的右端。扫描本层的位置，累计 `farthest`；到达 `end` 时，这一层已经全部处理，用一次跳跃进入下一层。只扫描到倒数第二个位置，避免已经到终点后又计一次跳跃。

## 手推一个小例子

取 `[2, 2, 1, 1, 0]`：
1. i=0：下一层最远到 2；碰到初始边界 0，次数变 1，边界变 2。
2. i=1：下一层最远扩至 3；i=2 仍为 3。
3. i=2 碰到边界，次数变 2，边界变 3。
4. i=3 扩至 4，再完成一层，答案 3。可选路径是 0→1→3→4。

## 为什么正确

设第 k 层右端为 Rₖ。所有不超过 Rₖ 的位置至多用 k 跳可达；再跳一次的最远位置是这些位置的 i+nums[i] 最大值。扫描到旧边界后才推进层数，恰好计算 Rₖ₊₁，没有漏掉本层更优的起跳点。终点首次被某层覆盖时，少一层不够，因此层数就是最少跳数。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0045_jump_game_ii.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def jump(self, nums: list[int]) -> int:
        steps = 0
        end = 0
        farthest = 0
        for i in range(len(nums) - 1):
            farthest = max(farthest, i + nums[i])
            if i == end:
                # 本层全部处理完，才用一跳进入下一层。
                steps += 1
                end = farthest
                if end >= len(nums) - 1:
                    break
        return steps
```

## 复杂度

时间 O(n)，辅助空间 O(1)。扫描保存的是压缩后的 BFS 层边界，并未构建边或队列。

## 边界与易错点

- 长度为 1 时答案 0。
- 不能每次选当前能到达的最远落点；真正重要的是下一次能覆盖多远。
- 本实现依赖官方“保证可达”契约；不可达输入的返回值不属于接口保证。要推广，应在边界无法推进时单独报错或返回约定值。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0045`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：`farthest` 为什么可以跨层保留？为什么循环不处理终点？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/jump-game-ii/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0045.Jump%20Game%20II/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/greedy/0045-jump-game-ii.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/greedy/0045-jump-game-ii.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[45. 跳跃游戏 II](https://www.bilibili.com/video/BV1Y24y1r7XZ)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：把当前可达范围看作一层，解释何时步数增加，以及到达最后下标后为何不再加一步。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
