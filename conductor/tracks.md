# Tracks

## Track A — Core (Bricks 1–9, STABLE)

All bricks complete. Playground verified on thelook, gcs_analytics, enterprise_mono.
Archived: slices 01–06, 08–09 in `conductor/archive/`.

| Item | Status |
|---|---|
| WP integration | parked — post prod loop; expose Strata IR via WP MCP |
| Ecosystem research | tracked — `docs/strata-ecosystem-report.md` |

---

## Track B — Productionization (Slices 11–19, STABLE)

Master plan: `conductor/master-plan-productionization.md`

All slices STABLE or offline-ready. One external gate remains: live Looker OAuth smoke
(Slice 12 / Brick P3). Not a conductor slice — requires a real Looker instance.

| Slice | Name | Status |
|---|---|---|
| 16 | Conductor + skills for agentic operation | ✅ STABLE |
| 11 | Store removal + pipeline simplification | ✅ STABLE |
| 12 | Looker live provider | offline-ready; live smoke = external gate |
| 13 | GH Actions + notifications | ✅ STABLE |
| 14 | Testing scenario docs | ✅ STABLE |
| 15 | Enterprise + Google controls | ✅ STABLE |
| 17 | Looker ecosystem breakdown | ✅ STABLE |
| 18 | Security hardening + offline-first | ✅ STABLE |
| 19 | Public-facing branch setup | ✅ STABLE (strata-oss live) |

---

## Track C — MCP Live Workflow + OSS (STABLE)

| Deliverable | Status |
|---|---|
| `.mcp.json` + `scripts/mcp_server.sh` — Claude Code wiring | ✅ STABLE |
| `scripts/test_mcp_live.py` — all 10 tools, 3-playground gate | ✅ STABLE |
| `skills/strata_workflow.md` — 4 MCP investigation workflows | ✅ STABLE |
| `docs/testing-findings.md` — full arc findings + Haiku benchmark | ✅ STABLE |
| `strata-oss` public repo — filtered OSS release | ✅ LIVE |
| `v0.4.0` tag | ✅ TAGGED |

---

## Track D — Enhancement (active)

Master plan: `conductor/master-plan-enhancement.md`

Sprint: Slices 20–22. Future: Slices 23–28 (not yet specced).

| Slice | Name | Status |
|---|---|---|
| 20 | PR validation bot | ✅ STABLE |
| 21 | Author attribution | planned |
| 22 | Historical trending | planned |
| 23 | dbt integration | future |
| 24 | Looker Extension panel | future |
| 25 | Slack governance bot | future |
| 26 | Incremental IR | future |
| 27 | Content network analysis | future |
| 28 | Namespace collision detection | future |
