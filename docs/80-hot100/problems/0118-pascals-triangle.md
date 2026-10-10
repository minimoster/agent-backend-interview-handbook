# 118. 杨辉三角

[官方题目](https://leetcode.cn/problems/pascals-triangle/) · EASY · 官方分类：动态规划

## 题意与接口

接口：`Solution.generate(numRows: int) -> list[list[int]]`。生成杨辉三角前 numRows 行；每行两端是 1，内部元素等于上一行相邻两个元素之和。官方行数为 1 至 30。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/pascals-triangle/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

独立用递归计算每个格子会重复计算祖先格子；按行构造可复用已经求出的上一行。虽然可以用组合数公式，本题直接递推更贴合结构，也无需阶乘。

## 核心思路

第 r 行使用从 0 开始的行号，长度为 r+1。先创建全 1 的新列表，再填下标 1 至 r−1 的内部位置。把完整的新行追加到结果，每行必须是不同的列表。

## 手推一个小例子

取 numRows=4：
1. r=0，新行 `[1]`。
2. r=1，没有内部格子，得到 `[1,1]`。
3. r=2，内部为 1+1，得到 `[1,2,1]`。
4. r=3，内部依次为 1+2、2+1，得到 `[1,3,3,1]`。

## 为什么正确

第一行满足定义。若上一行所有格子都正确，新行两端由初始化保证为 1，内部每个位置严格按定义相加，所以新行也正确。归纳可知依次追加的所有行都正确且顺序完整。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0118_pascals_triangle.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def generate(self, numRows: int) -> list[list[int]]:
        triangle = []
        for row_index in range(numRows):
            row = [1] * (row_index + 1)  # 每行独立，两端保持为 1。
            for column in range(1, row_index):
                row[column] = (
                    triangle[-1][column - 1] + triangle[-1][column]
                )
            triangle.append(row)
        return triangle
```

## 复杂度

共生成 r(r+1)/2 个数，时间 O(r²)，结果空间 O(r²)。正在构造的行是最终输出的一部分，排除输出后只有常数个引用和计数器；若把待追加行单独算工作内存，则至多 O(r)。

## 边界与易错点

- 不能用同一个可变列表反复追加，否则后续更新会影响旧行。
- 新行 r+1 个元素，内部循环不包含末尾。
- 三角形并非矩形，不能用共享行的二维列表初始化。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0118`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：如果只求最后一行，如何做到 O(r) 空间？原地更新这一行为什么要从右向左？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/pascals-triangle/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0118.Pascal's%20Triangle/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：逐行检查边缘的两个 1 与内部相邻两数之和，避免复用同一个列表造成所有行一起变化。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
