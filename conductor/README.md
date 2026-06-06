# Conductor

Conductor owns the workflow pipeline, planning artifacts, control-doc hierarchy,
and execution-system documentation for Strata.

## What Lives Here

| File / Dir | Purpose |
|---|---|
| `index.md` | Machine-first routing entry — context pack, control hierarchy, active strategy |
| `README.md` | This file — directory conventions, lifecycle model, archive policy |
| `CONDUCTOR_MODES.md` | Execution-mode contract for Patch, Slice, Full, and Audit work |
| `tracks.md` | Cross-repo spoke registry |
| `slice-*.md` | Active commit-sized execution artifacts |
| `master-plan-*.md` | Multi-slice initiative maps (added when a brick spans many slices) |
| `templates/` | Canonical templates: slice, starter prompt, review checklist |
| `review/` | Completed slices awaiting explicit review/stable disposition |
| `archive/` | Reviewed slices after stable checkpoint is cut |
| `handoff-log.md` | Current active handoff block only |
| `handoff-archive.md` | Historical handoff entries — not on the hot read path |

## Naming and Placement

- Machine-first routing stays at `conductor/index.md`.
- Active slice docs stay at `conductor/slice-*.md`.
- Multi-slice initiatives get a `conductor/master-plan-*.md`.
- Completed slices move to `conductor/review/` once all gates are checked.
- After the stable checkpoint is cut, reviewed slices move to `conductor/archive/`.
- Versioned starter prompts stay at `conductor/templates/`.
- `handoff-log.md` holds the current block only — move older entries to `handoff-archive.md`.

## Spec Package Pattern

- Multi-slice bricks should have one `master-plan-*.md` defining the canonical operating
  model and slice sequence.
- The active `slice-*.md` is the implementation contract for the current execution chunk.
- Every slice must declare its `conductor_mode`, `context_budget`, handoff posture, and
  stable tag posture in its mode tags block.
- Update the governing Conductor artifact before implementation — spec before build.
- `README.md` is the human-facing contract; `index.md` is the machine-facing router.
- `index.md`, `tracks.md`, and `handoff-log.md` stay current-state only — move history elsewhere.

## Lifecycle Model

```
slice-*.md (active)
    → conductor/review/    (all gates checked [x], ready for review)
    → conductor/archive/   (stable checkpoint cut)
```

- A slice is **active** while it governs implementation or validation work.
- A slice is **review-ready** only after all Acceptance Criteria are marked `[x]`.
- Move to `review/` when checklist is complete.
- Move to `archive/` after the stable checkpoint commit is made.
- `handoff-archive.md` is the only permanent history surface — keep it.
- Archive is a short-lived buffer; durable state belongs in `handoff-log.md` and git history.

## Context Hygiene

- Do not read `conductor/archive/**` or `handoff-archive.md` unless history is required.
- Read the active slice before reading every slice.
- `index.md` is the entry point — start there, not at the slice list.
