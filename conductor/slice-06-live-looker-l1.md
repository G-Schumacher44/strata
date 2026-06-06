# Slice 06: Live Looker L1 Adapter

Date: 2026-06-06
Status: queued
Brick: post-v0.1.0
Depends: v0.1.0 fixture-backed core

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Wire the existing L1 adapter contract to read-only Looker/System Activity facts on
the test instance. Keep fixture-backed gates as the baseline; live access is opt-in
and must never be required for ordinary CI.

## Scope

- `src/strata/l1/looker.py` — implement live read-only adapter
- `src/strata/l1/config.py` — load non-secret connection config from env or local config
- `scripts/` — add live adapter smoke/check command
- `tests/` — fixture and adapter-contract tests only; no live dependency in CI
- `conductor/` — handoff and gate updates

## Non-Goals

- No writes to Looker, prod, the LookML repo, or any live instance
- No LLM calls
- No live Looker dependency in `python -m pytest` or CI
- No org-specific schema/table names in generic source or fixtures

## Implementation Contract

1. Add a config loader that reads only non-secret settings from env/local config:
   `STRATA_LOOKER_BASE_URL`, `STRATA_LOOKER_CLIENT_ID`, `STRATA_LOOKER_CLIENT_SECRET`,
   and optional `STRATA_LOOKER_VERIFY_SSL`.
2. Implement a read-only adapter that maps live facts into existing L1 dataclasses:
   `ExploreUsage`, `ContentReference`, and `PDTBuild`.
3. Add a CLI smoke command that can be run manually against the test instance and emits
   counts plus redacted config status.
4. Preserve the fixture-backed `build_graph(..., usage_fixture=...)` path unchanged.
5. Document manual validation separately from automated gates.

## Acceptance Criteria

- [ ] Live adapter implements the existing L1 adapter contract
- [ ] Missing live config fails fast with a clear message
- [ ] Fixture-backed tests still pass without live Looker credentials
- [ ] Manual smoke command can fetch read-only test-instance facts
- [ ] `.venv/bin/pytest` passes
- [ ] `.venv/bin/python scripts/check_strata.py` passes
- [ ] `python3 scripts/validate.py` passes
- [ ] `conductor/handoff-log.md` updated with a real Commit: hash
