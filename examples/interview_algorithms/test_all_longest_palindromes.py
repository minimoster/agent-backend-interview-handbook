"""Small exhaustive oracle plus occurrence, deduplication and boundary cases."""
import itertools
import unittest

from all_longest_palindromes import all_longest_palindromes, longest_palindrome_spans


def brute_spans(s):
    candidates = [(start, end) for start in range(len(s))
                  for end in range(start + 1, len(s) + 1)
                  if s[start:end] == s[start:end][::-1]]
    best = max((end - start for start, end in candidates), default=0)
    return [(start, end) for start, end in candidates if end - start == best]


class AllLongestPalindromesTests(unittest.TestCase):
    def test_empty_and_single_character(self):
        self.assertEqual(longest_palindrome_spans(''), [])
        self.assertEqual(all_longest_palindromes(''), [])
        self.assertEqual(longest_palindrome_spans('a'), [(0, 1)])
        self.assertEqual(all_longest_palindromes('a'), ['a'])

    def test_odd_even_and_ties(self):
        self.assertEqual(longest_palindrome_spans('babad'), [(0, 3), (1, 4)])
        self.assertEqual(all_longest_palindromes('babad'), ['bab', 'aba'])
        self.assertEqual(longest_palindrome_spans('abbaZnoon'), [(0, 4), (5, 9)])
        self.assertEqual(all_longest_palindromes('abbaZnoon'), ['abba', 'noon'])

    def test_occurrences_are_not_distinct_values(self):
        self.assertEqual(longest_palindrome_spans('abaxyaba'), [(0, 3), (5, 8)])
        self.assertEqual(all_longest_palindromes('abaxyaba'), ['aba'])

    def test_larger_palindrome_discards_shorter_candidates(self):
        self.assertEqual(longest_palindrome_spans('xyabbaz'), [(2, 6)])
        self.assertEqual(all_longest_palindromes('aaaa'), ['aaaa'])

    def test_code_points_and_case_are_not_normalized(self):
        self.assertEqual(all_longest_palindromes('上海海上'), ['上海海上'])
        self.assertEqual(all_longest_palindromes('Aa'), ['A', 'a'])
        self.assertEqual(longest_palindrome_spans('abc'), [(0, 1), (1, 2), (2, 3)])

    def test_exhaustive_ternary_strings_up_to_length_seven(self):
        for length in range(8):
            for chars in itertools.product('abc', repeat=length):
                s = ''.join(chars)
                expected = brute_spans(s)
                with self.subTest(s=s):
                    self.assertEqual(longest_palindrome_spans(s), expected)
                    self.assertEqual(all_longest_palindromes(s),
                                     list(dict.fromkeys(s[a:b] for a, b in expected)))

    def test_thousand_character_work_and_output_boundaries(self):
        self.assertEqual(longest_palindrome_spans('a' * 1000), [(0, 1000)])
        distinct = ''.join(chr(0x400 + i) for i in range(1000))
        self.assertEqual(longest_palindrome_spans(distinct),
                         [(i, i + 1) for i in range(1000)])


if __name__ == '__main__':
    unittest.main(verbosity=2)
