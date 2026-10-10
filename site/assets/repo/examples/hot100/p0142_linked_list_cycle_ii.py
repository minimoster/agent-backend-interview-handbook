"""142 · 环形链表 II：原创教学实现。"""
class Solution:
    def detectCycle(self, head):
        slow = fast = head
        while fast and fast.next:
            slow, fast = slow.next, fast.next.next
            if slow is fast:
                # 相遇后同速走：头到入口的距离与环上剩余距离同余。
                seeker = head
                while seeker is not slow:
                    seeker, slow = seeker.next, slow.next
                return seeker
        return None
