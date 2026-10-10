"""2 · 两数相加：原创教学实现。"""
from examples.hot100.structures import ListNode

class Solution:
    def addTwoNumbers(self, l1, l2):
        dummy = tail = ListNode()
        carry = 0
        while l1 or l2 or carry:
            total = carry
            if l1:
                total += l1.val
                l1 = l1.next
            if l2:
                total += l2.val
                l2 = l2.next
            # 商留给下一位，余数成为本位；最后的 carry 也必须处理。
            carry, digit = divmod(total, 10)
            tail.next = ListNode(digit)
            tail = tail.next
        return dummy.next
