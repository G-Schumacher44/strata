# Strata — AI-Enabled BI Governance for Looker

LookML repos accumulate debt silently. Explores stop getting queried. PDTs keep rebuilding.
Fields reference columns that got dropped in the last migration. Nobody's dashboards break —
yet — but the cost is real and the risk is compounding.

The tools that exist today help you write LookML correctly. Strata helps you understand what
your LookML is actually doing, what it costs, and what it's safe to change — inside your
AI client, in CI, or from the terminal.

---

## The Gap

| Tool | What it does | Where it stops |
|---|---|---|
| **LookML IDE / Extension** | Syntax validation, autocomplete, inline errors | Doesn't know query history, cost, or which explores are actually used |
| **Looker MCP Server** | Gives Claude live API access to Looker objects and system activity | A bridge for agents — surfaces data, doesn't analyze it |
| **Spectacles / content validation** | Runs explores in Looker to catch SQL compile errors | Reactive — tests what exists, doesn't surface what should be removed |
| **Looker native alerting** | Flags broken dashboards and scheduled query failures | Catches failures after they happen, not structural risk before it does |

None of these answer:

- Which of my 80 explores has zero queries in the last 30 days?
- Which PDTs are rebuilding on a schedule but serving nobody?
- If I drop this BQ column, what breaks — and how bad?
- Can I remove this view without touching a dashboard anywhere?
- What's the minimum set of explores I need to revalidate before merging this PR?

Strata is the analysis layer between your static LookML files and your living Looker instance.

---

## The Workflow

Strata runs as a **local MCP server**. Your AI client (Claude, Cursor, Gemini) calls read-only
tools. Skills guide the investigation — pulled on demand, zero tokens until needed.

```
Agent calls: strata_dead_code_register
  → 6 dead explores, 2 zombie PDTs, $63,750/mo in unused compute

Agent reads skill: semantic_layer_audit
  → structured procedure: what to check, stop conditions, escalation scripts

Agent calls: strata_explore_deps("dead_finance_v2", "em_legacy_v2")
  → full join graph: 4 views, 1 zombie PDT backing this explore

Agent calls: strata_schema_drift
  → 14 drift hits across 3 tables — column drops not yet reflected in LookML

Agent produces: prioritized remediation backlog
```

**No Looker access required for L0/L1.** The IR is built from your LookML files only.

Usage data (query counts, PDT build costs) comes from fixture JSON files in offline mode,
or from the live Looker API when you authenticate via OAuth. The pipeline is identical either
way — the seam is at L1. Without usage data, the conservative default applies: any explore
with no evidence of queries is flagged as potentially dead.

---

## Philosophy

> Do the heavy lifting deterministically. Use AI as a thin synthesis layer over pre-digested structure.

Parsing LookML, resolving extends chains, detecting dead code, computing PDT cost — these
are deterministic problems. They cost zero tokens. The structure doesn't need an LLM to
understand it; it needs to be mapped.

Strata maps it first. Then a cheap model reasons over a clean, structured context. This gets
more capable as models improve, and cheaper over time. The deterministic layer never changes.

**L0 and L1 never call any LLM or external API.** The MCP server is stdio-only. All
analysis runs locally on a read-only clone. Nothing is sent anywhere.

---

## What It Detects

**Dead code campaigns.** Know exactly which explores haven't been queried, for how long,
and whether any dashboard content still references them. Dual evidence — structural orphan
status *and* zero usage — prevents false positives before you deprecate anything.

**PDT cost visibility.** Surface which PDTs are building on schedule but serving dead
explores. Cross-reference build cost with query volume to identify zombie compute. Get the
annualized number before you walk into the conversation with the team.

**Safe migrations.** Before dropping a BQ column or renaming a table, run impact analysis
across the full LookML graph. See every view, explore, and field that depends on it. Know
the blast radius before the first PR is opened.

**Schema drift detection.** LookML that references a column the warehouse dropped compiles
fine in Looker — it just fails silently at query time. Strata catches these before your users do.

**CI governance.** `strata check` runs the full analysis suite offline — no Looker instance,
no credentials, no flaky API calls. Every PR gets deterministic gate coverage: extends chains
resolved, dead code counted, drift checked, validation scope computed.

**IDE-native investigation.** Load Strata as an MCP server in Claude Code or Cursor.
Ask it which explores break if you change a view. Ask it to audit your PDT costs. Ask it
what needs revalidation before a merge. It answers from a pre-built IR — fast, read-only, local.

---

## Why Looker / LookML

Strata is specific by design. LookML's declarative model — explicit `explore:`, `join:`,
`view:`, `extends:` — makes deterministic graph traversal possible. Every dependency is named
and resolvable without executing a query.

Most BI tools don't have this. A dbt project has a DAG but no semantic layer. A Tableau
workbook has implicit dependencies that are hard to traverse programmatically. LookML's
structure is the moat: it means Strata can answer "what breaks if I change this?" with
certainty, not heuristics.

