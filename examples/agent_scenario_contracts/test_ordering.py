import unittest
from dataclasses import replace
from ordering import Approval, OrderTask, Quote, run_bounded


def quote():
    return Quote("Test shop", "Tea", "Small, no sugar", 1, 1200, "CNY", "Test pickup point", "v1")


def approved():
    task = OrderTask("test-user", "test-operation-1")
    task.preview(quote())
    task.approve(Approval(task.principal, task.quote.fingerprint()))
    return task


class ScenarioContracts(unittest.TestCase):
    def test_no_approval_no_effect(self):
        t = OrderTask("test-user", "op")
        t.preview(quote())
        calls = []
        with self.assertRaises(RuntimeError):
            t.submit(lambda *a: calls.append(a) or "order-1")
        self.assertEqual(calls, [])

    def test_wrong_principal_denied(self):
        t = OrderTask("test-user", "op")
        t.preview(quote())
        with self.assertRaises(PermissionError):
            t.approve(Approval("other-user", t.quote.fingerprint()))

    def test_changed_quote_invalidates_approval(self):
        t = approved()
        old = Approval(t.principal, t.quote.fingerprint())
        t.preview(replace(t.quote, total_cents=1300, revision="v2"))
        with self.assertRaises(PermissionError):
            t.approve(old)
        self.assertEqual(t.state, "preview")

    def test_same_operation_returns_known_result(self):
        t = approved()
        calls = []
        effect = lambda *a: calls.append(a) or "order-1"
        self.assertEqual(t.submit(effect), "order-1")
        self.assertEqual(t.submit(effect), "order-1")
        self.assertEqual(len(calls), 1)

    def test_effect_then_timeout_not_retried(self):
        t = approved()
        calls = []
        def effect(*args):
            calls.append(args)
            raise TimeoutError("response lost after provider created order")
        with self.assertRaises(TimeoutError):
            t.submit(effect)
        with self.assertRaises(RuntimeError):
            t.submit(effect)
        self.assertEqual(t.state, "unknown")
        self.assertEqual(len(calls), 1)
        t.reconcile_created(t.operation_id, "verified-order-1")
        self.assertEqual(t.state, "succeeded")

    def test_reconciliation_cannot_mix_identity(self):
        t = approved()
        t.state = "unknown"
        with self.assertRaises(RuntimeError):
            t.reconcile_created("other-op", "order-1")

    def test_cancel_prevents_creation(self):
        t = approved()
        t.cancel()
        with self.assertRaises(RuntimeError):
            t.submit(lambda *a: "order-1")
        self.assertEqual(t.state, "cancelled")

    def test_local_cancel_does_not_undo_created_order(self):
        t = approved()
        t.submit(lambda *a: "order-1")
        with self.assertRaises(RuntimeError):
            t.cancel()
        self.assertEqual(t.order_id, "order-1")

    def test_bad_provider_result_is_unknown(self):
        t = approved()
        with self.assertRaises(ValueError):
            t.submit(lambda *a: None)
        self.assertEqual(t.state, "unknown")

    def test_invalid_bool_and_empty_fields_rejected(self):
        for q in [replace(quote(), quantity=True), replace(quote(), destination="")]:
            with self.assertRaises(ValueError):
                q.validate()

    def test_loop_budget_checked_before_action(self):
        self.assertEqual(run_bounded(["one", "two"], 0), ("budget_exhausted", 0))
        self.assertEqual(run_bounded(["one", "two"], 1), ("budget_exhausted", 1))

    def test_loop_repeated_observation(self):
        self.assertEqual(run_bounded(["same", "same", "same"], 10), ("no_progress", 2))


if __name__ == "__main__":
    unittest.main()
