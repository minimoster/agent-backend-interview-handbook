# 42. 接雨水

[官方题目](https://leetcode.cn/problems/trapping-rain-water/) · HARD · 官方分类：双指针

## 题意与接口

给每个位置的非负柱高，求雨后可积累的总水量。`trap(height)` 返回整数，不修改输入。

## 从朴素方法到优化

每格向两边找最高墙需 O(n²)。左右最大值数组可降为 O(n) 时间/O(n)空间；再观察两侧已知边界中较低的一侧即可结算，把辅助空间降为 O(1)。

## 核心思路

维护left_max与right_max。当left_max≤right_max时，左侧当前位置的水位由left_max决定：右边已经有足够高的墙。否则对称地结算右格。每次只结算一格。

## 手推一个小例子

[3,0,1,0,2]：先建立左边3、右边2；右界较低，位置3接2，位置2接1，位置1接2，合计5。位置0和4作为边界不积水。

## 为什么正确

若left_max≤right_max，左侧已有最高墙left_max，右侧已有墙right_max保证不会更低；当前左格最多只能达到left_max，因此max(0,left_max-height[left])就是最终水量。更新边界后逐格结算，各格不重不漏。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0042_trapping_rain_water.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def trap(self, height: list[int]) -> int:
        left, right = 0, len(height) - 1
        left_max = right_max = water = 0
        while left <= right:
            # 另一侧已知有更高的墙，较低边界这一侧即可定案。
            if left_max <= right_max:
                left_max = max(left_max, height[left])
                water += left_max - height[left]
                left += 1
            else:
                right_max = max(right_max, height[right])
                water += right_max - height[right]
                right -= 1
        return water
```

## 复杂度

时间 O(n)，辅助空间 O(1)。每个位置恰处理一次。

## 边界与易错点

- 水量由两边最大值中的较小值决定，不是邻居高度。
- 更新所在侧最大值后再相减，避免负水量。
- 单调数组、空数组、长度小于3的数组均返回0。

## 本地测试与复习

测试平地、单调、多个凹槽；随机对拍逐位置扫描左右最大值的朴素法。

复习：为什么选择较低的“历史最大边界”而不是总等到两端相遇才计算？如何写O(n)空间版本交叉验证？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/trapping-rain-water/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0042.Trapping%20Rain%20Water/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0042.trapping-rain-water.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0042.trapping-rain-water.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[42. 接雨水](https://www.bilibili.com/video/BV1uD4y1u75P/)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：用两边高、中间低的输入比较逐列和双指针思路，说明当前水位受哪一侧的已知边界限制。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
