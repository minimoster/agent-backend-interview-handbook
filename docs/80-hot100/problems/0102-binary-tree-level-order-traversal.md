# 102. 二叉树的层序遍历

难度：MEDIUM · 分类：二叉树

## 题意与接口

按从上到下、每层从左到右返回节点值列表。接口：`levelOrder(root) -> list[list[int]]`。

约束核对（2026-10-09）：节点数 0..2000；逐层从左到右返回值。

## 从朴素方法到优化

可以 DFS 时按深度归档；广度优先天然按层处理。关键是在一层开始时冻结当前队列长度，以区分本层与新加入的下一层。

## 核心思路

队列最初只有根。每轮弹出固定数量的本层节点，收集值，同时把左、右孩子依序追加队尾，最后保存本层结果。

## 手推一个小例子

根 3，左 1、右 7；1 的右孩子 2，7 的左孩子 6。各轮队列分别为 `[3]`、`[1,7]`、`[2,6]`，输出 `[[3],[1,7],[2,6]]`。

## 为什么正确

归纳：每轮开始队列恰为当前层且从左到右。固定弹出这层节点，并按父顺序左后右加入孩子，就得到下一层正确顺序。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0102_binary_tree_level_order_traversal.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from collections import deque

class Solution:
    def levelOrder(self, root):
        if root is None:
            return []
        answer, queue = [], deque([root])
        while queue:
            level = []
            # range 在本层开始时冻结长度，新孩子留给下一层。
            for _ in range(len(queue)):
                node = queue.popleft()
                level.append(node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            answer.append(level)
        return answer
```

## 复杂度

时间 O(n)，辅助队列 O(w)，输出 O(n)，w 为最大层宽。

## 边界与易错点

循环中动态改变本层数量会把层混在一起。使用 deque.popleft，而非 list.pop(0)。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：队列里可能同时含两层节点，为什么空间仍是 O(w)？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：解释每层开始时固定队列长度的作用，避免刚入队的孩子被当作本层节点。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
