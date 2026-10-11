---
name: store-report
description: Explain reports from the bundled fictional store dataset using one of five fixed read-only query templates. Use for this fixture's catalog, historical top products, monthly order trend, aggregate totals or sample-based score. Do not use for real employees, private accounts, arbitrary SQL, writes, payments or publishing.
compatibility: CPython 3.12.14 and SQLite 3.53.1 for the recorded experiment. No network or model API required.
metadata:
  version: "1.0.0"
---

# Fictional store report

1. Confirm which registered report is needed and an explicit YYYY-MM-DD as-of date. Never silently substitute today's date for a historical request. Ask if a required date or fixture store is missing.
2. Read [schema and query meanings](references/schema.md) after the task is relevant. The dataset is entirely fictional; store 1 or 2 is a fixture selector, not a real authorization mechanism.
3. Run scripts/query.py with one registered report and a limit from 1 to 20. Do not accept arbitrary model-generated SQL. For a real deployment, the authenticated runtime supplies access scope and enforces it again at execution.
4. Check actual returned rows, units and as-of. Empty rows mean this query found no fixture matches; they do not prove a real-world event did not happen. NULL means unavailable, not zero.
5. Explain results using [report template](assets/report-template.md). The illustrative score is not a person's worth, influence or eligibility. Do not invent measured token savings or production latency.
6. If execution fails, report the exact category and retain the last verified result. Do not upload data, post a review or change any external state.

The bundled tests validate five SQL patterns and selected failure cases. They do not validate natural-language triggering, model SQL generation, production isolation or predictive usefulness of the score.
