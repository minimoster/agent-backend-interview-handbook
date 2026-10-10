"""146 · LRU 缓存：原创教学实现。"""
class _Entry:
    def __init__(self, key=0, value=0):
        self.key, self.value = key, value
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.nodes = {}
        # 左侧最近使用，右侧最久未用；哨兵不存入哈希表。
        self.left, self.right = _Entry(), _Entry()
        self.left.next, self.right.prev = self.right, self.left

    def _remove(self, node):
        # 已知节点时，双向链可 O(1) 摘除，不必寻找前驱。
        node.prev.next = node.next
        node.next.prev = node.prev

    def _front(self, node):
        node.prev, node.next = self.left, self.left.next
        self.left.next.prev = node
        self.left.next = node

    def get(self, key: int) -> int:
        node = self.nodes.get(key)
        if node is None:
            return -1
        self._remove(node)
        self._front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        node = self.nodes.get(key)
        if node is not None:
            node.value = value
            self._remove(node)
        else:
            node = _Entry(key, value)
            self.nodes[key] = node
        self._front(node)
        # 哈希表与链表必须同步删除同一项。
        if len(self.nodes) > self.capacity:
            oldest = self.right.prev
            self._remove(oldest)
            del self.nodes[oldest.key]
