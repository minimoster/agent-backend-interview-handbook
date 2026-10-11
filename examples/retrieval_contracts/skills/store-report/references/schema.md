# Fixture schema and query meanings

The script builds six in-memory tables: stores and products are lookup identities; orders links store and creation date; order_items links an order and product with quantity and price_cents; status_events records effective dated status changes; service_samples records dated binary failures. Foreign keys preserve fixture relationships. Dates are day-granularity canonical strings, and as_of includes that date. This is a deliberate demonstration convention, not a universal business-time schema. Real timestamp queries must fix timezone, inclusivity, and effective versus observed time.

The five registered reports are:
- catalog: product identities, no customer data
- current_top: latest effective status at or before as_of using ROW_NUMBER, then completed-order revenue by product
- trend: order counts by creation month and LAG change; the first month's change is NULL
- cross: order totals and service totals are aggregated separately before joining to avoid multiplying rows
- composite: a CTE computes sample_count and a fictional score 100 times (1 minus failure fraction); no samples produce NULL. This is only a described formula, not a validated predictive model

North fixture has booked order-item value 1500 cents at 2026-02-28; that includes a cancelled order, so booked_cents is deliberately not recognized revenue. Completed-order product totals on that date are 900 and 400 cents. A later cancellation changes the historical status view only when as_of reaches it. Future events must not leak into earlier snapshots.

Fixed queries use bound values and LIMIT. A read-only connection and authorizer deny writes and ATTACH. Those are teaching controls, not a complete security proof. Arbitrary SQL cannot enter this route. Explain query plans rather than assuming CTEs always improve performance; tiny fixture plans do not establish production latency.

Sources: [Python sqlite3](https://docs.python.org/3.12/library/sqlite3.html), [SQLite window functions](https://www.sqlite.org/windowfunctions.html), [SQLite query planning](https://www.sqlite.org/queryplanner.html). The actual recorded runtime versions are in the experiment README.
