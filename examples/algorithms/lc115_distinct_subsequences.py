"""Original exact-count teaching implementation for LC115.

Inputs are Python strings. The empty target has one index selection. No modulo
is applied; Python integers preserve intermediate counts without overflow.
"""


def count_subsequence_choices(s: str, t: str) -> int:
    """Count increasing original-index selections in s spelling exactly t."""
    if not t:
        return 1
    n, m = len(s), len(t)
    if m > n:
        return 0
    dp = [0] * (m + 1)
    dp[0] = 1
    for i, ch in enumerate(s, start=1):
        for j in range(min(i, m), 0, -1):
            if ch == t[j - 1]:
                dp[j] += dp[j - 1]
    return dp[m]
