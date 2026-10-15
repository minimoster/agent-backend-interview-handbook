# Original retrieval and tool contract experiments

These examples use fictional data and do not read user files, call model APIs, send credentials, query real services, or change repositories. Run from this directory.

Recorded environment on 2026-10-10:
- CPython 3.12.14
- SQLite runtime 3.53.1 for the standard-library fixture
- MCP Python SDK 1.29.0, Pydantic 2.13.4, AnyIO 4.14.2 for the optional local stdio test
- SDK supported protocols: 2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25

Commands:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest test_lab test_store_skill -v
PYTHONDONTWRITEBYTECODE=1 python test_mcp_legacy.py
python skills/store-report/scripts/query.py current_top --as-of 2026-02-28 --store 1
```

The first command passed 30 unit tests: 20 span/ranking/MMR/filter/catalog contracts and 10 synthetic SQL Skill tests. The second completed one real local stdio session with 11 named assertions, negotiated exactly 2025-11-25 and exercised tools, schemas, errors, resource templates, prompts, progress and logs. It is an explicitly legacy experiment, not a modern 2026-07-28 implementation.

The minimal FastMCP instance did not implement logging/setLevel in the first probe; the final smoke test verifies actual request-linked log emission without asserting that optional control method exists. No packages were installed for these runs; already available pinned packages were used. To reproduce elsewhere, supply the recorded versions and review the pinned official sources before using another version.

Not tested: model routing, real token counts, embedding/ANN retrieval, generation, semantic quality, HTTP, OAuth, modern MCP, cancellation, persistent recovery, concurrency, graph extraction, GPU serving, load tests, real database authorization, cross-product Skill support, or production business outcomes. The SQLite authorizer and fixture scope are teaching controls, not a security proof. The fixed ranking numbers are not model retrieval measurements.

Primary sources:

- Agent Skills format, checked 2026-10-10

The skill package is original instructional material. It was not derived from an external review ZIP and is not evidence of a user's prior project experience.
