# Slice 06: Govern Public Release Flow

Date: 2026-06-09
Status: stable
Phase: Governance Tooling
Depends: Slice 03

```yaml
conductor_mode: patch
context_budget: low
handoff_required: true
stable_tag_required: false
```

## Objective

Establish a deterministic public-release flow so `public/main` remains a
sanitized export target instead of an accidental mirror of private `main` or
`dev`. The flow must make the private/public boundary explicit and give agents a
local check before pushing to the public remote.

## Scope

- Governance documentation
- Maintenance scripts
- Public release safety checks

## Implementation Order

1. Document the branch model and public promotion sequence.
2. Add a read-only audit script for candidate public release refs.
3. Link the script from `scripts/README.md`.
4. Validate the script against the current private branch and public baseline.

## The Hard Constraint

The public release guardrail must be read-only. It may inspect git refs and file
contents, but it must never merge, write, delete, or push.

## Acceptance Criteria

- [x] Public release branch model is documented.
- [x] Public audit script exists and is read-only.
- [x] Script flags private conductor working files when comparing private `HEAD`
      to `public/main`.
- [x] `.venv/bin/python -m pytest` — all tests pass
- [x] `strata validate` — spine passes
- [x] `conductor/handoff-log.md` — review entry with Commit: hash
