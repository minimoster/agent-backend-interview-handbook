# 199. 二叉树的右视图

[官方题目](https://leetcode.cn/problems/binary-tree-right-side-view/) · MEDIUM · 官方分类：二叉树

## 题意与接口

从树的右侧看，返回每一层最右边的可见节点值。接口：`rightSideView(root) -> list[int]`。

约束核对（2026-10-09）：节点数 0..100；按从上到下返回右侧可见值。 [官方来源](https://leetcode.com/problems/binary-tree-right-side-view/)

## 从朴素方法到优化

右视图不是一直走右孩子：右子树缺失时左子树深处也会露出。先按层遍历，再选每层最后一个节点最直接。

## 核心思路

广度优先每层固定长度，孩子按左后右入队；本层最后弹出的节点就是最右节点。

## 手推一个小例子

根 1，左 4、右 8；4 的左孩子 6，而 8 无孩子。前两层看见 1、8，第三层只剩 6，结果 `[1,8,6]`。

## 为什么正确

层序队列维护每层从左到右的顺序，因此每层最后一项是该层最右位置，恰好遮住同层其他节点。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0199_binary_tree_right_side_view.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from collections import deque

class Solution:
    def rightSideView(self, root):
        if root is None:
            return []
        answer, queue = [], deque([root])
        while queue:
            width = len(queue)
            for i in range(width):
                node = queue.popleft()
                # 左孩子先入队，因此本层最后一项就是最右侧。
                if i == width - 1:
                    answer.append(node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
        return answer
```

## 复杂度

时间 O(n)，辅助队列 O(w)，输出 O(h)。

## 边界与易错点

仅沿 right 指针走会漏层。若改变孩子入队顺序，选择每层最后节点的规则也要同步调整。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：右优先 DFS 为什么能用“每层第一次访问”替代层序？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/binary-tree-right-side-view/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0199.Binary%20Tree%20Right%20Side%20View/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/binary-tree/0102-binary-tree-level-order-traversal.html#_199-%E4%BA%8C%E5%8F%89%E6%A0%91%E7%9A%84%E5%8F%B3%E8%A7%86%E5%9B%BE)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/binary-tree/0102-binary-tree-level-order-traversal.html#python-3)。可与上面的本仓库原创实现对照。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。
- 相关主题视频：[102. 二叉树的层序遍历](https://www.bilibili.com/video/BV1GY4y1u7b2)。仅用于方法迁移，不计为本题专属配套视频。
- 匹配说明：讲解和 rightSideView 实现在102文章的199独立区块；102层序视频只归为相关主题。

自主复习提示：对比层序遍历取每层最后一个节点与右优先 DFS，说明两者如何保证“最右可见”。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
