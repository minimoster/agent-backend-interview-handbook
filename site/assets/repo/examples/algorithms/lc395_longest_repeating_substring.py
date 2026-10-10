"""Original LC395 supplement, independent of Hot100.

Python str characters are supported; neither algorithm assumes a-z.
No network, model, or third-party implementation is used.
"""
from collections import Counter


def longest_divide(s: str, k: int) -> int:
    """Split on every character too rare in the current interval.

    Use an explicit interval stack instead of Python recursion/sliced copies.
    At each depth at least one distinct character disappears: O(U*n) time
    (O(n*n) if U grows with n), O(n+U) auxiliary memory in the worst case.
    """
    if k <= 1:
        return len(s)
    best = 0
    pending = [(0, len(s))]
    while pending:
        lo, hi = pending.pop()
        if hi - lo < max(k, best + 1):
            continue
        count = Counter(s[pos] for pos in range(lo, hi))
        bad = {char for char, frequency in count.items() if frequency < k}
        if not bad:
            best = max(best, hi - lo)
            continue
        start = lo
        for pos in range(lo, hi):
            if s[pos] in bad:
                if pos - start >= k:
                    pending.append((start, pos))
                start = pos + 1
        if hi - start >= k:
            pending.append((start, hi))
    return best


def longest_window(s: str, k: int) -> int:
    """Enumerate target distinct counts: O(U*n) time, O(U) space."""
    if k <= 1:
        return len(s)
    best = 0
    max_distinct = min(len(set(s)), len(s) // k)
    for target in range(1, max_distinct + 1):
        count = Counter()
        left = distinct = satisfied = 0
        for right, char in enumerate(s):
            if count[char] == 0:
                distinct += 1
            count[char] += 1
            if count[char] == k:
                satisfied += 1
            while distinct > target:
                old = s[left]
                if count[old] == k:
                    satisfied -= 1
                count[old] -= 1
                if count[old] == 0:
                    distinct -= 1
                    del count[old]
                left += 1
            if distinct == target and satisfied == target:
                best = max(best, right - left + 1)
    return best
