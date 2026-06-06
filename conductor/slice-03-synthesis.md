# Slice 03: Synthesis Skills + Governance (Brick 3 — L2/L3)

Date: 2026-06-06
Status: stable
Brick: 3
Depends: Brick 2 STABLE

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Create bounded synthesis inputs from IR+L1 evidence and validate verdicts before
they can ship. Model execution remains pluggable; tests use deterministic local
rules and no LLM calls.

## Acceptance Criteria

- [x] Explore slices include dependency, usage, orphan, and PDT evidence only
- [x] Verdict validation rejects missing evidence trails
- [x] Deterministic synthesis can produce a fixture verdict
- [x] No raw LookML is sent through synthesis inputs
- [x] `.venv/bin/pytest` passes with scenario coverage
- [x] `python3 scripts/validate.py` passes when active
