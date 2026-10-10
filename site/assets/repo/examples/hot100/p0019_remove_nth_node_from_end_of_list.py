"""19 · 删除链表的倒数第 N 个结点：原创教学实现。"""
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
