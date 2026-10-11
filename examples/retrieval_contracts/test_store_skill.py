import importlib.util
from pathlib import Path
import sqlite3
import unittest

path = Path(__file__).parent / "skills/store-report/scripts/query.py"
spec = importlib.util.spec_from_file_location("store_query", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StoreSkillTests(unittest.TestCase):
    def test_catalog(self):
        self.assertEqual(module.query("catalog", "2026-02-28", 1)[0], {"id": 1, "name": "Tea"})

    def test_as_of_does_not_use_future_cancellation(self):
        rows = module.query("current_top", "2026-02-28", 1)
        self.assertEqual([r["revenue_cents"] for r in rows], [900, 400])
        after = module.query("current_top", "2026-03-02", 1)
        self.assertEqual(after, [{"id": 1, "name": "Tea", "revenue_cents": 600}])

    def test_lag_first_month_null(self):
        rows = module.query("trend", "2026-02-28", 1)
        self.assertIsNone(rows[0]["change"])
        self.assertEqual(rows[1]["change"], 1)

    def test_aggregates_before_join(self):
        rows = module.query("cross", "2026-02-28", 1)
        self.assertEqual(rows[0]["orders_count"], 3)
        self.assertEqual(rows[0]["booked_cents"], 1500)
        self.assertEqual(rows[0]["sample_count"], 3)
        self.assertEqual(rows[0]["failure_count"], 1)

    def test_store_scope(self):
        rows = module.query("cross", "2026-02-28", 2)
        self.assertEqual(rows[0]["booked_cents"], 3000)
        self.assertEqual(rows[0]["sample_count"], 0)

    def test_composite_unknown_not_zero_or_perfect(self):
        self.assertAlmostEqual(module.query("composite", "2026-02-28", 1)[0]["fixture_score"], 100 * 2 / 3)
        self.assertIsNone(module.query("composite", "2026-02-28", 2)[0]["fixture_score"])

    def test_empty_result(self):
        self.assertEqual(module.query("current_top", "2025-01-01", 1), [])

    def test_invalid_parameters(self):
        for report, as_of, store, limit in [("DROP TABLE orders", "2026-02-28", 1, 5),
                                          ("catalog", "2026-02-28' OR 1=1", 1, 5),
                                          ("catalog", "2026-02-28", 1, 100),
                                          ("catalog", "2026-02-28", True, 5),
                                          ("catalog", "2026-02-28", 3, 5)]:
            with self.assertRaises(ValueError):
                module.query(report, as_of, store, limit)

    def test_write_and_attach_denied(self):
        conn = module.fixture_connection()
        try:
            for sql in ["DELETE FROM orders", "ATTACH DATABASE ':memory:' AS extra"]:
                with self.assertRaises(sqlite3.DatabaseError):
                    conn.execute(sql)
        finally:
            conn.close()

    def test_registered_query_plans(self):
        conn = module.fixture_connection()
        try:
            for sql in module.QUERIES.values():
                plan = conn.execute("EXPLAIN QUERY PLAN " + sql, {"as_of": "2026-02-28", "store": 1, "limit": 10}).fetchall()
                self.assertTrue(plan)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
