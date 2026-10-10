# 20. 有效的括号

[官方题目](https://leetcode.cn/problems/valid-parentheses/) · EASY · 官方分类：栈

## 题意与接口

判断只含三种括号的字符串是否完整、按正确嵌套顺序配对。`isValid(s)`返回布尔值。

## 从朴素方法到优化

反复删除相邻配对括号可以理解题意，但重复扫描可能O(n²)。最近打开的括号必须最先关闭，天然对应后进先出栈。

## 核心思路

左括号入栈；遇右括号，要求栈非空且栈顶正好是其对应左括号，然后弹出。结束时栈必须空。

## 手推一个小例子

"{[()]}"依次压入{、[、(；遇)弹(，遇]弹[，遇}弹{，栈空所以有效。"{[}]"遇}时栈顶[不匹配，应立即失败。

## 为什么正确

处理任意前缀后，栈恰保存尚未闭合的左括号，顺序与打开顺序相同。右括号只能关闭最近未闭合的左括号，任何空栈或类型不符都不可被后续字符修复；全部闭合且无剩余即合法。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0020_valid_parentheses.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def isValid(self, s: str) -> bool:
        matching = {')': '(', ']': '[', '}': '{'}
        # 栈顶是最近一个尚未闭合的左括号。
        stack = []
        for ch in s:
            if ch in '([{':
                stack.append(ch)
            elif ch not in matching or not stack or stack.pop() != matching[ch]:
                return False
        return not stack
```

## 复杂度

时间O(n)，辅助空间O(n)，最坏全是左括号。

## 边界与易错点

- 只统计左右括号数量相同不够，必须检查嵌套与类型。
- 右括号出现时可能栈空，应先检查再pop。
- 结束后还有左括号也必须判False。

## 本地测试与复习

测试空串扩展、错误嵌套、右括号开头、剩余左括号；随机与反复删除合法相邻对的参考法对拍。

复习：计数器为什么能判断单种括号平衡，却无法替代三种括号的栈？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/valid-parentheses/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0020.Valid%20Parentheses/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0020.valid-parentheses.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0020.valid-parentheses.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[20. 有效的括号](https://www.bilibili.com/video/BV1AF411w78g)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：检查遇到右括号时栈为空、类型不匹配与扫描后栈非空三种失败情况。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
