"""Center expansion with explicit occurrence and distinct-value interfaces."""


def longest_palindrome_spans(s: str) -> list[tuple[int, int]]:
    """Return every maximum-length occurrence as [start, end), in start order.

    Empty input returns []. Matching uses Python string code points as given.
    Equal text at different positions remains separate in this interface.
    """
    best_length = 0
    spans = []
    for center in range(len(s)):
        for left, right in ((center, center), (center, center + 1)):
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1
            length = right - left - 1
            if length > best_length:
                best_length = length
                spans = [(left + 1, right)]
            elif length == best_length and length > 0:
                spans.append((left + 1, right))
    return spans


def all_longest_palindromes(s: str) -> list[str]:
    """Return distinct maximum-length values in first-occurrence order."""
    seen = set()
    values = []
    for start, end in longest_palindrome_spans(s):
        value = s[start:end]
        if value not in seen:
            seen.add(value)
            values.append(value)
    return values
