# Slice 09: Offline Validation Scope

Date: 2026-06-06
Status: review
Brick: 9
Depends: Slice 08 review-ready; no Looker access during POC

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Add a deterministic offline validation-scope planner that turns changed LookML
views or warehouse tables into the minimal impacted explore set. This prepares
future Spectacles-scoped validation without requiring Spectacles, Looker, or a
warehouse during the POC.

## Scope

L0/L1 read-only graph queries, output artifacts, MCP repo-brain surface, tests,
and Conductor governance. No live Looker, Spectacles, or warehouse calls.

## Implementation Order

1. Add fixture changed-object inputs under `tests/fixtures/`.
2. Add validation-scope planner over the resolved IR graph.
3. Expose validation scope through MCP and output artifacts.
4. Wire an offline scenario gate into `scripts/check_strata.py`.
5. Add focused tests for view changes, physical-table changes, dedupe, and unknown input.
6. Run full local gates and update handoff.

## The Hard Constraint

The planner must be conservative and deterministic. If a changed object maps to
multiple views through PDT upstreams or physical table references, every impacted
explore must be included. Unknown inputs must be reported as unmatched, not
silently dropped.

## Acceptance Criteria

- [x] Changed view input returns only explores that use that view
- [x] Changed physical table input returns explores impacted through table/view/PDT edges
- [x] Duplicate changed inputs produce deterministic de-duplicated explore scope
- [x] Unknown changed inputs are reported as unmatched
- [x] Validation scope is exposed through output artifacts and MCP
- [x] Existing usage/replay/schema tests still pass
- [x] `.venv/bin/pytest` passes
- [x] `.venv/bin/python scripts/check_strata.py` passes
- [x] `python3 scripts/validate.py` passes
- [x] `conductor/handoff-log.md` updated with a real Commit: hash
