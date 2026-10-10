"""160 · 相交链表：原创教学实现。"""
class Solution:
    def getIntersectionNode(self, headA, headB):
        a, b = headA, headB
        # 换头后都遍历两条链，抵消独有前缀的长度差。
        while a is not b:
            a = a.next if a is not None else headB
            b = b.next if b is not None else headA
        return a
