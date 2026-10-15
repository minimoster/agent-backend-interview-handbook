"""15 independently runnable test entries, with deterministic reference checks.

Run from the repository root:
    python3 examples/algorithm_supplement/test_solutions.py

A case is one input pair, one matrix size, or one state-machine operation.
Assertions within a case also check mutation, identity, and representation
invariants where relevant. Random generators have fixed per-exercise seeds.
"""

from collections import Counter, deque
from itertools import combinations, combinations_with_replacement, product
import random
import re
import sys
import unittest

import solutions as sol


CASE_COUNTS: Counter[int] = Counter()


def all_arrays(alphabet, maximum_length):
    for length in range(maximum_length + 1):
        yield from product(alphabet, repeat=length)


def make_nodes(values):
    dummy = sol.ListNode()
    tail = dummy
    nodes = []
    for value in values:
        tail.next = sol.ListNode(value)
        tail = tail.next
        nodes.append(tail)
    return dummy.next, nodes


def read_nodes(head, limit):
    nodes = []
    while head is not None:
        if len(nodes) >= limit:
            raise AssertionError("unexpected cycle or extra nodes")
        nodes.append(head)
        head = head.next
    return nodes


def brute_minimum(target, nums):
    best = len(nums) + 1
    for left in range(len(nums)):
        total = 0
        for right in range(left, len(nums)):
            total += nums[right]
            if total >= target:
                best = min(best, right - left + 1)
    return 0 if best > len(nums) else best


def simulate_spiral(n):
    matrix = [[0] * n for _ in range(n)]
    directions = ((0, 1), (1, 0), (0, -1), (-1, 0))
    row, column, direction = 0, 0, 0
    for value in range(1, n * n + 1):
        matrix[row][column] = value
        dr, dc = directions[direction]
        nr, nc = row + dr, column + dc
        if not (0 <= nr < n and 0 <= nc < n) or matrix[nr][nc]:
            direction = (direction + 1) % 4
            dr, dc = directions[direction]
            nr, nc = row + dr, column + dc
        row, column = nr, nc
    return matrix


def happy_reference(n):
    if n <= 0:
        return False

    def step(value):
        return sum(int(digit) ** 2 for digit in str(value))

    slow, fast = step(n), step(step(n))
    while slow != fast:
        slow = step(slow)
        fast = step(step(fast))
    return slow == 1


