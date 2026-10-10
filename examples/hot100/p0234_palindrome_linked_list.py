"""234 · 回文链表：原创教学实现。"""
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
