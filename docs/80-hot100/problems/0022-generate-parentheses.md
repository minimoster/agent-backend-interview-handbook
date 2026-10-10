# 22. 括号生成

[官方题目](https://leetcode.cn/problems/generate-parentheses/) · MEDIUM · 官方分类：回溯

## 题意与接口

生成 n 对括号的全部合法括号串。接口：`generateParenthesis(n)`。每个前缀都不能出现右括号多于左括号。

约束核对（2026-10-09）：n 为 1..8；生成所有 n 对合法括号串。 [官方来源](https://leetcode.com/problems/generate-parentheses/)

## 从朴素方法到优化

枚举所有 2^(2n) 个括号串后再验证很浪费。构造过程中维护左右数量，立即剪去永远不能补救的非法前缀。

## 核心思路

左括号只要 left<n 就能加；右括号只有 right<left 时才能加。当前长度达到 2n 时保存字符串。

## 手推一个小例子

n=2：从 `(` 出发，可继续 `((`，之后只能补两个右括号得 `(())`；也可走 `()`，再补 `()` 得 `()()`。开头不能放 `)`。

## 为什么正确

规则保证任意前缀 left≥right，结束时左右各 n，因此输出合法。反过来任意合法串的每个前缀都满足这两个可选条件，故它对应的分支不会被剪掉。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0022_generate_parentheses.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def generateParenthesis(self, n):
        answer, path = [], []
        def search(left, right):
            if len(path) == 2 * n:
                answer.append("".join(path))
                return
            if left < n:
                path.append("(")
                search(left + 1, right)
                path.pop()
            # 右括号只能关闭尚未配对的左括号。
            if right < left:
                path.append(")")
                search(left, right + 1)
                path.pop()
        search(0, 0)
        return answer
```

## 复杂度

令 C_n 为第 n 个 Catalan 数（合法串数量）。时间 O(n·C_n)，辅助空间 O(n)，输出 O(n·C_n)。

## 边界与易错点

不能仅在最后验证左右总数相等；例如 `)(` 总数相等但非法。复制结果用 join，撤销后不能保存 path 引用。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：right<left 与 right<n 有什么区别？为何后者不足以保证合法？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/generate-parentheses/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0022.Generate%20Parentheses/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：在生成过程中限制已用左右括号数，解释哪些状态可直接剪掉，而不是生成后再检查。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
