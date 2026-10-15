# 234. 回文链表

难度：EASY · 分类：链表

## 题意与接口

判断链表节点值从前往后与从后往前是否相同。接口：`isPalindrome(head) -> bool`。本实现检查后恢复链表原结构。

约束核对（2026-10-09）：长度 1..100000，节点值为 0..9；进阶要求线性时间、常数辅助空间。

## 从朴素方法到优化

复制所有值到数组后和逆序比较，空间 O(n)。快慢指针找到前半段尾，反转后半段即可从两端同步比较，额外空间降到 O(1)。

## 核心思路

fast 每步走两格，slow 每步走一格。反转 slow.next 之后的链表，只比较后半段长度个节点；无论结果真假都再次反转后半段，恢复连接。

## 手推一个小例子

`5→2→9→2→5`：slow 落在中间 9；后半段 `2→5` 反成 `5→2`；比较 (5,5)、(2,2) 均相等；最后恢复成原链。中间 9 不参加比较。

## 为什么正确

回文当且仅当前半段与反转后的后半段逐位相等；奇数长度的中心不影响这个条件。两次反转互为逆操作，因此返回时节点连接和调用前相同。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0234_palindrome_linked_list.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def isPalindrome(self, head):
        if head is None or head.next is None:
            return True

        def reverse(node):
            prev = None
            while node:
                nxt = node.next
                node.next = prev
                prev, node = node, nxt
            return prev

        slow = fast = head
        while fast.next and fast.next.next:
            slow, fast = slow.next, fast.next.next
        second = reverse(slow.next)
        left, right, ok = head, second, True
        while right:
            if left.val != right.val:
                ok = False  # 不提前返回，确保恢复结构
            left, right = left.next, right.next
        slow.next = reverse(second)
        return ok
```

## 复杂度

时间 O(n)，辅助空间 O(1)。恢复结构增加一次线性遍历，不改变阶数。

## 边界与易错点

比较失败后直接 return 会遗漏恢复；偶数长度要让 slow 停在前半段尾。测试不仅检查布尔值，还检查原链表。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为什么比较循环由 right 是否为空决定？不恢复链表会给调用方带来什么副作用？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：检查奇数与偶数长度的中点位置；若承诺不改变输入，说明比较后如何恢复链表。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
