# 74. 搜索二维矩阵

[官方题目](https://leetcode.cn/problems/search-a-2d-matrix/) · MEDIUM · 官方分类：二分查找

## 题意与接口

矩阵每行有序，且每行首元素大于上一行末元素，查找目标是否存在。`searchMatrix(matrix,target)`返回布尔值，不修改输入。

## 从朴素方法到优化

逐格扫描O(mn)。行之间严格衔接有序，逻辑上就是长度mn的有序数组，但没必要真的展平成新数组。

## 核心思路

对逻辑下标二分；下标mid映射到行mid//cols、列mid%cols。找到第一个不小于目标的逻辑位置后核对相等。

## 手推一个小例子

[[1,4,7],[9,13,18]]查13：总长6，mid=3对应9，排除左半；mid=5对应18，右端缩到5；mid=4对应13，得到命中。

## 为什么正确

行内有序与跨行衔接共同保证逻辑一维序列有序，因此普通lower_bound的不变量直接成立。整除和取余是一一对应的位置映射，不影响比较结果。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0074_search_a_2d_matrix.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def searchMatrix(self, matrix: list[list[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False
        rows, cols = len(matrix), len(matrix[0])
        left, right = 0, rows * cols
        while left < right:
            middle = (left + right) // 2
            # 逻辑展平，不实际复制整个矩阵。
            value = matrix[middle // cols][middle % cols]
            if value < target:
                left = middle + 1
            else:
                right = middle
        return left < rows * cols and matrix[left // cols][left % cols] == target
```

## 复杂度

时间O(log(mn))，辅助空间O(1)，没有分配展平数组。

## 边界与易错点

- 不能把第240题只有行列分别有序的矩阵代入本算法。
- 商和余数都使用列数cols，不是行数rows。
- lower_bound可能等于mn，访问前必须检查范围。

## 本地测试与复习

测试单行单列、缺失目标、跨行分界；随机生成整体有序矩阵，与全表查找对拍。

复习：为什么第一行末元素与第二行首元素的关系是决定性前提？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/search-a-2d-matrix/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0074.Search%20a%202D%20Matrix/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0074.search-a-2d-matrix.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0074.search-a-2d-matrix.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：写出一维下标到行列的映射，说明整体有序条件为何允许一次二分。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
