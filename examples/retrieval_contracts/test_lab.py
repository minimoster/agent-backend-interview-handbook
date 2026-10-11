import unittest
from lab import (Span, covered_fraction, evidence_coverage, redundancy, ranking_metrics,
                 mmr, Evidence, select_current, route_catalog, union_length)


class SpanTests(unittest.TestCase):
    def test_partial_and_combined_coverage(self):
        gold = Span("rule", "v2", 10, 20)
        self.assertEqual(covered_fraction(gold, [Span("rule", "v2", 10, 15)]), .5)
        self.assertEqual(covered_fraction(gold, [Span("rule", "v2", 10, 15), Span("rule", "v2", 15, 20)]), 1)

    def test_old_revision_does_not_count(self):
        self.assertEqual(covered_fraction(Span("rule", "v2", 10, 20), [Span("rule", "v1", 0, 50)]), 0)

    def test_hit_is_not_all_evidence(self):
        gold = [Span("rule", "v2", 0, 10), Span("rule", "v2", 20, 30)]
        self.assertEqual(evidence_coverage(gold, [Span("rule", "v2", 0, 10)]), .5)

    def test_empty_gold_undefined(self):
        self.assertIsNone(evidence_coverage([], []))

    def test_overlaps_do_not_double_count(self):
        self.assertEqual(union_length([(0, 10), (3, 6), (5, 15)]), 15)

    def test_redundancy_and_source_grouping(self):
        self.assertEqual(redundancy([Span("a", "v1", 0, 10), Span("a", "v1", 5, 15)]), .25)
        self.assertEqual(redundancy([Span("a", "v1", 0, 10), Span("b", "v1", 0, 10)]), 0)

    def test_nonoverlap_is_valid(self):
        self.assertEqual(redundancy([Span("a", "v1", 0, 10), Span("a", "v1", 10, 20)]), 0)

    def test_invalid_and_zero_length(self):
        for args in [("a", "v1", 2, 2), ("a", "v1", -1, 2), ("", "v1", 0, 2), ("a", "v1", True, 3)]:
            with self.assertRaises(ValueError):
                Span(*args)


class RankingTests(unittest.TestCase):
    def test_hand_calculation(self):
        result = ranking_metrics(["X", "A", "Y", "B"], {"A": 1, "B": 1, "C": 1}, 4)
        self.assertEqual(result["recall_at_k"], 2 / 3)
        self.assertEqual(result["precision_at_k"], .5)
        self.assertEqual(result["rr_at_k"], .5)
        self.assertEqual(result["hit_at_k"], 1)

    def test_ideal_ndcg(self):
        self.assertEqual(ranking_metrics(["A", "B"], {"A": 3, "B": 1}, 2)["ndcg_at_k"], 1)

    def test_wrong_order_ndcg(self):
        self.assertLess(ranking_metrics(["B", "A"], {"A": 3, "B": 1}, 2)["ndcg_at_k"], 1)

    def test_short_list_precision_denominator(self):
        result = ranking_metrics(["A"], {"A": 1}, 4)
        self.assertEqual(result["precision_at_k"], .25)
        self.assertEqual(result["returned"], 1)

    def test_no_answer_not_perfect(self):
        result = ranking_metrics([], {}, 3)
        self.assertIsNone(result["recall_at_k"])
        self.assertIsNone(result["ndcg_at_k"])

    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):
            ranking_metrics(["A", "A"], {"A": 1}, 2)

    def test_invalid_k_and_grades(self):
        for k in [0, -1, True]:
            with self.assertRaises(ValueError):
                ranking_metrics([], {}, k)
        with self.assertRaises(ValueError):
            ranking_metrics([], {"A": -1}, 2)

    def test_mrr_first_hit_per_query(self):
        ranks = [["A"], ["X", "A"], ["X", "Y"]]
        rrs = [ranking_metrics(r, {"A": 1}, 2)["rr_at_k"] for r in ranks]
        self.assertEqual(sum(rrs) / len(rrs), .5)

    def test_mmr_diversity_and_weight(self):
        candidates = ["A", "B", "C"]
        rel = {"A": 1.0, "B": .95, "C": .8}
        similarity = {("A", "B"): .99, ("A", "C"): .1}
        self.assertEqual(mmr(candidates, rel, similarity, 2, 1), ["A", "B"])
        self.assertEqual(mmr(candidates, rel, similarity, 2, .5), ["A", "C"])


class FilteringTests(unittest.TestCase):
    def test_version_tenant_tombstone_and_dedupe(self):
        items = [Evidence("a1", "a", "doc", "v1", "old"), Evidence("a2", "a", "doc", "v2", "new"),
                 Evidence("b2", "b", "doc", "v2", "private"), Evidence("a2", "a", "doc", "v2", "new")]
        self.assertEqual([e.text for e in select_current(items, "a", {("a", "doc"): "v2"})], ["new"])
        self.assertEqual(select_current(items, "a", {}), [])

    def test_catalog_permission_and_budget(self):
        catalog = [{"identity": "s1.search", "tags": ["read", "docs"], "schema_units": 4},
                   {"identity": "s2.search", "tags": ["read", "docs"], "schema_units": 4},
                   {"identity": "s3.upload", "tags": ["write"], "schema_units": 1}]
        picked = route_catalog(catalog, {"s1.search", "s2.search"}, {"read"}, 5)
        self.assertEqual([item["identity"] for item in picked], ["s1.search"])
        self.assertEqual(route_catalog(catalog, set(), {"read"}, 10), [])

    def test_catalog_zero_budget(self):
        self.assertEqual(route_catalog([], set(), set(), 0), [])
        with self.assertRaises(ValueError):
            route_catalog([], set(), set(), -1)


if __name__ == "__main__":
    unittest.main()
