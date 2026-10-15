# 24. 两两交换链表中的节点

难度：MEDIUM · 分类：链表

## 题意与接口

两两交换相邻节点，奇数长度时最后一个保留；不能仅交换值。接口：`swapPairs(head)`。

约束核对（2026-10-09）：长度 0..100；必须交换节点连接，不得仅交换值。

## 从朴素方法到优化

借助数组重排节点需要线性空间。每一对的变换只涉及前驱、两个节点和后继，用常数个引用即可完成。

## 核心思路

prev 指向下一对之前的节点。记 first=prev.next、second=first.next，依次接好 first 到后继、second 到 first、prev 到 second，然后 prev 移到 first。

## 手推一个小例子

`2→4→6→8→9`：第一对变为 `4→2`，prev 到 2；第二对变为 `8→6`，prev 到 6；9 不成对，结果 `4→2→8→6→9`。

## 为什么正确

每轮只修改下一对及其前驱连接，不破坏已经交换的前缀或尚未处理的后缀；前缀增加两个节点，最终覆盖全部完整二元组。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0024_swap_nodes_in_pairs.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from examples.hot100.structures import ListNode

class Solution:
    def swapPairs(self, head):
        dummy = ListNode(0, head)
        prev = dummy
        while prev.next and prev.next.next:
            first, second = prev.next, prev.next.next
            first.next = second.next
            second.next = first
            prev.next = second
            prev = first  # 交换后的尾，亦是下一对的前驱
        return dummy.next
```

## 复杂度

时间 O(n)，辅助空间 O(1)。

## 边界与易错点

改指针前保存两个节点；循环要求后面至少两个节点；交换值不满足节点交换语义。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：交换后为什么 prev 不是 second？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：画出一对节点交换前后的三条边，检查奇数长度时末尾节点如何保留。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
