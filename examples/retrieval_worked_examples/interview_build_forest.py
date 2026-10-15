from collections import deque
from graphlib import CycleError, TopologicalSorter


def build_forest(rows):
    rows = list(rows)
    nodes = {}
    for row in rows:
        ident = row["id"]
        parent = row["parent_id"]
        if not isinstance(ident, str) or not ident:
            raise ValueError("id must be a nonempty string")
        if parent is not None and (
            not isinstance(parent, str) or not parent
        ):
            raise ValueError("parent_id must be a string or None")
        if ident in nodes:
            raise ValueError("duplicate id")
        nodes[ident] = {**row, "children": []}

    graph = {}
    for row in rows:
        ident, parent = row["id"], row["parent_id"]
        if parent is not None and parent not in nodes:
            raise ValueError("unknown parent")
        graph[ident] = () if parent is None else (parent,)
    try:
        TopologicalSorter(graph).prepare()
    except CycleError as exc:
        raise ValueError("parent cycle") from exc

    roots = []
    for row in rows:
        ident, parent = row["id"], row["parent_id"]
        if parent is None:
            roots.append(nodes[ident])
        else:
            nodes[parent]["children"].append(nodes[ident])
    return roots


def zigzag_level_order(root):
    """Level order values, alternating display direction; acyclic binary tree."""
    if root is None:
        return []
    queue = deque([root])
    answer = []
    reverse = False
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        answer.append(level[::-1] if reverse else level)
        reverse = not reverse
    return answer
