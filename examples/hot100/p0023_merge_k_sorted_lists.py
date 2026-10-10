"""23 · 合并 K 个升序链表：原创教学实现。"""
import heapq
from examples.hot100.structures import ListNode

class Solution:
    def mergeKLists(self, lists):
        # 每链只留一个候选；链编号处理值相等时的堆比较。
        heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
        heapq.heapify(heap)
        dummy = tail = ListNode()
        while heap:
            _, index, node = heapq.heappop(heap)
            nxt = node.next
            tail.next = node
            tail = node
            if nxt:
                heapq.heappush(heap, (nxt.val, index, nxt))
        tail.next = None
        return dummy.next
