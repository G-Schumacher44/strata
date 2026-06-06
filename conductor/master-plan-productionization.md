# Master Plan: Strata Productionization — Slices 11–19

Date: 2026-06-06
Status: active
Type: master-plan
Depends: master-plan-strata-core.md (all bricks STABLE)

## Objective

Take Strata from a proven playground tool to a production-grade system:
live Looker data path, GH Actions automation with notifications, enterprise
deployment guidance, and the conductor infrastructure for autonomous agentic
operation.

---

## Strategic Context

The core (Bricks 1–9) is STABLE. Three playgrounds (thelook, gcs_analytics,
enterprise_mono) are verified. The architectural pivot from this point:

- **Remove the SQLite store** — Looker system activity already holds 90 days of
  history. The store was duplicating what Looker provides live. Fixtures remain
  for offline dev and CI.

- **Two deployment modes:**
  1. Interactive MCP/skills — Claude uses Strata tools for on-demand analysis
  2. GH Actions CI — automated weekly run → Slack/Jira reporting

- **Agentic operation** — conductor slice specs are detailed enough for a Claude
  agent to execute end-to-end without human presence. Operator reviews handoffs
  asynchronously.

Key constraints (unchanged from core plan):
- Read-only always. No writes to LookML, Looker, or BQ.
- L0–L1 code never calls any LLM or external API.
- MCP server is stdio-only; no HTTP transport.
- Generic engine / private config separation.

---

## Slice Sequence

```
16 → 11 → 12 → 13 → 14 → 15 → 17 → 18 → 19
```

Slice 16 first — it establishes the agentic runbook. Then code slices (11–13),
then documentation (14–15, 17–18), then infra (19).

---

## Slice 16 — Conductor + Skills for Agentic Operation

**Status:** active (current)
**Spec:** this document + `skills/strata_agentic_runbook.md`
**Mode:** Patch
**Gate:** `scripts/validate.py` passes 10/10

Deliverables:
- This document (`conductor/master-plan-productionization.md`)
- `skills/strata_agentic_runbook.md` — autonomous agent playbook
- `conductor/tracks.md` — Track B Productionization added
- `conductor/index.md` — points to this master plan; Slice 10 archived
- `skills/strata_workflow.md` — enterprise_mono + Looker live tier added

No code changes. Gate: validate.py 10/10, index updated.

---

## Slice 11 — Store Removal + Pipeline Simplification

**Status:** queued
**Mode:** Patch
**Depends:** Slice 16 complete
**Gate:** `make ci` on gcs_analytics + enterprise_mono passes; store files gone

The SQLite time-series store (`store.py`) is removed. Looker already holds
the history we were accumulating. Fixtures remain as the offline/CI data path.

Files deleted: `src/strata/l1/store.py`, `scripts/import_usage.py`
Files modified: `pipeline.py` (remove `build_graph_from_store`),
`generate_outputs.py` (remove `--store`/`--days`), `serve_dashboard.py`
(same), `Makefile` (remove `import` target and STORE/DAYS vars),
`.strata.example` (remove store lines), `conductor/index.md` (Slice 10 archived)

Invariants: 36 tests pass, UsageProvider protocol unchanged, fixture format unchanged.

---

## Slice 12 — Looker Live Provider

**Status:** queued
**Mode:** Slice (new module)
**Depends:** Slice 11 complete
**Gate:** offline CI still passes; live smoke test fetches data without error

Wire `LookerSystemActivityProvider` in `src/strata/l1/looker.py` (currently a
stub). OAuth client flow with local token storage. Pipeline function
`build_graph_from_looker()`. CLI auth script `scripts/strata_auth.py`.

Auth: client GUID `com.gsanalytics.strata.cli`, redirect
`http://localhost:8765/oauth/callback`, tokens in `~/.strata/tokens.json`
(gitignored). No SA keys committed. Missing config fails fast with a clear message.

Files: `src/strata/l1/looker.py` (implement), `src/strata/pipeline.py`
(add `build_graph_from_looker`), `scripts/generate_outputs.py` and
`scripts/serve_dashboard.py` (add `--looker-url`/`--client-id`/`--client-secret`/
`--days`), `scripts/strata_auth.py` (new), `Makefile` (add `auth` target),
`.strata.example` (add Looker block), `conductor/slice-07-live-looker-l1.md`
(update status).

---

## Slice 13 — GH Actions + Notifications

**Status:** queued
**Mode:** Slice (new module)
**Depends:** Slice 12 complete
**Gate:** `strata-ci.yml` passes in GitHub Actions; `notify.py --dry-run` prints payload

