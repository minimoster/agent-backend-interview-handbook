# 236. 二叉树的最近公共祖先

难度：MEDIUM · 分类：二叉树

## 题意与接口

在普通二叉树中返回两个已存在且不同节点 p、q 的最近公共祖先，节点自身也可算祖先。接口：`lowestCommonAncestor(root, p, q)`。

约束核对（2026-10-09）：节点数 2..100000，值唯一；p、q 不同且均存在，节点自身也是祖先。

## 从朴素方法到优化

从根分别搜索两条路径再比公共前缀可行。记录每个节点父亲后，可以先存 p 的全部祖先，再从 q 往上找首次落入集合的节点，避免深递归。

## 核心思路

显式 DFS 建父映射，直到 p、q 都发现。p 向根走加入集合；q 向根走，第一个集合成员即答案。这里比较节点对象而非值。

## 手推一个小例子

根 8，左 4（孩子 2、6），右 12。p=2 的祖先为 {2,4,8}；q=6 向上依次 6、4，在 4 首次命中，返回 4。若 q=4，则直接返回 q。

## 为什么正确

p 的集合恰包含它及所有祖先。q 向上访问顺序从深到浅，因此第一个同时属于 p 祖先集合的节点，是所有公共祖先中深度最大者，即最近公共祖先。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0236_lowest_common_ancestor_of_a_binary_tree.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def lowestCommonAncestor(self, root, p, q):
        if root is None:
            return None
        parent, stack = {root: None}, [root]
        while p not in parent or q not in parent:
            node = stack.pop()
            for child in (node.left, node.right):
                if child:
                    parent[child] = node
                    stack.append(child)
        ancestors = set()
        while p is not None:
            ancestors.add(p)
            p = parent[p]
        # 从 q 由深到浅找，首次命中即最深的公共祖先。
        while q not in ancestors:
            q = parent[q]
        return q
```

## 复杂度

时间 O(n)，辅助空间 O(n)，用于父映射、祖先集合和栈。

## 边界与易错点

这是普通二叉树，不能使用 BST 大小剪枝。官方保证两个节点存在；若设计通用库，需要额外处理不存在的节点。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：如果树经常变化，缓存父映射时需要维护哪些一致性？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：区分节点身份与值，说明左右子树分别命中时为什么当前节点就是最近公共祖先。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
