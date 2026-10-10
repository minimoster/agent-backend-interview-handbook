# 53. 最大子数组和

[官方题目](https://leetcode.cn/problems/maximum-subarray/) · MEDIUM · 官方分类：普通数组

## 题意与接口

从非空整数数组中选择非空连续子数组，使其元素和最大。`maxSubArray(nums)` 返回最大和，输入不修改。

## 从朴素方法到优化

两层起止枚举并累加需 O(n²)。固定右端时，最佳候选要么从当前元素重新开始，要么接在“上一位置结尾的最佳子数组”之后。

## 核心思路

ending表示必须以当前元素结尾的最大和；转移ending=max(x,ending+x)。best保存所有ending的最大值，这是Kadane的滚动DP。

## 手推一个小例子

[-4,3,-1,5,-6]：ending依次-4、3、2、7、1；best依次-4、3、3、7、7，因此选[3,-1,5]。

## 为什么正确

以当前下标结尾的非空子数组只有两类：长度1，或由前一位置结尾子数组追加当前值。对后者，选择前一位置的最大和不会比任何更小和差。递推枚举了两类最优候选，再对所有结尾取最大。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0053_maximum_subarray.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        if not nums:
            raise ValueError("nums must be nonempty")
        ending = best = nums[0]
        for i in range(1, len(nums)):
            # 延长前缀不划算时，从当前位置重新开始。
            ending = max(nums[i], ending + nums[i])
            best = max(best, ending)
        return best
```

## 复杂度

时间 O(n)，辅助空间 O(1)。代码使用下标迭代，没有nums[1:]切片产生额外O(n)列表。

## 边界与易错点

- best初始化为第一个数，不能初始化0，否则全负数组会误选空区间。
- 子数组必须连续，不是把所有正数相加。
- 空数组不在题设内，此实现显式报错。

## 本地测试与复习

测试单元素、全负、最佳区间在中间；随机与枚举区间和对拍。

复习：如果还要返回区间下标，在哪个分支更新当前起点？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/maximum-subarray/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0053.Maximum%20Subarray/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0053.maximum-subarray.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0053.maximum-subarray.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[本题：动态规划](https://www.bilibili.com/video/BV19V4y1F7b5) · [本题：贪心](https://www.bilibili.com/video/BV1aY4y1Z7ya)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：用全负数数组检查初始答案；解释“以当前位置结尾的最佳和”与全局最佳和的区别。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
