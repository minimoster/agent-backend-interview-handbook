"""Hot100 链表、树、图、回溯：确定性边界、固定种子对拍和深树测试。

从仓库根目录运行：python -m unittest discover -s tests/hot100 -p 'test_*.py' -v
只依赖标准库；测试不连接在线判题服务。
部分空输入、极深树、重复值案例刻意超出当前官方输入域，用于验证实现的扩展健壮性；
它们不改变各题页面已核对的官方约束。
"""
import importlib
import itertools
import random
import unittest
from collections import OrderedDict, deque
from pathlib import Path

from examples.hot100.structures import (
    ListNode, TreeNode, Node, list_from, list_values, tree_from, tree_values,
)


def module(pid):
    paths = list((Path(__file__).resolve().parents[2] / 'examples' / 'hot100').glob(f'p{pid:04d}_*.py'))
    # tests/hot100/file -> repo 为 parents[2]。
    if len(paths) != 1:
        raise AssertionError(f'expected exactly one module for {pid}: {paths}')
    return importlib.import_module('examples.hot100.' + paths[0].stem)


def solution(pid):
    return module(pid).Solution()


def nodes_of(head):
    result = []
    while head:
        if head in result:
            raise AssertionError('unexpected cycle')
        result.append(head)
        head = head.next
    return result


def preorder(root):
    values, stack = [], [root] if root else []
    while stack:
        node = stack.pop()
        values.append(node.val)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return values


def small_tree(rng, size, unique=False):
    if size == 0:
        return None, []
    nodes = [TreeNode(i if unique else rng.randrange(-9, 10)) for i in range(size)]
    slots = [(nodes[0], 'left'), (nodes[0], 'right')]
    for node in nodes[1:]:
        parent, attr = slots.pop(rng.randrange(len(slots)))
        setattr(parent, attr, node)
        slots.extend([(node, 'left'), (node, 'right')])
    return nodes[0], nodes


def adjacency(nodes):
    graph = {node: [] for node in nodes}
    for node in nodes:
        for child in (node.left, node.right):
            if child:
                graph[node].append(child)
                graph[child].append(node)
    return graph


def canonical(rows):
    return sorted(tuple(row) for row in rows)


