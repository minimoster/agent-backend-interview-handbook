"""Exhaustive synthetic checks for the independently authored LC395 code."""
import importlib.util
import itertools
import pathlib
import unittest
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "lc395", ROOT / "examples/algorithms/lc395_longest_repeating_substring.py"
)
LC395 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LC395)


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
