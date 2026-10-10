# 101. 对称二叉树

[官方题目](https://leetcode.cn/problems/symmetric-tree/) · EASY · 官方分类：二叉树

## 题意与接口

判断一棵二叉树是否关于根轴对称，既比较值也比较空位置。接口：`isSymmetric(root) -> bool`。

约束核对（2026-10-09）：节点数 1..1000；同时比较镜像结构与节点值。 [官方来源](https://leetcode.com/problems/symmetric-tree/)

## 从朴素方法到优化

分别序列化左树和右树也能比较，但容易漏掉空节点且使用完整序列。直接成对检查镜像位置更清晰。

## 核心思路

队列保存应互为镜像的 `(a,b)`。同为空则继续，只有一个为空或值不同则失败；否则加入 `(a.left,b.right)` 和 `(a.right,b.left)`。

## 手推一个小例子

根 5，左右都是 2；左 2 只有右孩子 7，右 2 只有左孩子 7。比较 (2,2)，再比较 (None,None)、(7,7)，都匹配，因此对称。

## 为什么正确

两棵子树镜像当且仅当根值相同，且左对右、右对左递归镜像。队列逐一验证这些必要充分条件；全部通过恰是对称。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0101_symmetric_tree.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from collections import deque

class Solution:
    def isSymmetric(self, root):
        if root is None:
            return True
        queue = deque([(root.left, root.right)])
        while queue:
            a, b = queue.popleft()
            if a is None and b is None:
                continue
            if a is None or b is None or a.val != b.val:
                return False
            # 镜像比较必须交叉配对，空位置也参与结构检查。
            queue.append((a.left, b.right))
            queue.append((a.right, b.left))
        return True
```

## 复杂度

时间 O(n)，辅助队列 O(w)，w 为最大层宽，最坏 O(n)。

## 边界与易错点

只检查每层值回文不能可靠刻画结构。两个缺失孩子要当作成功匹配，而非失败。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：举一个“每层值对称但空节点结构不对称”的例子。

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/symmetric-tree/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0101.Symmetric%20Tree/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0101.symmetric-tree.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0101.symmetric-tree.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[101. 对称二叉树](https://www.bilibili.com/video/BV1ue4y1Y7Mf)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：把成对节点的比较方向画出来，检查外侧与内侧是否交叉匹配，并包含单侧为空的情况。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
