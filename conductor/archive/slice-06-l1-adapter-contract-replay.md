# Slice 06: L1 Adapter Contract + Replay Harness

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

Harden the L1 provider boundary without live Looker/test-instance access. Build a
replay harness that maps sanitized Looker/System Activity-shaped rows into the same
L1 dataclasses used by fixture-backed enrichment. Live Looker work moves to Slice 07
and remains blocked on test-instance credentials/access.

## Scope

- `src/strata/l1/provider.py` — provider protocol and normalized collection helpers
- `src/strata/l1/fixtures.py` — normalized fixture provider
- `src/strata/l1/replay.py` — sanitized replay provider for raw-ish System Activity rows
- `tests/fixtures/replay_facts.json` — sanitized replay rows
- `scripts/` — replay validation CLI
- `tests/` — provider contract/scenario tests; no live dependency in CI
- `conductor/` — master plan, index, and handoff updates

## Non-Goals

- No live Looker connection
- No writes to Looker, prod, the LookML repo, or any live instance
- No LLM calls
- No org-specific schema/table names in generic fixtures/source
- No secrets or OAuth client work

## Implementation Contract

1. Define a provider protocol that returns normalized `ExploreUsage`,
   `ContentReference`, and `PDTBuild` lists.
2. Wrap existing normalized JSON fixtures in a `FixtureUsageProvider`.
3. Add a `ReplayLookerUsageProvider` that reads sanitized raw-ish rows and maps them
   into existing L1 dataclasses.
4. Add provider contract tests that run against both fixture and replay providers.
5. Preserve `build_graph(..., usage_fixture=...)` compatibility.
6. Add a CLI that validates replay facts and prints normalized counts.

## Acceptance Criteria

- [x] Provider protocol exists and is used by fixture/replay providers
- [x] Replay provider maps raw query/content/PDT rows to existing L1 dataclasses
- [x] Provider contract tests pass for fixture and replay providers
- [x] Replay CLI validates sanitized rows without network or secrets
- [x] Fixture-backed `build_graph(..., usage_fixture=...)` remains compatible
- [x] `.venv/bin/pytest` passes
- [x] `.venv/bin/python scripts/check_strata.py` passes
- [x] `python3 scripts/validate.py` passes
- [x] `conductor/handoff-log.md` updated with a real Commit: hash
