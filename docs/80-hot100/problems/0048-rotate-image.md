# 48. 旋转图像

[官方题目](https://leetcode.cn/problems/rotate-image/) · MEDIUM · 官方分类：矩阵

## 题意与接口

把n×n方阵顺时针旋转90度。`rotate(matrix)` 原地修改并返回None，不分配另一个矩阵。

## 从朴素方法到优化

新建矩阵并按(i,j)→(j,n-1-i)放置需要 O(n²)额外空间。该映射可拆成转置(i,j)→(j,i)，再将每一行反转。

## 核心思路

仅交换主对角线上方与下方对应格完成转置，然后调用各行原地reverse。每个跨对角格只交换一次，行反转使用常数辅助空间。

## 手推一个小例子

[[1,4],[7,9]]先转置成[[1,7],[4,9]]，再反转两行得到[[7,1],[9,4]]；原左下角7到左上角，符合顺时针。

## 为什么正确

转置后原(i,j)位于(j,i)；反转该行后列i变成n-1-i，最终位置(j,n-1-i)恰是90度顺时针映射。两个变换都是一一对应的原地交换，不丢失元素。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0048_rotate_image.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def rotate(self, matrix: list[list[int]]) -> None:
        n = len(matrix)
        for row in range(n):
            # 只交换对角线一侧，避免同一对称格交换两次。
            for col in range(row + 1, n):
                matrix[row][col], matrix[col][row] = matrix[col][row], matrix[row][col]
        for row in matrix:
            row.reverse()
```

## 复杂度

时间 O(n²)，辅助空间 O(1)。Python list.reverse是原地操作，与row[::-1]复制不同。

## 边界与易错点

- 内层必须从row+1开始，否则对称格交换两次会抵消。
- 先转置再反转每行是顺时针；顺序/方向改动会得到另一种旋转。
- 原题要求方阵；矩形旋转会改变形状，不属于本接口。

## 本地测试与复习

测试1×1、奇偶边长；随机与坐标映射的新矩阵对拍，并验证四次旋转还原。

复习：逆时针90度应怎样分解？连续旋转4次为什么是一个好的性质测试？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/rotate-image/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0048.Rotate%20Image/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：先画出一个元素旋转后的坐标，再验证转置加反转的方向；确认整个过程是否原地。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
