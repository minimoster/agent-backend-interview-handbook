"""24 · 两两交换链表中的节点：原创教学实现。"""
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
