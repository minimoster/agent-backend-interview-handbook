# 2. 两数相加

[官方题目](https://leetcode.cn/problems/add-two-numbers/) · MEDIUM · 官方分类：链表

## 题意与接口

两条非空链表以低位在前的方式保存非负整数，每个节点一个十进制数字，返回同样表示的和。接口：`addTwoNumbers(l1, l2)`。

约束核对（2026-10-09）：每条链长度 1..100，节点值 0..9，低位在前；除数字 0 外无高位前导零。 [官方来源](https://leetcode.com/problems/add-two-numbers/)

## 从朴素方法到优化

先转成整数相加会掩盖逐位运算，也依赖任意精度整数处理很长数字。直接模拟竖式加法，只需保存进位。

## 核心思路

每轮把两条链当前位（不存在记 0）和 carry 相加。`divmod(total, 10)` 分别得到下一轮进位和本轮结果位；两条都结束但仍有进位时再创建节点。

## 手推一个小例子

`8→6` 表示 68，`7→4→1` 表示 147。个位 8+7=15 写 5 进 1；十位 6+4+1=11 写 1 进 1；百位 0+1+1=2，结果 `5→1→2` 表示 215。

## 为什么正确

处理完前 i 位后，结果链保存总和的低 i 位，carry 保存向第 i 位的进位。十进制商余分解维持此不变式；终止时没有未处理位或进位，得到完整和。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0002_add_two_numbers.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from examples.hot100.structures import ListNode

class Solution:
    def addTwoNumbers(self, l1, l2):
        dummy = tail = ListNode()
        carry = 0
        while l1 or l2 or carry:
            total = carry
            if l1:
                total += l1.val
                l1 = l1.next
            if l2:
                total += l2.val
                l2 = l2.next
            # 商留给下一位，余数成为本位；最后的 carry 也必须处理。
            carry, digit = divmod(total, 10)
            tail.next = ListNode(digit)
            tail = tail.next
        return dummy.next
```

## 复杂度

时间 O(max(m,n))。除输出节点外辅助空间 O(1)，输出空间 O(max(m,n))。

## 边界与易错点

循环条件必须包含 carry。较短链耗尽不代表运算结束。本实现不修改输入。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：最大可能的 carry 是多少？如果高位在前，哪个数据结构能帮助逆序处理？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/add-two-numbers/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0002.Add%20Two%20Numbers/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：手推两条长度不同的链表和最高位进位，说明循环为何还要检查 carry。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
