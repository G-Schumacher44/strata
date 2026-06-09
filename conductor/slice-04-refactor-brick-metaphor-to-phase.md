# Slice 04: Refactor Brick Metaphor to Phase

Date: 2026-06-09
Status: stable
Phase: Governance Cleanup
Depends: none

```yaml
conductor_mode: full
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

The term "Brick" was introduced during the initial AI scaffolding phase as a proprietary metaphor for architectural milestones or epics. This is an "AI smell" that adds unnecessary cognitive load. This slice refactors all 31 occurrences of "Brick" across the project to the industry-standard term "Phase".

## Scope

- Conductor templates (`conductor/templates/`)
- Active Conductor tracking files (`conductor/index.md`, active slices)
- Bootstrap templates (`src/strata/bootstrap/templates/`)
- Governance documentation (`GOVERNANCE.md`, `AGENTS.md`)
- Python source code strings (`src/strata/cli/conductor.py`, `src/strata/ir/parser.py`)

## Implementation Order

1. **Python CLI**: Update `src/strata/cli/conductor.py` so `strata conductor new-slice` generates `Phase: TBD` instead of `Brick: TBD`.
2. **Bootstrap Templates**: Update all files in `src/strata/bootstrap/templates/` to use "Phase".
3. **Active Conductor**: Update `conductor/index.md`, `conductor/CONDUCTOR_MODES.md`, and all `conductor/templates/` to use "Phase". Update the header metadata of existing `slice-*.md` files.
4. **Governance & Source**: Replace the term in `GOVERNANCE.md`, `AGENTS.md`, and python docstrings.

## The Hard Constraint

Because `src/strata/bootstrap/templates/` contains the files used by `strata bootstrap` to initialize *new* repositories, we must ensure that no new repository is ever initialized with the word "Brick". A clean search for `\b[Bb]rick[s]?\b` must return exactly 0 results across the entire repository before this slice is complete.

## Acceptance Criteria

- [x] `strata conductor new-slice "Test"` generates a file with `Phase: TBD`.
- [x] A case-insensitive regex search for `\bbrick[s]?\b` returns 0 results across the repository.
- [x] `.venv/bin/pytest` passes (ensuring no Python docstring changes broke tests).
- [x] `conductor/handoff-log.md` — STABLE entry with Commit: hash
