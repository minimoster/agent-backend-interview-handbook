"""Original Python 3 solutions for six explicitly specified interview variants.

No third-party problem text or solution code is copied.
"""
from dataclasses import dataclass


def reverse_words_in_place(chars: list[str]) -> None:
    """Mutate an existing character list; words separated by one ASCII space."""
    def reverse(left: int, right: int) -> None:
        while left < right:
            chars[left], chars[right] = chars[right], chars[left]
            left += 1
            right -= 1
    reverse(0, len(chars) - 1)
    start = 0
    for end in range(len(chars) + 1):
        if end == len(chars) or chars[end] == " ":
            reverse(start, end - 1)
            start = end + 1


@dataclass(slots=True)
class Node:
    value: int
    next: "Node | None" = None


def sort_odd_up_even_down(head: Node | None) -> Node | None:
    """1-based odd positions nondecreasing, even positions nonincreasing.

Input is acyclic. Relinks existing nodes; consumes the original list topology.
"""
    if head is None or head.next is None:
        return head
    odd = head
    even_head = head.next
    even = even_head
    while even is not None and even.next is not None:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = None
    previous = None
    current = even_head
    while current is not None:
        following = current.next
        current.next = previous
        previous, current = current, following
    left, right = head, previous
    dummy = Node(0)
    tail = dummy
    while left is not None and right is not None:
        if left.value <= right.value:
            tail.next, left = left, left.next
        else:
            tail.next, right = right, right.next
        tail = tail.next
    tail.next = left if left is not None else right
    return dummy.next


def add_decimal_strings(a: str, b: str) -> str:
    """Nonempty ASCII decimal, nonnegative; no whole-input int conversion."""
    if not a or not b or any(c < "0" or c > "9" for c in a + b):
        raise ValueError("expected nonempty ASCII decimal strings")
    i, j, carry = len(a) - 1, len(b) - 1, 0
    reversed_digits = []
    while i >= 0 or j >= 0 or carry:
        x = ord(a[i]) - ord("0") if i >= 0 else 0
        y = ord(b[j]) - ord("0") if j >= 0 else 0
        carry, digit = divmod(x + y + carry, 10)
        reversed_digits.append(chr(ord("0") + digit))
        i -= 1
        j -= 1
    return "".join(reversed(reversed_digits)).lstrip("0") or "0"


def largest_below_decimal(n: str, digits: set[int]) -> str | None:
    """Largest positive decimal < n, with reusable digits and no leading zero.

    n is nonempty ASCII decimal; leading zeros are accepted and normalized.
    No whole-input integer conversion or interpreter-limit changes occur.
    """
    if not isinstance(n, str) or not n or any(c < "0" or c > "9" for c in n):
        raise ValueError("n must be a nonempty ASCII decimal string")
    if any(type(d) is not int or d < 0 or d > 9 for d in digits):
        raise ValueError("digits must be integers in 0..9")
    bound = n.lstrip("0") or "0"
    if bound in ("0", "1") or not digits or not (digits - {0}):
        return None
    allowed = sorted(digits)
    last_drop = None
    for i, char in enumerate(bound):
        limit = ord(char) - ord("0")
        smaller = [d for d in allowed if d < limit and (i != 0 or d != 0)]
        if smaller:
            last_drop = (i, smaller[-1])
        if limit not in digits:
            break
    if last_drop is not None:
        i, digit = last_drop
        return bound[:i] + str(digit) + str(allowed[-1]) * (len(bound) - i - 1)
    shorter = len(bound) - 1
    if shorter == 0:
        return None
    largest_nonzero = max(digits - {0})
    return str(largest_nonzero) + str(allowed[-1]) * (shorter - 1)


def largest_below(n: int, digits: set[int]) -> int | None:
    """Integer convenience wrapper; decimal conversion limits remain active.

    Non-int bounds raise ValueError; n <= 1 has no positive solution.
    Oversized decimal conversions raise ValueError; use the string API instead.
    """
    if type(n) is not int:
        raise ValueError("n must be an integer")
    if any(type(d) is not int or d < 0 or d > 9 for d in digits):
        raise ValueError("digits must be integers in 0..9")
    if n <= 1:
        return None
    try:
        result = largest_below_decimal(str(n), digits)
        return int(result) if result is not None else None
    except ValueError as error:
        raise ValueError(
            "decimal conversion limit exceeded; use largest_below_decimal "
            "with a decimal string"
        ) from error


def remove_all_duplicate_values(head: Node | None) -> Node | None:
    """Sorted acyclic list; remove every node whose value occurs more than once."""
    dummy = Node(0, head)
    kept = dummy
    current = head
    while current is not None:
        if current.next is not None and current.value == current.next.value:
            repeated = current.value
            while current is not None and current.value == repeated:
                current = current.next
            kept.next = current
        else:
            kept = current
            current = current.next
    return dummy.next


def are_anagrams(a: str, b: str) -> bool:
    """Exact case-sensitive Unicode code-point counts; no normalization."""
    if len(a) != len(b):
        return False
    counts = {}
    for char in a:
        counts[char] = counts.get(char, 0) + 1
    for char in b:
        count = counts.get(char, 0)
        if count == 0:
            return False
        if count == 1:
            del counts[char]
        else:
            counts[char] = count - 1
    return not counts
