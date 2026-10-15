"""Focused tests with independent sort and exact rational reference oracles."""
from fractions import Fraction
import math
import random
import unittest

from retrieval_worked_examples import rrf, rrf_scores, score_query, top_k


class RetrievalExamplesTests(unittest.TestCase):
    def test_worked_metrics(self):
        result = score_query(["B", "X", "A"], {"A": 3, "B": 2, "C": 1, "X": 0}, 3)
        self.assertAlmostEqual(result["precision_at_k"], 2 / 3)
        self.assertAlmostEqual(result["recall_at_k"], 2 / 3)
        self.assertEqual(result["rr_at_k"], 1)
        self.assertAlmostEqual(result["ndcg_at_k"], 6.5 / (7 + 3 / math.log2(3) + .5))

    def test_perfect_and_empty_results(self):
        grades = {"A": 3, "B": 2, "C": 1}
        self.assertEqual(score_query(["A", "B", "C"], grades, 3)["ndcg_at_k"], 1)
        result = score_query([], grades, 3)
        self.assertEqual(result["precision_at_k"], 0)
        self.assertEqual(result["recall_at_k"], 0)
        self.assertEqual(result["rr_at_k"], 0)
        self.assertEqual(result["ndcg_at_k"], 0)

    def test_short_result_uses_fixed_k(self):
        result = score_query(["A"], {"A": 1}, 5)
        self.assertEqual(result["precision_at_k"], .2)
        self.assertEqual(result["recall_at_k"], 1)

    def test_missing_judgment_and_no_positive(self):
        result = score_query(["unjudged"], {"A": 0}, 2)
        self.assertEqual(result["unjudged_returned"], 1)
        self.assertIsNone(result["recall_at_k"])
        self.assertIsNone(result["rr_at_k"])
        self.assertIsNone(result["ndcg_at_k"])

    def test_metric_contract_errors(self):
        for k in [0, -1, True, 1.5]:
            with self.assertRaises(ValueError):
                score_query([], {}, k)
        with self.assertRaises(ValueError):
            score_query(["A", "A"], {"A": 1}, 2)
        for grade in [-1, 4, True, 1.5]:
            with self.assertRaises(ValueError):
                score_query([], {"A": grade}, 2)

    def test_top_k_ties_and_negatives(self):
        self.assertEqual(top_k([("A", .2), ("B", .9), ("C", .5), ("D", .9)], 2),
                         [("B", .9), ("D", .9)])
        self.assertEqual(top_k([("A", -2), ("B", -1)], 1), [("B", -1)])
        self.assertEqual(top_k([], 4), [])

    def test_top_k_random_against_full_stable_sort(self):
        rng = random.Random(20261015)
        for n in range(50):
            items = [(f"doc-{i}", float(rng.randrange(-5, 6))) for i in range(n)]
            for k in [0, 1, 2, 10, 60]:
                expected = sorted(items, key=lambda item: item[1], reverse=True)[:k]
                self.assertEqual(top_k(iter(items), k), expected)

    def test_top_k_invalid_values_and_zero_consumption(self):
        for score in [float("nan"), float("inf"), float("-inf")]:
            with self.assertRaises(ValueError):
                top_k([("A", score)], 1)
        for k in [-1, True, 1.5]:
            with self.assertRaises(ValueError):
                top_k([], k)
        values = iter([("A", 2)])
        self.assertEqual(top_k(values, 0), [])
        self.assertEqual(next(values), ("A", 2))

    def test_rrf_worked_example_exact_reference(self):
        scores = rrf_scores([["A", "B", "C"], ["B", "D", "A"]], 10)
        expected = {"A": Fraction(1, 11) + Fraction(1, 13),
                    "B": Fraction(1, 12) + Fraction(1, 11),
                    "C": Fraction(1, 13), "D": Fraction(1, 12)}
        for doc_id, score in expected.items():
            self.assertAlmostEqual(scores[doc_id], float(score))
        self.assertEqual([x[0] for x in rrf([["A", "B", "C"], ["B", "D", "A"]], 4, 10)],
                         ["B", "A", "D", "C"])

    def test_rrf_within_list_duplicates_keep_first_physical_rank(self):
        scores = rrf_scores([["A", "A", "B"]], 10)
        self.assertAlmostEqual(scores["A"], 1 / 11)
        self.assertAlmostEqual(scores["B"], 1 / 13)

    def test_rrf_empty_ties_and_invalid_c(self):
        self.assertEqual(rrf([], 3), [])
        self.assertEqual([x[0] for x in rrf([["A"], ["B"]], 2)], ["A", "B"])
        for c in [0, -1, float("nan"), float("inf")]:
            with self.assertRaises(ValueError):
                rrf_scores([], c)


if __name__ == "__main__":
    unittest.main()
