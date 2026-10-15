# 5. 最长回文子串

难度：MEDIUM · 分类：多维动态规划

## 题意与接口

接口：`Solution.longestPalindrome(s: str) -> str`。返回最长的连续回文片段；有多个最长答案时，任意一个都合法。官方字符串非空，长度至多 1000，由数字和英文字母构成。

约束与规则于 2026-10-09 查阅官方英文题面核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

枚举子串再逐字符判断需要 O(n³)。二维 DP 可用“端点相同且内部是回文”在 O(n²) 时间、O(n²) 空间内判断。本实现进一步利用回文都有中心，直接向两侧扩展，保留 O(n²) 时间并将工作空间降到常数。

## 核心思路

每个位置尝试两类中心：单字符中心 (i,i) 对应奇数长度，两个字符间的中心 (i,i+1) 对应偶数长度。扩展时只比较字符，不创建子串；当扩展停止后，合法区间为 (left,right)，即 s[left+1:right]。仅记录最好区间，最后切片一次。

## 手推一个小例子

取 `s="xaabac"`：
1. 中心 (1,2) 的两个 a 相等，得到 `aa`；向外 x 与 b 不同，停止。
2. 中心 (3,3) 是 b；向外比较下标 2 和 4 的 a，扩成 `aba`。
3. 再向外下标 1 为 a、5 为 c，不同，停止。
4. 其他中心无法超过长度 3，返回 `aba`。

## 为什么正确

任何回文串都有唯一的单字符或双字符中心。本算法枚举全部这些中心；从中心出发，只要两侧相同就保持回文，遇到不同或边界时不可能继续变长。因此每个中心的最长回文都被发现，取其中最长就覆盖全局最优。只在严格更长时更新，不影响存在多个答案时的合法性。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0005_longest_palindromic_substring.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def longestPalindrome(self, s: str) -> str:
        best_start = 0
        best_length = 0
        for center in range(len(s)):
            for left, right in ((center, center), (center, center + 1)):
                while left >= 0 and right < len(s) and s[left] == s[right]:
                    left -= 1
                    right += 1
                # 停止时两指针恰在合法回文区间之外。
                length = right - left - 1
                if length > best_length:
                    best_start = left + 1
                    best_length = length
        return s[best_start:best_start + best_length]
```

## 复杂度

最坏时间 O(n²)，例如所有字符相同。除返回结果外辅助空间 O(1)；最终切片长为 k，需要 O(k) 返回空间与复制时间，k≤n。若在每次扩展时创建切片，不能再沿用这一复杂度说明。

## 边界与易错点

- 奇数、偶数中心都要考虑。
- 子串需要连续，不能混淆为最长回文子序列。
- 测试多解时应验证回文性质、出现位置与最优长度，不能硬编码唯一文本。
- 大小写按原字符比较，不自动忽略大小写。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0005`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：二维 DP 应按什么顺序计算区间？中心扩展在哪类输入上达到平方级时间？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：分别枚举奇数与偶数回文中心，检查停止边界并说明怎样从区间恢复子串。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
