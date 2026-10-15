# 39. 组合总和

难度：MEDIUM · 分类：回溯

## 题意与接口

从互不相同的正整数 candidates 中选若干数，使和为 target，每种数可重复使用；返回不重复组合。接口：`combinationSum(candidates, target)`。本题约定候选为 2..40、target 为 1..40。

约束核对（2026-10-09）：候选数 1..30，值互异且为 2..40；target 为 1..40，每个候选可重用。

## 从朴素方法到优化

枚举有序选取序列会重复产生相同组合，例如 2+5 与 5+2。将候选排序并只允许下标非递减选择，一条分支可继续选同一个下标，既允许重复使用又消除排列重复。

## 核心思路

状态是 start 和剩余和 remain。若 remain=0 输出；遍历 i≥start，当前数超过 remain 即结束该层，因为后面更大。选择后递归传 i 而非 i+1。使用 sorted 副本不改变输入。

## 手推一个小例子

候选 `[3,4,7]`，target=10：分支 3→3→4 输出 `[3,3,4]`；分支 3→7 输出 `[3,7]`；以 4 开头找不到合法剩余，7 后也不能再选 3，因此不会重复 `[3,7]`。

## 为什么正确

正整数保证剩余和严格下降，所以搜索终止。非递减下标为每种数的多重集合提供唯一表示，排除重复；任意合法组合排序后都能沿允许分支走到剩余 0，故完整。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0039_combination_sum.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def combinationSum(self, candidates, target):
        values = sorted(candidates)
        answer, path = [], []
        def search(start, remain):
            if remain == 0:
                answer.append(path.copy())
                return
            for i in range(start, len(values)):
                value = values[i]
                # 排序后本项过大，后面的项也一定过大。
                if value > remain:
                    break
                path.append(value)
                # 仍传 i 允许重用当前数，同时保持下标非递减。
                search(i, remain - value)
                path.pop()
        search(0, target)
        return answer
```

## 复杂度

设 m 为候选数，D=⌊target/min(candidates)⌋，S 为实际搜索状态数，Z 为输出元素总数。时间上界 O(m log m + mS + Z)，其中 S 不超过 1+m+…+m^D，搜索通常为指数级，剪枝后会更少；此写法也覆盖 m=1 的情况。辅助空间 O(m+D)，输出 O(Z)。

## 边界与易错点

候选为正且互异是终止和无重复的前提；包含 0 会破坏递归下降。传 i 允许重用，传 i+1 则改变问题。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：排序在这里分别帮助了哪两个目的？若允许负数，为何不能照搬 remain 剪枝？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：说明允许重复选取为何递归仍传当前起点；检查排序剪枝与去重策略的适用条件。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
