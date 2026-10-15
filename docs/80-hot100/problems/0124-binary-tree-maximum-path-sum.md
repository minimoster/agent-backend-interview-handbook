# 124. 二叉树中的最大路径和

难度：HARD · 分类：二叉树

## 题意与接口

求任意非空简单路径的最大节点值总和；路径可拐弯、可不经过根。接口：`maxPathSum(root)`。本题约定树非空且至多 30000 节点，使用迭代后序避免深递归。

约束核对（2026-10-09）：节点数 1..30000，节点值 -1000..1000；路径非空且不得重复节点。

## 从朴素方法到优化

枚举路径端点代价高。对每个节点只保留能向父亲延伸的一条最大贡献，同时把“左右两侧经过当前节点”的完整路径用于更新答案。

## 核心思路

子树贡献若为负则舍弃。当前完整候选为 `value+left_gain+right_gain`；向父亲返回的贡献只能为 `value+max(left_gain,right_gain)`，否则会出现分叉而不是路径。

## 手推一个小例子

根 -4，左 3，右 7（左 -2、右 6）。节点 7 舍弃 -2，向上贡献 13；根完整候选为 -4+3+13=12；节点 7 内部路径 7→6 的和 13 更大，因此答案 13。

## 为什么正确

任何简单路径有唯一最高节点；以它为最高节点的最优路径独立选择两侧非负最佳向下链。遍历所有节点更新即可覆盖全局最优。向父亲传单侧贡献保持不分叉的约束。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0124_binary_tree_maximum_path_sum.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def maxPathSum(self, root):
        if root is None:
            raise ValueError("the problem requires a non-empty tree")
        gains, best = {}, float("-inf")
        stack = [(root, False)]
        while stack:
            node, expanded = stack.pop()
            if not expanded:
                stack.append((node, True))
                if node.right:
                    stack.append((node.right, False))
                if node.left:
                    stack.append((node.left, False))
            else:
                left = max(0, gains.get(node.left, 0))
                right = max(0, gains.get(node.right, 0))
                # 完整路径能接两边，但向父亲延伸只能保留一边。
                best = max(best, node.val + left + right)
                gains[node] = node.val + max(left, right)
        return best
```

## 复杂度

时间 O(n)，辅助空间 O(n)：贡献字典 O(n)，后序栈 O(h)。

## 边界与易错点

全负数时仍须选择一个节点，所以 best 不能初始化为 0。空树不在题目范围，本实现明确抛错。返回父亲的贡献不能把两边都加上。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：比较本题和直径题的“局部答案”与“向上返回值”，两者为什么不同？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：解释向父节点返回的贡献只能选一侧，而当前节点更新答案可以连接两侧；检查全负数树。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
