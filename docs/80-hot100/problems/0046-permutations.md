# 46. 全排列

[官方题目](https://leetcode.cn/problems/permutations/) · MEDIUM · 官方分类：回溯

## 题意与接口

返回互不相同整数数组的全部排列。接口：`permute(nums)`；排列中的相对次序不同即不同答案。

约束核对（2026-10-09）：长度 1..6，整数互异；返回所有排列，顺序不限。 [官方来源](https://leetcode.com/problems/permutations/)

## 从朴素方法到优化

枚举 n^n 个长度 n 序列再过滤重复元素太浪费。回溯只从尚未使用的位置选择，搜索树直接由合法前缀组成。

## 核心思路

path 保存当前排列，used[i] 表示原位置 i 已选。每层枚举所有未用位置，做选择、递归、撤销；长度达到 n 时复制 path。

## 手推一个小例子

`[2,5,8]`：先选 2，再选 5，再选 8，输出 `[2,5,8]`；撤销 8、5，改选 8 再选 5，输出 `[2,8,5]`；撤销 2 后探索以 5、8 开头的分支。

## 为什么正确

每条根到叶路径恰选每个原位置一次，因此输出合法排列。任意排列的第 i 项都对应搜索树第 i 层唯一选择，故所有排列都被找到且无重复。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0046_permutations.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def permute(self, nums):
        answer, path = [], []
        used = [False] * len(nums)
        def search():
            if len(path) == len(nums):
                # 保存快照，否则后续撤销会改动已保存的答案。
                answer.append(path.copy())
                return
            for i, value in enumerate(nums):
                if used[i]:
                    continue
                used[i] = True
                path.append(value)
                search()
                # 撤销本层选择，允许下一候选复用这些位置。
                path.pop()
                used[i] = False
        search()
        return answer
```

## 复杂度

时间 O(n·n!)，含复制每个排列的 n 个元素；辅助空间 O(n)，输出 O(n·n!)。

## 边界与易错点

append(path) 会保存可变对象引用，必须复制。输入互异是去重前提；带重复值需要另设计同层去重。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为什么撤销顺序必须对应本层所做选择？排列问题与组合问题的递归参数有何差别？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/permutations/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0046.Permutations/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0046.permutations.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0046.permutations.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[46. 全排列](https://www.bilibili.com/video/BV19v4y1S79W/)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：分别检查 used 状态和路径撤销；说明保存答案时为什么需要复制当前路径。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
