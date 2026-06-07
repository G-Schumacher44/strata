# Slice 21 — Author Attribution

Status: planned
Track: D
Depends: Slice 20 (STABLE)
Master plan: conductor/master-plan-enhancement.md § Slice 21

## Problem

When Strata flags a zombie PDT or dead explore, the next question is always "who owns this?"
Without attribution, the cleanup conversation stalls — nobody knows who to ping.

## Solution

`src/strata/outputs/attribution.py` — runs `git log` / `git blame` over each flagged item's
source file to extract last committer, last commit date, and original author.

New artifact: `ownership.json`
```json
[
  {
    "item": "em_legacy_v2.dead_finance_v2",
    "kind": "explore",
    "source_file": "models/em_legacy_v2.model.lkml",
    "last_author": "Jane Smith <jane@example.com>",
    "last_touched": "2025-03-14",
    "original_author": "Bob Jones <bob@example.com>",
    "created": "2023-08-01"
  }
]
```

Integrated into `cleanup_roadmap.json` and `scripts/notify.py` Slack payload.

## Files

- `src/strata/outputs/attribution.py` — NEW
- `scripts/generate_outputs.py` — add `ownership.json` to artifact set
- `src/strata/outputs/artifacts.py` — register new artifact
- `src/strata/outputs/notifications.py` — add owner name to Slack payload

## Constraints

- git operations are read-only subprocess calls — no mutation
- Graceful fallback if git not available or file history absent (attribution = "unknown")
- No LLM in attribution logic

## Gate (activate when implementation begins)

- `python scripts/generate_outputs.py --repo tests/lookml/enterprise_mono ...` produces `ownership.json` with 11 entries (6 dead explores + 5 zombie views) each having author fields
- `python scripts/notify.py --artifacts output/enterprise_mono --dry-run` includes owner names in Slack payload
- Graceful fallback when source_file has no git history — entry present, author = "unknown"
- 49+ tests passing, validate.py 10/10
