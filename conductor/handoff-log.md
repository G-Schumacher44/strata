# Handoff Log & State Preservation

## Date: 2026-06-06 — Bricks 2-5: L1 through MCP Repo-Brain
Commit: ecef63f
Target Branch: codex/strata-bricks-2-5
Status: Bricks 1-5 STABLE on fixture-backed offline core.
Conductor Mode: slice
Context Budget: medium
Context Loaded: AGENTS.md, intent.md, conductor/CONDUCTOR_MODES.md, conductor/index.md, conductor/README.md, conductor/master-plan-strata-core.md, conductor/slice-01-ir-extractor.md, conductor/slice-02-usage-enrichment.md, conductor/slice-03-synthesis.md, conductor/slice-04-ci-suite.md, conductor/slice-05-mcp-repobrain.md, src/strata/ir/AGENTS.md, src/strata/mcp/AGENTS.md, src/vendor/AGENTS.md, handoff-log latest block.
Context Skipped: archive/**, handoff-archive.md.
Stage/DUOS: not used; not required.
Ledger: not applicable.
Tag Posture: no stable tag required.

## Reality Check
- Brick 1 implementation anchor is `3b5a0e7`; final handoff anchor commit was `f713465`.
- Work proceeded on feature branch `codex/strata-bricks-2-5` for one review PR.
- L1 live Looker access remains adapter-only and disabled by default; fixture-backed facts are the test gate.

## Files Created / Updated
- `conductor/slice-02-usage-enrichment.md` through `slice-05-mcp-repobrain.md` — stable slice contracts.
- `src/strata/l1/` — fixture-backed usage/content/PDT facts, live adapter contract, enrichment join, dead-code register, PDT ledger.
- `src/strata/synthesis/` — compact explore slices, deterministic verdicts, evidence validation.
- `src/strata/outputs/` — catalog, dead-code register, PDT ledger, cleanup roadmap, migration-impact artifacts.
- `src/strata/mcp/tools.py`, `server.py` — expanded repo-brain tools while preserving Brick 1 tools.
- `scripts/check_strata.py`, `scripts/generate_outputs.py`, `.github/workflows/strata-ci.yml` — offline scenario gates and artifact CLI.
- `tests/fixtures/usage_facts.json`, `pdt_orders.view.lkml`, `tests/test_l1_synthesis_outputs.py` — fixture-backed scenario coverage.

## Validation
- `.venv/bin/pytest` — 21 passed.
- `.venv/bin/python scripts/build_ir.py --repo tests/fixtures --usage-fixture tests/fixtures/usage_facts.json --cache /tmp/strata_ir_enriched.db --json` — exits 0.
- `.venv/bin/python scripts/check_strata.py` — scenario gates passed.
- `.venv/bin/python scripts/generate_outputs.py --repo tests/fixtures --usage-fixture tests/fixtures/usage_facts.json --out /tmp/strata_outputs` — writes six artifacts.
- MCP stdio protocol smoke — listed eight tools and called `strata_usage_summary` + `strata_impact`.
- `python3 scripts/validate.py` — passes after final commit anchor update.

## Exact Next Steps
1. Merge `codex/strata-bricks-2-5` → `dev` via PR (Bricks 1-5 STABLE + 10 review findings patched).
2. Decide whether to wire the live read-only Looker/System Activity adapter against the test instance.
3. Keep fixture-backed scenario gates as the non-blocking baseline for all future Python work.

---

## Date: 2026-06-06 — Post-review patch: 10 code-review findings addressed
Commit: 3311b05
Target Branch: codex/strata-bricks-2-5
Status: All 10 findings from high-effort code review patched. 21 tests pass. Ready to merge.
Conductor Mode: patch
Context Budget: low

## Summary of Fixes
- C1 enrich.py — double-call guard: raises RuntimeError instead of silently clobbering l1 metadata
- C2 enrich.py — dead-code now flags explores with NO usage row (not just zero-query rows)
- C3 fixtures.py — _coerce() filters unknown JSON keys so schema evolution doesn't TypeError
- C4 verdicts.py — query_count default 1→0; absent usage row correctly triggers deprecate verdict
- C5 verdicts.py — validate_verdict checks uncited evidence on actionable verdicts (hide/deprecate/kill)
- C6 slices.py — PDT ledger scoped to explore only; removed repo-wide unused PDT leak
- C7 tools.py — strata_impact raises KeyError on missing physical_table instead of silent empty
- C8 tools.py — reverse adjacency index built once O(E); eliminates O(V×E) nested loop
- C9 enrich.py — None sentinel distinguishes "not provided" from "provided empty" for content_references; prevents mass false-positive dead-code
- C10 pipeline.py — captures enrich_graph return value; guards against future mutation→return refactor
- Bonus: validate_verdict no longer requires evidence for keep/review verdicts (only actionable verdicts)

## Validation
- `.venv/bin/pytest` — 21 passed
- `python scripts/validate.py` — 10 passed, 0 failed

## Exact Next Steps
1. Open PR: `codex/strata-bricks-2-5` → `dev` and merge.
2. Tag `dev` as `v0.1.0` after merge (Bricks 0–5 complete on fixture-backed offline core).
3. Next work gate: wire live read-only Looker/System Activity adapter on test instance (OAuth client registration — Garrett has admin role).
