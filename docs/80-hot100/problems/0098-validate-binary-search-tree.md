# 98. 验证二叉搜索树

难度：MEDIUM · 分类：二叉树

## 题意与接口

判断每个节点的整个左子树均严格小于它、整个右子树均严格大于它。接口：`isValidBST(root) -> bool`。

约束核对（2026-10-09）：节点数 1..10000，值在有符号 32 位整数范围；左右子树分别严格小于/大于根。

## 从朴素方法到优化

仅比较根与直接孩子会漏掉跨层违规。给每个节点传上下界可以解决；另一等价办法是验证完整中序序列严格递增。

## 核心思路

迭代中序遍历，不保存完整结果，只记上一个访问的值 prev。若当前值不大于 prev，则不是严格 BST。

## 手推一个小例子

根 7，左 3，右 10，而 10 的左孩子是 6。父子局部比较都看似合法，但中序为 `[3,7,6,10]`，在 7→6 处下降，因此返回 False。

## 为什么正确

合法 BST 的中序严格递增。反过来，中序严格递增意味着每个节点左子树的全部值都在它之前且更小，右子树全部值都在它之后且更大，因此满足全局定义。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0098_validate_binary_search_tree.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def isValidBST(self, root):
        stack, cur, prev = [], root, None
        while cur or stack:
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            # BST 中序必须严格递增，重复值也应拒绝。
            if prev is not None and cur.val <= prev:
                return False
            prev = cur.val
            cur = cur.right
        return True
```

## 复杂度

时间 O(n)，辅助栈 O(h)。

## 边界与易错点

必须严格递增，重复值不合法。用 None 表示尚无前值，不能用可能出现的整数哨兵。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为什么只验证父子大小不足够？中序判断成立需要二叉树满足什么结构前提？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：用深层节点违反祖先边界的例子检查算法，说明只比较直接父子为什么不够。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
