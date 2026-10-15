# 72. 编辑距离

难度：MEDIUM · 分类：多维动态规划

## 题意与接口

接口：`Solution.minDistance(word1: str, word2: str) -> int`。通过插入、删除、替换单个字符，把 word1 变为 word2，求最少操作次数，每次代价都是 1。官方允许空串，长度各至多 500。

约束与规则于 2026-10-09 查阅官方英文题面核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

直接枚举编辑过程有大量重叠。将“把两个前缀变得相同”作为子问题，按最后的编辑动作分类。二维表可保存所有结果；这里用一行加一个旧左上角变量压缩空间。

## 核心思路

D(i,j) 表示前 i 个字符变为前 j 个字符的最少编辑数。若末字符相同，沿用左上角；不同则在上方+1（删除）、左方+1（插入）、左上+1（替换）中取最小。空源串需 j 次插入，空目标需 i 次删除。

## 手推一个小例子

取 word1=`"cat"`、word2=`"cut"`：
1. 空源前缀对应 `[0,1,2,3]`。
2. 读 c 后为 `[1,0,1,2]`。
3. 读 a 后为 `[2,1,1,2]`，其中 a→u 的替换让中间状态为 1。
4. 读 t 后为 `[3,2,2,1]`，最后字符相同，沿用左上角 1。答案 1。

## 为什么正确

对前缀末端的编辑对齐分类：一方末字符不与另一方匹配时，最后一步必可归入删除、插入或替换，对应三个更小前缀，候选都可构造合法编辑过程。若两末字符相同，可以直接匹配这对字符，不增加代价；相同末字符不需要额外编辑。边界为空串时只能逐个插删，递推取最小，按前缀长度归纳得到最少次数。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0072_edit_distance.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        # 插入和删除代价相同，交换两串不改变距离，短串作列。
        if len(word1) < len(word2):
            word1, word2 = word2, word1
        dp = list(range(len(word2) + 1))
        for row, first in enumerate(word1, 1):
            diagonal = dp[0]
            dp[0] = row
            for column, second in enumerate(word2, 1):
                above = dp[column]
                if first == second:
                    dp[column] = diagonal
                else:
                    dp[column] = 1 + min(above, dp[column - 1], diagonal)
                diagonal = above
        return dp[-1]
```

## 复杂度

时间 O(mn+m+n)，其中 m 或 n 为 0 时仍需初始化或逐行推进；两串都非空时通常简写为 O(mn)。辅助空间 O(min(m,n)+1)。

## 边界与易错点

- 两空串距离 0，一空串距离为另一串长度。
- 左方是本行更新后的值，上方和左上方是上一行旧值。
- 这里不包含交换相邻字符操作，不能将 `ab`→`ba` 计为 1。
- 若插入、删除代价不同，交换两串前需重新分析对称性。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0072`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：三个转移分别对应什么实际编辑？如果替换代价变为 2，哪些地方需要改？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：为空前缀初始化编辑次数，再解释增、删、替换各来自哪个状态。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
