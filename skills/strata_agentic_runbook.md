# Strata Agentic Runbook

Operational playbook for a Claude agent executing Strata conductor slices
autonomously. The operator sets up the slice spec and kicks off the session;
the agent executes end-to-end and writes the handoff. The operator reviews
asynchronously.

---

## Turn 1 — Always

Before proposing or executing any work, run:

```bash
git status -sb && git log -n 5 --oneline && cat conductor/handoff-log.md
```

Then read:
1. `conductor/index.md` — active slice and reading order
2. The active slice spec file (`conductor/slice-N-*.md`)
3. Any referenced source files (read before touching)

Do not skip Turn 1. Do not write code before reading the active slice spec.

---

## Reading Order (full session)

```
AGENTS.md → intent.md → conductor/index.md → active slice spec → handoff-log.md
```

Skip `conductor/archive/**` unless the active slice explicitly requires history.

---

## Execution Rules

**Read before changing.** Always read an existing file before editing it.

**Spec before build.** If the slice spec is incomplete, write the clarification
to the handoff and stop. Do not improvise on consequential decisions.

**Deterministic core (L0–L1).** These layers must never call any LLM or external
API. No network calls, no subprocess shell-outs to cloud CLIs, no imports of
libraries that make HTTP calls. Pure Python only.

**Read-only is non-negotiable.** No writes to the LookML repo, Looker instance,
or BQ. No mutations anywhere except local output files and the local strata DB.

**Gate before handoff.** Run the gate verification listed in the slice spec before
writing the handoff. A green handoff on a failing gate is a contract violation.

---

## Slice Execution Pattern

```
1. Turn 1 (git + handoff read)
2. Read slice spec
3. Read all files the spec says to modify
4. Execute changes (code or docs)
5. Run gate verification
6. If gate passes → write handoff + commit
7. If gate fails → fix or write clarification to handoff, then stop
```

For code slices: make the smallest change that satisfies the spec. Do not
refactor adjacent code unless the spec explicitly calls for it.

For doc slices: write docs that are accurate to the current code state. If a doc
references a feature that isn't implemented yet, say so explicitly in the doc.

---

## Gate Verification

Run the gate listed in the slice spec. Common gates:

```bash
# Standard CI gate (must pass for every code change)
make ci

# Conductor validation gate (for conductor/docs changes)
python scripts/validate.py

# Playground-specific gate
make ci REPO=tests/lookml/enterprise_mono \
  USAGE=tests/fixtures/enterprise_usage_facts.json \
  SCHEMA=tests/fixtures/enterprise_schema_facts.json
```

If a gate fails: diagnose the root cause, fix it, re-run. Do not use `--no-verify`
or skip hooks. Do not amend commits to bypass a failing gate — fix the issue and
commit fresh.

---

## Handoff Format

Every handoff entry in `conductor/handoff-log.md` must include:

```markdown
## Date: YYYY-MM-DD — [Slice N: Short Title]
Commit: [7-char hash]
Target Branch: dev
Status: [active | review | complete]
[What was done — 3-5 bullet points]
[What was NOT done (if relevant)]
Conductor Mode: [patch | slice | full]
Context Budget: [low | medium | high]
Context Loaded: [files read in this session]
Context Skipped: [conductor/archive/**, etc.]
Exact Next Steps: [clear instruction for the next session]
```

The `Commit:` field is mandatory — it anchors the handoff to a real git state.
Write the handoff entry, then commit. Both the code change and the handoff update
must be in the repo before the session ends.

---

## Stop Conditions

Stop immediately (do not proceed to the next step) when:

- **Gate fails and root cause is not in the slice scope** — write the failure
  details to handoff and stop. Do not widen scope without operator approval.
- **Slice spec is ambiguous on a consequential decision** — write a clarification
  question to the "Exact Next Steps" field and stop.
- **Unexpected repo state** — files you didn't expect, merge conflicts, broken
  imports not caused by your changes. Investigate; if cause is unclear, stop.
- **L0/L1 code would need to make an HTTP call** — this is a design constraint
  violation. Stop and propose an alternative in the handoff.

Do not use `ScheduleWakeup` to avoid a stop — stops are how the operator stays
in the loop. Use `ScheduleWakeup` only when waiting on a slow background process
(build, test run) that you've already started.

---

## Async Progress Reporting

For long-running slices (multiple files, test suites), report progress at milestones:

```python
# After completing a major sub-step, report via DUOS
mcp__workspace-partner__duos_report_progress(
    message="Slice 12: LookerSystemActivityProvider implemented. Running gate..."
)
```

Use this for:
- "Starting gate verification — running make ci"
- "Gate passed — writing handoff and committing"
- "Gate failed on [test name] — investigating"

Do not spam. One report per major milestone, not per file edited.

---

## ScheduleWakeup Usage

Only use `ScheduleWakeup` when:
1. You've started a long background process (e.g., a slow test suite)
2. You need to wait for it before proceeding
3. The process cannot be run synchronously (rare)

Use the loop prompt verbatim from the original invocation. Set delay to match
the expected process duration — don't sleep longer than needed, but don't poll
faster than every 60 seconds.

Do NOT use `ScheduleWakeup` to:
- Avoid writing a handoff and stopping
- "Check back later" on ambiguous decisions
- Poll a process you haven't started yet

---

## Multi-Slice Autonomous Sessions

When the operator grants permission to run multiple slices in sequence:

1. Complete Slice N fully (code → gate → handoff → commit)
2. Report progress via DUOS
3. Read the next slice spec
4. If the next slice spec is clear and the gate passed: proceed
5. If any gate fails or spec is ambiguous: stop, regardless of how many slices remain

The operator can interrupt at any handoff boundary. Each handoff is a safe pause
point. Never skip a handoff to save time.

---

## Context Management

Load context in this order and stop when you have enough:
1. `AGENTS.md` + `conductor/index.md` + active slice spec — always
2. Source files the slice modifies — always read before editing
3. `handoff-log.md` latest block — when resuming
4. `intent.md` — when architecture decisions are in scope
5. `conductor/CONDUCTOR_MODES.md` — when mode choice is in question

Skip unless needed:
- `conductor/archive/**`
- `handoff-archive.md`
- Source files not mentioned in the slice spec
