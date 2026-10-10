# 543. 二叉树的直径

[官方题目](https://leetcode.cn/problems/diameter-of-binary-tree/) · EASY · 官方分类：二叉树

## 题意与接口

求树中任意两节点间最长简单路径的边数，路径不必经过根。接口：`diameterOfBinaryTree(root) -> int`。

约束核对（2026-10-09）：节点数 1..10000；直径按边数计，可不经过根。 [官方来源](https://leetcode.com/problems/diameter-of-binary-tree/)

## 从朴素方法到优化

对每个节点重新计算左右高度会在链状树上达到 O(n²)。后序遍历一次保存每个节点高度，可复用子问题结果。

## 核心思路

栈中用 expanded 标记区分首次进入和孩子已处理两种时刻。高度以节点数计：空为 0，当前为 `1+max(left,right)`；经过当前节点的路径边数恰为 `left+right`。

## 手推一个小例子

根 9，左 4（左 2、右 6），右 11。叶子高度 1；节点 4 的高度 2、候选直径 2；根左右高度 2、1，候选 3，因此答案 3。

## 为什么正确

任何简单路径都有唯一最高节点，该路径最多包含该节点左右两条最长向下路径，长度为两侧高度之和。逐节点取此候选最大值覆盖所有可能最高节点。后序确保高度已计算。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0543_diameter_of_binary_tree.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def diameterOfBinaryTree(self, root):
        if root is None:
            return 0
        heights, best = {}, 0
        stack = [(root, False)]
        while stack:
            node, expanded = stack.pop()
            if not expanded:
                # 压入退出状态；左右孩子会先于它被弹出。
                stack.append((node, True))
                if node.right:
                    stack.append((node.right, False))
                if node.left:
                    stack.append((node.left, False))
            else:
                left = heights.get(node.left, 0)
                right = heights.get(node.right, 0)
                # 高度按节点数计，两侧高度之和恰是路径边数。
                best = max(best, left + right)
                heights[node] = 1 + max(left, right)
        return best
```

## 复杂度

时间 O(n)，辅助空间 O(n)：高度字典 O(n)，显式栈 O(h)。这是避免深递归、易理解的实现，不声称辅助空间 O(h)。

## 边界与易错点

直径单位是边，单节点答案为 0。最大值必须检查每个节点。高度字典依赖本地节点按对象身份哈希。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为什么返回给父节点的高度只能选一边，而更新全局直径可以同时用两边？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/diameter-of-binary-tree/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0500-0599/0543.Diameter%20of%20Binary%20Tree/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0543.diameter-of-binary-tree.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0543.diameter-of-binary-tree.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：分别定义向上返回的高度和更新全局答案的路径长度；说明边数与节点数的换算。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