Update `strata-ci.yml` (fix stale `build_ir.py` reference, run all 3 playgrounds).
New `strata-weekly.yml`: scheduled Monday 8am UTC, `workflow_dispatch` with `days`
input, OIDC workload identity for GCP (no SA keys in secrets).

New `src/strata/outputs/notifications.py`: `build_slack_payload()` → Block Kit JSON,
`build_jira_tickets()` → issue payloads. New `scripts/notify.py` CLI.
New `docs/notifications-setup.md`: Slack app, Jira token, GH secrets setup guide.

---

## Slice 14 — Testing Scenario Documentation

**Status:** queued
**Mode:** Patch (docs + minor script change)
**Depends:** Slice 13 complete (or can run in parallel with 13)
**Gate:** `make ci` on all 3 playgrounds; `check_strata.py` enterprise_mono assertions pass

Three public-facing testing scenarios:
1. **Structural (L0)** — parse + resolve, extends chains, orphans
2. **Enrichment (L1)** — dead code, schema drift, PDT cost, period label
3. **Enterprise G4** — enterprise_mono: 34 explores, 6 dead, $765K zombie PDTs, 7 drift hits

Files: `docs/testing-scenarios.md`, `docs/playground-guide.md`,
`scripts/check_strata.py` (add enterprise_mono assertions).

---

## Slice 15 — Enterprise + Google Controls

**Status:** queued
**Mode:** Patch (docs only)
**Depends:** Slice 12 complete (auth model must be defined before docs)
**Gate:** doc review; no code gate

IAM, ADC, network isolation, data isolation, OIDC for GH Actions, audit trail,
BYOK, easy-path guide for Google Workspace + GCP org constraints.

File: `docs/enterprise-deployment.md`

---

## Slice 17 — Looker Ecosystem Breakdown

**Status:** queued
**Mode:** Patch (docs only)
**Depends:** Slice 12 complete (so Looker provider role is accurate)
**Gate:** doc review

3-column table: Looker MCP Server | Looker Extension | Strata — what each is,
what it does, data access model, where it runs, how Strata fits within.

File: `docs/looker-ecosystem.md`

---

## Slice 18 — Security Hardening + Offline-First

**Status:** queued
**Mode:** Patch (docs only)
**Depends:** Slices 12, 15 complete
**Gate:** doc review

Security: read-only enforcement, credential matrix, MCP security model, audit
trail, what Strata never does.
Offline-first: full offline analysis guide, MCP workflow without live config,
capability tier table (formalized from strata_workflow.md).

Files: `docs/security-hardening.md`, `docs/offline-first-walkthrough.md`

---

## Slice 19 — Public-Facing Branch Setup

**Status:** queued
**Mode:** Patch (infra + docs)
**Depends:** All prior slices complete; README and docs polished
**Gate:** public repo `make ci` passes; no internal conductor docs or enterprise BQ refs present

Two-repo architecture: private `strata` (all branches) + public `strata-oss`.
GH Actions sync on push to `main`, filtering out conductor/, enterprise fixtures,
internal config.

Files: `.github/workflows/sync-public.yml`, `docs/CONTRIBUTING.md`,
`.publicignore`, `README.md` (public-facing rewrite).

---

## Brick Status (productionization track)

| Brick | Name | Status |
|---|---|---|
| P1 | Conductor + agentic runbook | ✅ STABLE (Slice 16) |
| P2 | Store removal + simplification | queued |
| P3 | Looker live provider | queued |
| P4 | GH Actions + notifications | queued |
| P5 | Testing scenario docs | queued |
| P6 | Enterprise + Google controls | queued |
| P7 | Looker ecosystem breakdown | queued |
| P8 | Security hardening + offline-first | queued |
| P9 | Public branch setup | queued |

---

## Agentic Execution Model

Every slice executes as a bounded session:

1. **Turn 1:** `git status -sb && git log -n 5 --oneline && cat conductor/handoff-log.md`
2. Read active slice spec (this document + the slice's own spec file if one exists)
3. Execute bounded work following the spec exactly — read code before changing it
4. Run gate verification
5. Commit with handoff-log update (same commit or adjacent commit, both required)
6. Stop — write "Exact Next Steps" pointing to the next slice

Stop conditions (do not proceed without operator approval):
- Any gate fails
- Slice spec is ambiguous on a consequential decision
- Unexpected state found (unfamiliar files, merge conflicts, broken imports)

For async progress during a long session:
- Use `mcp__workspace-partner__duos_report_progress` to post milestone updates
- Use `ScheduleWakeup` only if waiting on a slow build step; otherwise run sequentially
