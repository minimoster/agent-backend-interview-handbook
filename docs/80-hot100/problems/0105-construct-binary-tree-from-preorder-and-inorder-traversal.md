# 105. 从前序与中序遍历序列构造二叉树

难度：MEDIUM · 分类：二叉树

## 题意与接口

已知同一棵树的先序与中序序列，重建树。接口：`buildTree(preorder, inorder)`。本题约定值互不重复、两序列有效且长度至多 3000。

约束核对（2026-10-09）：长度 1..3000，两遍历合法且值互异，来自同一棵树。

## 从朴素方法到优化

递归每次在中序里线性找根并切片，最坏 O(n²)。下标表能降到 O(n)，但深链仍有 Python 递归问题。这里用栈同时模拟先序建节点和中序关闭左子树。

## 核心思路

栈顶若不等于当前中序值，说明它的左侧尚未完成，新先序节点是其左孩子。若相等，连续弹出已完成中序访问的祖先，最后弹出的节点应连接新的右孩子。每个新节点入栈。

## 手推一个小例子

先序 `[8,4,6,11]`，中序 `[4,6,8,11]`：8 先入栈；栈顶 8≠4，4 接为左孩子；4=当前中序，弹出 4 后把 6 接其右侧；接着弹 6、8，把 11 接到 8 右侧。

## 为什么正确

先序决定新节点到达顺序，中序决定某节点的左子树何时完成。栈保留尚未完成中序访问的祖先；相等时弹栈恰好跨过已完成左侧的节点，新节点只能是最后弹出祖先的右子树根。唯一值使判断无歧义。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0105_construct_binary_tree_from_preorder_and_inorder_traversal.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from examples.hot100.structures import TreeNode

class Solution:
    def buildTree(self, preorder, inorder):
        if not preorder:
            return None
        root = TreeNode(preorder[0])
        stack, index = [root], 0
        for offset in range(1, len(preorder)):
            value = preorder[offset]
            parent = stack[-1]
            child = TreeNode(value)
            # 中序尚未轮到栈顶：它的左子树还未完成。
            if parent.val != inorder[index]:
                parent.left = child
            else:
                # 连续弹出已完成中序访问的祖先，找到右分支的父亲。
                while stack and stack[-1].val == inorder[index]:
                    parent = stack.pop()
                    index += 1
                parent.right = child
            stack.append(child)
        return root
```

## 复杂度

时间 O(n)，每个节点入栈出栈各一次；辅助栈 O(h)，输出节点 O(n)。使用下标访问，不复制遍历数组的切片。

## 边界与易错点

依赖输入有效和值唯一，不尝试纠正矛盾的遍历。测试应比较重建后的两种遍历；单边 3000 节点树也要跑。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：弹出多个祖先意味着在原树中完成了什么？为何下标推进总共只有 O(n) 次？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：用前序确定根后，解释中序分界怎样决定左右子树大小；注意不要套用后序构树的根位置。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
