"""141 · 环形链表：原创教学实现。"""
class Solution:
    def hasCycle(self, head):
        slow = fast = head
        while fast is not None and fast.next is not None:
            # 先移动再比较，初始同在 head 不代表有环。
            slow, fast = slow.next, fast.next.next
            if slow is fast:
                return True
        return False
