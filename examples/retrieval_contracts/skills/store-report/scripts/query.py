"""Original six-table synthetic fixture and five fixed read-only query templates.
CPython 3.12.14, SQLite 3.53.1. No real accounts, files, model calls or network.
"""
import argparse
from datetime import date
import json
import sqlite3
import time

SCHEMA = """
CREATE TABLE stores (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, store_id INTEGER NOT NULL REFERENCES stores(id), created_on TEXT NOT NULL);
CREATE TABLE order_items (order_id INTEGER NOT NULL REFERENCES orders(id), product_id INTEGER NOT NULL REFERENCES products(id), quantity INTEGER NOT NULL, price_cents INTEGER NOT NULL);
CREATE TABLE status_events (order_id INTEGER NOT NULL REFERENCES orders(id), effective_on TEXT NOT NULL, status TEXT NOT NULL, PRIMARY KEY(order_id,effective_on));
CREATE TABLE service_samples (store_id INTEGER NOT NULL REFERENCES stores(id), observed_on TEXT NOT NULL, failed INTEGER NOT NULL CHECK(failed IN (0,1)));
CREATE INDEX orders_by_store_date ON orders(store_id,created_on);
CREATE INDEX samples_by_store_date ON service_samples(store_id,observed_on);
"""
QUERIES = {
    "catalog": """SELECT id,name FROM products ORDER BY id LIMIT :limit""",
    "current_top": """
WITH ranked AS (
 SELECT se.order_id,se.status,
 ROW_NUMBER() OVER(PARTITION BY se.order_id ORDER BY se.effective_on DESC) AS rn
 FROM status_events se JOIN orders o ON o.id=se.order_id
 WHERE o.store_id=:store AND o.created_on<=:as_of AND se.effective_on<=:as_of
)
SELECT p.id,p.name,SUM(oi.quantity*oi.price_cents) AS revenue_cents
FROM ranked r JOIN order_items oi ON oi.order_id=r.order_id JOIN products p ON p.id=oi.product_id
WHERE r.rn=1 AND r.status='completed'
GROUP BY p.id,p.name ORDER BY revenue_cents DESC,p.id LIMIT :limit
""",
    "trend": """
WITH monthly AS (
 SELECT substr(created_on,1,7) AS month,COUNT(*) AS orders_count
 FROM orders WHERE store_id=:store AND created_on<=:as_of GROUP BY month
)
SELECT month,orders_count,orders_count-LAG(orders_count) OVER(ORDER BY month) AS change
FROM monthly ORDER BY month LIMIT :limit
""",
    "cross": """
WITH order_totals AS (
 SELECT o.store_id,COUNT(DISTINCT o.id) AS orders_count,SUM(oi.quantity*oi.price_cents) AS booked_cents
 FROM orders o JOIN order_items oi ON oi.order_id=o.id
 WHERE o.store_id=:store AND o.created_on<=:as_of GROUP BY o.store_id
), sample_totals AS (
 SELECT store_id,COUNT(*) AS sample_count,SUM(failed) AS failure_count
 FROM service_samples WHERE store_id=:store AND observed_on<=:as_of GROUP BY store_id
)
SELECT s.id,s.name,COALESCE(o.orders_count,0) AS orders_count,COALESCE(o.booked_cents,0) AS booked_cents,
 COALESCE(t.sample_count,0) AS sample_count,COALESCE(t.failure_count,0) AS failure_count
FROM stores s LEFT JOIN order_totals o ON o.store_id=s.id LEFT JOIN sample_totals t ON t.store_id=s.id
WHERE s.id=:store LIMIT :limit
""",
    "composite": """
WITH stats AS (
 SELECT store_id,COUNT(*) AS sample_count,SUM(failed) AS failures
 FROM service_samples WHERE store_id=:store AND observed_on<=:as_of GROUP BY store_id
)
SELECT s.id,s.name,COALESCE(t.sample_count,0) AS sample_count,
 CASE WHEN t.sample_count>0 THEN 100.0*(1.0-t.failures*1.0/t.sample_count) ELSE NULL END AS fixture_score
FROM stores s LEFT JOIN stats t ON t.store_id=s.id WHERE s.id=:store LIMIT :limit
""",
}


def fixture_connection():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO stores VALUES (?,?)", [(1, "North fixture"), (2, "South fixture")])
    conn.executemany("INSERT INTO products VALUES (?,?)", [(1, "Tea"), (2, "Bread")])
    conn.executemany("INSERT INTO orders VALUES (?,?,?)", [(1, 1, "2026-01-03"), (2, 1, "2026-02-04"), (3, 1, "2026-02-20"), (4, 2, "2026-02-10")])
    conn.executemany("INSERT INTO order_items VALUES (?,?,?,?)", [(1, 1, 2, 300), (2, 1, 1, 300), (2, 2, 2, 200), (3, 2, 1, 200), (4, 1, 10, 300)])
    conn.executemany("INSERT INTO status_events VALUES (?,?,?)", [(1, "2026-01-03", "completed"), (2, "2026-02-04", "completed"), (2, "2026-03-01", "cancelled"), (3, "2026-02-20", "cancelled"), (4, "2026-02-10", "completed")])
    conn.executemany("INSERT INTO service_samples VALUES (?,?,?)", [(1, "2026-02-01", 0), (1, "2026-02-02", 1), (1, "2026-02-03", 0)])
    conn.commit()
    conn.execute("PRAGMA query_only=ON")
    deadline = time.monotonic() + 2
    conn.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
    permitted = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
    conn.set_authorizer(lambda action, a1, a2, db, source: sqlite3.SQLITE_OK if action in permitted else sqlite3.SQLITE_DENY)
    return conn


def query(report: str, as_of: str, store: int, limit: int = 10):
    if report not in QUERIES:
        raise ValueError("choose a registered report, not arbitrary SQL")
    if type(store) is not int or store not in {1, 2}:
        raise ValueError("fixture store required; real scope must come from authenticated runtime")
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("limit must be an integer in [1,20]")
    try:
        parsed = date.fromisoformat(as_of)
    except (TypeError, ValueError) as exc:
        raise ValueError("canonical YYYY-MM-DD as_of required") from exc
    if parsed.isoformat() != as_of:
        raise ValueError("canonical YYYY-MM-DD as_of required")
    conn = fixture_connection()
    try:
        return [dict(row) for row in conn.execute(QUERIES[report], {"as_of": as_of, "store": store, "limit": limit})]
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report", choices=QUERIES)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--store", required=True, type=int, choices=[1, 2])
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    print(json.dumps({"fixture": True, "as_of": args.as_of, "store": args.store,
                      "rows": query(args.report, args.as_of, args.store, args.limit)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
