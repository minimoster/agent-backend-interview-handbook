# 230. 二叉搜索树中第 K 小的元素

[官方题目](https://leetcode.cn/problems/kth-smallest-element-in-a-bst/) · MEDIUM · 官方分类：二叉树

## 题意与接口

返回合法 BST 中按升序第 k 小的值，k 从 1 开始且题目保证有效。接口：`kthSmallest(root, k) -> int`。

约束核对（2026-10-09）：1<=k<=节点数<=10000；k 从 1 开始，输入为 BST。 [官方来源](https://leetcode.com/problems/kth-smallest-element-in-a-bst/)

## 从朴素方法到优化

遍历全部节点排序是 O(n log n)，但 BST 中序已按序。找到第 k 个就提前返回，无需保存或排序完整序列。

## 核心思路

迭代中序，每弹出一个节点就消耗一个名额；k 减到 0 时返回当前值。

## 手推一个小例子

BST 的中序为 `[1,4,6,9,12]`，k=3：访问 1 后剩 2，访问 4 后剩 1，访问 6 后剩 0，直接返回 6，无需访问 9、12。

## 为什么正确

中序访问顺序就是 BST 的升序排名。每次减一恰好计数一个更靠前的节点，第 k 次访问的节点定义上就是第 k 小。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0230_kth_smallest_element_in_a_bst.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def kthSmallest(self, root, k):
        stack, cur = [], root
        while cur or stack:
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            # 弹栈即完成下一次中序访问，排名从 1 开始。
            k -= 1
            if k == 0:
                return cur.val
            cur = cur.right
        raise ValueError("k must be within the tree size")
```

## 复杂度

时间 O(h+k)，最坏 O(n)；辅助空间 O(h)。

## 边界与易错点

k 是排名，不是数组下标。输入需为 BST。频繁查询可增强节点维护子树大小，但更新时也必须维护计数。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为什么寻找最小值也可能花 O(h) 而非 O(1)？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/kth-smallest-element-in-a-bst/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0230.Kth%20Smallest%20Element%20in%20a%20BST/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：解释中序顺序为何对应 BST 排名；检查 k 的计数起点与提前停止条件。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
