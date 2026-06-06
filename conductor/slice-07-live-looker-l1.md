# Slice 07: Live Looker L1 Adapter

Date: 2026-06-06
Status: blocked
Brick: post-v0.1.0
Depends: Slice 06 STABLE; read-only test-instance credentials/access

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Wire the Slice 06 provider boundary to read-only live Looker/System Activity facts
on the test instance. This slice is blocked until test-instance access is available.

## Blocker

Need read-only Looker test-instance credentials/config and confirmation of the access
route: Looker SDK/API, Looker MCP, or both with a preferred primary path.

## Acceptance Criteria

- [ ] Live adapter implements the Slice 06 provider protocol
- [ ] Missing live config fails fast with a clear message
- [ ] Fixture/replay tests still pass without live Looker credentials
- [ ] Manual smoke command can fetch read-only test-instance facts
- [ ] No live dependency in ordinary CI
- [ ] `conductor/handoff-log.md` updated with a real Commit: hash
