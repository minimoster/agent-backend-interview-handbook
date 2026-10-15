# 131. 分割回文串

难度：MEDIUM · 分类：回溯

## 题意与接口

把字符串切成若干非空片段，使每片都是回文，返回所有切法。接口：`partition(s)`。

约束核对（2026-10-09）：字符串长度 1..16，只含小写英文字母；每个片段必须非空且回文。

## 从朴素方法到优化

枚举切割并每次重新检查片段回文，会重复检查同一区间。先做二维回文 DP，再回溯枚举每一刀，候选是否合法可 O(1) 查询。

## 核心思路

从短区间依赖到长区间：`pal[i][j] = s[i]==s[j] 且（长度<=2 或 pal[i+1][j-1]）`。回溯从 start 枚举 end，只选择回文区间；到 n 时复制切分路径。

## 手推一个小例子

`s="abba"`：DP 确认 `bb` 和 `abba` 为回文。回溯先走 `a|b|b|a`，再走 `a|bb|a`，根层还可直接选择 `abba`，共三种。

## 为什么正确

DP 由回文的两端相等且内部回文这一定义归纳成立。任何完整切分对应唯一的一串结束下标；回溯恰枚举其中所有片段均为回文的路径，故正确且无重复。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0131_palindrome_partitioning.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def partition(self, s):
        n = len(s)
        pal = [[False] * n for _ in range(n)]
        # i 递减保证内区间 pal[i+1][j-1] 已求出。
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i+1][j-1])
        answer, path = [], []
        def search(start):
            if start == n:
                answer.append(path.copy())
                return
            for end in range(start, n):
                # 只沿回文片段切一刀，回文查询本身 O(1)。
                if pal[start][end]:
                    path.append(s[start:end+1])
                    search(end + 1)
                    path.pop()
        search(0)
        return answer
```

## 复杂度

最坏时间 O(n²+n·2^n)，包含预处理、枚举、切片和结果复制。辅助空间 O(n²) 的 DP 加 O(n) 路径/栈；输出最坏 O(n·2^n)。

## 边界与易错点

区间端点 j 在这里含尾，切片需 end+1。DP 要保证内区间先算；i 递减、j 递增满足依赖。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：全由同一字符组成的长度 n 字符串有多少种切法？为何最多 2^(n-1)？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：区分子串回文判定与枚举切分，检查单字符、整串回文和多个相邻切分的情况。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
