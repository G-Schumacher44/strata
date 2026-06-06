# Master Plan: Strata Core — L0 through MCP Repo-Brain

Date: 2026-06-05
Status: active
Type: master-plan

## Objective

Build the deterministic foundation and IDE-facing surface of Strata in five bricks:
parse the LookML repo into a canonical IR (B1), enrich with live usage and cost data
(B2), add governed AI synthesis (B3), wire the CI gate (B4), and ship the full MCP
repo-brain with output artifacts (B5).

Each brick has a hard definition of done. No brick is started until its dependency
brick is STABLE. The IR contract (`src/strata/ir/types.py`) is the shared seam —
changes to it are Full Conductor Mode and require all downstream layers to be re-verified.

---

## Strategic Context

See `intent.md` §1–§3 for the full thesis, principles, and architecture. See
`docs/strata-ecosystem-report.md` for ecosystem research covering Looker tooling
fit, OAuth posture, and future integration candidates. Key constraints that govern
every decision in this plan:

- **Read-only always.** No brick may introduce writes to the LookML repo, prod, or any
  live instance.
- **Deterministic core.** Bricks 1–2 must be pure Python, zero tokens, reproducible.
- **Generic engine / private config separation.** Zero org fingerprints in any code that
  ships under the Apache license.
- **Governed.** The validate.py gate and Conductor handoff are required for every brick.
  A brick is not STABLE until `scripts/validate.py` passes with all gates checked.

---

## Brick Sequence

### Brick 1 — Generic IR Extractor (L0)
**Spec:** `conductor/slice-01-ir-extractor.md`
**Status:** STABLE
**Depends:** none
**Scope:** `src/strata/ir/`, `tests/fixtures/`, thin MCP shell

The deterministic foundation. Parse any LookML repo into a canonical node/edge graph
with full extends + refinement chain resolution. Everything downstream reasons over
this — never raw files. `lkml` is prior art to mine, not a runtime dependency to vendor.

**The make-or-break:** `resolver.py` must resolve the full extends/refinement chain
before emitting any orphan verdict. The three-level extends stress test is the
correctness oracle. If it fails, nothing downstream ships.

**Done when:** parses synthetic LookML into full IR, resolves extends chain correctly,
emits structural-orphan list, 4 MCP tools respond correctly, all 9 gates checked.

---

### Brick 2 — Usage & Cost Enrichment (L1)
**Spec:** `conductor/slice-02-usage-enrichment.md`
**Status:** STABLE
**Depends:** Brick 1 STABLE
**Scope:** `src/strata/l1/`, Looker System Activity (read-only MCP/API)

Join the IR against Looker System Activity (`i__looker`): explore query counts,
last-queried timestamps, content→explore references, PDT build events. L1 is
**optional and feature-flagged** — the full tool works offline on a cloned repo;
L1 enriches when a live Looker connection exists.

The PDT cost ledger lives here: rebuild frequency × bytes processed vs. query count
→ $/yr. This is the gap prior art doesn't cover — own it.

**Done when:** dead-code register exists with static∩usage evidence (not static-only,
not usage-only — the intersection), and the PDT ledger prices at least one unused PDT
in $/yr on the test instance.

---

### Brick 3 — Synthesis Skills + Conductor (L2/L3)
**Spec:** `conductor/slice-03-synthesis.md`
**Status:** STABLE
**Depends:** Brick 2 STABLE (or Brick 1 STABLE + mocked L1 for development)
**Scope:** `src/strata/synthesis/`, skill files, validate gate wired to L2

The only LLM layer. One explore = one slice = one bounded, validatable unit. Per
slice: what it does, working/broken, dependencies, dependents, and a verdict
(`keep` / `hide` / `deprecate` / `kill`) **with evidence attached**.

Implemented as runtime-injected skills using Looker's skill-file convention:
`dep-graph`, `dead-code`, `pdt-cost`, `explore-summarize`. The validate gate
enforces: no verdict ships without its evidence trail.

**Model posture:** cheapest model that does the job. Gemini Flash or local MLX
first; escalate only if quality degrades. Token budget per slice must be measured
and documented.

**Done when:** one explore slice produces a verdict + evidence trail that passes
the validate gate, on a cheap/local model.

---

### Brick 4 — CI Suite
**Spec:** `conductor/slice-04-ci-suite.md`
**Status:** STABLE
**Depends:** Brick 1 STABLE (L0 gate only); Brick 3 STABLE for full gate
**Scope:** `.github/workflows/`, `scripts/`, PR check wiring

