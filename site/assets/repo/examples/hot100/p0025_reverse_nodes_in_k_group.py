"""25 · K 个一组翻转链表：原创教学实现。"""
from examples.hot100.structures import ListNode

class Solution:
    def reverseKGroup(self, head, k):
        dummy = ListNode(0, head)
        group_prev = dummy
        while True:
            # 先确认完整的 k 个节点，尾部残组绝不改写。
            kth = group_prev
            for _ in range(k):
                kth = kth.next
                if kth is None:
                    return dummy.next
            group_next = kth.next
            # 初始接向组后继，反转结束后原组头自动成为组尾。
            prev, cur = group_next, group_prev.next
            while cur is not group_next:
                nxt = cur.next
                cur.next = prev
                prev, cur = cur, nxt
            old_head = group_prev.next
            group_prev.next = kth
            group_prev = old_head
