# Conductor Index — Strata

Date: 2026-06-06 (post-POC synthesis)
Status: active
Type: conductor-index

Machine-first routing entry for Conductor-aware agents.

## Control Hierarchy

- [Root Charter](../AGENTS.md)
- [Architectural Lens](../CLAUDE.md)
- [Thesis + Intent + Architecture](../intent.md)
- [Conductor Modes](./CONDUCTOR_MODES.md)
- [Conductor Overview](./README.md)
- [Full Governance Reference](../GOVERNANCE.md)
- [Ecosystem Research](../docs/strata-ecosystem-report.md)

## Context Pack

- [Thesis & Architecture](../intent.md) — §1 thesis, §2 principles, §3 architecture, §5 the hard problem
- [Layer Rules — IR](../src/strata/ir/AGENTS.md)
- [Layer Rules — MCP](../src/strata/mcp/AGENTS.md)
- [Vendor Rules](../src/vendor/AGENTS.md)
- [Track Registry](./tracks.md)
- [Ecosystem Research](../docs/strata-ecosystem-report.md) — Looker tooling fit, OAuth posture, and future integration ideas

## Execution Mode

Default to **Slice Mode** for planned Conductor work. Use **Patch Mode** for
narrow fixes. Use **Full Conductor Mode** for cross-layer changes, new bricks,
or IR contract changes. Use **Audit Mode** for review only.

Resolve mode from `conductor/CONDUCTOR_MODES.md` before widening context.

Avoid reading `conductor/archive/**` and `handoff-archive.md` unless the
active slice requires history.

## Active Strategy

### Track A — Core (STABLE)
- **Strata Core:** [L0 through MCP Repo-Brain](./master-plan-strata-core.md) — Bricks 1–9 STABLE
- **L1 Adapter Replay:** archived (v0.2.0)
- **Offline Schema Drift:** archived (v0.2.0)
- **Offline Validation Scope:** archived (v0.2.0)
- **Playground POC Loop:** thelook + gcs_analytics + enterprise_mono verified — v0.4.0 candidate

### Track B — Productionization (active)
- **Master Plan:** [Productionization Slices 11–19](./master-plan-productionization.md)
- **Slice 16:** Conductor + skills for agentic operation — stable
- **Slice 11:** Store removal — **STABLE**
- **Slice 12:** Looker live provider — offline-ready; live smoke pending
- **Slice 13:** GH Actions + notifications — **STABLE**
- **Slices 14–18:** Docs — **STABLE**
- **Slice 19:** Public-facing branch setup — offline-ready; public remote pending

## Active Slice

Active slice: None — Slices 12–19 offline-ready; live Looker smoke and public remote sync remain manual external gates

## Brick Status

### Track A — Core
| Brick | Name | Status |
|---|---|---|
| 0 | Design doc (thesis / intent / outline) | ✅ STABLE |
| 1 | Generic IR extractor (L0) | ✅ STABLE |
| 2 | Usage + cost enrichment (L1) | ✅ STABLE |
| 3 | Synthesis skills + Conductor (L2/L3) | ✅ STABLE |
| 4 | CI suite | ✅ STABLE |
| 5 | MCP repo-brain + output artifacts | ✅ STABLE |
| 6 | L1 adapter contract + replay harness | ✅ STABLE |
| 7 | Live Looker L1 adapter | offline-ready; manual smoke pending |
| 8 | Offline schema drift | ✅ STABLE |
| 9 | Offline validation scope | ✅ STABLE |

### Track B — Productionization
| Brick | Name | Status |
|---|---|---|
| P1 | Conductor + agentic runbook | ✅ STABLE (Slice 16) |
| P2 | Store removal + simplification | ✅ STABLE (Slice 11) |
| P3 | Looker live provider | offline-ready; manual smoke pending |
| P4 | GH Actions + notifications | ✅ STABLE (Slice 13) |
| P5 | Testing scenario docs | ✅ STABLE (Slice 14) |
| P6 | Enterprise + Google controls | ✅ STABLE (Slice 15) |
| P7 | Looker ecosystem breakdown | ✅ STABLE (Slice 17) |
| P8 | Security hardening + offline-first | ✅ STABLE (Slice 18) |
| P9 | Public branch setup | offline-ready; public remote pending |

## Reading Order

1. `AGENTS.md` — root charter + conductor loop
2. `intent.md` — thesis, principles, architecture (§3–§5 are the implementation spec)
3. `conductor/CONDUCTOR_MODES.md` — choose mode before widening context
4. `conductor/index.md` — this file
5. `conductor/README.md` — directory conventions + lifecycle model
6. active `conductor/slice-*.md` — implementation contract
7. `conductor/handoff-log.md` — latest block when resuming
8. `GOVERNANCE.md` — full rules reference (when mode or rules are in question)

## Deferred / Blocked

- Slice 07 live Looker L1 is deferred until after the POC. POC work assumes no Looker instance access.

## Reference

- [Handoff Log](./handoff-log.md)
- [Conductor README](./README.md)