---

## How It Works

```
LookML repo (read-only clone)
        │
        ▼
   L0 — IR Builder
        Parse all .lkml files → canonical node/edge graph
        Resolve extends chains, refinements, cross-model dependencies
        No LLM. No network. Pure deterministic Python.
        │
        ▼
   L1 — Enrichment
        Join IR against usage facts (explore queries, PDT builds)
        Join IR against schema facts (warehouse column inventory)
        Produces: dead code evidence, PDT cost ledger, schema drift records
        Offline: fixture JSON  |  Live: Looker OAuth → System Activity API
        │
        ▼
   L2 — Synthesis
        One explore = one verdict with evidence
        Cheap model, clean structured context
        Outputs: cleanup roadmap, migration impact, validation scope
        │
        ├── JSON artifacts   catalog / dead code / PDT ledger / drift / impact
        ├── HTML dashboard   strata dashboard
        ├── MCP server       14 read-only tools, stdio, any MCP client
        └── CLI              strata check / outputs / bootstrap / chart
```

---

## The MCP Layer

14 read-only tools over stdio. Works with any MCP client.

```json
{
  "mcpServers": {
    "strata": {
      "command": "strata-mcp",
      "env": { "STRATA_REPO_PATH": "/path/to/your/lookml" }
    }
  }
}
```

| Tool | Returns |
|---|---|
| `strata_ir_status` | Graph summary: node counts, model list, resolution errors |
| `strata_dead_code_register` | Dead explores + zombie views with dual evidence |
| `strata_pdt_costs` | PDT ledger: cost/mo, build count, bytes, status |
| `strata_schema_drift` | Column-level drift: field exists in LookML, missing in warehouse |
| `strata_explore_deps` | Full join graph for an explore |
| `strata_query_field` | Field definition: type, SQL, tags, usage |
| `strata_list_orphans` | Orphaned views and fields by kind |
| `strata_usage_summary` | Query counts, top explores, usage gaps |
| `strata_validation_scope` | Impact set for a set of changed .lkml files |
| `strata_impact` | All explores affected by a physical table change |
| `strata_list_skills` | Compact metadata for all bundled skills |
| `strata_skill` | Full skill content — loaded only when requested |
| `strata_render_chart` | Vega-Lite spec + data → interactive HTML |
| `strata_chart_templates` | Available chart types |
| `strata_conductor_status` | Active slice and next steps from handoff-log |

---

## The Skills Layer

13 domain skills bundled with the package. Zero tokens until an agent calls `strata_skill("name")`.

```
bi/bq/          bq_query_guardrail  bq_schema_probe  grain_validator
                sql_builder         sql_optimizer
bi/lookml/      lookml_explore_join_reviewer  lookml_view_reviewer
bi/looker/      semantic_layer_audit
bi/delivery/    bi_incident_responder  jira_to_bi_spec  release_notes_generator
bi/viz/         chart_composer  dashboard_composer
```

Each skill defines: trigger conditions, allowed tools, step-by-step procedure, stop conditions,
output format, and escalation scripts. Designed to run with cheap models — `[JUDGMENT]` marks
the few steps that require reasoning; everything else is mechanical.

**The BQ investigation chain:**
```
bq_schema_probe → grain_validator → sql_builder → sql_optimizer → bq_query_guardrail
```

---

## Vega-Lite Charts — Built In

```bash
strata chart bar data.json --title "Revenue by Region" --open
strata chart line trend.json --open
strata chart scatter correlation.csv --open
```

![Bar chart showing revenue by region rendered as a Vega-Lite interactive HTML](docs/assets/dashboard-overview.png)

