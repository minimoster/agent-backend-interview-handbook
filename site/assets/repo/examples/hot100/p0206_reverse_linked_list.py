"""206 · 反转链表：原创教学实现。"""
class Solution:
    def reverseList(self, head):
        prev, cur = None, head
        while cur is not None:
            nxt = cur.next  # 改写前保存未处理部分
            cur.next = prev
            prev, cur = cur, nxt
        return prev
