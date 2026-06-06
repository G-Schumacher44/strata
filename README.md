# Strata

**Deterministic LookML analysis engine.** Maps your entire LookML graph, surfaces dead
explores, zombie PDTs, and schema drift — offline, read-only, zero tokens for the hard parts.

> Do the heavy lifting deterministically. Use AI as a thin synthesis layer over pre-digested structure.

Parsing, dependency graphing, dead-code detection, and PDT cost analysis are deterministic
problems. They cost zero tokens. The LLM only touches a synthesis layer over a clean,
pre-built IR — cheap model, competent output. Gets cheaper over time.

---

## What It Finds

| Finding | Example |
|---|---|
| **Zombie PDTs** | 2 PDTs rebuilding at $63,750/month — backed by explores with zero queries |
| **Dead explores** | 6 explores with no queries in 30 days, surfaced with dual evidence |
| **Schema drift** | 7 LookML fields referencing columns dropped from the warehouse |
| **Orphan views** | Views defined but never joined or used as an explore base |
| **Migration blast radius** | Drop a BQ table → immediately see every view, explore, and field that breaks |
| **Validation scope** | Change a view file → minimal set of explores that need revalidation before merge |

---

## Architecture

```
LookML repo (read-only clone)
        │
        ▼
   [L0 — IR]  Parse entire repo → canonical node/edge graph. No LLM. No network.
        │
        ▼
   [L1 — Enrichment]  Join IR against usage facts + schema facts. No LLM.
        │           ▲
        │           └── fixture JSON (offline CI)
        │           └── Looker System Activity (opt-in live)
        ▼
   [L2 — Synthesis]  One explore = one verdict with evidence. Cheap model.
        │
        ├── JSON artifacts  (catalog, dead code, PDT ledger, schema drift, ...)
        ├── HTML dashboard  (make dashboard)
        └── MCP tools       (stdio, read-only, IDE-native)
```

**L0 and L1 never call any LLM or external API.** The MCP server is stdio-only — no
inbound ports, no cloud dependency. All analysis runs locally.

---

## Quickstart

```bash
git clone https://github.com/G-Schumacher44/strata-oss.git
cd strata-oss
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run against the included gcs_analytics playground
make ci

# See the dashboard
make dashboard
```

`make ci` runs in order: pytest → validate.py → check_strata.py → check_replay.py → generate_outputs.py

All 44 tests pass offline. No Looker instance, no BQ credentials, no API keys.

---

## Run Against Your Repo

Point Strata at any LookML repo with a usage fixture and schema fixture:

```bash
# Minimal — structural analysis only (L0)
python scripts/generate_outputs.py \
  --repo /path/to/your/lookml \
  --out output/myrepo

# With usage facts — adds dead code, PDT cost, cleanup roadmap
python scripts/generate_outputs.py \
  --repo /path/to/your/lookml \
  --usage-fixture /path/to/usage_facts.json \
  --out output/myrepo

# With schema facts — adds schema drift, migration impact
python scripts/generate_outputs.py \
  --repo /path/to/your/lookml \
  --usage-fixture /path/to/usage_facts.json \
  --schema-fixture /path/to/schema_facts.json \
  --out output/myrepo
```

Use `.strata` at project root (gitignored) to make your repo the default:

```makefile
# .strata  (copy from .strata.example)
REPO  = /path/to/your/lookml
USAGE = /path/to/usage_facts.json
SCHEMA = /path/to/schema_facts.json
```

Then `make ci`, `make outputs`, `make dashboard` all use your repo.

---

## Output Artifacts

`generate_outputs.py` writes 8 JSON files under `output/<repo-name>/`:

| File | What it tells you |
|---|---|
| `catalog.json` | Every model, explore, view, field, PDT, and physical table |
| `usage_summary.json` | Query counts, dead/active totals, period metadata |
| `dead_code_register.json` | Dead explores + orphan views with dual evidence (structural + usage) |
| `pdt_ledger.json` | Every PDT: build count, bytes processed, cost/period, zombie status |
| `schema_drift.json` | Fields referencing columns or tables absent from warehouse schema |
| `migration_impact.json` | Per physical table: views, explores, fields that break if it changes |
| `cleanup_roadmap.json` | Prioritized action list: kill zombie PDT, deprecate explore, fix drift |
| `validation_scope.json` | Minimal explore set to revalidate for a given set of changed files |

---

## MCP Server (Claude Code / IDE Integration)

Strata runs as a stdio MCP server — Claude Code picks it up automatically from `.mcp.json`.

```bash
# Launch manually (defaults to enterprise_mono playground)
bash scripts/mcp_server.sh

# Point at your repo
STRATA_REPO_PATH=/path/to/lookml \
STRATA_USAGE_FIXTURE=/path/to/usage_facts.json \
bash scripts/mcp_server.sh
```

**10 read-only MCP tools:**

