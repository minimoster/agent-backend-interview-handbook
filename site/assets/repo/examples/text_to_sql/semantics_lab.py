"""Fixed synthetic SQLite counterexamples, not a SQL service or a sandbox.

Only named, developer-written queries and fixtures are executed in memory.
No model, network, file database, user SQL or production accuracy is involved.
"""
from collections import Counter
from contextlib import closing
import sqlite3

PARAMETERS = {"status": "paid", "start": "2026-10-01T00:00:00Z",
              "end": "2026-10-02T00:00:00Z"}
# One row per order; unknown buyers are excluded by the agreed metric.
CORRECT = """
SELECT buyer_id, COUNT(*) AS paid_orders
FROM orders
WHERE status = :status AND buyer_id IS NOT NULL
  AND paid_at >= :start AND paid_at < :end
GROUP BY buyer_id
"""
QUERIES = {
    "correct": CORRECT,
    "equivalent": """
        select o.buyer_id, count(1) as n
        from orders as o
        where o.paid_at < :end and o.status = :status
          and o.buyer_id is not null and o.paid_at >= :start
        group by o.buyer_id
    """,
    "wrong_join": """
        SELECT o.buyer_id, COUNT(*) AS paid_orders
        FROM orders AS o JOIN order_items AS i ON i.order_id = o.order_id
        WHERE o.status = :status AND o.buyer_id IS NOT NULL
          AND o.paid_at >= :start AND o.paid_at < :end
        GROUP BY o.buyer_id
    """,
    "wrong_end": CORRECT.replace("paid_at < :end", "paid_at <= :end"),
    "wrong_null": CORRECT.replace("buyer_id IS NOT NULL", "buyer_id != NULL"),
    "missing_null_policy": CORRECT.replace(" AND buyer_id IS NOT NULL", ""),
}
# All timestamp strings have the same UTC format. No timezone conversion is tested.
FIXTURES = {
    "empty": ([], []),
    "ordinary": (
        [(1, 7, "2026-10-01T00:00:00Z", "paid"),
         (2, 8, "2026-10-01T12:00:00Z", "paid")],
        [(1, "A"), (2, "B")]),
    "fanout": (
        [(1, 7, "2026-10-01T12:00:00Z", "paid")],
        [(1, "A"), (1, "A")]),
    "boundary": (
        [(1, 7, "2026-10-01T00:00:00Z", "paid"),
         (2, 7, "2026-10-02T00:00:00Z", "paid"),
         (3, 7, "2026-09-30T23:59:59Z", "paid")],
        [(1, "A"), (2, "B"), (3, "C")]),
    "nulls": (
        [(1, None, "2026-10-01T12:00:00Z", "paid"),
         (2, 7, "2026-10-01T12:00:00Z", "paid")],
        [(1, "A"), (2, "B")]),
}


def run_case(fixture_name, query_name):
    """Run one registered query on one registered fixture; return positional rows."""
    if fixture_name not in FIXTURES or query_name not in QUERIES:
        raise ValueError("Use a registered fixture and query name")
    orders, items = FIXTURES[fixture_name]
    with closing(sqlite3.connect(":memory:")) as connection:
        connection.executescript("""
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY, buyer_id INTEGER,
                paid_at TEXT NOT NULL, status TEXT NOT NULL);
            CREATE TABLE order_items (order_id INTEGER NOT NULL, sku TEXT NOT NULL);
        """)
        connection.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)
        connection.executemany("INSERT INTO order_items VALUES (?, ?)", items)
        return connection.execute(QUERIES[query_name], PARAMETERS).fetchall()


def same_result(left, right, *, ordered=False):
    """Exact positional Python-value comparison for this fixture's int/None rows.

    Bag comparison preserves duplicate multiplicity. This does not implement
    SQL type/collation/float equivalence or check column names and business units.
    """
    return left == right if ordered else Counter(left) == Counter(right)


if __name__ == "__main__":
    for fixture in FIXTURES:
        expected = run_case(fixture, "correct")
        actual = run_case(fixture, "wrong_join")
        print(f"{fixture}: correct={expected}, wrong_join={actual}, "
              f"bag_equal={same_result(expected, actual)}")
