# 226. 翻转二叉树

[官方题目](https://leetcode.cn/problems/invert-binary-tree/) · EASY · 官方分类：二叉树

## 题意与接口

将每个节点的左右子树交换，原地翻转整棵二叉树并返回根。接口：`invertTree(root)`。

约束核对（2026-10-09）：节点数 0..100；翻转树并返回根。 [官方来源](https://leetcode.com/problems/invert-binary-tree/)

## 从朴素方法到优化

可以新建镜像树，但那会占用 O(n) 输出节点。目标允许原地修改，只需访问每个节点并交换两个引用。

## 核心思路

显式栈遍历；弹出节点后同时交换左右孩子，再把非空孩子入栈。访问顺序不影响最终镜像结构。

## 手推一个小例子

根 6，左 2（孩子 1、4），右 8。根交换后左为 8、右为 2；再交换 2 的孩子为 4、1，得到镜像。

## 为什么正确

镜像树定义为“根不变，镜像后的右子树放左边，镜像后的左子树放右边”。算法在所有节点交换两个孩子，等价于递归应用这一定义；没有新建或丢弃节点。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0226_invert_binary_tree.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def invertTree(self, root):
        stack = [root] if root else []
        while stack:
            node = stack.pop()
            # 同时赋值保留两边旧引用，再继续处理它们。
            node.left, node.right = node.right, node.left
            if node.left:
                stack.append(node.left)
            if node.right:
                stack.append(node.right)
        return root
```

## 复杂度

时间 O(n)，辅助栈 O(h)，最坏 O(n)。原地修改树。

## 边界与易错点

必须同时保存两边引用，不能先覆盖左孩子再读取旧值。对同一棵树翻转两次应恢复原结构。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：翻转 BST 后中序仍递增吗？为什么？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/invert-binary-tree/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0226.Invert%20Binary%20Tree/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0226.invert-binary-tree.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0226.invert-binary-tree.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[226. 翻转二叉树](https://www.bilibili.com/video/BV1sP4y1f7q7)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：逐节点检查交换左右孩子后，遍历是否会漏掉或重复访问某个子树。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
