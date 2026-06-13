# Slice 06: Add Conductor CLI Tests

Date: 2026-06-13
Status: stable
Phase: Test Coverage
Depends: slice-05

```yaml
conductor_mode: slice
context_budget: low
handoff_required: true
stable_tag_required: false
```

## Objective

The `strata conductor init` and `strata conductor new-slice` CLI commands were
implemented in slice-04/05 but have zero test coverage. Every other CLI
sub-command group (`mcp`, `query`, `skill`, `bootstrap`, `generate-schema`) has
tests in `tests/test_cli.py`. This slice closes that gap with targeted,
fixture-isolated tests.

## Scope

- **Tests** — `tests/test_cli.py` (new conductor test block)
- **No source changes** — tests only

## The Hard Constraint

Each test must use `tmp_path` for full filesystem isolation. No test may touch
the live `conductor/` directory or any real slice file. Tests must pass whether
or not the repo's own conductor state is clean.

## Implementation Order

1. Add `test_conductor_init_creates_expected_files` — verify all 7 expected
   files are written by `strata conductor init`.
2. Add `test_conductor_init_skips_existing_without_force` — verify skip
   behaviour (no overwrite) and that output says "skip".
3. Add `test_conductor_init_force_overwrites_existing` — verify `--force`
   replaces existing files.
4. Add `test_conductor_new_slice_creates_numbered_file` — verify file is
   created with auto-numbered name and "Phase: TBD" in content.
5. Add `test_conductor_new_slice_auto_increments` — verify second slice gets
   number 02.
6. Add `test_conductor_new_slice_mode_and_budget_in_content` — verify
   `--mode patch --budget low` appear in the generated file.
7. Add `test_conductor_new_slice_fails_without_conductor_dir` — verify
   non-zero exit and error message when `conductor/` is missing.

## Acceptance Criteria

- [x] All 7 new tests exist in `tests/test_cli.py` under a `# conductor CLI` heading.
- [x] `python -m pytest tests/test_cli.py -k "conductor" -v` — all 7 pass.
- [x] `python -m pytest` — full suite passes (no regressions).
- [x] `ruff check src/ tests/ scripts/` — clean.
- [x] `conductor/handoff-log.md` — STABLE entry with Commit: hash.