| Tool | What it returns |
|---|---|
| `strata_ir_status` | IR health: node/edge counts, build time, cache state |
| `strata_usage_summary` | Aggregates: explore count, dead count, PDT count, drift count |
| `strata_dead_code_register` | All dead explores and orphan views with dual evidence |
| `strata_pdt_costs` | All PDTs with build count, cost, zombie status, backing explores |
| `strata_schema_drift` | All missing column/table drift records |
| `strata_explore_deps` | Base view, joins, field count, resolution chain for an explore |
| `strata_query_field` | SQL, type, tags, source file for a specific field |
| `strata_list_orphans` | All structural orphans (views, explores, fields) |
| `strata_validation_scope` | Explores to revalidate given a set of changed files/objects |
| `strata_impact` | Views, explores, fields that depend on a physical table |

Run the full governance workflow test (all 10 tools, 3 playgrounds):
```bash
python scripts/test_mcp_live.py --playground enterprise_mono
```

---

## Playgrounds

Three offline test repos with matching usage and schema fixtures:

| Playground | Models | Explores | What it demonstrates |
|---|---|---|---|
| `thelook` | 1 | 8 | Basic extends, dead explores, zombie PDT ($432/30d) |
| `gcs_analytics` | 3 | 7 | Gold/silver layer, orphan views, unused PDT ($156/30d) |
| `enterprise_mono` | 19 | 34 | Cross-model extends, $63,750/30d zombie PDTs (~$765K/yr), 6 dead explores, 7 schema drift hits |

```bash
make ci                                          # gcs_analytics (default)
make ci REPO=tests/lookml/thelook \
        USAGE=tests/fixtures/playground_usage_facts.json \
        SCHEMA=tests/fixtures/playground_schema_facts.json
make ci REPO=tests/lookml/enterprise_mono \
        USAGE=tests/fixtures/enterprise_usage_facts.json \
        SCHEMA=tests/fixtures/enterprise_schema_facts.json
```

---

## Capability Tiers

Strata is offline-first. It gains capability as you provide more data — but the core never
makes network calls.

| Tier | What you provide | What Strata adds |
|---|---|---|
| L0 only | LookML repo | Structural graph, extends chains, orphans |
| + usage fixture | Usage JSON | Dead code, PDT ledger, cleanup roadmap |
| + schema fixture | Schema JSON | Schema drift, migration blast radius |
| + Looker live | OAuth token | Usage pulled directly from Looker System Activity |

---

## Live Looker (opt-in)

```bash
python scripts/strata_auth.py login --looker-url https://your-instance.looker.com
python scripts/generate_outputs.py \
  --repo /path/to/lookml \
  --looker-url https://your-instance.looker.com \
  --out output/live
```

Missing live config fails fast with a clear message. Ordinary CI has no live dependency.

---

## Fixture Formats

**Usage facts** (`--usage-fixture`):
```json
{
  "period": {"start": "2026-05-07", "end": "2026-06-06", "days": 30},
  "explore_usage": [
    {"model": "my_model", "explore": "my_explore", "query_count": 120, "last_queried_at": "2026-06-06T08:00:00Z"}
  ],
  "pdt_builds": [
    {"view": "my_pdt", "build_count": 30, "last_built_at": "2026-06-06T04:00:00Z",
     "bytes_processed": 5200000000, "estimated_cost_usd": 28.0}
  ]
}
```

**Schema facts** (`--schema-fixture`):
```json
{
  "tables": [
    {"name": "project.dataset.table", "columns": ["col1", "col2", "col3"]}
  ]
}
```

Table names must match `sql_table_name` values in your LookML (without backticks).
For BQ: query `INFORMATION_SCHEMA.COLUMNS` and reshape to this format.

---

## Docs

| Doc | What's in it |
|---|---|
| [`docs/testing-scenarios.md`](docs/testing-scenarios.md) | Three public verification scenarios (L0, L1, Enterprise G4) |
| [`docs/testing-findings.md`](docs/testing-findings.md) | Full findings from all three playgrounds with real numbers |
| [`docs/playground-guide.md`](docs/playground-guide.md) | Tour of each playground and what to look for |
| [`docs/offline-first-walkthrough.md`](docs/offline-first-walkthrough.md) | Full offline analysis guide — no internet required |
| [`docs/security-hardening.md`](docs/security-hardening.md) | Read-only enforcement, credential matrix, MCP security model |
| [`docs/enterprise-deployment.md`](docs/enterprise-deployment.md) | IAM, ADC, OIDC for GH Actions, Google Workspace path |
| [`docs/looker-ecosystem.md`](docs/looker-ecosystem.md) | How Strata fits with Looker MCP Server and Looker Extension |
| [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) | Contribution guide |
| [`skills/strata_workflow.md`](skills/strata_workflow.md) | Step-by-step workflow for agents and humans |
| [`skills/strata_agentic_runbook.md`](skills/strata_agentic_runbook.md) | Autonomous agent playbook |

---

## License

Apache 2.0. See [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md).
