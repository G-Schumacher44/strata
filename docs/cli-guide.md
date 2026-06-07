# Strata CLI Reference

All commands installed with `pip install -e .`. Run `strata <command> --help` for full options.

---

## Command Summary

| Command | What it does |
|---|---|
| `strata bootstrap` | Scaffold Strata governance into a repo — creates conductor/, .mcp.json, config |
| `strata build` | Parse LookML and write the IR cache (strata_ir.db) |
| `strata check` | Run offline governance gates — dead code, drift, PDT ledger, verdict validation |
| `strata clean` | Remove output/, strata_ir.db, \_\_pycache\_\_ |
| `strata outputs` | Build IR and write 8 JSON artifacts to an output directory |
| `strata dashboard` | Build artifacts and serve the local HTML observability dashboard |
| `strata validate` | Validate Conductor spine — handoff format, active slice, commit hash, replay facts |
| `strata mcp run` | Start the MCP server (normally launched by your AI client via .mcp.json) |
| `strata mcp validate` | Check repo path, IR cache, skills, and Looker token before opening your AI client |
| `strata mcp config` | Show resolved paths and env vars the MCP server will use |
| `strata auth login` | Start Looker OAuth flow and save token to ~/.strata/tokens.json |
| `strata auth status` | Show current token status and expiry |
| `strata chart` | Render a Vega-Lite chart (bar/line/scatter/heatmap) to self-contained HTML |
| `strata query` | Inspect the IR from the terminal — same tools the MCP server exposes |
| `strata conductor` | Slice-based workflow management for agent sessions |

---

## Common Workflows

### First-time setup on a new repo
```bash
pip install -e ".[dev]"
strata bootstrap --repo /path/to/your/lookml
strata mcp validate
```

### Run offline governance check
```bash
strata check \
  --repo /path/to/your/lookml \
  --usage-fixture /path/to/usage_facts.json \
  --schema-fixture /path/to/schema_facts.json
```

### Build IR cache (so MCP server loads instantly)
```bash
strata build \
  --repo /path/to/your/lookml \
  --usage-fixture /path/to/usage_facts.json
```

### Generate full output artifacts
```bash
strata outputs \
  --repo /path/to/your/lookml \
  --usage-fixture /path/to/usage_facts.json \
  --schema-fixture /path/to/schema_facts.json \
  --out output/my-repo
```

### Run against a playground to try it
```bash
strata check \
  --repo tests/lookml/enterprise_mono \
  --usage-fixture tests/fixtures/enterprise_usage_facts.json \
  --schema-fixture tests/fixtures/enterprise_schema_facts.json
```

### Render a chart
```bash
strata chart bar data.json --title "Revenue by Region" --open
strata chart list                   # see available templates
strata chart scatter usage.csv --open
```

### Start the MCP server manually (for debugging)
```bash
STRATA_REPO_PATH=/path/to/your/lookml \
STRATA_USAGE_FIXTURE=/path/to/usage_facts.json \
strata mcp run
```

### Clean up generated artifacts
```bash
strata clean
strata clean --repo /path/to/your/lookml   # also removes strata_ir.db inside repo
```

---

## Configuration

Strata resolves config in this order for most commands:

1. `STRATA_REPO_PATH` env var
2. `~/.strata/config.json` → `{ "repo_path": "/path/to/your/lookml" }`
3. Current working directory

`strata bootstrap` creates `~/.strata/config.json` during setup.

---

## Environment Variables

| Variable | Used by | Description |
|---|---|---|
| `STRATA_REPO_PATH` | MCP server, CLI | Path to the LookML repo |
| `STRATA_USAGE_FIXTURE` | MCP server | Usage facts JSON for L1 enrichment |
| `STRATA_SCHEMA_FIXTURE` | MCP server | Schema facts JSON for drift detection |
| `STRATA_CACHE_PATH` | MCP server | Override default strata_ir.db path |
| `STRATA_SKILLS_PATH` | MCP server | Override bundled skills directory |
| `STRATA_CHARTS_PATH` | MCP server | Override bundled chart templates |
| `STRATA_CONDUCTOR_PATH` | MCP server | Override conductor directory path |
| `CONDUCTOR_PROJECT_ROOT` | `strata validate` | Project root for spine validation |

---

## Output Artifacts

`strata outputs` writes 8 JSON files per run:

| File | Content |
|---|---|
| `catalog.json` | Full explore/view/field inventory |
| `usage_summary.json` | Query counts, dead/active totals, period metadata |
| `dead_code_register.json` | Dead explores + orphan views + zombie views with dual evidence |
| `pdt_ledger.json` | All PDTs: build counts, costs, explore backers, status |
| `schema_drift.json` | Missing column/table hits with field → table → source traceability |
| `migration_impact.json` | Blast radius per explore (fields, joins, content) |
| `cleanup_roadmap.json` | Prioritized cleanup steps with cost/risk labels |
| `validation_scope.json` | What was and wasn't validated, offline tier, fixture period |
