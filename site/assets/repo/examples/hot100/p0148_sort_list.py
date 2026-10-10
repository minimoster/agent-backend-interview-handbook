"""148 · 排序链表：原创教学实现。"""
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
