"""Independent Python answers for the fifteen supplemental algorithm exercises.

Only Python's standard library is used. Public contracts and worked examples are
in docs/85-algorithm-supplement/README.md.
"""

from collections import deque


def combine(n: int, k: int) -> list[list[int]]:
    """Return increasing k-element selections from 1..n, in lexical order."""
    if n < 0 or k < 0:
        raise ValueError("n and k must be nonnegative")
    if k > n:
        return []
    result: list[list[int]] = []
    path: list[int] = []

    def visit(start: int) -> None:
        needed = k - len(path)
        if needed == 0:
            result.append(path.copy())
            return
        for value in range(start, n - needed + 2):
            path.append(value)
            visit(value + 1)
            path.pop()

    visit(1)
    return result


def binary_search(nums: list[int], target: int) -> int:
    """Search a strictly increasing array; return -1 if target is absent."""
    left, right = 0, len(nums)
    while left < right:
        middle = (left + right) // 2
        if nums[middle] < target:
            left = middle + 1
        elif nums[middle] > target:
            right = middle
        else:
            return middle
    return -1


def remove_element(nums: list[int], val: int) -> int:
    """Write retained values into nums' prefix, stably; return its length."""
    write = 0
    for read in range(len(nums)):
        if nums[read] != val:
            nums[write] = nums[read]
            write += 1
    return write


def sorted_squares(nums: list[int]) -> list[int]:
    """Return nondecreasing squares of a nondecreasing integer array."""
    result = [0] * len(nums)
    left, right = 0, len(nums) - 1
    for write in range(len(nums) - 1, -1, -1):
        if abs(nums[left]) > abs(nums[right]):
            result[write] = nums[left] * nums[left]
            left += 1
        else:
            result[write] = nums[right] * nums[right]
            right -= 1
    return result


def min_sub_array_len(target: int, nums: list[int]) -> int:
    """For positive nums and target, return shortest sum>=target length, or 0."""
    if target <= 0:
        raise ValueError("target must be positive")
    left = 0
    total = 0
    best = len(nums) + 1
    for right, value in enumerate(nums):
        total += value
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best == len(nums) + 1 else best


def generate_matrix(n: int) -> list[list[int]]:
    """Fill an n-by-n matrix clockwise from its upper-left corner with 1..n²."""
    if n < 0:
        raise ValueError("n must be nonnegative")
    matrix = [[0] * n for _ in range(n)]
    top, bottom, left, right = 0, n - 1, 0, n - 1
    value = 1
    while top <= bottom and left <= right:
        for column in range(left, right + 1):
            matrix[top][column] = value
            value += 1
        top += 1
        for row in range(top, bottom + 1):
            matrix[row][right] = value
            value += 1
        right -= 1
        if top <= bottom:
            for column in range(right, left - 1, -1):
                matrix[bottom][column] = value
                value += 1
            bottom -= 1
        if left <= right:
            for row in range(bottom, top - 1, -1):
                matrix[row][left] = value
                value += 1
            left += 1
    return matrix


class ListNode:
    """A mutable node shared by exercises 203 and 707."""

    def __init__(self, val: int = 0, next: "ListNode | None" = None) -> None:
        self.val = val
        self.next = next


def remove_elements(head: ListNode | None, val: int) -> ListNode | None:
    """Unlink all matching nodes from an acyclic list; reuse retained nodes."""
    dummy = ListNode(next=head)
    previous = dummy
    while previous.next is not None:
        if previous.next.val == val:
            previous.next = previous.next.next
        else:
            previous = previous.next
    return dummy.next


class MyLinkedList:
    """Zero-based singly linked list; invalid reads return -1."""

    def __init__(self) -> None:
        self._dummy = ListNode()
        self._size = 0

    def _predecessor(self, index: int) -> ListNode:
        previous = self._dummy
        for _ in range(index):
            previous = previous.next
        return previous

    def get(self, index: int) -> int:
        if index < 0 or index >= self._size:
            return -1
        return self._predecessor(index).next.val

    def addAtHead(self, val: int) -> None:
        self.addAtIndex(0, val)

    def addAtTail(self, val: int) -> None:
        self.addAtIndex(self._size, val)

    def addAtIndex(self, index: int, val: int) -> None:
        index = max(0, index)
        if index > self._size:
            return
        previous = self._predecessor(index)
        previous.next = ListNode(val, previous.next)
        self._size += 1

    def deleteAtIndex(self, index: int) -> None:
        if index < 0 or index >= self._size:
            return
        previous = self._predecessor(index)
        previous.next = previous.next.next
        self._size -= 1


def is_anagram(s: str, t: str) -> bool:
    """Compare exact character frequencies, without case/Unicode normalization."""
    if len(s) != len(t):
        return False
    counts: dict[str, int] = {}
    for character in s:
        counts[character] = counts.get(character, 0) + 1
    for character in t:
        if counts.get(character, 0) == 0:
            return False
        counts[character] -= 1
    return True


def intersection(nums1: list[int], nums2: list[int]) -> list[int]:
    """Return distinct common values in order of first occurrence in nums2."""
    remaining = set(nums1)
    result: list[int] = []
    for value in nums2:
        if value in remaining:
            result.append(value)
            remaining.remove(value)
    return result


def is_happy(n: int) -> bool:
    """Return whether positive n reaches 1 under decimal digit-square sums."""
    if n <= 0:
        return False
    seen: set[int] = set()
    while n != 1 and n not in seen:
        seen.add(n)
        total = 0
        while n:
            n, digit = divmod(n, 10)
            total += digit * digit
        n = total
    return n == 1


def reverse_string(characters: list[str]) -> None:
    """Reverse a mutable character array in place and return None."""
    left, right = 0, len(characters) - 1
    while left < right:
        characters[left], characters[right] = characters[right], characters[left]
        left += 1
        right -= 1


def reverse_words(s: str) -> str:
    """Reverse whitespace-separated words; join with one ASCII space."""
    return " ".join(reversed(s.split()))


class MyQueue:
    """FIFO queue using two stacks. Empty pop/peek raise IndexError."""

    def __init__(self) -> None:
        self._in: list[int] = []
        self._out: list[int] = []

    def push(self, x: int) -> None:
        self._in.append(x)

    def _prepare(self) -> None:
        if not self._out:
            while self._in:
                self._out.append(self._in.pop())

    def pop(self) -> int:
        self._prepare()
        if not self._out:
            raise IndexError("pop from empty queue")
        return self._out.pop()

    def peek(self) -> int:
        self._prepare()
        if not self._out:
            raise IndexError("peek from empty queue")
        return self._out[-1]

    def empty(self) -> bool:
        return not self._in and not self._out


class MyStack:
    """LIFO stack using a FIFO queue. Empty pop/top raise IndexError."""

    def __init__(self) -> None:
        self._queue: deque[int] = deque()

    def push(self, x: int) -> None:
        self._queue.append(x)
        for _ in range(len(self._queue) - 1):
            self._queue.append(self._queue.popleft())

    def pop(self) -> int:
        if not self._queue:
            raise IndexError("pop from empty stack")
        return self._queue.popleft()

    def top(self) -> int:
        if not self._queue:
            raise IndexError("top from empty stack")
        return self._queue[0]

    def empty(self) -> bool:
        return not self._queue