class TestLinkedLists(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(20261009)

    def test_p0160_intersection_identity(self):
        fn = solution(160).getIntersectionNode
        common = list_from([7, 9])
        a, b = ListNode(4, common), ListNode(1, ListNode(2, common))
        self.assertIs(fn(a, b), common)
        self.assertIs(fn(common, common), common)
        self.assertIsNone(fn(list_from([1, 2]), list_from([1, 2])))
        self.assertIsNone(fn(None, common))
        for left in range(5):
            for right in range(5):
                tail = ListNode(99)
                a = b = tail
                for i in range(left):
                    a = ListNode(i, a)
                for i in range(right):
                    b = ListNode(i, b)
                self.assertIs(fn(a, b), tail)

    def test_p0206_reverse_nodes(self):
        fn = solution(206).reverseList
        for size in range(40):
            values = [self.rng.randrange(-9, 10) for _ in range(size)]
            head = list_from(values)
            nodes = nodes_of(head)
            result = fn(head)
            self.assertEqual(list_values(result), values[::-1])
            self.assertEqual(nodes_of(result), nodes[::-1])
            self.assertIs(fn(result), head)

    def test_p0234_palindrome_and_restore(self):
        fn = solution(234).isPalindrome
        cases = [[], [1], [1, 1], [1, 2], [5, 2, 9, 2, 5], [1, 2, 2, 1]]
        cases += [[self.rng.randrange(3) for _ in range(self.rng.randrange(20))] for _ in range(80)]
        # 官方最大规模：不使用辅助 nodes_of 的二次扫描来核验。
        large = list_from([7] * 100000)
        self.assertTrue(fn(large))
        self.assertEqual(len(list_values(large, limit=100001)), 100000)
        for values in cases:
            head = list_from(values)
            original_nodes = nodes_of(head)
            self.assertEqual(fn(head), values == values[::-1])
            self.assertEqual(nodes_of(head), original_nodes)
            self.assertEqual(list_values(head), values)

    def test_p0141_cycle(self):
        fn = solution(141).hasCycle
        self.assertFalse(fn(None))
        for size in range(1, 15):
            for entry in range(-1, size):
                head = list_from(range(size))
                nodes = nodes_of(head)
                if entry >= 0:
                    nodes[-1].next = nodes[entry]
                self.assertEqual(fn(head), entry >= 0)

    def test_p0142_cycle_entry(self):
        fn = solution(142).detectCycle
        self.assertIsNone(fn(None))
        for size in range(1, 15):
            for entry in range(-1, size):
                head = list_from([2] * size)
                nodes = nodes_of(head)
                expected = None
                if entry >= 0:
                    expected = nodes[entry]
                    nodes[-1].next = expected
                self.assertIs(fn(head), expected)

    def test_p0021_merge_two(self):
        fn = solution(21).mergeTwoLists
        for _ in range(80):
            a = sorted(self.rng.randrange(-5, 6) for _ in range(self.rng.randrange(20)))
            b = sorted(self.rng.randrange(-5, 6) for _ in range(self.rng.randrange(20)))
            left, right = list_from(a), list_from(b)
            originals = set(nodes_of(left) + nodes_of(right))
            result = fn(left, right)
            self.assertEqual(list_values(result), sorted(a + b))
            self.assertEqual(set(nodes_of(result)), originals)
        self.assertIsNone(fn(None, None))

    def test_p0002_add_numbers(self):
        fn = solution(2).addTwoNumbers
        for a, b in [(0, 0), (999, 1), (68, 147)] + [(self.rng.randrange(10**12), self.rng.randrange(10**9)) for _ in range(80)]:
            av, bv = list(map(int, str(a)[::-1])), list(map(int, str(b)[::-1]))
            left, right = list_from(av), list_from(bv)
            result = fn(left, right)
            self.assertEqual(list_values(result), list(map(int, str(a+b)[::-1])))
            self.assertEqual(list_values(left), av)
            self.assertEqual(list_values(right), bv)
            self.assertFalse(set(nodes_of(result)) & set(nodes_of(left) + nodes_of(right)))

    def test_p0019_remove_nth(self):
        fn = solution(19).removeNthFromEnd
        for size in range(1, 20):
            values = list(range(size))
            for n in range(1, size + 1):
                result = fn(list_from(values), n)
                self.assertEqual(list_values(result), values[:size-n] + values[size-n+1:])

    def test_p0024_swap_pairs(self):
        fn = solution(24).swapPairs
        for size in range(30):
            head = list_from(range(size))
            original = nodes_of(head)
            expected = original.copy()
            for i in range(0, size-1, 2):
                expected[i:i+2] = [expected[i+1], expected[i]]
            self.assertEqual(nodes_of(fn(head)), expected)

    def test_p0025_reverse_k_group(self):
        fn = solution(25).reverseKGroup
        for size in range(1, 25):
            for k in range(1, size + 1):
                head = list_from(range(size))
                originals = nodes_of(head)
                expected = []
                for i in range(0, size, k):
                    group = originals[i:i+k]
                    expected.extend(group[::-1] if len(group) == k else group)
                self.assertEqual(nodes_of(fn(head, k)), expected)
        head = list_from(range(5000))
        self.assertEqual(list_values(fn(head, 5000)), list(range(4999, -1, -1)))

    def test_p0138_copy_random_deep(self):
        fn = solution(138).copyRandomList
        self.assertIsNone(fn(None))
        for size in range(1, 25):
            original = [Node(self.rng.randrange(3)) for _ in range(size)]
            for i, node in enumerate(original):
                node.next = original[i+1] if i+1 < size else None
                node.random = self.rng.choice(original + [None])
            before_next = [node.next for node in original]
            before_random = [node.random for node in original]
            copied = nodes_of(fn(original[0]))
            self.assertEqual([node.val for node in copied], [node.val for node in original])
            self.assertFalse(set(copied) & set(original))
            indices = {node: i for i, node in enumerate(original)}
            for old, new in zip(original, copied):
                expected = None if old.random is None else copied[indices[old.random]]
                self.assertIs(new.random, expected)
            self.assertEqual([node.next for node in original], before_next)
            self.assertEqual([node.random for node in original], before_random)

    def test_p0148_sort_bottom_up(self):
        fn = solution(148).sortList
        cases = [[], [1], list(range(200, -1, -1))]
        cases += [[self.rng.randrange(-20, 21) for _ in range(self.rng.randrange(80))] for _ in range(100)]
        for values in cases:
            head = list_from(values)
            originals = set(nodes_of(head))
            result = fn(head)
            self.assertEqual(list_values(result), sorted(values))
            self.assertEqual(set(nodes_of(result)), originals)

        # 官方上限规模，核对迭代归并不会遇到递归深度限制。
        large = fn(list_from(range(49999, -1, -1)))
        self.assertEqual(list_values(large, limit=50001), list(range(50000)))

    def test_p0023_merge_k_heap(self):
        fn = solution(23).mergeKLists
        self.assertIsNone(fn([]))
        self.assertIsNone(fn([None, None]))
        for _ in range(100):
            arrays = [sorted(self.rng.randrange(-10, 11) for _ in range(self.rng.randrange(15))) for _ in range(self.rng.randrange(10))]
            chains = [list_from(a) for a in arrays]
            originals = {node for head in chains for node in nodes_of(head)}
            result = fn(chains)
            self.assertEqual(list_values(result), sorted(x for a in arrays for x in a))
            self.assertEqual(set(nodes_of(result)), originals)

    def test_p0146_lru_against_ordered_dict(self):
        cls = module(146).LRUCache
        for capacity in (1, 2, 7):
            cache, expected = cls(capacity), OrderedDict()
            for _ in range(1000):
                key = self.rng.randrange(12)
                if self.rng.randrange(3):
                    value = self.rng.randrange(101)
                    cache.put(key, value)
                    expected[key] = value
                    expected.move_to_end(key)
                    if len(expected) > capacity:
                        expected.popitem(last=False)
                else:
                    result = cache.get(key)
                    self.assertEqual(result, expected.get(key, -1))
                    if key in expected:
                        expected.move_to_end(key)
                self.assertEqual(set(cache.nodes), set(expected))
                # 检查双向指针与真实最近使用顺序。
                order, prev, cur = [], cache.left, cache.left.next
                while cur is not cache.right:
                    self.assertIs(cur.prev, prev)
                    order.append(cur.key)
                    prev, cur = cur, cur.next
                    self.assertLessEqual(len(order), capacity)
                self.assertIs(cache.right.prev, prev)
                self.assertEqual(order, list(reversed(expected)))


class TestTrees(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(20261010)

    def test_p0094_inorder_iterative(self):
        fn = solution(94).inorderTraversal
        def reference(node):
            return reference(node.left) + [node.val] + reference(node.right) if node else []
        for size in range(35):
            root, _ = small_tree(self.rng, size)
            self.assertEqual(fn(root), reference(root))
        root = None
        for value in range(2000):
            root = TreeNode(value, root)
        self.assertEqual(fn(root), list(range(2000)))

    def test_p0104_depth(self):
        fn = solution(104).maxDepth
        self.assertEqual(fn(None), 0)
        def reference(node):
            return 1 + max(reference(node.left), reference(node.right)) if node else 0
        for size in range(40):
            root, _ = small_tree(self.rng, size)
            self.assertEqual(fn(root), reference(root))
        root = None
        for _ in range(3000):
            root = TreeNode(1, root)
        self.assertEqual(fn(root), 3000)

    def test_p0226_invert_twice(self):
        fn = solution(226).invertTree
        self.assertIsNone(fn(None))
        root = tree_from([6, 2, 8, 1, 4])
        self.assertIs(fn(root), root)
        self.assertEqual(tree_values(root), [6, 8, 2, None, None, 4, 1])
        for size in range(30):
            root, _ = small_tree(self.rng, size)
            before = tree_values(root)
            fn(root)
            fn(root)
            self.assertEqual(tree_values(root), before)

    def test_p0101_symmetric_shape(self):
        fn = solution(101).isSymmetric
        self.assertTrue(fn(None))
        self.assertTrue(fn(tree_from([5, 2, 2, None, 7, 7, None])))
        self.assertFalse(fn(tree_from([5, 2, 2, None, 7, None, 7])))
        self.assertFalse(fn(tree_from([5, 2, 3])))
        root = TreeNode(0)
        left = right = root
        for _ in range(1500):
            left.left, right.right = TreeNode(1), TreeNode(1)
            left, right = left.left, right.right
        self.assertTrue(fn(root))

    def test_p0543_diameter_against_all_pairs(self):
        fn = solution(543).diameterOfBinaryTree
        for size in range(30):
            root, nodes = small_tree(self.rng, size)
            graph, expected = adjacency(nodes), 0
            for start in nodes:
                stack = [(start, None, 0)]
                while stack:
                    node, prev, distance = stack.pop()
                    expected = max(expected, distance)
                    stack.extend((neighbor, node, distance+1) for neighbor in graph[node] if neighbor is not prev)
            self.assertEqual(fn(root), expected)
        root = None
        for _ in range(2500):
            root = TreeNode(1, root)
        self.assertEqual(fn(root), 2499)

    def test_p0102_level_order(self):
        fn = solution(102).levelOrder
        self.assertEqual(fn(None), [])
        self.assertEqual(fn(tree_from([3, 1, 7, None, 2, 6])), [[3], [1, 7], [2, 6]])
        for size in range(30):
            root, _ = small_tree(self.rng, size)
            by_depth = []
            def visit(node, depth):
                if not node:
                    return
                if depth == len(by_depth):
                    by_depth.append([])
                by_depth[depth].append(node.val)
                visit(node.left, depth+1)
                visit(node.right, depth+1)
            visit(root, 0)
            self.assertEqual(fn(root), by_depth)

    def test_p0108_balanced_bst_properties(self):
        fn = solution(108).sortedArrayToBST
        def height(node):
            if not node:
                return 0
            left, right = height(node.left), height(node.right)
            self.assertLessEqual(abs(left-right), 1)
            return 1 + max(left, right)
        for size in list(range(50)) + [10000]:
            values = list(range(-size, 0))
            root = fn(values)
            self.assertEqual(solution(94).inorderTraversal(root), values)
            height(root)

    def test_p0098_bst_global_bounds(self):
        fn = solution(98).isValidBST
        self.assertTrue(fn(None))
        self.assertFalse(fn(tree_from([7, 3, 10, None, None, 6])))
        self.assertFalse(fn(tree_from([1, 1])))
        self.assertTrue(fn(tree_from([0, -2**31, 2**31-1])))
        def check(node, lo, hi):
            return not node or (lo < node.val < hi and check(node.left, lo, node.val) and check(node.right, node.val, hi))
        for _ in range(100):
            root, _ = small_tree(self.rng, self.rng.randrange(30))
            self.assertEqual(fn(root), bool(check(root, float('-inf'), float('inf'))))

    def test_p0230_kth_smallest(self):
        fn = solution(230).kthSmallest
        for size in range(1, 40):
            values = sorted(self.rng.sample(range(-100, 101), size))
            root = solution(108).sortedArrayToBST(values)
            for k in range(1, size+1):
                self.assertEqual(fn(root, k), values[k-1])
        root = None
        for value in range(2000):
            root = TreeNode(value, root)
        self.assertEqual(fn(root, 2000), 1999)

    def test_p0199_right_view(self):
        fn = solution(199).rightSideView
        self.assertEqual(fn(None), [])
        self.assertEqual(fn(tree_from([1, 4, 8, 6])), [1, 8, 6])
        def right_first_reference(node, depth, visible):
            # 独立右优先DFS：每个深度第一次见到的就是最右可见节点。
            if node is None:
                return
            if depth == len(visible):
                visible.append(node.val)
            right_first_reference(node.right, depth + 1, visible)
            right_first_reference(node.left, depth + 1, visible)
        for size in range(40):
            root, _ = small_tree(self.rng, size)
            expected = []
            right_first_reference(root, 0, expected)
            self.assertEqual(fn(root), expected)

    def test_p0114_flatten_preserves_preorder_identity(self):
        fn = solution(114).flatten
        self.assertIsNone(fn(None))
        for size in range(1, 60):
            root, originals = small_tree(self.rng, size, unique=True)
            expected = preorder(root)
            self.assertIsNone(fn(root))
            actual, seen, cur = [], set(), root
            while cur:
                self.assertNotIn(cur, seen)
                seen.add(cur)
                self.assertIsNone(cur.left)
                actual.append(cur.val)
                cur = cur.right
            self.assertEqual(actual, expected)
            self.assertEqual(seen, set(originals))
        root = None
        for value in range(3000):
            root = TreeNode(value, root)
        fn(root)
        self.assertEqual(preorder(root), list(range(2999, -1, -1)))

    def test_p0105_build_two_traversals(self):
        fn = solution(105).buildTree
        self.assertIsNone(fn([], []))
        for size in range(1, 60):
            original, _ = small_tree(self.rng, size, unique=True)
            pre = preorder(original)
            ino = solution(94).inorderTraversal(original)
            result = fn(pre, ino)
            self.assertEqual(preorder(result), pre)
            self.assertEqual(solution(94).inorderTraversal(result), ino)
            self.assertEqual(tree_values(result), tree_values(original))
        for ino in (list(range(3000)), list(range(2999, -1, -1))):
            root = fn(list(range(3000)), ino)
            self.assertEqual(preorder(root), list(range(3000)))
            self.assertEqual(solution(94).inorderTraversal(root), ino)

    def test_p0437_path_sum_bruteforce(self):
        fn = solution(437).pathSum
        def from_node(node, target):
            if not node:
                return 0
            return int(node.val == target) + from_node(node.left, target-node.val) + from_node(node.right, target-node.val)
        self.assertEqual(fn(None, 0), 0)
        for _ in range(120):
            root, nodes = small_tree(self.rng, self.rng.randrange(30))
            target = self.rng.randrange(-20, 21)
            self.assertEqual(fn(root, target), sum(from_node(node, target) for node in nodes))
        root = None
        for _ in range(1000):
            root = TreeNode(0, root)
        self.assertEqual(fn(root, 0), 1000*1001//2)
        # 相同前缀只可在当前根路径计数，不能跨兄弟分支。
        self.assertEqual(fn(tree_from([0, 0, 0]), 0), 5)

    def test_p0236_lca_identity(self):
        fn = solution(236).lowestCommonAncestor
        for size in range(2, 45):
            root, nodes = small_tree(self.rng, size)
            p, q = self.rng.sample(nodes, 2)
            def path(node, target):
                if node is None:
                    return []
                if node is target:
                    return [node]
                rest = path(node.left, target) or path(node.right, target)
                return [node] + rest if rest else []
            common = None
            for a, b in zip(path(root, p), path(root, q)):
                if a is not b:
                    break
                common = a
            self.assertIs(fn(root, p, q), common)
        root = TreeNode(1)
        root.left = TreeNode(1)
        self.assertIs(fn(root, root, root.left), root)
        cur = root.left
        for _ in range(3000):
            cur.left = TreeNode(1)
            cur = cur.left
        self.assertIs(fn(root, root.left, cur), root.left)

    def test_p0124_max_path_all_pairs_and_deep(self):
        fn = solution(124).maxPathSum
        self.assertEqual(fn(tree_from([-8, -4, -9])), -4)
        self.assertEqual(fn(tree_from([-4, 3, 7, None, None, -2, 6])), 13)
        for size in range(1, 30):
            root, nodes = small_tree(self.rng, size)
            graph, expected = adjacency(nodes), float('-inf')
            for start in nodes:
                stack = [(start, None, start.val)]
                while stack:
                    node, prev, total = stack.pop()
                    expected = max(expected, total)
                    stack.extend((neighbor, node, total+neighbor.val) for neighbor in graph[node] if neighbor is not prev)
            self.assertEqual(fn(root), expected)
        root = None
        for _ in range(30000):
            root = TreeNode(1, root)
        self.assertEqual(fn(root), 30000)


class TestGraphs(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(20261011)

    def test_p0200_islands_dsu_oracle(self):
        fn = solution(200).numIslands
        self.assertEqual(fn([]), 0)
        self.assertEqual(fn([list('110'), list('010'), list('001')]), 2)
        for _ in range(100):
            rows, cols = self.rng.randrange(1, 8), self.rng.randrange(1, 8)
            grid = [[self.rng.choice('01') for _ in range(cols)] for _ in range(rows)]
            copy = [row[:] for row in grid]
            parent = {(r,c):(r,c) for r in range(rows) for c in range(cols) if grid[r][c]=='1'}
            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x
            for r, c in list(parent):
                for neighbor in ((r+1,c), (r,c+1)):
                    if neighbor in parent:
                        parent[find(neighbor)] = find((r,c))
            expected = len({find(node) for node in parent})
            self.assertEqual(fn(grid), expected)
            self.assertEqual(grid, copy)
        self.assertEqual(fn([['1'] * 300 for _ in range(300)]), 1)

    def test_p0994_rotting_synchronous_oracle(self):
        fn = solution(994).orangesRotting
        self.assertEqual(fn([[2, 1, 1, 1, 2]]), 2)
        self.assertEqual(fn([[0, 2]]), 0)
        self.assertEqual(fn([[1]]), -1)
        def reference(grid):
            rows, cols, time = len(grid), len(grid[0]), 0
            while any(1 in row for row in grid):
                changing = []
                for r in range(rows):
                    for c in range(cols):
                        if grid[r][c] == 1 and any(0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 2 for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1))):
                            changing.append((r,c))
                if not changing:
                    return -1
                for r,c in changing:
                    grid[r][c] = 2
                time += 1
            return time
        for _ in range(100):
            grid = [[self.rng.randrange(3) for _ in range(5)] for _ in range(4)]
            self.assertEqual(fn([row[:] for row in grid]), reference([row[:] for row in grid]))

    def test_p0207_courses_color_dfs_oracle(self):
        fn = solution(207).canFinish
        self.assertTrue(fn(4, [[1,0], [2,0], [3,1], [3,2]]))
        self.assertFalse(fn(1, [[0,0]]))
        self.assertTrue(fn(7, []))
        def reference(n, edges):
            graph, state = [[] for _ in range(n)], [0]*n
            for a,b in edges:
                graph[b].append(a)
            def visit(node):
                if state[node] == 1:
                    return False
                if state[node] == 2:
                    return True
                state[node] = 1
                if not all(visit(child) for child in graph[node]):
                    return False
                state[node] = 2
                return True
            return all(visit(node) for node in range(n))
        for n in range(1, 12):
            for _ in range(15):
                edges = [[a,b] for a in range(n) for b in range(n) if self.rng.random()<.12]
                self.assertEqual(fn(n, edges), reference(n, edges))
        self.assertTrue(fn(2000, [[i,i-1] for i in range(1,2000)]))

    def test_p0208_trie_vs_set(self):
        trie, words = module(208).Trie(), set()
        trie.insert('cat')
        trie.insert('car')
        words.update(('cat', 'car'))
        self.assertFalse(trie.search('ca'))
        self.assertTrue(trie.startsWith('ca'))
        for _ in range(500):
            word = ''.join(self.rng.choice('abcd') for _ in range(self.rng.randrange(1,9)))
            if self.rng.randrange(2):
                trie.insert(word)
                words.add(word)
            self.assertEqual(trie.search(word), word in words)
            prefix = word[:self.rng.randrange(1,len(word)+1)]
            self.assertEqual(trie.startsWith(prefix), any(w.startswith(prefix) for w in words))
        trie.insert('a'*2000)
        self.assertTrue(trie.search('a'*2000))


class TestBacktracking(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(20261012)

    def test_p0046_permutations_itertools(self):
        fn = solution(46).permute
        for size in range(1, 7):
            values = self.rng.sample(range(-10, 11), size)
            result = fn(values)
            self.assertEqual(canonical(result), sorted(itertools.permutations(values)))
            self.assertEqual(len({tuple(row) for row in result}), len(result))

    def test_p0078_subsets_bitmask(self):
        fn = solution(78).subsets
        for size in range(1, 11):
            values = list(range(size))
            expected = [[values[i] for i in range(size) if mask >> i & 1] for mask in range(1<<size)]
            self.assertEqual(canonical(fn(values)), canonical(expected))

    def test_p0017_letters_product(self):
        fn = solution(17).letterCombinations
        mapping = dict(zip('23456789', ['abc','def','ghi','jkl','mno','pqrs','tuv','wxyz']))
        self.assertEqual(fn(''), [])
        for digits in ['2', '7', '9', '72', '279', '9999']:
            expected = sorted(''.join(chars) for chars in itertools.product(*(mapping[d] for d in digits)))
            self.assertEqual(sorted(fn(digits)), expected)

    def test_p0039_combination_sum_count_vectors(self):
        fn = solution(39).combinationSum
        self.assertEqual(canonical(fn([3,4,7],10)), [(3,3,4), (3,7)])
        self.assertEqual(fn([4],3), [])
        for _ in range(80):
            values = self.rng.sample(range(2,10), self.rng.randrange(1,5))
            before, target = values.copy(), self.rng.randrange(1,21)
            expected = []
            ordered = sorted(values)
            for counts in itertools.product(*(range(target//v+1) for v in ordered)):
                if sum(v*c for v,c in zip(ordered,counts)) == target:
                    expected.append([v for v,c in zip(ordered,counts) for _ in range(c)])
            self.assertEqual(canonical(fn(values,target)), canonical(expected))
            self.assertEqual(values, before)

    def test_p0022_parentheses_exhaustive(self):
        fn = solution(22).generateParenthesis
        def valid(chars):
            balance = 0
            for char in chars:
                balance += 1 if char == '(' else -1
                if balance < 0:
                    return False
            return balance == 0
        for n in range(1, 6):
            expected = [''.join(chars) for chars in itertools.product('()', repeat=2*n) if valid(chars)]
            self.assertEqual(sorted(fn(n)), sorted(expected))
        self.assertEqual(len(fn(8)), 1430)

    def test_p0079_word_search_set_oracle_restore(self):
        fn = solution(79).exist
        def reference(board, word):
            rows, cols = len(board), len(board[0])
            def search(r,c,index,seen):
                if not (0<=r<rows and 0<=c<cols) or (r,c) in seen or board[r][c] != word[index]:
                    return False
                if index == len(word)-1:
                    return True
                next_seen = seen | {(r,c)}
                return any(search(nr,nc,index+1,next_seen) for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)))
            return any(search(r,c,0,set()) for r in range(rows) for c in range(cols))
        board = [list('AB'), list('CD')]
        self.assertTrue(fn(board, 'ABD'))
        self.assertFalse(fn(board, 'ABA'))
        self.assertEqual(board, [list('AB'),list('CD')])
        for _ in range(100):
            board = [[self.rng.choice('ABC') for _ in range(3)] for _ in range(3)]
            word = ''.join(self.rng.choice('ABC') for _ in range(self.rng.randrange(1,8)))
            before = [row[:] for row in board]
            self.assertEqual(fn(board,word), reference(before,word))
            self.assertEqual(board,before)

    def test_p0131_partition_cut_masks(self):
        fn = solution(131).partition
        self.assertEqual(canonical(fn('abba')), [('a','b','b','a'), ('a','bb','a'), ('abba',)])
        for _ in range(80):
            text = ''.join(self.rng.choice('abc') for _ in range(self.rng.randrange(1,10)))
            expected = []
            for mask in range(1 << (len(text)-1)):
                starts = [0] + [i+1 for i in range(len(text)-1) if mask >> i & 1] + [len(text)]
                parts = [text[a:b] for a,b in zip(starts,starts[1:])]
                if all(part == part[::-1] for part in parts):
                    expected.append(parts)
            self.assertEqual(canonical(fn(text)), canonical(expected))

    def test_p0051_queens_counts_and_constraints(self):
        fn = solution(51).solveNQueens
        known = {1:1, 2:0, 3:0, 4:2, 5:10, 6:4, 7:40, 8:92, 9:352}
        for n,count in known.items():
            boards = fn(n)
            self.assertEqual(len(boards), count)
            self.assertEqual(len({tuple(board) for board in boards}), count)
            for board in boards:
                self.assertEqual(len(board), n)
                self.assertTrue(all(len(row)==n and row.count('Q')==1 for row in board))
                cols = [row.index('Q') for row in board]
                self.assertEqual(len(set(cols)), n)
                self.assertEqual(len({r-c for r,c in enumerate(cols)}), n)
                self.assertEqual(len({r+c for r,c in enumerate(cols)}), n)


if __name__ == '__main__':
    unittest.main()
