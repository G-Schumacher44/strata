# Slice 08: Offline Schema Drift

Date: 2026-06-06
Status: review
Brick: 8
Depends: Slice 06 review-ready; Slice 07 blocked

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Add a deterministic offline schema-drift layer that compares resolved LookML table
and field references against fixture/replay warehouse schema facts. This keeps
Phase 2 moving while live Looker access remains blocked and prepares the eventual
BigQuery `INFORMATION_SCHEMA` adapter without adding live dependencies.

## Scope

L1 schema facts, enrichment, output artifacts, MCP repo-brain surface, tests, and
Conductor governance. No live BigQuery or Looker calls.

## Implementation Order

1. Add fixture schema facts under `tests/fixtures/`.
2. Add L1 schema dataclasses and provider protocol.
3. Add fixture schema provider and schema-drift enrichment.
4. Expose schema drift through output artifacts and MCP tools.
5. Add focused tests for provider, enrichment, artifacts, and MCP surface.
6. Run full local gates and update handoff.

## The Hard Constraint

Schema drift evidence must be deterministic and offline. A missing-table or
missing-column verdict must cite the IR node and the fixture schema source state;
ordinary CI must not require warehouse credentials.

## Acceptance Criteria

- [x] Fixture-backed schema provider loads deterministic table/column facts
- [x] Schema drift detects at least one missing physical table
- [x] Schema drift detects at least one missing referenced column
- [x] Clean fixture schema produces no drift records
- [x] Schema drift is exposed through output artifacts and MCP
- [x] Existing usage/replay tests still pass
- [x] `.venv/bin/pytest` passes
- [x] `.venv/bin/python scripts/check_strata.py` passes
- [x] `python3 scripts/validate.py` passes
- [x] `conductor/handoff-log.md` updated with a real Commit: hash
