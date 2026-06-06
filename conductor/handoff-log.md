# Handoff Log & State Preservation

## Date: 2026-06-06 — Enterprise Mono Playground (Slice 11)
Commit: e9e91b0
Target Branch: dev
Status: Complete. Third playground added to validate cross-model extends, G4 zombie PDT detection, schema drift, and legacy dead-explore patterns against real BQ schema.
Structure: 19 models, 34 explores (28 active / 6 dead), 20 views, 5 PDTs, 3 legacy views with schema drift.
Cross-model extends: 8 base models (one per domain), 8 analytics/functional models using `extends: [explore_name]`. Resolver correctly builds resolution_chain across files (verified: `customers_us` chain = `['customers', 'customers_us']`).
G4 zombie PDTs: `pdt_customer_value_score` ($18,750/30d) + `pdt_attribution_full_funnel` ($45,000/30d) — backed only by dead_orders_v2 / dead_finance_v2 (0 queries since Q3/Q4 2025). Combined: ~$765K/year. Strata surfaces them via cleanup_roadmap `review_for_deprecation` on the dead explores.
Schema drift: 7 real hits (unit_cost_usd × 3, customer_status_v1, segment_score_v1, warehouse_zone, reorder_threshold) + 3 CTE false-positives in PDT SQL (clv_base, enriched, scored — known limitation of SQL regex upstream detection).
Legacy connections: legacy_redshift (decommissioned), legacy_warehouse_v1 (broken rename) — both produce dead explore clusters in IR.
make ci REPO=tests/lookml/enterprise_mono USAGE=tests/fixtures/enterprise_usage_facts.json SCHEMA=tests/fixtures/enterprise_schema_facts.json → 36 passed, 10/10, all 8 artifacts.
Conductor Mode: slice
Context Budget: medium
Context Loaded: AGENTS.md, conductor/handoff-log.md, src/strata/ir/resolver.py, src/strata/l1/*.py, tests/fixtures/gcs_usage_facts.json.
Context Skipped: archive/**.
Stage/DUOS: not used.
Tag Posture: v0.4.0 candidate — three playgrounds, full L1 time-series store, repo-agnostic config, enterprise mono.

## Date: 2026-06-06 — Post-POC Synthesis & Architecture Formalization
Commit: c4824e7
Target Branch: dev
Status: Patch mode. Six items from post-POC synthesis plan:
(6a) SO_REUSEADDR on dashboard server — no more OSError on restart.
(6b) Period contract: `period` block in usage fixture → enrich_graph → l1["period"] → usage_summary artifact → dashboard KPI ("last 30 days" / "PDT Cost / 30d").
(6c) `make ci` target: test + validate + check + check-replay + outputs in sequence.
(6d) `skills/strata_workflow.md`: step-by-step guide for less-capable agents.
(6e) Conductor handoff + index updated.
Architecture decision recorded: Strata stays stdio + offline-first. BQ MCP / Looker MCP inject data through UsageProvider / SchemaProvider protocols — Strata code never makes HTTP calls. Capability tiers formalized (L0 → fixture → replay → BQ-MCP → Looker-MCP → full live).
36 tests green, validate.py 10/10, make ci passes.
Conductor Mode: patch
Context Budget: medium
Context Loaded: conductor/index.md, conductor/handoff-log.md, src/strata/l1/*, src/strata/outputs/dashboard.py, src/strata/mcp/tools.py, scripts/serve_dashboard.py, Makefile.
Context Skipped: archive/**.
Stage/DUOS: not used.
Ledger: not applicable.
Tag Posture: v0.3.0 candidate after this batch lands.

## Date: 2026-06-06 — Local HTML Dashboard
Commit: da0aefa
Target Branch: dev
Status: Patch mode. Local observability dashboard added. One command: python scripts/serve_dashboard.py --repo ... --usage-fixture ... --schema-fixture ... Opens browser at localhost:8765/dashboard.html. Self-contained HTML (CDN JS, embedded JSON). Sections: health KPIs, Cytoscape dependency graph, dead code register, PDT cost ledger, cleanup roadmap, schema drift, migration impact accordion. 36 tests green, validate.py 10/10. No active slice.
Conductor Mode: slice
Context Budget: medium
Context Loaded: AGENTS.md, conductor/index.md, conductor/master-plan-strata-core.md, conductor/handoff-log.md, docs/strata-ecosystem-report.md, src/strata/l1/*, src/strata/outputs/*, src/strata/mcp/*, tests/fixtures/*.
Context Skipped: archive/**.
Stage/DUOS: not used; not required.
Ledger: not applicable.
Tag Posture: `v0.1.0` pushed.

## Reality Check
- `main` and tag `v0.1.0` point at green commit `3aff5ce`.
- `dev` is ahead at `b469721` with offline-only POC posture, Slice 06 replay/provider work, Slice 08 schema drift, Slice 09 validation scope, and live Looker deferred post-POC.
- PR #1 was merged before the final CI workflow fix; `dev`/`main` CI is green after `3aff5ce`.
- POC work has no Looker instance access, so the build path is offline-only.

## Files Updated
- `conductor/review/slice-09-validation-scope-offline.md` — completed offline validation-scope slice.
- `src/strata/validation.py` — offline validation-scope planner for changed views/tables.
- `src/strata/mcp/tools.py`, `server.py`, `__init__.py` — `strata_validation_scope` repo-brain surface.
- `src/strata/outputs/artifacts.py` — validation-scope artifact.
- `scripts/generate_outputs.py`, `check_strata.py` — validation-scope fixture wiring and scenario gate.
- `tests/fixtures/pdt_scope_orders.view.lkml`, `pdt_validation.model.lkml`, `validation_scope_changed.json`, `tests/test_validation_scope.py` — scoped validation fixtures and tests.
- `src/strata/l1/schema.py`, `types.py`, `pipeline.py` — offline schema facts, schema-drift enrichment, and provider-backed graph build.
- `src/strata/mcp/tools.py`, `server.py`, `__init__.py` — `strata_schema_drift` repo-brain surface and summary count.
- `src/strata/outputs/artifacts.py` — schema drift artifact and cleanup-roadmap items.
- `scripts/build_ir.py`, `generate_outputs.py`, `check_strata.py` — schema fixture wiring and scenario gate.
- `tests/fixtures/schema_facts_clean.json`, `schema_facts_drift.json`, `tests/test_schema_drift.py` — clean/drift schema scenarios.
- `conductor/review/slice-08-schema-drift-offline.md` — completed offline schema-drift slice.
- `docs/strata-ecosystem-report.md` — tracked ecosystem research on Looker tooling fit, OAuth posture, and future integration candidates.
- `conductor/tracks.md`, `conductor/index.md`, `conductor/master-plan-strata-core.md` — research doc linked into Conductor references and roadmap context.
- `conductor/archive/slice-01-ir-extractor.md` through `slice-05-mcp-repobrain.md` — stable slices moved off the hot path.
- `conductor/review/slice-06-l1-adapter-contract-replay.md` — complete replay-harness slice moved to review.
- `conductor/review/slice-08-schema-drift-offline.md` — completed offline schema-drift slice moved to review.
- `conductor/slice-07-live-looker-l1.md` — post-POC deferred live adapter slice.
- `conductor/index.md`, `conductor/master-plan-strata-core.md` — Phase 2 plan updated.
- `src/strata/l1/provider.py`, `fixtures.py`, `replay.py`, `pipeline.py` — provider boundary, normalized fixture provider, replay provider, and provider-backed graph build.
- `tests/fixtures/replay_facts.json`, `tests/test_l1_providers.py` — sanitized replay facts and provider contract tests.
- `scripts/check_replay.py`, `.github/workflows/strata-ci.yml` — offline replay validation gate.

## Validation
- `.venv/bin/pytest` — 36 passed.
- `.venv/bin/python scripts/check_replay.py` — passes.
- `.venv/bin/python scripts/check_strata.py` — passes.
- `python3 scripts/validate.py` — passes.

## Exact Next Steps
1. Review Slice 09 and decide whether to cut a new stable checkpoint from `dev`.
2. Keep Slice 07 out of POC scope until read-only Looker instance access and OAuth client app registration are available.
3. Keep all POC validation fixture-backed and offline.
