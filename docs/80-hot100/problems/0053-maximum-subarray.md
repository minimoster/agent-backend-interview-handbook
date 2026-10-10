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

答案核对：选择“从nums[i]重新开始”时把当前起点改为i；best更新时同时保存当前起点与i。和相等时应先约定取最早区间、最短区间等规则，避免只比较和而让下标策略含糊。

### 官方追问：分治如何做到O(n)？

每个非空区间返回四元组`(total, prefix, suffix, best)`，分别是总和、最大非空前缀和、最大非空后缀和、最大非空子数组和。单个元素x的四个值都为x，不能把负数情况下的前后缀或答案初始化为0。

相邻左右区间L、R只需O(1)合并：

- total = L.total + R.total
- prefix = max(L.prefix, L.total + R.prefix)
- suffix = max(R.suffix, R.total + L.suffix)
- best = max(L.best, R.best, L.suffix + R.prefix)

前缀要么完全在L，要么包含整个L和R的一个非空前缀；后缀同理。最优子数组要么在一侧，要么跨分界，跨界部分恰好是L的非空后缀与R的非空前缀。对子区间归纳即可证明四个字段都正确。

例子：L=`[-4,3]`摘要为`(-1,-1,3,3)`，R=`[-1,5,-6]`摘要为`(-2,4,-1,5)`；合并得到`(-3,3,1,7)`，跨界和3+4=7。`[-8,-2,-5]`摘要为`(-15,-8,-5,-2)`，仍选非空区间。

平衡拆分形成n个叶子、n−1次常数合并，故总时间O(n)，递归栈O(log n)；使用下标区间，不复制切片。若每层另从中点扫描左右以求跨界和，则是O(n log n)的另一种分治版本。主接口仍采用上面的Kadane方法。

[可运行分治实现](../../../examples/hot100/followup_algorithms.py)提供`maximum_subarray_summary`与`max_subarray_divide_conquer`；[独立测试](../../../examples/hot100/test_followup_algorithms.py)对97,655个非空小数组逐项核对四个字段，并测试全负与100,000项边界。根目录运行`python -B -m unittest examples.hot100.test_followup_algorithms -v`。追问来自[官方英文题页](https://leetcode.com/problems/maximum-subarray/)；合并推导与代码为本仓库原创。

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
