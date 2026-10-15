# 148. 排序链表

难度：MEDIUM · 分类：链表

## 题意与接口

把单链表按值非递减排序，返回新头。接口：`sortList(head)`；复用节点。选择迭代归并以兼顾 O(n log n) 时间和 O(1) 辅助空间。

约束核对（2026-10-09）：长度 0..50000；进阶要求 O(n log n) 时间和 O(1) 辅助空间。

## 从朴素方法到优化

插入排序在逆序链上要 O(n²)。递归归并已能 O(n log n)，但递归栈占 O(log n)；自底向上把有序段长度依次扩大到 1、2、4、8，可避免调用栈。

## 核心思路

先统计长度。每轮切出相邻两个至多 width 长度的段，归并后接回输出尾。split 在第 width 个节点后断开并返回下一段头；一轮结束 width 翻倍。

## 手推一个小例子

`7→1→5→2→4`：width=1 合成 `[1,7] [2,5] [4]`；width=2 合成 `[1,2,5,7] [4]`；width=4 得 `[1,2,4,5,7]`。

## 为什么正确

初始长度为 1 的段天然有序。若一轮开始每段长度至多 width 且有序，两段归并必得到有序的至多 2×width 段；归纳到 width 不小于总长度，整链有序。断链与重连保证每个原节点恰出现一次。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0148_sort_list.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from examples.hot100.structures import ListNode

class Solution:
    def sortList(self, head):
        def split(start, size):
            if start is None:
                return None
            for _ in range(size - 1):
                if start.next is None:
                    break
                start = start.next
            rest = start.next
            start.next = None
            return rest

        length, node = 0, head
        while node:
            length += 1
            node = node.next
        dummy = ListNode(0, head)
        width = 1
        while width < length:
            tail, cur = dummy, dummy.next
            while cur:
                left = cur
                right = split(left, width)
                cur = split(right, width)
                while left and right:
                    if left.val <= right.val:
                        tail.next, left = left, left.next
                    else:
                        tail.next, right = right, right.next
                    tail = tail.next
                tail.next = left if left else right
                while tail.next:  # 定位合并段尾，总遍历仍线性
                    tail = tail.next
            width *= 2
        return dummy.next
```

## 复杂度

时间 O(n log n)，每轮切分和归并总计 O(n)，共 O(log n) 轮。辅助空间 O(1)。

## 边界与易错点

split 必须真正断链，否则归并可能串到后续段。最后一段可短于 width 或没有配对段。不要把 O(log n) 递归栈误记为 O(1)。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：逐轮证明有序段长度怎样增长；tail 找尾循环为何不会使总时间变成 O(n²)？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：手推归并排序的拆分与合并，说明切断链表的必要性及递归栈是否计入辅助空间。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