class SupplementalSolutionsTest(unittest.TestCase):
    def test_077_combinations(self):
        for n in range(9):
            for k in range(n + 2):
                expected = [list(values) for values in combinations(range(1, n + 1), k)]
                actual = sol.combine(n, k)
                self.assertEqual(actual, expected)
                if len(actual) >= 2:
                    before = actual[1].copy()
                    actual[0].append(-1)
                    self.assertEqual(actual[1], before, "answers must own independent lists")
                CASE_COUNTS[77] += 1
        for n, k in ((-1, 0), (1, -1)):
            with self.assertRaises(ValueError):
                sol.combine(n, k)
            CASE_COUNTS[77] += 1

    def test_704_binary_search(self):
        for length in range(10):
            for values in combinations(range(-4, 5), length):
                nums = list(values)
                for target in range(-5, 6):
                    expected = nums.index(target) if target in nums else -1
                    self.assertEqual(sol.binary_search(nums, target), expected)
                    self.assertEqual(nums, list(values))
                    CASE_COUNTS[704] += 1

    def test_027_remove_element(self):
        for values in all_arrays((-1, 0, 1), 6):
            for target in (-1, 0, 1, 2):
                nums = list(values)
                original_id = id(nums)
                expected = [value for value in values if value != target]
                length = sol.remove_element(nums, target)
                self.assertEqual(length, len(expected))
                self.assertEqual(nums[:length], expected)
                self.assertEqual(len(nums), len(values))
                self.assertEqual(id(nums), original_id)
                CASE_COUNTS[27] += 1

    def test_977_sorted_squares(self):
        for length in range(8):
            for values in combinations_with_replacement(range(-3, 4), length):
                nums = list(values)
                actual = sol.sorted_squares(nums)
                self.assertEqual(actual, sorted(value * value for value in values))
                self.assertEqual(nums, list(values))
                self.assertIsNot(actual, nums)
                CASE_COUNTS[977] += 1

    def test_209_positive_window(self):
        for values in all_arrays((1, 2, 3), 6):
            for target in range(1, 13):
                nums = list(values)
                self.assertEqual(sol.min_sub_array_len(target, nums), brute_minimum(target, nums))
                self.assertEqual(nums, list(values))
                CASE_COUNTS[209] += 1
        rng = random.Random(209)
        for _ in range(300):
            nums = [rng.randint(1, 20) for _ in range(rng.randint(0, 60))]
            target = rng.randint(1, 400)
            self.assertEqual(sol.min_sub_array_len(target, nums), brute_minimum(target, nums))
            CASE_COUNTS[209] += 1
        for target in (0, -1):
            with self.assertRaises(ValueError):
                sol.min_sub_array_len(target, [])
            CASE_COUNTS[209] += 1

    def test_059_spiral_matrix(self):
        for n in range(13):
            actual = sol.generate_matrix(n)
            self.assertEqual(actual, simulate_spiral(n))
            self.assertEqual(sorted(value for row in actual for value in row), list(range(1, n*n + 1)))
            self.assertEqual(len({id(row) for row in actual}), n, "rows must not alias")
            CASE_COUNTS[59] += 1
        with self.assertRaises(ValueError):
            sol.generate_matrix(-1)
        CASE_COUNTS[59] += 1

    def test_203_remove_list_elements(self):
        def check(values, target):
            head, original_nodes = make_nodes(values)
            actual = sol.remove_elements(head, target)
            kept = read_nodes(actual, len(values) + 1)
            expected = [node for node in original_nodes if node.val != target]
            self.assertEqual(kept, expected, "must retain the original nodes and their order")
            self.assertEqual([node.val for node in kept], [x for x in values if x != target])
            CASE_COUNTS[203] += 1

        for values in all_arrays((-1, 0, 1), 5):
            for target in (-1, 0, 1, 2):
                check(values, target)
        rng = random.Random(203)
        for _ in range(100):
            check([rng.randrange(4) for _ in range(rng.randrange(101))], rng.randrange(4))

    def test_707_linked_list_operations(self):
        def run(operations):
            linked = sol.MyLinkedList()
            model = []
            for operation, arguments in operations:
                if operation == "get":
                    (index,) = arguments
                    expected = model[index] if 0 <= index < len(model) else -1
                    self.assertEqual(linked.get(index), expected)
                else:
                    result = getattr(linked, operation)(*arguments)
                    self.assertIsNone(result)
                    if operation == "addAtHead":
                        model.insert(0, arguments[0])
                    elif operation == "addAtTail":
                        model.append(arguments[0])
                    elif operation == "addAtIndex":
                        index, value = arguments
                        index = max(0, index)
                        if index <= len(model):
                            model.insert(index, value)
                    else:
                        (index,) = arguments
                        if 0 <= index < len(model):
                            model.pop(index)
                nodes = read_nodes(linked._dummy.next, len(model) + 1)
                self.assertEqual([node.val for node in nodes], model)
                self.assertEqual(linked._size, len(model))
                CASE_COUNTS[707] += 1

        run([
            ("get", (0,)), ("addAtHead", (1,)), ("addAtTail", (3,)),
            ("addAtIndex", (1, 2)), ("get", (1,)), ("deleteAtIndex", (1,)),
            ("get", (1,)), ("addAtIndex", (-2, 9)), ("addAtIndex", (99, 5)),
            ("deleteAtIndex", (-1,)), ("deleteAtIndex", (99,)), ("addAtIndex", (3, 4)),
            ("deleteAtIndex", (0,)), ("deleteAtIndex", (2,)), ("deleteAtIndex", (1,)),
            ("deleteAtIndex", (0,)), ("get", (-1,)), ("addAtTail", (7,)),
        ])
        rng = random.Random(707)
        for _ in range(80):
            operations = []
            for _ in range(200):
                name = rng.choice(("get", "addAtHead", "addAtTail", "addAtIndex", "deleteAtIndex"))
                index, value = rng.randint(-3, 30), rng.randint(-20, 20)
                arguments = (index, value) if name == "addAtIndex" else ((index,) if name in ("get", "deleteAtIndex") else (value,))
                operations.append((name, arguments))
            run(operations)

    def test_242_anagram(self):
        strings = ["".join(values) for values in all_arrays("abc", 4)]
        for left in strings:
            for right in strings:
                self.assertEqual(sol.is_anagram(left, right), sorted(left) == sorted(right))
                CASE_COUNTS[242] += 1
        for left, right in (("你🙂你", "🙂你你"), ("A", "a"), ("é", "e\u0301"), ("aab", "abb"), ("", "你"), ("🙂🙂", "🙂")):
            self.assertEqual(sol.is_anagram(left, right), sorted(left) == sorted(right))
            CASE_COUNTS[242] += 1
        rng = random.Random(242)
        for _ in range(200):
            left = "".join(rng.choice("abc你🙂") for _ in range(rng.randrange(81)))
            right_chars = list(left) if rng.randrange(2) else [rng.choice("abc你🙂") for _ in range(rng.randrange(81))]
            rng.shuffle(right_chars)
            right = "".join(right_chars)
            self.assertEqual(sol.is_anagram(left, right), sorted(left) == sorted(right))
            CASE_COUNTS[242] += 1

    def test_349_intersection(self):
        def check(left, right):
            before_left, before_right = left.copy(), right.copy()
            expected = []
            for value in right:
                if value in left and value not in expected:
                    expected.append(value)
            self.assertEqual(sol.intersection(left, right), expected)
            self.assertEqual(left, before_left)
            self.assertEqual(right, before_right)
            CASE_COUNTS[349] += 1

        arrays = list(all_arrays((-1, 0, 1), 3))
        for left in arrays:
            for right in arrays:
                check(list(left), list(right))
        rng = random.Random(349)
        for _ in range(500):
            check([rng.randint(-10, 10) for _ in range(rng.randrange(41))], [rng.randint(-10, 10) for _ in range(rng.randrange(41))])

    def test_202_happy_number(self):
        for value in list(range(-10, 2001)) + [10**1000, 10**1000 + 1, 2**256 + 1, 9999999999]:
            self.assertEqual(sol.is_happy(value), happy_reference(value))
            CASE_COUNTS[202] += 1

    def test_344_reverse_string(self):
        def check(values):
            original = values.copy()
            identity = id(values)
            self.assertIsNone(sol.reverse_string(values))
            self.assertEqual(values, original[::-1])
            self.assertEqual(id(values), identity)
            sol.reverse_string(values)
            self.assertEqual(values, original)
            CASE_COUNTS[344] += 1

        for values in all_arrays("abc", 7):
            check(list(values))
        check(["你", "🙂", "a"])
        rng = random.Random(344)
        for _ in range(100):
            check([rng.choice("abc你🙂") for _ in range(rng.randrange(101))])

    def test_151_reverse_words(self):
        def check(text):
            expected = " ".join(re.findall(r"\S+", text)[::-1])
            self.assertEqual(sol.reverse_words(text), expected)
            CASE_COUNTS[151] += 1

        for values in all_arrays("ab ", 6):
            check("".join(values))
        for text in ("  the sky  is blue ", "\t\n", "你\t好\n世界", " a\u3000b ", "single"):
            check(text)
        rng = random.Random(151)
        for _ in range(300):
            check("".join(rng.choice("ab你🙂 \t\n\u3000") for _ in range(rng.randrange(101))))

    def test_232_two_stack_queue(self):
        def run(operations):
            queue = sol.MyQueue()
            model = deque()
            for name, argument in operations:
                if name == "push":
                    self.assertIsNone(queue.push(argument))
                    model.append(argument)
                elif name == "empty":
                    self.assertEqual(queue.empty(), not model)
                elif model:
                    expected = model.popleft() if name == "pop" else model[0]
                    self.assertEqual(getattr(queue, name)(), expected)
                else:
                    with self.assertRaises(IndexError):
                        getattr(queue, name)()
                self.assertEqual(queue._out[::-1] + queue._in, list(model))
                self.assertEqual(queue.empty(), not model)
                CASE_COUNTS[232] += 1

        run([(name, value) for name, value in [
            ("pop", None), ("peek", None), ("empty", None), ("push", 1), ("push", 2),
            ("peek", None), ("pop", None), ("push", 3), ("peek", None),
            ("pop", None), ("pop", None), ("empty", None), ("pop", None),
        ]])
        rng = random.Random(232)
        for _ in range(80):
            run([(rng.choice(("push", "pop", "peek", "empty")), rng.randint(-20, 20)) for _ in range(200)])

    def test_225_one_queue_stack(self):
        def run(operations):
            stack = sol.MyStack()
            model = []
            for name, argument in operations:
                if name == "push":
                    self.assertIsNone(stack.push(argument))
                    model.append(argument)
                elif name == "empty":
                    self.assertEqual(stack.empty(), not model)
                elif model:
                    expected = model.pop() if name == "pop" else model[-1]
                    self.assertEqual(getattr(stack, name)(), expected)
                else:
                    with self.assertRaises(IndexError):
                        getattr(stack, name)()
                self.assertEqual(list(stack._queue), model[::-1])
                self.assertEqual(stack.empty(), not model)
                CASE_COUNTS[225] += 1

        run([
            ("pop", None), ("top", None), ("empty", None), ("push", 1), ("push", 2),
            ("top", None), ("pop", None), ("push", 3), ("pop", None),
            ("pop", None), ("empty", None), ("top", None),
        ])
        rng = random.Random(225)
        for _ in range(80):
            run([(rng.choice(("push", "pop", "top", "empty")), rng.randint(-20, 20)) for _ in range(200)])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SupplementalSolutionsTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Test entries: {result.testsRun}; cases: {sum(CASE_COUNTS.values())}")
    print("Cases by problem: " + ", ".join(f"{number}={count}" for number, count in sorted(CASE_COUNTS.items())))
    sys.exit(0 if result.wasSuccessful() else 1)