Wire the L0 IR + validate gate into the PR pipeline as the third gate alongside
Codex review + Looker native validation. This is the permanence move — it breaks
the cycle of slop by making Strata a hygiene tool, not just an archaeology tool.

PR-time flags: new orphan view, unreferenced PDT, `sql_table_name` pointing at
nothing, broken extends chain.

**Done when:** a deliberately-broken test PR (orphan view / dead PDT / broken
extends) is flagged automatically.

---

### Brick 5 — MCP Repo-Brain + Output Artifacts
**Spec:** `conductor/slice-05-mcp-repobrain.md`
**Status:** STABLE
**Depends:** Bricks 1–4 STABLE
**Scope:** `src/strata/mcp/` (full), `src/strata/outputs/`, Cursor MCP config

Full MCP repo-brain: L0–L1 exposed as IDE tools. Full output artifact suite:
dependency graph (queryable + Plotly visual), repo catalog, dead-code register,
PDT cost ledger, cleanup roadmap, migration-impact view (Looker-side blast radius
per Data Den table change).

**Done when:** team can ask "what breaks if I touch X" in the IDE and get an answer
in seconds. All six output artifacts generated on the test instance.

---

## Status Table

| Brick | Name | Status | Spec |
|---|---|---|---|
| 1 | Generic IR extractor (L0) | STABLE | archive/slice-01-ir-extractor.md |
| 2 | Usage + cost enrichment (L1) | STABLE | archive/slice-02-usage-enrichment.md |
| 3 | Synthesis skills + Conductor (L2/L3) | STABLE | archive/slice-03-synthesis.md |
| 4 | CI suite | STABLE | archive/slice-04-ci-suite.md |
| 5 | MCP repo-brain + output artifacts | STABLE | archive/slice-05-mcp-repobrain.md |

---

## IR Contract — The Shared Seam

`src/strata/ir/types.py` defines `IRNode`, `IREdge`, `IRGraph`. This is the
contract every other layer depends on. Treat changes to it as Full Conductor Mode:

1. Write a new slice spec before touching types.py
2. Update all downstream layers (MCP tools, L1 enrichment, synthesis skills)
3. Re-run the full test suite + validate gate before marking stable
4. Record the contract change in the handoff with explicit downstream impact

---

## Open Decisions

| # | Decision | Status |
|---|---|---|
| 1 | Name (Strata / Sift / Bedrock / Quarry / Lodestar) | Open |
| 2 | Pilot scope — which explores to run B1–B2 against first on test instance | Open — suggest most-extended explore (exercises §5 immediately) |
| 3 | OAuth client registration for read-only Looker MCP | Deferred — no Looker access during POC |
| 4 | IDE-first vs batch-first emphasis for B5 | Open — repo-brain prioritized |
| 5 | Model for B3 synthesis (Gemini Flash / local MLX / other) | Open — cheapest that passes the verdict quality bar |

---

## After Brick 5

### Phase 2 — Offline POC Hardening

The v0.1.0 fixture-backed core is stable. During the POC phase, Strata assumes
there is no Looker instance access. All proof work must run from a cloned LookML
repo plus offline fixtures/replay extracts. Live Looker OAuth/System Activity work
is explicitly post-POC.

1. **Slice 06 — L1 Adapter Contract + Replay Harness.** Offline, deterministic,
   replay-backed mapping from sanitized Looker/System Activity-shaped rows into
   existing L1 dataclasses. This keeps forward motion without test-instance access.
2. **Slice 07 — Live Looker L1 Adapter.** Deferred until after the POC. When
   instance access is available, it should implement the Slice 06 provider
   protocol and add only opt-in/manual live smoke validation. Preferred auth
   remains a registered Looker OAuth client app with stable `client_guid`
   (`com.gsanalytics.strata.cli`) and localhost redirect
   (`http://localhost:8765/oauth/callback`), with tokens stored only locally.
   API client-secret auth is an explicit admin fallback, not the default.

Research-backed future candidates, tracked outside the blocked live adapter path:
Spectacles-scoped blast-radius validation, LAMS lint/style ingestion, BigQuery
`INFORMATION_SCHEMA` schema checks, and Vertex AI as an enterprise L2 deployment
option.
3. **Slice 08 — Offline Schema Drift.** Review-ready offline build path. It adds
   fixture/replay warehouse schema facts and deterministic schema-drift evidence
   without waiting on live BigQuery or Looker access.

POC loop on offline clone + sanitized extracts → post-POC live read-only proof
when sanctioned access exists → pitch via Adhyan's sanctioned pathway →
open-source under Apache 2.0. Public-readiness is a phase, not a prerequisite.
Build private, prove offline first, dress it up only when the pathway is live.
