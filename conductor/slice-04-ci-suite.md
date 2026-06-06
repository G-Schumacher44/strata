# Slice 04: CI Suite (Brick 4)

Date: 2026-06-06
Status: stable
Brick: 4
Depends: Brick 1 STABLE; Brick 3 STABLE for evidence gates

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Add non-blocking-by-design scenario gates that run offline in CI: pytest,
IR build, evidence validation, output generation, and Conductor validation.

## Acceptance Criteria

- [x] CI workflow runs pytest, IR build, Strata gates, and Conductor validation
- [x] Gate script flags broken extends chains
- [x] Gate script validates synthesis verdict evidence
- [x] Gate script runs without live Looker access
- [x] `.venv/bin/pytest` passes with scenario coverage
- [x] `python3 scripts/validate.py` passes when active
