# 136. 只出现一次的数字

[官方题目](https://leetcode.cn/problems/single-number/) · EASY · 官方分类：技巧

## 题意与接口

接口：`Solution.singleNumber(nums: list[int]) -> int`。非空整数数组中，恰有一个值出现一次，其余每个值恰好出现两次，找出单独的值。要求线性时间、常量额外空间。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/single-number/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

频次字典直观但要 O(n) 空间；排序后成对检查要 O(n log n) 时间。题目的“其余恰好两次”提供了代数消去性质，可以把所有数异或起来。

## 核心思路

异或满足 x^x=0、x^0=x，以及交换律、结合律。以 0 开始累积所有数，重复的成对消去，剩下唯一一次的数。Python 的 `^` 是按位异或，`**` 才是乘方。

## 手推一个小例子

取 `[6, 1, 6, 4, 4]`：
1. 0^6=6。
2. 6^1=7。
3. 7^6=1，两次 6 已抵消。
4. 1^4=5。
5. 5^4=1，最终得到唯一值 1。

## 为什么正确

利用交换律和结合律，可以把异或表达式重新分组，让每一对相等数靠在一起。每组都等于 0，所有 0 再与单独值异或仍得到该值，因此答案与输入顺序无关。负数同样满足这些恒等式。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0136_single_number.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def singleNumber(self, nums: list[int]) -> int:
        answer = 0
        for value in nums:
            answer ^= value  # 成对相等值会在累计异或中抵消。
        return answer
```

## 复杂度

时间 O(n)，辅助空间 O(1)，采用题目有界整数运算模型。

## 边界与易错点

- 此法依赖其他数恰好出现两次，出现三次不是同一道题。
- 唯一值可能为 0 或负数。
- 不能用逻辑运算 `or` 或按位或 `|` 替代异或。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0136`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：若恰有两个值各出现一次，所有数异或的结果是什么？如何借此继续区分它们？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/single-number/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0136.Single%20Number/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：说明异或的交换律与自消去性质，检查题设的出现次数条件改变后方法是否仍成立。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
