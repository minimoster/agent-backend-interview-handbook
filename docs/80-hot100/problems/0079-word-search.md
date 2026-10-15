# 79. 单词搜索

难度：MEDIUM · 分类：回溯

## 题意与接口

判断网格中是否存在一条上下左右相邻路径，按顺序拼出 word；同一次路径不能重复使用格子。接口：`exist(board, word)`，本实现搜索后恢复网格。

约束核对（2026-10-09）：行列 1..6，词长 1..15；字符是大小写英文字母，同一路径不能重复使用格子。

## 从朴素方法到优化

枚举所有路径再拼字符串浪费大量不匹配分支。逐个字符匹配，遇到不同就剪枝，并在当前路径上临时标记已使用格。

## 核心思路

每个格子都尝试作起点。匹配第 i 个字符后临时设为 None，只递归四邻查 i+1；返回前恢复原字符，包括成功返回的路径。

## 手推一个小例子

网格 `AB / CD`，word=`ABD`：从 A 匹配，再向右 B，再向下 D 成功。word=`ABA` 不成功，因为最后 A 只能回到已用起点；该格在当前分支被标记。

## 为什么正确

递归状态表示已匹配 word[:i] 且这些格均被标记。只走未标记且字符正确的四邻，保持路径合法；枚举所有起点和四邻选择涵盖全部可能路径。返回恢复使不同分支互不影响。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0079_word_search.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def exist(self, board, word):
        if not word:
            return True
        if not board or not board[0]:
            return False
        rows, cols = len(board), len(board[0])
        if len(word) > rows * cols:
            return False
        def search(r, c, index):
            if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[index]:
                return False
            if index == len(word) - 1:
                return True
            original = board[r][c]
            board[r][c] = None  # 输入是字符，None 可作当前路径标记
            found = (search(r-1, c, index+1) or search(r+1, c, index+1)
                     or search(r, c-1, index+1) or search(r, c+1, index+1))
            board[r][c] = original
            return found
        return any(search(r, c, 0) for r in range(rows) for c in range(cols))
```

## 复杂度

R×C 网格、词长 L。粗上界时间 O(RC·4^L)，不回头使更紧的常见上界为 O(RC·3^L)（吸收第一步常数）；辅助栈 O(L)，无额外访问矩阵。

## 边界与易错点

标记仅针对当前路径，不能全局永久 visited。成功后也要恢复输入。题目词长较短；若扩展成很长词库搜索，需另外设计显式栈与 Trie。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为何四个方向的短路 or 不会漏掉成功路径？为什么不能复用上一条失败路径的 visited 集合？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：手推一条失败路径如何恢复访问状态，检查同一个格子不能在一次路径中重复使用。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
