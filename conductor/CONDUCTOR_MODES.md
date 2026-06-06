# Conductor Modes

Choose mode before widening context. Use the smallest mode that covers the work.
Starting too wide wastes context budget and introduces drift. Starting too narrow
misses cross-cutting effects — widen deliberately when the slice demands it.

---

## Mode Reference

### Patch Mode
**When:** Bug fix, one-file change, doc update, minor config tweak.
**Context to load:**
- `AGENTS.md`
- The affected file(s)
- `conductor/handoff-log.md` — latest block only
**Do not load:** slice spec, index, intent.md (unless directly relevant)
**Commit posture:** one focused commit; no slice spec update required unless a gate changes.

---

### Slice Mode
**When:** Bounded feature work described by an active slice spec. One slice = one session.
**Context to load:**
- `AGENTS.md`
- `intent.md`
- `conductor/index.md`
- active `conductor/slice-*.md`
- `conductor/handoff-log.md` — latest block only
- subdirectory `AGENTS.md` for the layer being modified
**Do not load:** archive, prior slices, unrelated docs.
**Commit posture:** atomic commits per logical unit; handoff-log updated in final commit.

---

### Full Conductor Mode
**When:** Cross-cutting change (new layer, API boundary change, major refactor, new brick).
**Context to load:** everything in the reading order defined in `conductor/index.md`.
**Commit posture:** may span multiple commits; slice spec must be updated or created first.
**Use sparingly** — most work is Patch or Slice.

---

### Audit Mode
**When:** Review only. No implementation. Assessing correctness, coverage, or drift.
**Context to load:** whatever is under review.
**Commit posture:** none (read-only pass). If issues are found, write them as a
new slice spec or patch proposal — do not fix inline during an audit.

---

## Context Budget Guide

| Budget | What it means | Typical mode |
|---|---|---|
| **Low** | Under 20k tokens loaded | Patch |
| **Medium** | 20–60k tokens | Slice |
| **High** | 60k+ tokens | Full Conductor |

Record the budget in the handoff-log entry so the next agent knows how much context
was available and what was skipped.

---

## Mode Discipline Rules

- **Declare mode before starting.** First line of your plan: "Conductor Mode: Patch / Slice / Full / Audit."
- **Record mode in handoff.** Every handoff-log entry includes `Conductor Mode:` and `Context Loaded:` / `Context Skipped:`.
- **Do not widen mid-session** unless you hit a hard blocker that requires it. Record the reason.
- **Coordination surfaces (Stage, Ledger, Duos) are optional** — not default execution gates. Use them only when the operator needs visibility into an in-flight change.
