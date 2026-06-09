# Slice 03: Decouple Conductor CI into Soft-Gated PR Comment

Date: 2026-06-09
Status: stable
Phase: CI Governance
Depends: none

```yaml
conductor_mode: slice
context_budget: low
handoff_required: true
stable_tag_required: false
```

## Objective

To reduce friction on human contributors and non-Conductor adoption, we need to decouple the Conductor spine validation (`strata validate`) from the main GitHub Actions CI pipeline (`strata-ci.yml`). Instead of failing the build hard, the validation should run as part of the PR comment bot (`scripts/pr_comment.py`), appending its output to the PR comment as a visible but non-blocking "soft gate".

## Scope

- CI Workflows (`.github/workflows/strata-ci.yml`)
- Scripts (`scripts/pr_comment.py`)

## Implementation Order

1. **Modify `scripts/pr_comment.py`**: Add a function `_run_conductor_validation()` that executes `strata validate` via subprocess, captures both stdout and stderr, ignores the non-zero exit code (soft gate), and formats the output into a markdown block.
2. **Update PR Comment Construction**: Append the output of `_run_conductor_validation()` to the end of the markdown comment posted to the PR.
3. **Remove Hard CI Gate**: Delete the "Conductor spine validation" step from `.github/workflows/strata-ci.yml`.

## The Hard Constraint

The PR comment script *must not* fail or crash if `strata validate` fails or if the `conductor/` directory doesn't exist. It must swallow the exit code and gracefully print the text output into the PR comment.

## Acceptance Criteria

- [x] `.github/workflows/strata-ci.yml` no longer runs `strata validate`.
- [x] `scripts/pr_comment.py` captures `strata validate` output regardless of exit code.
- [x] `scripts/pr_comment.py` appends the validation output as a markdown section at the bottom of the PR comment.
- [x] `.venv/bin/pytest` — all tests pass
- [x] `conductor/handoff-log.md` — STABLE entry with Commit: hash
