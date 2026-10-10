"""Finite independent oracles for LC53/LC295 follow-ups and LC3/LC45 traces.

Run from the repository root:
python -B -m unittest examples.hot100.test_followup_algorithms -v
"""
import itertools
import random
import statistics
import unittest

from examples.hot100.followup_algorithms import (
    BandCountMedianFinder, BoundedMedianFinder, ExactPrefixMedianFinder,
    maximum_subarray_summary, max_subarray_divide_conquer,
)
from examples.hot100.p0003_longest_substring_without_repeating_characters import Solution as WindowSolution
from examples.hot100.p0045_jump_game_ii import Solution as JumpSolution
from examples.hot100.p0053_maximum_subarray import Solution as KadaneSolution


def brute_summary(values):
    return (sum(values),
            max(sum(values[:stop]) for stop in range(1, len(values) + 1)),
            max(sum(values[start:]) for start in range(len(values))),
            max(sum(values[start:stop]) for start in range(len(values))
                for stop in range(start + 1, len(values) + 1)))


class FollowupTests(unittest.TestCase):
    def test_tuple_hashability_depends_on_elements(self):
        counts = (1, 0, 2)
        self.assertEqual({counts: ["acc"]}[tuple([1, 0, 2])], ["acc"])
        with self.assertRaises(TypeError):
            hash(([],))
        with self.assertRaises(TypeError):
            {( [], ): "not a valid key"}

    def test_maximum_subarray_four_fields_exhaustive(self):
        # 97,655 nonempty arrays; every summary field has its own brute oracle.
        for size in range(1, 8):
            for values in itertools.product(range(-2, 3), repeat=size):
                nums = list(values)
                self.assertEqual(maximum_subarray_summary(nums), brute_summary(nums), values)
                self.assertEqual(nums, list(values))

    def test_maximum_subarray_random_and_scale(self):
        rng = random.Random(530)
        for _ in range(300):
            nums = [rng.randrange(-10000, 10001) for _ in range(rng.randrange(1, 50))]
            expected = brute_summary(nums)[3]
            self.assertEqual(max_subarray_divide_conquer(nums), expected)
            self.assertEqual(KadaneSolution().maxSubArray(nums), expected)
        self.assertEqual(maximum_subarray_summary([-8, -2, -5]), (-15, -8, -5, -2))
        self.assertEqual(maximum_subarray_summary([-4, 3, -1, 5, -6]), (-3, 3, 1, 7))
        self.assertEqual(max_subarray_divide_conquer([-1] * 100000), -1)
        self.assertEqual(maximum_subarray_summary([0] * 100000), (0, 0, 0, 0))
        for function in (maximum_subarray_summary, max_subarray_divide_conquer):
            with self.assertRaises(ValueError):
                function([])

    def test_bounded_median_exhaustive_prefixes(self):
        for size in range(1, 7):
            for values in itertools.product((0, 1, 50, 99, 100), repeat=size):
                finder = BoundedMedianFinder()
                prefix = []
                for value in values:
                    finder.addNum(value)
                    prefix.append(value)
                    self.assertEqual(finder.findMedian(), statistics.median(prefix), prefix)
                self.assertEqual(len(finder.frequencies), 101)
                self.assertEqual(sum(finder.frequencies), size)

    def test_outlier_rank_selection_exhaustive_prefixes(self):
        # 19,607 streams; low/high outlier ranks, duplicates and both parities.
        alphabet = (-100000, -1, 0, 50, 100, 101, 100000)
        for size in range(1, 6):
            for values in itertools.product(alphabet, repeat=size):
                exact, counts, prefix = ExactPrefixMedianFinder(), BandCountMedianFinder(), []
                for value in values:
                    exact.addNum(value)
                    counts.addNum(value)
                    prefix.append(value)
                    ordered = sorted(prefix)
                    expected = statistics.median(prefix)
                    self.assertEqual(exact.findMedian(), expected, prefix)
                    first = ordered[(len(prefix) - 1) // 2]
                    second = ordered[len(prefix) // 2]
                    if 0 <= first <= second <= 100:
                        self.assertEqual(counts.findMedian(), expected, prefix)
                    else:
                        with self.assertRaises(ValueError):
                            counts.findMedian()

    def test_query_time_99_percent_promise(self):
        cases = [([-1] + [0] * 49 + [100] * 50, 50.0),
                 ([0] * 50 + [100] * 49 + [101], 50.0),
                 ([-1] + [0] * 99 + [100] * 99 + [101], 50.0)]
        rng = random.Random(295)
        for size in (1, 2, 3, 99, 100, 101, 200, 1000):
            for _ in range(20):
                values = [rng.randrange(101) for _ in range(size)]
                for index in range(size // 100):
                    values[index] = rng.choice((-100000, -1, 101, 100000))
                rng.shuffle(values)
                cases.append((values, statistics.median(values)))
        for values, expected in cases:
            finder = BandCountMedianFinder()
            for value in values:
                finder.addNum(value)
            self.assertGreaterEqual(100 * sum(finder.frequencies), 99 * finder.size)
            self.assertEqual(finder.findMedian(), expected)
            self.assertEqual(sum(finder.frequencies) + finder.below + finder.above, len(values))

    def test_completed_stream_promise_does_not_cover_early_prefixes(self):
        values = [-999, 999] + [50] * 198  # Completed stream is exactly 99% in-band.
        exact, counts, prefix = ExactPrefixMedianFinder(), BandCountMedianFinder(), []
        for index, value in enumerate(values):
            exact.addNum(value)
            counts.addNum(value)
            prefix.append(value)
            self.assertEqual(exact.findMedian(), statistics.median(prefix))
            if index < 2:
                with self.assertRaises(ValueError):
                    counts.findMedian()
            else:
                self.assertEqual(counts.findMedian(), statistics.median(prefix))
        self.assertEqual(exact.lower_outliers, [-999])
        self.assertEqual(exact.upper_outliers, [999])

    def test_median_validation_keeps_state(self):
        for cls in (BoundedMedianFinder, BandCountMedianFinder, ExactPrefixMedianFinder):
            finder = cls()
            with self.assertRaises(ValueError):
                finder.findMedian()
            finder.addNum(50)
            invalid = (True, 1.5, "50", None, -100001, 100001)
            if cls is BoundedMedianFinder:
                invalid += (-1, 101)
            for value in invalid:
                with self.assertRaises(ValueError):
                    finder.addNum(value)
                self.assertEqual(finder.size, 1)
                self.assertEqual(finder.findMedian(), 50.0)

    def test_transfer_answer_failure_traces(self):
        self.assertEqual(WindowSolution().lengthOfLongestSubstring("abba"), 2)
        left, last, wrong_best = 0, {}, 0
        for right, char in enumerate("abba"):
            if char in last:
                left = last[char] + 1  # Deliberately missing max.
            last[char] = right
            wrong_best = max(wrong_best, right - left + 1)
        self.assertEqual(wrong_best, 3)  # The alleged "bba" window repeats b.
        self.assertEqual(JumpSolution().jump([0]), 0)
        # Keeping break but scanning the terminal index miscounts a singleton.
        singleton_steps = singleton_end = singleton_farthest = 0
        singleton = [0]
        for index in range(len(singleton)):
            singleton_farthest = max(singleton_farthest, index + singleton[index])
            if index == singleton_end:
                singleton_steps += 1
                singleton_end = singleton_farthest
                if singleton_end >= len(singleton) - 1:
                    break
        self.assertEqual(singleton_steps, 1)
        self.assertEqual(JumpSolution().jump([1, 1, 0]), 2)
        # If both arrival guards are removed, the terminal index adds a third step.
        steps = end = farthest = 0
        for index, value in enumerate([1, 1, 0]):
            farthest = max(farthest, index + value)
            if index == end:
                steps += 1
                end = farthest
        self.assertEqual(steps, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
