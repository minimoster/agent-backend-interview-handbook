# 236. 二叉树的最近公共祖先

[官方题目](https://leetcode.cn/problems/lowest-common-ancestor-of-a-binary-tree/) · MEDIUM · 官方分类：二叉树

## 题意与接口

在普通二叉树中返回两个已存在且不同节点 p、q 的最近公共祖先，节点自身也可算祖先。接口：`lowestCommonAncestor(root, p, q)`。

约束核对（2026-10-09）：节点数 2..100000，值唯一；p、q 不同且均存在，节点自身也是祖先。 [官方来源](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/)

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

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/lowest-common-ancestor-of-a-binary-tree/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0236.Lowest%20Common%20Ancestor%20of%20a%20Binary%20Tree/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/binary-tree/0236-lowest-common-ancestor-of-a-binary-tree.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/binary-tree/0236-lowest-common-ancestor-of-a-binary-tree.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[236. 二叉树的最近公共祖先](https://www.bilibili.com/video/BV1jd4y1B7E2)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：区分节点身份与值，说明左右子树分别命中时为什么当前节点就是最近公共祖先。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
