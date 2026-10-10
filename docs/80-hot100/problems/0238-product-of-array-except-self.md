# 238. 除了自身以外数组的乘积

[官方题目](https://leetcode.cn/problems/product-of-array-except-self/) · MEDIUM · 官方分类：普通数组

## 题意与接口

对每个位置，计算数组中除它自身外所有元素的乘积，禁止使用除法。`productExceptSelf(nums)` 返回新数组，输入不修改。

## 从朴素方法到优化

逐位置重算其他元素乘积为 O(n²)。答案可以拆成左侧所有元素乘积×右侧所有元素乘积，各做一遍累计即可。

## 核心思路

先用答案数组写每个位置左侧的前缀乘积，再从右往左维护一个后缀乘积并乘上。空前缀和空后缀的乘积都定义为1。

## 手推一个小例子

[3,2,4]：前缀阶段ans=[1,3,6]；从右往左，位置2乘1得6；位置1乘4得12；位置0乘8得8，返回[8,12,6]。

## 为什么正确

第一轮处理位置i前，prefix恰好是下标小于i的乘积。第二轮处理i前，suffix恰好是下标大于i的乘积。两者覆盖除i外所有位置且无重叠，因此乘积正确；零也自然参与。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0238_product_of_array_except_self.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def productExceptSelf(self, nums: list[int]) -> list[int]:
        answer = [1] * len(nums)
        prefix = 1
        for i, value in enumerate(nums):
            # 先写再乘，answer[i]因此不含nums[i]。
            answer[i] = prefix
            prefix *= value
        suffix = 1
        for i in range(len(nums) - 1, -1, -1):
            answer[i] *= suffix
            suffix *= nums[i]
        return answer
```

## 复杂度

时间 O(n)。除返回数组外辅助空间O(1)，返回数组O(n)；按题设乘积范围计整数运算为常数成本。

## 边界与易错点

- 不能总乘积除以当前值：题目禁止除法且有零会出错。
- 写入prefix后再乘当前值，避免把自身纳入。
- 两个零时所有答案都是零；一个零时只有零位置可能非零。

## 本地测试与复习

测试零个、一个、多个零及负数；随机与排除当前索引的math.prod对拍。

复习：为什么答案数组可以同时充当前缀数组？若把乘法替换成其他运算，需要什么性质？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/product-of-array-except-self/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0238.Product%20of%20Array%20Except%20Self/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：用一个零、两个零分别手推前缀积和后缀积，说明为何无需除法，并区分输出空间与辅助空间。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
