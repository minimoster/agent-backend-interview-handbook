# 94. 二叉树的中序遍历

[官方题目](https://leetcode.cn/problems/binary-tree-inorder-traversal/) · EASY · 官方分类：二叉树

## 题意与接口

返回二叉树的中序遍历节点值：左子树、根、右子树。接口：`inorderTraversal(root) -> list[int]`。

约束核对（2026-10-09）：节点数 0..100；返回中序值序列，进阶明确要求迭代写法。 [官方来源](https://leetcode.com/problems/binary-tree-inorder-traversal/)

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

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/binary-tree-inorder-traversal/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0094.Binary%20Tree%20Inorder%20Traversal/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0094.binary-tree-inorder-traversal.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0094.binary-tree-inorder-traversal.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[94. 二叉树的中序遍历](https://www.bilibili.com/video/BV1Zf4y1a77g)。上传者已核验为代码随想录（MID 525438321）。
- 相关主题视频：[递归遍历专题（多种遍历的共用说明）](https://www.bilibili.com/video/BV1Wh411S7xt) · [非递归遍历专题（其他遍历方法）](https://www.bilibili.com/video/BV15f4y1W7i2)。仅用于方法迁移，不计为本题专属配套视频。

自主复习提示：对同一棵树画出递归与显式栈访问顺序，确认输出发生在左子树处理之后。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
