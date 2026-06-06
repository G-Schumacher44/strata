# Slice 05: MCP Repo-Brain + Output Artifacts (Brick 5)

Date: 2026-06-06
Status: stable
Brick: 5
Depends: Bricks 1-4 STABLE

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Expose L0-L1 answers through the local stdio MCP server and generate durable
offline artifacts for review: catalog, dead-code register, PDT ledger, cleanup
roadmap, and migration-impact data.

## Acceptance Criteria

- [x] MCP repo-brain answers dependency, usage, dead-code, PDT cost, and impact queries
- [x] Output artifacts are generated from fixture-backed enriched IR
- [x] Artifact generation is deterministic and offline
- [x] MCP stdio smoke lists/calls tools successfully
- [x] `.venv/bin/pytest` passes with scenario coverage
- [x] `python3 scripts/validate.py` passes
