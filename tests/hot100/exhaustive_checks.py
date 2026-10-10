"""Optional, deterministic exhaustive checks for five error-prone Hot100 algorithms.

Run from the repository root with Python 3.10+ and the standard library only:
    python -B tests/hot100/exhaustive_checks.py

These bounded checks provide local evidence, not a proof or an online AC record.
The references enumerate intervals, values, or sorted order rather than copying
the implementations under test. They do not write files or change source code.
"""

from datetime import datetime, timezone
import hashlib
import importlib
import itertools
import json
from pathlib import Path
import platform
import random
import statistics
import sys
import time

ROOT = Path.cwd().resolve()
if (ROOT / "examples/hot100").is_dir():
    sys.path.insert(0, str(ROOT))


def solution(problem_id):
    paths = list((ROOT / "examples/hot100").glob(f"p{problem_id:04d}_*.py"))
    if len(paths) != 1:
        raise RuntimeError("Run this script from the repository root.")
    return importlib.import_module("examples.hot100." + paths[0].stem).Solution()


def check(condition, problem_id, case):
    if not condition:
        raise AssertionError(f"Problem {problem_id} failed on {case!r}")


def check_histograms():
    solve = solution(84).largestRectangleArea
    count = 0
    for length in range(7):
        for values in itertools.product(range(4), repeat=length):
            expected = max(
                (min(values[left:right]) * (right - left)
                 for left in range(length)
                 for right in range(left + 1, length + 1)),
                default=0,
            )
            data = list(values)
            check(solve(data) == expected, 84, values)
            check(data == list(values), 84, ("input changed", values))
            count += 1
    return count


def check_missing_positive():
    solve = solution(41).firstMissingPositive
    count = 0
    for length in range(7):
        for values in itertools.product(range(-1, 5), repeat=length):
            expected = next(value for value in range(1, length + 2)
                            if value not in values)
            check(solve(list(values)) == expected, 41, values)
            count += 1
    return count


def check_minimum_windows():
    solve = solution(76).minWindow
    sources = ["".join(chars) for length in range(7)
               for chars in itertools.product("ab", repeat=length)]
    patterns = ["".join(chars) for length in range(1, 5)
                for chars in itertools.product("ab", repeat=length)]
    count = 0
    for source in sources:
        for pattern in patterns:
            candidates = [
                source[left:right]
                for left in range(len(source))
                for right in range(left + 1, len(source) + 1)
                if all(source[left:right].count(char) >= pattern.count(char)
                       for char in set(pattern))
            ]
            result = solve(source, pattern)
            expected_length = min(map(len, candidates), default=0)
            check(len(result) == expected_length
                  and (not result or result in candidates),
                  76, (source, pattern, result))
            count += 1
    return count


def check_medians():
    solve = solution(4).findMedianSortedArrays
    arrays = [values for length in range(6)
              for values in itertools.combinations_with_replacement(
                  range(-2, 3), length)]
    count = 0
    for left in arrays:
        for right in arrays:
            if not left and not right:
                continue
            left_data, right_data = list(left), list(right)
            check(solve(left_data, right_data) == statistics.median(left + right),
                  4, (left, right))
            check(left_data == list(left) and right_data == list(right),
                  4, ("input changed", left, right))
            count += 1
    return count


def check_kth_largest():
    solve = solution(215)
    saved_random_state = random.getstate()
    random.seed(99831)
    count = 0
    try:
        for length in range(1, 7):
            for values in itertools.product(range(-1, 3), repeat=length):
                for rank in range(1, length + 1):
                    expected = sorted(values)[-rank]
                    data = list(values)
                    check(solve.findKthLargest(data, rank) == expected,
                          215, ("quickselect", values, rank))
                    check(data == list(values), 215,
                          ("quickselect input changed", values, rank))
                    check(solve.findKthLargestHeap(data, rank) == expected,
                          215, ("heap", values, rank))
                    check(data == list(values), 215,
                          ("heap input changed", values, rank))
                    count += 1
    finally:
        random.setstate(saved_random_state)
    return count


def main():
    started = time.perf_counter()
    checks = {
        84: check_histograms,
        41: check_missing_positive,
        76: check_minimum_windows,
        4: check_medians,
        215: check_kth_largest,
    }
    cases = {str(problem_id): run() for problem_id, run in checks.items()}
    print(json.dumps({
        "status": "passed",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for pid in checks for path in (ROOT / "examples/hot100").glob(f"p{pid:04d}_*.py")},
        "python": platform.python_version(),
        "case_counts": cases,
        "total_cases": sum(cases.values()),
        "seconds": round(time.perf_counter() - started, 3),
        "scope": "bounded local exhaustive checks; not online AC",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
