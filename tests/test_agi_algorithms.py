"""Independent synthetic checks for the original LC395 and LC115 lessons."""
import importlib.util
import itertools
import math
import pathlib
import re
import unittest
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "lc395", ROOT / "examples/algorithms/lc395_longest_repeating_substring.py"
)
LC395 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LC395)

SPEC115 = importlib.util.spec_from_file_location(
    "lc115", ROOT / "examples/algorithms/lc115_distinct_subsequences.py"
)
LC115 = importlib.util.module_from_spec(SPEC115)
SPEC115.loader.exec_module(LC115)


def brute_subsequence_choices(source, target):
    """Enumerate original-index subsets, without a DP recurrence."""
    return sum(
        "".join(ch for i, ch in enumerate(source) if mask & (1 << i)) == target
        for mask in range(1 << len(source))
    )


def binary_words(max_length):
    for size in range(max_length + 1):
        for chars in itertools.product("ab", repeat=size):
            yield "".join(chars)


class LC115Checks(unittest.TestCase):
    def test_exhaustive_original_index_subsets(self):
        cases = 0
        for source in binary_words(6):
            for target in binary_words(5):
                expected = brute_subsequence_choices(source, target)
                self.assertEqual(LC115.count_subsequence_choices(source, target),
                                 expected, (source, target))
                cases += 1
        self.assertEqual(cases, 8001)

    def test_boundaries_repeated_positions_and_unicode(self):
        for source, target, expected in [
            ("", "", 1), ("abc", "", 1), ("", "a", 0), ("a", "aa", 0),
            ("abc", "d", 0), ("abc", "abc", 1), ("aaba", "aa", 3),
            ("aaaa", "aa", 6), ("aa", "aa", 1), ("Aaa", "aa", 1),
            ("学学习", "学习", 2), ("🙂🙂a🙂", "🙂🙂", 3),
            ("é", "e\u0301", 0),
        ]:
            self.assertEqual(LC115.count_subsequence_choices(source, target),
                             expected, (source, target))

    def test_repeated_character_binomial_identity(self):
        for source_size in range(31):
            for target_size in range(source_size + 2):
                expected = (math.comb(source_size, target_size)
                            if target_size <= source_size else 0)
                self.assertEqual(LC115.count_subsequence_choices(
                    "a" * source_size, "a" * target_size), expected)

    def test_large_counts_and_zero_final_with_large_intermediates(self):
        expected = math.comb(100, 50)
        self.assertGreater(expected, 2**63 - 1)
        self.assertEqual(LC115.count_subsequence_choices("a" * 100, "a" * 50),
                         expected)
        self.assertEqual(LC115.count_subsequence_choices(
            "a" * 100, "a" * 50 + "b"), 0)

    def test_published_snippet_matches_executable_implementation(self):
        lesson = (ROOT / "docs/70-practice/interview-algorithm-supplements.md").read_text()
        section = lesson.split('<a id="lc115"></a>', 1)[1]
        snippets = re.findall(r"```python\n(.*?)\n```", section, re.S)
        self.assertEqual(len(snippets), 1)
        code = (ROOT / "examples/algorithms/lc115_distinct_subsequences.py").read_text()
        self.assertTrue(code.rstrip().endswith(snippets[0].rstrip()))
        namespace = {}
        exec(compile(snippets[0], "published-lc115-snippet", "exec"), namespace)
        for source, target in [("", ""), ("aa", "aa"), ("aaba", "aa")]:
            self.assertEqual(namespace["count_subsequence_choices"](source, target),
                             brute_subsequence_choices(source, target))


def brute(s, k):
    return max((j-i for i in range(len(s)+1) for j in range(i, len(s)+1)
                if all(n >= k for n in Counter(s[i:j]).values())), default=0)


class LC395Checks(unittest.TestCase):
    def test_exhaustive_three_characters(self):
        cases = 0
        for size in range(8):
            for chars in itertools.product("abc", repeat=size):
                text = "".join(chars)
                for k in range(10):
                    expected = brute(text, k)
                    self.assertEqual(LC395.longest_divide(text, k), expected, (text, k))
                    self.assertEqual(LC395.longest_window(text, k), expected, (text, k))
                    cases += 1
        self.assertEqual(cases, 32800)

    def test_unicode_and_boundary_cases(self):
        for text, k in [("aaabb",3),("ababbc",2),("",2),("a",2),
                        ("学学习习学",2),("🙂🙂a🙂",3),("abca",0),
                        ("a"*2000+"b"+"a"*2000,3000)]:
            expected = brute(text,k) if len(text)<20 else 0
            self.assertEqual(LC395.longest_divide(text,k),expected)
            self.assertEqual(LC395.longest_window(text,k),expected)


if __name__ == "__main__":
    unittest.main()
