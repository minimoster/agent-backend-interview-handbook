# 114. 二叉树展开为链表

[官方题目](https://leetcode.cn/problems/flatten-binary-tree-to-linked-list/) · MEDIUM · 官方分类：二叉树

## 题意与接口

原地把树展开为沿 right 前进的链，顺序为先序遍历，所有 left 置空。接口：`flatten(root) -> None`。

约束核对（2026-10-09）：节点数 0..2000；同一批 TreeNode 原地按先序排列，left 全空，right 为后继。 [官方来源](https://leetcode.com/problems/flatten-binary-tree-to-linked-list/)

## 从朴素方法到优化

先序遍历收集节点再重连要 O(n) 空间。原地方法在每个有左子树的节点处，把原右子树接到左子树最右端，再把左子树整体移到右侧。

## 核心思路

cur 有左子树时，找到其中沿 right 的末端 predecessor，让它指向原右子树；cur.right 改为 cur.left，再清空 cur.left。最后沿新的 right 继续。

## 手推一个小例子

根 5，左子树 2（右孩子 3），右孩子 9。先把 3.right 接 9，再让 5.right=2、5.left=None；后续处理得到 `5→2→3→9`。

## 为什么正确

先序顺序为根、完整左子树、完整右子树。把右子树挂到左子树右边界末端，保证在沿途展开完左子树后才能进入原右子树；每次变换保留这三个部分的先序相对次序。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0114_flatten_binary_tree_to_linked_list.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def flatten(self, root) -> None:
        cur = root
        while cur:
            if cur.left:
                predecessor = cur.left
                while predecessor.right:
                    predecessor = predecessor.right
                # 原右子树接到左子树末端，保留先序的左右相对顺序。
                predecessor.right = cur.right
                cur.right = cur.left
                cur.left = None
            cur = cur.right
```

## 复杂度

时间 O(n)，辅助空间 O(1)。内层扫描的原右向边属于被挂接左子树的右边界；这些边不会在后续另一次这样的边界搜索中重复扫描，整体摊还线性。

## 边界与易错点

要求原地并返回 None。清空 left 前先保存/接好左子树。仅移动值不满足重建指针结构的目的。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：如何用先序序列不变证明正确性？为何嵌套 while 仍可为 O(n)？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/flatten-binary-tree-to-linked-list/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0114.Flatten%20Binary%20Tree%20to%20Linked%20List/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：画出重连后的引用关系，确认每个节点只出现一次、左指针清空且先序顺序保持。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
