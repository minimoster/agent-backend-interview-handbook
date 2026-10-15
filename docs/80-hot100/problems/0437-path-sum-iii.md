# 437. 路径总和 III

难度：MEDIUM · 分类：二叉树

## 题意与接口

统计向下的连续父子路径中，节点值之和等于 targetSum 的条数；起点和终点均可任意。接口：`pathSum(root, targetSum)`。本题约定可有负值、空树，至多 1000 节点。

约束核对（2026-10-09）：节点数 0..1000，值可达正负 10^9；路径必须向下，起终点不限于根/叶。

## 从朴素方法到优化

枚举每个起点再向下累加，最坏 O(n²)。根到当前节点的前缀和为 s，若祖先之前的前缀为 s-target，则两者之差就是目标路径；用频次表同时计数所有起点。

## 核心思路

freq 只保存当前根路径上的前缀，初始 `{0:1}`。进入节点时先查 `s-target` 次数，再加入 s；离开节点时减去本次贡献。显式 enter/exit 栈保证兄弟分支互不污染。

## 手推一个小例子

根 2，左孩子 -1，左孙 2，target=3。进入根 s=2；进入 -1 得 s=1；进入孙子得 s=3，查 freq[0]=1，找到整条 `2→-1→2`。退出该支后撤销 3、1，其他分支不能使用它们。

## 为什么正确

一条以当前节点结束的向下路径唯一对应当前根路径上一个更早前缀，差值为目标当且仅当前缀为 s-target。频次计数保留重复前缀对应的不同起点；退出撤销使候选只含祖先，故无漏计或跨分支误计。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0437_path_sum_iii.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def pathSum(self, root, targetSum):
        freq, answer = {0: 1}, 0
        stack = [(root, 0, False)] if root else []
        while stack:
            node, total, exiting = stack.pop()
            # 离开时撤销前缀，保证频次表只描述当前祖先路径。
            if exiting:
                freq[total] -= 1
                if freq[total] == 0:
                    del freq[total]
                continue
            total += node.val
            # 先查后加入，避免 target=0 时统计空路径。
            answer += freq.get(total - targetSum, 0)
            freq[total] = freq.get(total, 0) + 1
            stack.append((node, total, True))
            if node.right:
                stack.append((node.right, total, False))
            if node.left:
                stack.append((node.left, total, False))
        return answer
```

## 复杂度

期望时间 O(n)，辅助空间 O(h)：栈和当前路径前缀表；删除零频次条目才能维持此空间界。

## 边界与易错点

先查再加入，避免 target=0 时把长度为 0 的路径算进去。值可负，不能以“和过大”剪枝。一定撤销前缀。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：全零的 n 节点单链，目标为 0 时为什么答案是 n(n+1)/2？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：沿一条路径维护前缀和频次，说明回溯时为何必须撤销，否则相邻分支会互相污染。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
