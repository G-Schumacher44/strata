# MCP Layer — Read-Only Repo Brain

**Layer:** MCP server (exposes L0–L1 to the IDE)
**Full governance:** `GOVERNANCE.md`
**Authority:** `AGENTS.md` (root) → `intent.md` → `conductor/index.md` → active slice → this file

---

## What this layer is

A local stdio MCP server that exposes the pre-built IR (L0) and usage data (L1, Brick 2+)
as read-only tools in the IDE. The team asks questions; this layer answers from the cache.
It never reads raw LookML files directly — it always goes through the IR.

## Hard constraints (non-negotiable)

- **stdio only.** No HTTP server, no TCP, no WebSocket. Transport is stdio exclusively.
  This is a local-only tool — no cloud dependency, no external endpoint.
- **Read-only tools only.** Every tool in this layer is a query over the IR cache.
  No tool may write to the LookML repo, to the IR cache during a live request, or to
  any external system.
- **Never call an LLM.** Tools return structured data. Synthesis is L2's job, not the
  MCP server's.
- **IR is the source of truth.** Never parse raw LookML files at request time. Load the
  cache on startup; rebuild if stale (default: > 5 min).
- **No writes on tool calls.** Cache rebuilds happen at startup only, not mid-request.

## Files in this layer

| File | Responsibility |
|---|---|
| `server.py` | stdio MCP entry point; loads IR cache on startup; routes tool calls |
| `tools.py` | Tool implementations — pure query functions over `IRGraph` |

## Tool contract (Brick 1)

```
strata_query_field(view, field)   → sql, type, tags, source_file, resolution_chain
strata_list_orphans(kind="all")   → [{id, kind, name, source_file, reason}]
strata_explore_deps(explore, model) → {base_view, joins, resolution_chain, field_count}
strata_ir_status()                → {repo_path, built_at, node_counts, edge_count, cache_path}
```

Config via `STRATA_REPO_PATH` env var or `~/.strata/config.json`.

## Adding new tools

1. Add implementation in `tools.py` — pure function over `IRGraph`
2. Register in `server.py`
3. Add tests in `tests/test_mcp_tools.py` using fixture IR (not a live server)
4. Update `conductor/slice-*.md` if the tool is part of a slice deliverable

## What does NOT belong here

- IR parsing or graph building — that is `src/strata/ir/`
- LLM calls or synthesis — that is L2 (Brick 3+)
- HTTP transport or cloud endpoints — local stdio only
- Any tool that modifies state
