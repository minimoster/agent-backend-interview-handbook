# 21. 合并两个有序链表

难度：EASY · 分类：链表

## 题意与接口

把两条非递减单链表合并为一条非递减链表。接口：`mergeTwoLists(list1, list2)`，本实现重用输入节点并改变连接。

约束核对（2026-10-09）：每条链长度 0..50，均非递减；要求拼接原节点。

## 从朴素方法到优化

取出值、排序、重建需要 O((m+n) log(m+n)) 时间并新建节点。已有的内部有序性让我们每次只比较两个头。

## 核心思路

用 dummy 消除首次接节点的分支。tail 指向已合并尾；每轮接较小头并推进对应链，某条耗尽后直接接另一条剩余部分。

## 手推一个小例子

`1→7` 和 `2→4→9`：依次选 1、2、4、7；第一条耗尽，直接接 9，得到 `1→2→4→7→9`。

## 为什么正确

两个剩余链的最小值必是它们的头之一。选较小头是全体剩余节点的最小值，接在已有有序前缀之后保持有序；所有节点恰好接入一次。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0021_merge_two_sorted_lists.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from examples.hot100.structures import ListNode

class Solution:
    def mergeTwoLists(self, list1, list2):
        dummy = tail = ListNode()
        while list1 and list2:
            # 两条剩余有序链的最小值，一定出现在两个头中。
            if list1.val <= list2.val:
                tail.next, list1 = list1, list1.next
            else:
                tail.next, list2 = list2, list2.next
            tail = tail.next
        tail.next = list1 if list1 else list2
        return dummy.next
```

## 复杂度

时间 O(m+n)，辅助空间 O(1)，输出复用节点。

## 边界与易错点

输入必须有序且不共享节点；共享后缀不属于本题通常模型。相等时选左侧可保持稳定顺序。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为什么剩余部分不用逐节点比较？dummy 的值参与排序吗？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：检查相等值的选择与尾部拼接；说明节点复用是否会修改输入链表的引用关系。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
