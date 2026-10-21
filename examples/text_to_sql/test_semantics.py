"""Finite witnesses for the registered teaching queries; no semantic proof."""
import unittest

from semantics_lab import FIXTURES, QUERIES, run_case, same_result


class SemanticWitnessTests(unittest.TestCase):
    def test_empty_database_cannot_distinguish_wrong_queries(self):
        expected = run_case("empty", "correct")
        self.assertEqual(expected, [])
        for name in QUERIES:
            with self.subTest(query=name):
                self.assertTrue(same_result(expected, run_case("empty", name)))

    def test_nonempty_but_one_item_per_order_still_hides_fanout(self):
        expected = run_case("ordinary", "correct")
        self.assertTrue(same_result(expected, [(7, 1), (8, 1)]))
        self.assertTrue(same_result(expected, run_case("ordinary", "wrong_join")))
        self.assertTrue(same_result(expected, run_case("ordinary", "wrong_end")))

    def test_duplicate_items_are_a_wrong_grain_witness(self):
        self.assertEqual(run_case("fanout", "correct"), [(7, 1)])
        self.assertEqual(run_case("fanout", "wrong_join"), [(7, 2)])
        self.assertFalse(same_result(run_case("fanout", "correct"),
                                     run_case("fanout", "wrong_join")))

    def test_half_open_window_includes_start_but_excludes_end(self):
        self.assertEqual(run_case("boundary", "correct"), [(7, 1)])
        self.assertEqual(run_case("boundary", "wrong_end"), [(7, 2)])

    def test_null_comparison_and_unknown_buyer_policy_are_distinct(self):
        self.assertEqual(run_case("nulls", "correct"), [(7, 1)])
        self.assertEqual(run_case("nulls", "wrong_null"), [])
        self.assertTrue(same_result(run_case("nulls", "missing_null_policy"),
                                    [(None, 1), (7, 1)]))

    def test_text_different_equivalent_queries_agree_on_all_fixtures(self):
        self.assertNotEqual(QUERIES["correct"], QUERIES["equivalent"])
        for fixture in FIXTURES:
            with self.subTest(fixture=fixture):
                self.assertTrue(same_result(run_case(fixture, "correct"),
                                            run_case(fixture, "equivalent")))

    def test_unordered_bags_keep_duplicate_counts_and_nulls(self):
        rows = [(7,), (None,), (7,)]
        self.assertTrue(same_result(rows, [(7,), (7,), (None,)]))
        self.assertFalse(same_result(rows, [(7,), (None,)]))
        self.assertEqual(set(rows), set([(7,), (None,)]))  # a set would hide this bug

    def test_order_is_compared_only_when_contract_requests_it(self):
        left = [(7, 1), (8, 1)]
        right = list(reversed(left))
        self.assertTrue(same_result(left, right))
        self.assertFalse(same_result(left, right, ordered=True))
        self.assertTrue(same_result(left, list(left), ordered=True))

    def test_only_registered_examples_can_be_selected(self):
        with self.assertRaises(ValueError):
            run_case("ordinary", "SELECT * FROM orders")
        with self.assertRaises(ValueError):
            run_case("unknown", "correct")


if __name__ == "__main__":
    unittest.main()
