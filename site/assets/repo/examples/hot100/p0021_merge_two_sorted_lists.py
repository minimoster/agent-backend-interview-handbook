"""21 · 合并两个有序链表：原创教学实现。"""
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
