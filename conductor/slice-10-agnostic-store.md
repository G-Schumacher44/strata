# Slice 10 — Repo-Agnostic Config + L1 Time-Series Store

Date: 2026-06-06
Status: active → review
Type: slice
Mode: slice (cross-file, new module)

## Problem

1. **Hardcoding**: Makefile pointed `REPO`/`USAGE`/`SCHEMA` at gcs_analytics playground.
   Any user analyzing a different repo had to manually override multiple Makefile vars.
   The scripts were already generic (`--repo` etc.) but the Makefile made gcs_analytics
   the de-facto default.

2. **No date slicing offline**: Usage fixture was an aggregated snapshot (total query
   counts for a fixed window). Without time-series rows, re-slicing by window (7d vs 30d)
   was impossible offline. The `period` label on the dashboard was decoration, not function.

## Solution

### A — Config file

`.strata` (gitignored Makefile fragment) lets users set `REPO`, `SCHEMA`, `DAYS` once.
Makefile uses `-include .strata` + `?=` fallbacks to the playground defaults.
`.strata.example` checked in as the template. Zero Makefile changes required for new repos.

### B — L1 time-series store (`strata_usage.db`)

`src/strata/l1/store.py` — SQLite with three tables:
- `explore_queries (model, explore, query_date, query_count)`
- `pdt_builds (view, build_date, bytes_processed, cost_usd)`
- `content_refs (content_id, content_type, model, explore, title, recorded_date)`

`import_fixture(store, fixture)` — imports a period-aware fixture JSON into the store,
distributing aggregated counts evenly across each day in the declared period.
ON CONFLICT replaces (safe to re-import).

`query_window(store, days=30)` — returns aggregated `UsageFacts`-shaped dict for
the last N days anchored to the store's own max date (not wall-clock time).
Drop-in replacement for `load_usage_facts()`.

## Files Changed

| File | Change |
|---|---|
| `src/strata/l1/store.py` | NEW — SQLite L1 time-series store |
| `scripts/import_usage.py` | NEW — fixture → store import entry point |
| `src/strata/pipeline.py` | Added `build_graph_from_store(repo, store, days, schema)` |
| `scripts/generate_outputs.py` | Added `--store` / `--days`; uses store when present |
| `scripts/serve_dashboard.py` | Added `--store` / `--days`; uses store when present |
| `Makefile` | `-include .strata`, `?=` defaults, `import` target, `DAYS` var, `make ci` includes `import` |
| `.strata.example` | NEW — config template |
| `.gitignore` | Added `.strata` |
| `src/strata/outputs/dashboard.py` | Period tag in header (start→end · N-day window) |

## Invariants Preserved

- IR contract (`types.py`) — untouched
- `UsageProvider` protocol — untouched (store implements same dict shape)
- Artifact JSON formats — unchanged
- Test fixtures — unchanged; tests still use fixture files
- `strata_ir.db` — untouched

## make ci flow (updated)

```
test → validate → check → check-replay → import → outputs
```

`import` seeds/updates the store from `USAGE` fixture. `outputs` reads from store.
Both steps are idempotent. First run seeds; subsequent runs refresh.

## Verification

```bash
make ci           # 36 passed, 10/10, store seeded, artifacts written
make dashboard    # header shows "2026-05-08 → 2026-06-06 · 30-day window"
make ci DAYS=7    # re-runs with 7-day window; total_queries drops proportionally
```

## Next Steps

1. Move to review/ once `make ci` and `make dashboard` confirmed green
2. BQ MCP provider: agent calls `bq_query` → appends rows directly to store (skips fixture)
3. Slice 07 (live Looker): `LookerSystemActivityProvider` appends to same store on each run
