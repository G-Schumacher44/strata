# Strata Workflow Skill

A step-by-step guide for running the full Strata analysis pipeline. Intended for agents
that can execute shell commands and read JSON — no codebase knowledge required.

---

## Prerequisites

- Python virtualenv at `.venv/` (run `python -m venv .venv && pip install -e .` once)
- A LookML repo cloned locally (path = `<REPO_PATH>`)
- Optional: a usage facts JSON file (see §3 below)
- Optional: a schema facts JSON file (see §4 below)

---

## Step 1 — Run the CI suite

```bash
make ci
```

This runs in order:
1. `pytest` — unit + integration tests (must all pass)
2. `scripts/validate.py` — deterministic gate (must return 10/10)
3. `scripts/check_strata.py` — scenario gates on gcs_analytics playground
4. `scripts/check_replay.py` — replay harness validation
5. `scripts/generate_outputs.py` — writes 8 JSON artifacts to `output/gcs_analytics/`

If any step fails, stop and report the error. Do not proceed to the dashboard.

---

## Step 2 — View the dashboard

```bash
make dashboard
```

Opens `http://localhost:8765/dashboard.html` in your browser. The dashboard is
self-contained HTML — you can also open `output/gcs_analytics/dashboard.html`
directly without the server.

If you get `OSError: [Errno 48] Address already in use`, kill the old server first:
```bash
pkill -f serve_dashboard
make dashboard
```

---

## Step 3 — Run against a different LookML repo

```bash
.venv/bin/python scripts/generate_outputs.py \
  --repo <REPO_PATH> \
  --usage-fixture <USAGE_JSON> \
  --schema-fixture <SCHEMA_JSON> \
  --out output/<REPO_NAME>

.venv/bin/python scripts/serve_dashboard.py \
  --repo <REPO_PATH> \
  --usage-fixture <USAGE_JSON> \
  --schema-fixture <SCHEMA_JSON>
```

Both `--usage-fixture` and `--schema-fixture` are optional. Without them, Strata
runs L0-only (structural analysis, no usage enrichment).

### Using .strata for repo-agnostic config

Create a `.strata` file at repo root (gitignored):

```makefile
REPO = /path/to/your/lookml
USAGE = /path/to/usage_facts.json
SCHEMA = /path/to/schema_facts.json
```

Then `make ci`, `make outputs`, `make dashboard` all use your repo automatically.
Copy `.strata.example` as your starting point.

---

## Step 4 — Understand the output files

All artifacts land in `output/<repo-name>/`:

| File | What it tells you |
|---|---|
| `catalog.json` | Every model/explore/view/field/PDT/table in the repo |
| `dead_code_register.json` | Views + explores with zero usage (safe to deprecate) |
| `pdt_ledger.json` | Each PDT: build count, bytes, cost/period, used/unused |
| `cleanup_roadmap.json` | Prioritized action list (deprecate / kill PDT / repair schema) |
| `schema_drift.json` | IR references tables or columns absent from warehouse schema |
| `migration_impact.json` | Per physical table: which views and explores break if it changes |
| `validation_scope.json` | Minimal explore set to revalidate for a set of changed files |
| `usage_summary.json` | Counts: explores, queries, dead, PDTs, schema drift issues |

---

## Step 5 — Interpret the findings

**Dead code** (`dead_code_register.json`): safe to deprecate when `static_reason`
(structural orphan) AND `usage_reason` (zero queries) both present. Never act on
static-only signal — extends chains can make views look orphaned when they aren't.

**PDT cost** (`pdt_ledger.json`): `status: "unused"` + `estimated_cost_usd > 0` →
immediate kill candidate. Confirm with the explore team before deleting.

**Schema drift** (`schema_drift.json`): `missing_table` → LookML points at a table
that doesn't exist in the warehouse. `missing_column` → a field's SQL references a
column the warehouse doesn't have. Both are silent breakage; fix before the next deploy.

**Migration impact** (`migration_impact.json`): before touching a physical table,
check this file. It lists every view, explore, and field that will break.

---

## Usage Facts Format

If you have Looker System Activity data (or are building a fixture), the usage facts
JSON must follow this schema:

```json
{
  "period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "days": 30},
  "explore_usage": [
    {"model": "my_model", "explore": "my_explore", "query_count": 120, "last_queried_at": "2026-06-06T08:00:00Z"}
  ],
  "content_references": [
    {"content_id": "dashboard_42", "content_type": "dashboard", "model": "my_model", "explore": "my_explore", "title": "Sales Overview"}
  ],
  "pdt_builds": [
    {"view": "my_pdt", "build_count": 30, "last_built_at": "2026-06-06T04:00:00Z", "bytes_processed": 5200000000, "estimated_cost_usd": 28.0}
  ]
}
```

`period` is optional but strongly recommended — without it the dashboard shows
"period unknown" instead of "last 30 days".

---

## Schema Facts Format

```json
{
  "tables": [
    {"name": "project.dataset.table", "columns": ["col1", "col2", "col3"]}
  ]
}
```

Table names must match the `sql_table_name` values in your LookML (without backticks).

---

## Capability Tiers

Strata is offline-first. It gains additional abilities when external data is available,
but its core never makes HTTP calls.

| Tier | What you provide | What Strata adds |
|---|---|---|
| L0 only | LookML repo | Structural analysis, extends chain, orphans |
| + usage fixture | Usage JSON | Dead code register, PDT ledger, cleanup roadmap |
| + schema fixture | Schema JSON | Schema drift, migration impact |
| + BQ MCP | Agent fetches schema via bq_query → writes schema JSON | Same as above, but live |
| + Looker MCP | Agent fetches usage via Looker API → writes usage JSON | Same as above, but live |
| + Looker live | `make auth` + `.strata` with LOOKER_URL | Full live: usage + cost pulled directly from Looker system activity |

For BQ schema via MCP: query `INFORMATION_SCHEMA.COLUMNS` in your project, write
the result as schema facts JSON, pass with `--schema-fixture`.

---

## Available Playgrounds

Three reference repos in `tests/lookml/` with matching fixtures in `tests/fixtures/`:

| Playground | Models | Explores | Focus |
|---|---|---|---|
| `thelook` | 1 | 3 | Basic extends, dead explore, active PDT |
| `gcs_analytics` | 2 | 7 | Gold/silver layer, legacy explores, PDT cost |
| `enterprise_mono` | 19 | 34 | Cross-model extends, zombie PDTs ($765K/yr), 3 legacy connections, schema drift |

Run any playground:

```bash
# thelook
make ci REPO=tests/lookml/thelook USAGE=tests/fixtures/thelook_usage_facts.json

# gcs_analytics (default)
make ci

# enterprise_mono
make ci REPO=tests/lookml/enterprise_mono \
  USAGE=tests/fixtures/enterprise_usage_facts.json \
  SCHEMA=tests/fixtures/enterprise_schema_facts.json
```

The enterprise_mono playground demonstrates the G4 scenario: two PDTs
(`pdt_customer_value_score` + `pdt_attribution_full_funnel`) running at $63,750/month
backed only by explores with zero queries — $765K/year in zombie compute surfaced.
