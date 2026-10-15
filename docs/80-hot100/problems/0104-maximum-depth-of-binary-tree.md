# 104. 二叉树的最大深度

难度：EASY · 分类：二叉树

## 题意与接口

返回二叉树最大深度，根所在层深度为 1，空树为 0。接口：`maxDepth(root) -> int`。

约束核对（2026-10-09）：节点数 0..10000；深度是最长根到叶路径上的节点数。

## 从朴素方法到优化

递归高度公式很好理解，但深链有栈限制。用显式深度优先搜索把每个节点连同自身深度压栈，取遇到的最大深度。

## 核心思路

栈元素 `(node, depth)`。弹出节点后更新最大值，孩子以 depth+1 入栈。使用列表尾部 pop，避免队首删除的线性移动。

## 手推一个小例子

树根 8，左孩子 5，5 的左孩子 1，根右孩子 9。依次记录深度 1、2、2、3（具体左右访问顺序无关），最大值 3。

## 为什么正确

根深度正确为 1；父节点深度正确时孩子深度必为它加 1。每个节点恰入栈一次，因此最终取到所有节点深度的最大值。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0104_maximum_depth_of_binary_tree.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def maxDepth(self, root):
        if root is None:
            return 0
        best, stack = 0, [(root, 1)]
        while stack:
            node, depth = stack.pop()
            # 孩子携带父深度加一，不依赖 Python 递归调用栈。
            best = max(best, depth)
            if node.left:
                stack.append((node.left, depth + 1))
            if node.right:
                stack.append((node.right, depth + 1))
        return best
```

## 复杂度

时间 O(n)，显式 DFS 栈 O(h)；最坏 O(n)。不计输入树。

## 边界与易错点

深度按节点层数，空树为 0；不要与直径的边数混淆。使用显式栈支持很深的单链树。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：如果改成广度优先，额外空间由树高还是树宽决定？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：用退化长链检查递归深度风险；解释迭代时保存的深度或层数如何对应答案。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
