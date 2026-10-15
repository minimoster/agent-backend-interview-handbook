# 19. 删除链表的倒数第 N 个结点

难度：MEDIUM · 分类：链表

## 题意与接口

删除链表倒数第 n 个节点并返回头；题目保证 `1 <= n <= 链表长度`。接口：`removeNthFromEnd(head, n)`。

约束核对（2026-10-09）：链长 1..30，1<=n<=链长；删除倒数第 n 个节点。

## 从朴素方法到优化

先算长度，再走到删除点要两趟。让 fast 领先 slow n+1 条边，则 fast 到空指针时 slow 正好是待删节点前驱。

## 核心思路

增加 dummy 指向原头，使删除头也有前驱。两个指针从 dummy 开始，fast 先走 n+1 步，再同步推进，最后令 slow.next 跳过目标。

## 手推一个小例子

`3→6→9→2`，n=2。fast 从 dummy 先走三步到 9；再同步走两步后 fast=None、slow=6；跳过 9 得 `3→6→2`。

## 为什么正确

同步阶段始终保持 n+1 条边的间距。fast 在末尾之后时，slow 后面恰有 n 个实际节点，因此 slow.next 是倒数第 n 个节点。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0019_remove_nth_node_from_end_of_list.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from examples.hot100.structures import ListNode

class Solution:
    def removeNthFromEnd(self, head, n):
        dummy = ListNode(0, head)
        fast = slow = dummy
        # 保持 n+1 条边的间距，让 slow 最终落在删除点前驱。
        for _ in range(n + 1):
            fast = fast.next
        while fast:
            fast, slow = fast.next, slow.next
        slow.next = slow.next.next
        return dummy.next
```

## 复杂度

时间 O(L)，辅助空间 O(1)。

## 边界与易错点

本题保证 n 有效，不对越界 n 做修复。返回 dummy.next 才能正确处理删除原头。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：若快指针仅先走 n 步，同步循环的终止条件需要怎样变化？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：用删除头节点和删除尾节点检查 dummy 与快慢指针间距，明确 n 的合法范围。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