4 chart types (bar, line, scatter, heatmap). No JavaScript dependencies to install —
charts load [Vega-Lite](https://vega.github.io/vega-lite/) via CDN and render as
self-contained HTML files. Works in any browser, including over a local server on mobile.

Built by the [UW Interactive Data Lab](https://idl.cs.washington.edu/) ([@uwdata](https://github.com/vega)).

---

## Dashboard

![Strata dashboard overview — enterprise_mono playground showing 28 active explores, 6 dead artifacts, $63,755.94 PDT cost/30d, 10 schema drift records, and the full dependency graph](docs/assets/dashboard-overview.png)

*enterprise_mono playground — 34 explores, 19 models, 30-day window. Color legend: green = active explore, red = dead explore, blue = view, orange = unused PDT, gray = physical table.*

![Dependency graph zoomed on dead_finance_v2 — QUERY COUNT: 0, backed by pdt_attribution_full_funnel (orange zombie PDT diamond)](docs/assets/graph-dead-explore.png)

*Dependency graph — `dead_finance_v2` selected. Node detail shows KIND: EXPLORE, QUERY COUNT: 0, MODEL: em_legacy_v2. The orange diamond is `pdt_attribution_full_funnel` — a zombie PDT rebuilding at $45,000/month to serve this explore. Both are flagged for removal.*

![Dead Code Register showing 6 dead explores with dual structural and usage evidence](docs/assets/dashboard-pdt-section.png)

*Dead Code Register — each item carries two evidence tags: structural (exists in resolved IR) and usage (zero queries in L1 facts). Both must be present before anything is flagged.*

---

## Evidence

These findings come from the three reference playgrounds included in the repo (`tests/lookml/`).
Full numbers and methodology in [`docs/testing-findings.md`](docs/testing-findings.md).

**enterprise_mono** — 19 models, 34 explores, cross-model extends, 3 legacy connection clusters:

- 6 dead explores (0 queries over 30 days) — all flagged with dual evidence
- 5 zombie views — referenced only by dead explores
- 2 zombie PDTs rebuilding at $63,750/month — backed exclusively by dead explores
- Annualized exposure: **~$765,000/year** in compute serving no users
- 14 schema drift hits across 3 tables

**gcs_analytics** — gold/silver BQ layer, mixed active and legacy:

- 4 dead items (2 orphan views, 2 dead explores)
- 1 unused PDT ($156/month)
- 1 schema drift hit

**thelook** — Looker's public demo repo, structural baseline:

- 5 dead items (1 orphan view, 4 dead explores)
- 1 zombie PDT ($432/month)

Each playground ships with matching fixture JSON files (`tests/fixtures/`) that simulate
Looker System Activity API responses — so the full analysis runs offline with no credentials.

---

## Ecosystem Fit

| | Looker MCP Server | Looker Extension | Strata |
|---|---|---|---|
| **What it is** | Claude ↔ Looker API bridge | React app embedded in Looker UI | LookML static analysis engine |
| **What it does** | Live explore queries, system activity, content management via agent | In-UI tooling: custom actions, AI panels, embedded views | IR graph, dead code, PDT cost, drift, blast radius — offline |
| **Data access** | Live Looker API | Live Looker embed | Read-only LookML clone + usage/schema facts |
| **Where it runs** | Local MCP server (stdio) | Inside Looker UI | Local CLI, CI, or IDE MCP server |
| **Analysis** | Surfaces data — agent reasons over it | In-product actions and display | Deterministic analysis — agent reasons over structured IR |

Strata consumes what the Looker MCP Server surfaces (usage facts, system activity) and
produces what a Looker Extension could display (cost ledger, cleanup roadmap, drift report).
The three tools are complementary layers, not competitors.

---

## Quick Start

```bash
# Install
pip install -e ".[dev]"   # from clone, or pip install from GitHub Releases

# Bootstrap any repo with Strata governance
strata bootstrap --repo /path/to/your/lookml

# Run the MCP server (point at a playground to try it)
STRATA_REPO_PATH=tests/lookml/enterprise_mono \
STRATA_USAGE_FIXTURE=tests/fixtures/enterprise_usage_facts.json \
strata mcp run

# Or use the full CLI
strata check --repo tests/lookml/enterprise_mono \
             --usage-fixture tests/fixtures/enterprise_usage_facts.json
strata chart bar tests/fixtures/sample_data.json --open
```

Point at your own repo via `~/.strata/config.json`:
```json
{ "repo_path": "/path/to/your/lookml" }
```

---

## CI Integration

```yaml
# .github/workflows/strata-check.yml
- name: Strata LookML governance check
  run: strata check --repo . --usage-fixture usage_facts.json
```

The included `strata-pr.yml` workflow posts impact analysis as a PR comment whenever
`.lkml` files change. See [`.github/workflows/strata-pr.yml`](.github/workflows/strata-pr.yml).

---

## Docs

| | |
|---|---|
| [`docs/testing-findings.md`](docs/testing-findings.md) | Full findings from all three playgrounds — real numbers, methodology, known gaps |
| [`docs/testing-scenarios.md`](docs/testing-scenarios.md) | Three verification scenarios: structural, enrichment, enterprise G4 |
| [`docs/playground-guide.md`](docs/playground-guide.md) | Tour of each playground and what signals to look for |
| [`docs/offline-first-walkthrough.md`](docs/offline-first-walkthrough.md) | Full analysis without any external dependencies |
| [`docs/security-hardening.md`](docs/security-hardening.md) | Read-only enforcement, credential handling, MCP security model |
| [`docs/enterprise-deployment.md`](docs/enterprise-deployment.md) | IAM, ADC, OIDC for GH Actions, Google Workspace path |
| [`docs/looker-ecosystem.md`](docs/looker-ecosystem.md) | Full ecosystem breakdown: Looker MCP, Extension, and Strata |
| [`skills/strata_workflow.md`](skills/strata_workflow.md) | Step-by-step workflow for humans and agents |
| [`skills/strata_agentic_runbook.md`](skills/strata_agentic_runbook.md) | Autonomous governance investigation playbook |
| [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) | Contribution guide |

---

## License

[Apache 2.0](LICENSE) — © 2026 Garrett Schumacher
