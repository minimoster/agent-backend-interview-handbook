"""Synthetic arithmetic only: no model, credentials, real prices or payments."""
import unittest
from decimal import Decimal as D

from cost_ledger import Attempt, RateCard, Usage, estimate, summarize


class CostLedgerTests(unittest.TestCase):
    def setUp(self):
        self.rates = RateCard("fictional-v1", "USD", D("2"), D("0.2"), D("8"))
        self.turns = [
            Attempt("r1", "succeeded", Usage(4000, 0, 500)),
            Attempt("r2", "failed", Usage(8000, 2000, 500)),
            Attempt("r3", "succeeded", Usage(12000, 4000, 1000)),
        ]

    def test_worked_example_and_failed_attempt_still_costs(self):
        result = summarize(self.turns, self.rates)
        self.assertEqual(result["requests"], 3)
        self.assertEqual(result["input_tokens"], 24000)
        self.assertEqual(result["cached_input_tokens"], 6000)
        self.assertEqual(result["output_tokens"], 2000)
        self.assertEqual(result["known_estimate"], D("0.0532"))
        self.assertEqual(result["known_estimate"] * 1000, D("53.2"))

    def test_cache_is_not_charged_twice(self):
        self.assertEqual(estimate(Usage(1000, 1000, 0), self.rates), D("0.0002"))

    def test_unknown_reserve_is_not_an_invoice_or_fabricated_tokens(self):
        result = summarize(self.turns + [Attempt("r4", "unknown", reserve=D("0.04"))], self.rates)
        self.assertEqual(result["unknown_requests"], 1)
        self.assertEqual(result["unknown_reserve"], D("0.04"))
        self.assertEqual(result["accounted_exposure"], D("0.0932"))
        self.assertEqual(result["input_tokens"], 24000)

    def test_reconciliation_replaces_unknown_row_not_appends_duplicate(self):
        reconciled = self.turns + [Attempt("r4", "failed", Usage(1000, 0, 0))]
        self.assertEqual(summarize(reconciled, self.rates)["accounted_exposure"], D("0.0552"))
        with self.assertRaises(ValueError):
            summarize(reconciled + [Attempt("r4", "unknown", reserve=D("0.04"))], self.rates)

    def test_empty_and_zero_usage(self):
        self.assertEqual(summarize([], self.rates)["accounted_exposure"], 0)
        self.assertEqual(estimate(Usage(0, 0, 0), self.rates), 0)

    def test_invalid_token_counts(self):
        for value in (-1, True, 0.5, "1"):
            for position in range(3):
                counts = [1, 0, 1]
                counts[position] = value
                with self.subTest(value=value, position=position), self.assertRaises(ValueError):
                    Usage(*counts)

    def test_cache_cannot_exceed_total_input(self):
        with self.assertRaises(ValueError):
            Usage(5, 6, 0)

    def test_invalid_money(self):
        for value in (D("-1"), D("NaN"), D("Infinity"), 0.2):
            with self.subTest(value=value), self.assertRaises(ValueError):
                RateCard("v1", "USD", value, D(0), D(0))
            with self.subTest(reserve=value), self.assertRaises(ValueError):
                Attempt("r", "unknown", reserve=value)

    def test_unknown_requires_explicit_reserve_and_no_usage(self):
        with self.assertRaises(ValueError):
            Attempt("r", "unknown")
        with self.assertRaises(ValueError):
            Attempt("r", "unknown", Usage(1, 0, 0), D(1))

    def test_known_usage_cannot_also_count_reservation(self):
        with self.assertRaises(ValueError):
            Attempt("r", "failed")
        with self.assertRaises(ValueError):
            Attempt("r", "succeeded", Usage(1, 0, 0), D(1))

    def test_identity_status_and_rate_snapshot(self):
        with self.assertRaises(ValueError):
            Attempt(" ", "unknown", reserve=D(0))
        with self.assertRaises(ValueError):
            Attempt("r", "not-sent", reserve=D(0))
        for snapshot, currency in (("", "USD"), ("v1", " ")):
            with self.assertRaises(ValueError):
                RateCard(snapshot, currency, D(0), D(0), D(0))


if __name__ == "__main__":
    unittest.main()
