"""Original single-threaded teaching LRU; see FB29 for limitations."""
class Node:
    def __init__(self, key=None, value=None):
        self.key, self.value = key, value
        self.prev = self.next = None

class LRU:
    def __init__(self, capacity):
        if capacity < 0:
            raise ValueError("capacity must be nonnegative")
        self.capacity, self.nodes = capacity, {}
        self.head, self.tail = Node(), Node()
        self.head.next, self.tail.prev = self.tail, self.head

    def _detach(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _front(self, node):
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key, default=None):
        node = self.nodes.get(key)
        if node is None:
            return default
        self._detach(node)
        self._front(node)
        return node.value

    def put(self, key, value):
        if self.capacity == 0:
            return
        node = self.nodes.get(key)
        if node is not None:
            node.value = value
            self._detach(node)
            self._front(node)
            return
        node = Node(key, value)
        self.nodes[key] = node
        self._front(node)
        if len(self.nodes) > self.capacity:
            victim = self.tail.prev
            self._detach(victim)
            del self.nodes[victim.key]
