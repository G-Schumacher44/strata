# Slice 01: Generic IR Extractor (Brick 1 — L0)

Date: 2026-06-05
Status: queued
Brick: 1
Depends: none

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

Master: intent.md §3 (The Hard Problem)
Scope: src/strata/ir/, tests/fixtures/, scripts/

## Objective

Build the deterministic L0 intermediate representation extractor: parse any LookML repo
into a canonical, cached node/edge graph with full extends + refinement chain resolution.
This is the foundation every other layer stands on. No LLM, zero tokens, pure Python.

`lkml` is prior art to mine for parsing ideas, not a runtime dependency. Do not vendor
`lkml`, do not import it from pip, and do not copy its source into this repo. If `lkml`
is inspected, clone it only to a temporary path outside the repo, copy no source files,
and delete the clone before implementation continues.

## Nodes

| Kind | Description |
|---|---|
| `connection` | Database connection declaration |
| `physical_table` | sql_table_name reference |
| `pdt` | Persistent derived table (derived_table block) |
| `view` | LookML view |
| `explore` | LookML explore |
| `model` | LookML model file |
| `lookml_dashboard` | Dashboard definition |
| `field` | dimension / measure / filter / parameter |

## Edges

| Relation | Description |
|---|---|
| `model→connection` | model declares connection |
| `model→include` | model includes view/explore file |
| `explore→base_view` | explore's primary view |
| `explore→joined_view` | join target |
| `view→physical_table` | sql_table_name |
| `view→pdt` | derived_table definition |
| `pdt→upstream` | SQL references in derived_table.sql |
| `extends` | view/explore extends another |
| `refinement` | +explore or +view refinement |
| `dashboard→explore` | dashboard query targets explore |
| `field→underlying_sql` | dimension/measure SQL expression |

## Implementation Order

1. `tests/fixtures/` — synthetic LookML fixtures (write these before parser)
2. `src/strata/ir/types.py` — IRNode, IREdge, IRGraph dataclasses
3. `src/strata/ir/parser.py` — in-house LookML parser for the Brick 1 IR surface
4. `src/strata/ir/builder.py` — build NetworkX DiGraph from parsed trees
5. `src/strata/ir/resolver.py` — extends + refinement chain resolution (§ The Hard Problem)
6. `src/strata/ir/store.py` — IRGraph ↔ SQLite cache (stdlib sqlite3)
7. `src/strata/mcp/server.py` + `tools.py` — thin stdio MCP (4 tools)
8. `tests/` — test_ir_parser.py, test_ir_resolver.py, test_mcp_tools.py
9. `scripts/build_ir.py` — CLI entry point

## The Hard Problem: resolver.py

Resolution algorithm (deterministic, no LLM):

1. Collect all `extends:` and `+refinement` declarations across all parsed files
2. Build extends graph; topological sort (NetworkX) — detect cycles, report, don't crash
3. Merge properties in order: base → extended → refined
   - Scalar fields: later wins
   - Field lists: merge by name (later definition overrides earlier by field name)
4. Tag each resolved node with `resolution_chain: list[str]` (full ancestry, for L2 evidence)

**First test that must pass:** `multi_level_extends.view.lkml` — 3-level chain A→B→C must
emit the correct merged field list. If this test fails, nothing downstream is trustworthy.

## Synthetic Test Fixtures

```
tests/fixtures/
  simple.view.lkml               # One view, no dependencies
  base_customer.view.lkml        # Base view, 5 dimensions + 2 measures
  customer_extended.view.lkml    # extends base_customer, adds 2 dims, overrides 1
  multi_level_extends.view.lkml  # A extends B extends C — the §5 stress test
  orphan_view.view.lkml          # Not referenced by any explore
  test_model.model.lkml          # 2 explores: uses customer_extended + orphan_view
  refined_explore.model.lkml     # Explore + +refinement in a second model file
```

## MCP Tools (4, stdio, Brick 1)

```python
strata_query_field(view: str, field: str)
    → {sql, type, tags, source_file, resolution_chain}

strata_list_orphans(kind: str = "all")   # all | view | explore | field
    → [{id, kind, name, source_file, reason}]

strata_explore_deps(explore: str, model: str)
    → {base_view, joins: [{name, view, type}], resolution_chain, field_count}

strata_ir_status()
    → {repo_path, built_at, node_counts: {view, explore, ...}, edge_count, cache_path}
```

Config: `STRATA_REPO_PATH` env var or `~/.strata/config.json`.
Startup: load cache if < 5 min old; else rebuild and cache.

## Acceptance Criteria

- [x] `tests/test_ir_resolver.py::test_three_level_chain` — resolves correctly
- [x] `tests/test_ir_resolver.py::test_orphan_detection` — orphan_view.view.lkml detected
- [x] `tests/test_ir_resolver.py::test_refinement` — +refinement merges correctly
- [x] `tests/test_mcp_tools.py` — all 4 tools return correct data from fixture IR
- [x] `scripts/build_ir.py --repo tests/fixtures/` — exits 0, writes valid cache
- [x] `scripts/validate.py` — spine passes (all gates checked, handoff written)
- [x] `.venv/bin/pytest` — all tests pass
- [x] MCP server connects via stdio config (protocol smoke verified)
- [x] `conductor/handoff-log.md` — Brick 1 STABLE entry with Commit: hash
