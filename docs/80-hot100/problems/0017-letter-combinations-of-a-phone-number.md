# 17. 电话号码的字母组合

[官方题目](https://leetcode.cn/problems/letter-combinations-of-a-phone-number/) · MEDIUM · 官方分类：回溯

## 题意与接口

给定只含 2 到 9 的数字字符串，输出电话按键字母映射的所有组合。接口：`letterCombinations(digits)`。当前官方长度范围为 1..4；本实现额外兼容空串并返回空列表。

约束核对（2026-10-09）：当前中英官方均为长度 1..4、数字 2..9；空串是本实现的额外兼容输入。 [官方来源](https://leetcode.com/problems/letter-combinations-of-a-phone-number/)；[中国站同样核实](https://leetcode.cn/problems/letter-combinations-of-a-phone-number/)。

## 从朴素方法到优化

可以迭代维护所有前缀；回溯只保留当前一路的字符，走到末尾再生成字符串，减少中间完整字符串的存储。

## 核心思路

第 i 层只选择 digits[i] 所对应的字母。完成一个位置后进入 i+1，返回后弹出该字母。

## 手推一个小例子

输入 `"72"`：第一层选 p、q、r、s，第二层选 a、b、c。以 p 开头先得到 pa、pb、pc，再得到 qa、qb、qc 等，共 4×3=12 个。

## 为什么正确

每一层恰对应一个数字位置，候选集合正是该按键的合法字母。所有位置独立组合，搜索树叶子与所有合法字符串一一对应。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0017_letter_combinations_of_a_phone_number.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def letterCombinations(self, digits):
        if not digits:
            return []
        mapping = {"2":"abc", "3":"def", "4":"ghi", "5":"jkl",
                   "6":"mno", "7":"pqrs", "8":"tuv", "9":"wxyz"}
        answer, path = [], []
        def search(index):
            if index == len(digits):
                answer.append("".join(path))
                return
            # 一层只对应一个按键，各位置的选择彼此独立。
            for char in mapping[digits[index]]:
                path.append(char)
                search(index + 1)
                path.pop()
        search(0)
        return answer
```

## 复杂度

n 为数字长度，P 为各按键字母数的乘积。时间 O(nP)，辅助空间 O(n)，输出 O(nP)；最坏 P=4^n。

## 边界与易错点

7 和 9 对应四个字母，不能统一按三个处理。空输入返回 [] 是本地兼容扩展；2026-10-09 核实的中英官方当前都要求非空输入。0、1 不在输入域。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为什么输出复杂度必须包含字符串长度 n？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/letter-combinations-of-a-phone-number/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0017.Letter%20Combinations%20of%20a%20Phone%20Number/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/backtracking/0017-letter-combinations-of-a-phone-number.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/backtracking/0017-letter-combinations-of-a-phone-number.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：[17. 电话号码的字母组合](https://www.bilibili.com/video/BV1yV4y1V7Ug)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：用一位与多位数字画搜索树，解释每层选择集为何由该位置的数字决定。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
