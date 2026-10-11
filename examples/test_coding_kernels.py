import json
import unittest
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier
from coding_kernels import (InventoryError, InventoryOrders, analyze_jsonl,
                            parse_safe_command, taxi_quote)

class InventoryTests(unittest.TestCase):
    def shop(self, bread=2):
        return InventoryOrders({"bread": bread, "leaf": 3},
                               {"sandwich": {"bread": 1}, "tea": {"leaf": 1}},
                               {"sandwich": 500, "tea": 200})
    def test_quote_original_pair_rule(self):
        self.assertEqual(self.shop().quote({"sandwich": 2, "tea": 1}), 1150)
    def test_atomic_reservation_and_repeated_request(self):
        shop = self.shop()
        order = shop.place("c", "one", {"sandwich": 1})
        self.assertEqual(shop.place("c", "one", {"sandwich": 1}), order)
        self.assertEqual(shop.snapshot_stock()["bread"], 1)
        with self.assertRaises(InventoryError):
            shop.place("c", "one", {"sandwich": 2})
        with self.assertRaises(InventoryError):
            shop.place("c", "two", {"sandwich": 2, "tea": 1})
        self.assertEqual(shop.snapshot_stock(), {"bread": 1, "leaf": 3})
    def test_cancel_releases_exactly_once(self):
        shop = self.shop()
        order = shop.place("c", "one", {"sandwich": 1})
        for _ in range(2):
            self.assertEqual(shop.transition("c", order, "cancelled"), "cancelled")
        self.assertEqual(shop.snapshot_stock()["bread"], 2)
        with self.assertRaises(InventoryError):
            shop.transition("c", order, "making")
    def test_state_and_customer(self):
        shop = self.shop()
        order = shop.place("c", "one", {"tea": 1})
        with self.assertRaises(InventoryError):
            shop.transition("other", order, "making")
        with self.assertRaises(InventoryError):
            shop.transition("c", order, "ready")
        for target in ("making", "ready", "picked_up"):
            self.assertEqual(shop.transition("c", order, target), target)
    def test_two_buyers_last_stock(self):
        shop = self.shop(bread=1)
        barrier = Barrier(2)
        def place(customer):
            barrier.wait(timeout=5)
            try:
                shop.place(customer, "key", {"sandwich": 1})
                return True
            except InventoryError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(place, ["a", "b"]))
        self.assertEqual(sorted(results), [False, True])
        self.assertEqual(shop.snapshot_stock()["bread"], 0)
    def test_bad_quantities(self):
        for quantity in (0, -1, True, 1.5):
            with self.assertRaises(InventoryError):
                self.shop().place("c", "k", {"tea": quantity})

class LogTests(unittest.TestCase):
    def test_p95_and_invalid_records(self):
        rows = [json.dumps({"ts": "2026-10-10T00:00:00Z", "status": 200, "latency_ms": 10}),
                json.dumps({"ts": "2026-10-10T00:00:01+00:00", "status": 503, "latency_ms": 100}),
                "bad secret", json.dumps({"ts": "2026-10-10T00:00:00", "status": 200, "latency_ms": 4})]
        result = analyze_jsonl(rows)
        self.assertEqual(result, {"valid": 2, "invalid_lines": [3, 4],
                                  "server_errors": 1, "p95_ms": 100})
        self.assertNotIn("secret", str(result))
    def test_empty_and_nonfinite(self):
        self.assertIsNone(analyze_jsonl([])["p95_ms"])
        row = '{"ts":"2026-10-10T00:00:00Z","status":200,"latency_ms":NaN}'
        self.assertEqual(analyze_jsonl([row])["invalid_lines"], [1])

class TaxiTests(unittest.TestCase):
    def test_day_and_night_only_fare(self):
        day = taxi_quote(distance_km="3", bags=2, wait_minutes="4", night=False)
        night = taxi_quote(distance_km="3", bags=2, wait_minutes="4", night=True)
        self.assertEqual(day["total"], "18.00")
        self.assertEqual(night["fare"], "15.60")
        self.assertEqual(night["luggage"], day["luggage"])
        self.assertEqual(night["waiting"], day["waiting"])
        self.assertEqual(night["total"], "20.60")
    def test_boundary_and_rounding(self):
        result = taxi_quote(distance_km="2.005", bags=0, wait_minutes="0", night=False)
        self.assertEqual(result["fare"], "10.02")
        self.assertEqual(taxi_quote(distance_km="2", bags=0, wait_minutes="0", night=False)["fare"], "10.00")
    def test_invalid_input(self):
        for distance in ("-1", "NaN", "abc", 2.5):
            with self.assertRaises(ValueError):
                taxi_quote(distance_km=distance, bags=0, wait_minutes="0", night=False)

class CommandTests(unittest.TestCase):
    def test_quoted_argument(self):
        self.assertEqual(parse_safe_command('grep "two words" sample.txt'),
                         {"command": "grep", "args": ["two words", "sample.txt"]})
    def test_reject_execution_constructs(self):
        for text in ('cat x; rm y', 'cat x | grep y', 'cat $(whoami)',
                     'cat `whoami`', 'cat x > y', 'unknown x', 'grep "unterminated', 'cat x\nrm y'):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_safe_command(text)

if __name__ == "__main__":
    unittest.main()
