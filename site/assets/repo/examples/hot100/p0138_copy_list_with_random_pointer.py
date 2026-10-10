"""138 · 随机链表的复制：原创教学实现。"""
from examples.hot100.structures import Node

class Solution:
    def copyRandomList(self, head):
        # 先建立全部对象映射，再填边，支持 random 指向未来节点。
        clones = {None: None}
        cur = head
        while cur:
            clones[cur] = Node(cur.val)
            cur = cur.next
        cur = head
        while cur:
            clones[cur].next = clones[cur.next]
            clones[cur].random = clones[cur.random]
            cur = cur.next
        return clones[head]
