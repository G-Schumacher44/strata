# Conductor Index — Strata

Date: 2026-06-05
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

- **Strata Core:** [L0 through MCP Repo-Brain](./master-plan-strata-core.md) — Bricks 1–5 STABLE
- **L1 Adapter Replay:** [L1 Adapter Contract + Replay Harness](./review/slice-06-l1-adapter-contract-replay.md) — review-ready
- **Live L1:** [Live Looker L1 Adapter](./slice-07-live-looker-l1.md) — blocked
- **Offline Schema Drift:** [Offline Schema Drift](./review/slice-08-schema-drift-offline.md) — review-ready

## Active Slice

Active slice: None — Slice 08 review-ready; Slice 07 blocked

## Brick Status

| Brick | Name | Status |
|---|---|---|
| 0 | Design doc (thesis / intent / outline) | ✅ STABLE |
| 1 | Generic IR extractor (L0) | ✅ STABLE |
| 2 | Usage + cost enrichment (L1) | ✅ STABLE |
| 3 | Synthesis skills + Conductor (L2/L3) | ✅ STABLE |
| 4 | CI suite | ✅ STABLE |
| 5 | MCP repo-brain + output artifacts | ✅ STABLE |
| 6 | L1 adapter contract + replay harness | review-ready |
| 7 | Live Looker L1 adapter | blocked |
| 8 | Offline schema drift | review-ready |

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

- Slice 07 live Looker L1 requires read-only test-instance access and OAuth client registration.

## Reference

- [Handoff Log](./handoff-log.md)
- [Conductor README](./README.md)
