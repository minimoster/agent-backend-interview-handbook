# 104. 二叉树的最大深度

[官方题目](https://leetcode.cn/problems/maximum-depth-of-binary-tree/) · EASY · 官方分类：二叉树

## 题意与接口

返回二叉树最大深度，根所在层深度为 1，空树为 0。接口：`maxDepth(root) -> int`。

约束核对（2026-10-09）：节点数 0..10000；深度是最长根到叶路径上的节点数。 [官方来源](https://leetcode.com/problems/maximum-depth-of-binary-tree/)

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

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/maximum-depth-of-binary-tree/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0104.Maximum%20Depth%20of%20Binary%20Tree/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0104.maximum-depth-of-binary-tree.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0104.maximum-depth-of-binary-tree.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[104. 二叉树的最大深度](https://www.bilibili.com/video/BV1Gd4y1V75u)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：用退化长链检查递归深度风险；解释迭代时保存的深度或层数如何对应答案。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
