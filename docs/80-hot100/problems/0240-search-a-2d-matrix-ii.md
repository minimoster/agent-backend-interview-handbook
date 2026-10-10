# 240. 搜索二维矩阵 II

[官方题目](https://leetcode.cn/problems/search-a-2d-matrix-ii/) · MEDIUM · 官方分类：矩阵

## 题意与接口

矩阵每行从左到右递增、每列从上到下递增，判断目标是否存在。`searchMatrix(matrix,target)` 返回布尔值，不修改矩阵；不保证跨行完全有序。

## 从朴素方法到优化

逐行二分可用 O(m log n)，暴力为 O(mn)。从右上角开始，一个比较就能完整排除一行或一列。

## 核心思路

右上角元素大于目标时，该列下面更大，可以删掉这一列，指针左移；小于目标时，该行左边更小，可以删掉这一行，指针下移。

## 手推一个小例子

矩阵[[1,4,8],[2,5,9],[3,7,11]]找7：右上8过大左移到4；4过小下移到5；5过小下移到7，找到。

## 为什么正确

候选区域始终是当前行及以下、当前列及左侧组成的矩形。每次依据行列有序性，只删除绝不包含目标的整行/整列，所以若目标存在，它始终留在候选区内；区域为空即可判无解。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0240_search_a_2d_matrix_ii.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def searchMatrix(self, matrix: list[list[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False
        row, col = 0, len(matrix[0]) - 1
        while row < len(matrix) and col >= 0:
            value = matrix[row][col]
            if value == target:
                return True
            # 太大时本列下方更大，整列都可排除。
            if value > target:
                col -= 1
            else:
                row += 1
        return False
```

## 复杂度

时间 O(m+n)，辅助空间 O(1)。指针至多下移m次、左移n次。

## 边界与易错点

- 不能把矩阵整体展平后二分，行之间不保证前行最大值小于后行最小值。
- 左上角无法凭一次比较排除唯一一侧，右上或左下才合适。
- 重复值不破坏非递减版本的正确性。

## 本地测试与复习

测试重复、目标在四角、低于最小或高于最大；随机生成行列有序矩阵，与全表查找对拍。

复习：从左下角出发的两个移动方向是什么？与第74题的前提有什么不同？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/search-a-2d-matrix-ii/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0240.Search%20a%202D%20Matrix%20II/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：比较每行有序与整体有序的差别；解释从右上角移动一步能排除哪一行或哪一列。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
