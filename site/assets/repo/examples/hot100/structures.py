"""本地运行使用的节点和构造助手；LeetCode 会提供对应节点类型。"""
from collections import deque


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Node:
    """138 题的带 random 指针节点；按对象身份比较和哈希。"""
    def __init__(self, x=0, next=None, random=None):
        self.val = x
        self.next = next
        self.random = random


RandomNode = Node


def list_from(values):
    dummy = tail = ListNode()
    for value in values:
        tail.next = ListNode(value)
        tail = tail.next
    return dummy.next


def list_values(head, limit=10000):
    values, seen = [], set()
    while head is not None:
        if head in seen:
            raise ValueError("list contains a cycle")
        if len(values) >= limit:
            raise ValueError("list exceeds limit")
        seen.add(head)
        values.append(head.val)
        head = head.next
    return values


def tree_from(values):
    """层序序列；None 表示缺失孩子，不使用完全二叉树数组下标规则。"""
    values = iter(values)
    first = next(values, None)
    if first is None:
        return None
    root = TreeNode(first)
    queue = deque([root])
    while queue:
        parent = queue.popleft()
        for attr in ("left", "right"):
            value = next(values, None)
            if value is not None:
                child = TreeNode(value)
                setattr(parent, attr, child)
                queue.append(child)
    return root


def tree_values(root):
    if root is None:
        return []
    values, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        values.append(None if node is None else node.val)
        if node is not None:
            queue.extend((node.left, node.right))
    while values and values[-1] is None:
        values.pop()
    return values
