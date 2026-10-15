# 94. 二叉树的中序遍历

难度：EASY · 分类：二叉树

## 题意与接口

返回二叉树的中序遍历节点值：左子树、根、右子树。接口：`inorderTraversal(root) -> list[int]`。

约束核对（2026-10-09）：节点数 0..100；返回中序值序列，进阶明确要求迭代写法。

## 从朴素方法到优化

递归表达简短，但树退化成链时 Python 默认调用栈可能溢出。用显式栈模拟“先保存根，再处理左边”的返回过程，不改变访问顺序。

## 核心思路

cur 沿左孩子不断下降，把沿途祖先压栈；左侧耗尽后弹出一个节点记录值，再令 cur 指向它的右孩子，继续同样过程。

## 手推一个小例子

根 4，左孩子 2，右孩子 7，且 2 的右孩子为 3。先压 4、2；弹 2 输出 2；转向 3 输出 3；弹 4 输出 4；最后输出 7，得到 `[2,3,4,7]`。

## 为什么正确

栈中保存左子树尚未完全访问的祖先。弹出节点时它的左子树已完成，而自身和右子树尚未访问，所以记录当前节点后处理右子树正符合中序定义。每个节点入栈、出栈各一次。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0094_binary_tree_inorder_traversal.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def inorderTraversal(self, root):
        answer, stack, cur = [], [], root
        while cur or stack:
            # 保存返回路径，等左子树处理完才访问当前节点。
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            answer.append(cur.val)
            cur = cur.right
        return answer
```

## 复杂度

时间 O(n)，辅助栈 O(h)，输出 O(n)。h 为树高，退化时 h=n。

## 边界与易错点

外层条件是 `cur or stack`；cur 为空时祖先仍可能未处理。中序结果仅对合法 BST 才保证有序。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：栈顶节点何时才能输出？把“输出”移动到压栈时会得到哪种遍历？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：对同一棵树画出递归与显式栈访问顺序，确认输出发生在左子树处理之后。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
