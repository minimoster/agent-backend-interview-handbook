# 1. 两数之和

[官方题目](https://leetcode.cn/problems/two-sum/) · EASY · 官方分类：哈希

## 题意与接口

给整数数组与目标和，返回两个不同位置的下标，使对应值相加等于目标。`twoSum(nums, target)` 返回两个下标；题设保证恰有一组。数组不修改。

## 从朴素方法到优化

两层枚举检查所有位置对，时间 O(n²)。当右端值为 x，只需知道左边是否出现 target-x，不需要重新扫描整个前缀。

## 核心思路

哈希表保存“已走过的数值 → 一个下标”。先查补数，再记录当前值，避免把当前元素用两次。

## 手推一个小例子

nums=[8, 1, 6, 4]，target=10。读8，缺2，存8→0；读1，缺9，存1→1；读6，缺4；读4时找到6→2，得到[2,3]。

## 为什么正确

处理下标 i 前，表中只有 i 左侧元素。若补数存在，则两下标不同且和正确；任意合法对的右端被处理时，其左端已在表中，所以不会漏解。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0001_two_sum.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        # 表里只存已经走过的位置，避免一个元素使用两次。
        seen = {}
        for i, value in enumerate(nums):
            complement = target - value
            if complement in seen:  # 先查询，确保不能复用当前位置
                return [seen[complement], i]
            seen[value] = i
        return []  # 非题设的无解输入，方便本地复用
```

## 复杂度

设 n 为数组长度。哈希操作平均 O(1)，时间平均 O(n)，辅助空间 O(n)；极端哈希碰撞不是这里的平均复杂度保证。

## 边界与易错点

- [5,5] 的答案需要两个位置，不能先写入再查询。
- 负数和零不改变补数逻辑。
- 重复键覆盖旧下标仍保留一个可用的左侧位置。

## 本地测试与复习

确定性测试覆盖重复值、零和负数；随机生成小数组，使用枚举下标对核验返回结果。

复习：如果答案有多组且要求返回所有下标对，字典的值还够用吗？为什么先查后存是本题关键？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/two-sum/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0001.Two%20Sum/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0001.two-sum.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0001.two-sum.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[1. 两数之和](https://www.bilibili.com/video/BV1aT41177mK)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：用两个相等的数手推一次，解释为什么查询补数必须发生在登记当前下标之前。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
