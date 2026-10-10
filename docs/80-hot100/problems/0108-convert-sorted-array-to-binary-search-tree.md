# 108. 将有序数组转换为二叉搜索树

[官方题目](https://leetcode.cn/problems/convert-sorted-array-to-binary-search-tree/) · EASY · 官方分类：二叉树

## 题意与接口

把严格递增数组构造成高度平衡的二叉搜索树，返回根。接口：`sortedArrayToBST(nums)`。允许多个正确形状。

约束核对（2026-10-09）：数组长度 1..10000，严格递增；接受任意符合要求的高度平衡 BST。 [官方来源](https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/)

## 从朴素方法到优化

逐个将有序元素插入普通 BST 会退化成链。每次选区间中点为根，使左右子数组大小至多相差一，递归构造可保证平衡。

## 核心思路

用半开下标区间 `[lo,hi)`，不做数组切片。中点建立节点，左右分别递归 `[lo,mid)` 与 `[mid+1,hi)`。

## 手推一个小例子

`[-5,-1,2,6,10]` 选中间 2 为根；左区间选 -1（左 -5），右区间选 10（左 6）。每个子树都由自身中点分割。

## 为什么正确

递增数组使左区间全部小于根、右区间全部大于根；递归子树也是 BST。每次等分元素数量，各子树高度由规模决定，左右高度差至多一，故全树平衡。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0108_convert_sorted_array_to_binary_search_tree.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from examples.hot100.structures import TreeNode

class Solution:
    def sortedArrayToBST(self, nums):
        def build(lo, hi):
            if lo >= hi:
                return None
            # 用半开下标区间而非数组切片，左右规模尽量相等。
            mid = (lo + hi) // 2
            node = TreeNode(nums[mid])
            node.left = build(lo, mid)
            node.right = build(mid + 1, hi)
            return node
        return build(0, len(nums))
```

## 复杂度

时间 O(n)，辅助递归栈 O(log n)，输出节点 O(n)。不切片，避免额外数组复制。

## 边界与易错点

此题构造过程始终平衡，递归深度是对数级，与任意输入树的深链风险不同。测试应验证中序和每个节点平衡，不能只比一种固定树形。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：偶数长度选另一个中点是否仍正确？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/convert-sorted-array-to-binary-search-tree/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0108.Convert%20Sorted%20Array%20to%20Binary%20Search%20Tree/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/binary-tree/0108-convert-sorted-array-to-binary-search-tree.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/binary-tree/0108-convert-sorted-array-to-binary-search-tree.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[108. 将有序数组转换为二叉搜索树](https://www.bilibili.com/video/BV1uR4y1X7qL?share_source=copy_web)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：选定中点后说明左右区间如何划分；用偶数长度检查不同中点选择都能得到平衡树。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
