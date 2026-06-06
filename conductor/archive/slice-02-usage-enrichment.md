# Slice 02: Usage & Cost Enrichment (Brick 2 — L1)

Date: 2026-06-06
Status: stable
Brick: 2
Depends: Brick 1 STABLE

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Join the resolved L0 IR against read-only usage, content, and PDT build facts.
Default execution is offline and fixture-backed; live Looker access is adapter-only
and disabled unless explicitly configured.

## Acceptance Criteria

- [x] Fixture-backed L1 adapter loads explore usage, content references, and PDT build facts
- [x] L1 enrichment joins facts to resolved IR without changing L0 node IDs
- [x] Static orphan ∩ zero-usage evidence emits dead-code records
- [x] PDT cost ledger emits used/unused build-cost records
- [x] `.venv/bin/pytest` passes with scenario coverage
- [x] `python3 scripts/validate.py` passes when active
