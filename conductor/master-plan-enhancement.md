# Master Plan: Strata Enhancement — Track D

Date: 2026-06-06
Status: active
Type: master-plan
Depends: master-plan-productionization.md (all bricks STABLE), Track C (MCP + OSS shipped)

## Objective

Close the loop between analysis and action. Strata surfaces findings — the next layer
is getting those findings in front of the right people at the right moment: in a PR,
in a Slack message, in a git blame. Also lay groundwork for deeper integrations
(dbt, Looker Extension, incremental IR) that make Strata useful at larger scale.

---

## Strategic Context

Tracks A–C delivered:
- Complete deterministic IR (L0–L1), three verified playgrounds
- MCP server (10 tools, Claude Code native)
- GH Actions CI, Slack/Jira notification scaffolding
- OSS public repo (strata-oss) with thesis-driven docs

The gap that remains: findings are produced but reaching the team still requires manual
steps. A zombie PDT report sitting in `output/` doesn't create a Jira ticket. A dead
explore doesn't file its own deprecation PR. Author attribution doesn't happen automatically.

Track D closes that gap — findings → action, automatically.

One external gate from Track B remains open (live Looker OAuth smoke) but it is not a
conductor slice; it requires a real Looker instance. It does not block Track D.

---

## Slice Sequence

```
20 → 21 → 22 → [23+ future]
```

Slices 20–22 are the immediate sprint. Slices 23+ are specced as future work — do not
start until 20–22 are STABLE.

---

## Slice 20 — PR Validation Bot

**Status:** planned
**Mode:** Slice (new module + GH Actions)
**Gate:** On a test PR touching a LookML view, the bot comments with correct validation scope
and impact analysis within 2 minutes of push.

### Problem
Engineers opening LookML PRs have no automated signal for which explores are affected.
The reviewer has to know the IR by memory, or run `strata_validation_scope` manually.

### Solution
A new GH Actions workflow (`strata-pr.yml`) triggers on `pull_request` events touching
`.lkml` files. It:
1. Detects changed `.lkml` files from the PR diff
2. Runs Strata offline (no Looker needed) against the repo at that commit
3. Calls `strata_validation_scope(changed=[...])` and `strata_impact(...)` for each changed file
4. Posts a structured PR comment via `gh pr comment`

**Comment format:**
```markdown
## Strata Analysis

**Changed files:** 3 LookML files

| Changed | Explores to revalidate | Impact |
|---|---|---|
| `views/customers.view.lkml` | 4 explores | 12 views, 2 explores, 47 fields |
| `views/orders.view.lkml` | 2 explores | 8 views, 1 explore, 23 fields |

_Run `make ci` locally to verify all explores pass before merging._
```

**Files:**
- `.github/workflows/strata-pr.yml` — NEW: PR trigger, lkml diff detection, Strata run, comment post
- `scripts/pr_comment.py` — NEW: builds the PR comment from validation scope + impact results
- `src/strata/outputs/pr_report.py` — NEW: `build_pr_comment(scope, impacts)` → markdown string

**Invariants:** No LLM in L0/L1. PR analysis uses offline fixtures (or no fixtures for pure L0).
Comment is posted via `gh` CLI, not direct GitHub API calls in Python.

**Gate:** Push a test PR touching `tests/lookml/gcs_analytics/` → bot comments within 2 min.

---

## Slice 21 — Author Attribution

**Status:** planned
**Mode:** Slice (new module)
**Gate:** `scripts/generate_outputs.py` produces `ownership.json` with author and last-touch
date for every dead explore and zombie PDT.

### Problem
When Strata flags a zombie PDT or dead explore, the next question is always "who owns this?"
Without attribution, the cleanup conversation stalls — nobody knows who to ping.

### Solution
`src/strata/outputs/attribution.py` — runs `git log` / `git blame` over each flagged item's
source file to extract:
- Last committer (name + email)
- Last commit date for that file
- First committer (original author, from `git log --follow --diff-filter=A`)

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

Integrated into `cleanup_roadmap.json` — each action item gains `owner` and `last_touched` fields.
Integrated into `scripts/notify.py` — Slack message includes "@jane the `dead_finance_v2` explore
is flagged; last touched 2025-03-14."

**Files:**
- `src/strata/outputs/attribution.py` — NEW: git blame/log wrappers, `build_ownership(dead_code, repo_path)`
- `scripts/generate_outputs.py` — add `ownership.json` to artifact set
- `src/strata/outputs/artifacts.py` — register new artifact
- `src/strata/outputs/notifications.py` — add owner name to Slack payload

**Constraints:** git operations are read-only subprocess calls. No mutation. Graceful fallback
if `git` not available or file history is absent (attribution = "unknown").

**Gate:** `make ci` on enterprise_mono produces `ownership.json` with authors for all 6 dead
explores. `notify.py --dry-run` includes owner names in the Slack payload.

---

## Slice 22 — Historical Trending

**Status:** planned
**Mode:** Slice (new module)
**Gate:** `scripts/generate_outputs.py --compare output/prev_run/` produces `trend.json`
showing delta in dead code count, PDT cost, and drift between two runs.

### Problem
Strata produces a point-in-time snapshot. Teams want to know: is our dead code growing
or shrinking? Did the cleanup campaign last quarter actually work? Are zombie PDTs coming
back after we killed them?

### Solution
`src/strata/outputs/trend.py` — diffs two `usage_summary.json` files (current vs. prior run):
- Dead code delta (`+3 new / -1 removed`)
- PDT zombie cost delta (`+$12,000/mo since last run`)
- Schema drift delta (`+2 new hits / -1 resolved`)
- Explore count delta (net adds and removes)

New artifact: `trend.json`
```json
{
  "period": {"current": "2026-06-06", "prior": "2026-05-07"},
  "dead_code": {"current": 6, "prior": 4, "delta": +2, "new": ["em_legacy_v3.new_dead"], "resolved": []},
  "zombie_cost_usd": {"current": 63750, "prior": 51000, "delta": +12750},
  "schema_drift": {"current": 7, "prior": 5, "delta": +2}
}
```

CLI: `python scripts/generate_outputs.py --compare output/prior_run/ --out output/current_run/`

GH Actions integration: weekly run archives prior output, compares on next run, posts
trend delta to Slack ("Dead explores grew by 2 this week — new: ...").

**Files:**
- `src/strata/outputs/trend.py` — NEW: `build_trend(current_summary, prior_summary)` → trend dict
- `scripts/generate_outputs.py` — add `--compare` arg, produce `trend.json` when prior provided
- `src/strata/outputs/artifacts.py` — register trend artifact
- `.github/workflows/strata-weekly.yml` — add prior-output caching step (artifact upload/download)
- `src/strata/outputs/notifications.py` — add trend section to Slack block kit payload

**Gate:** Run generate_outputs twice with different fixture sets, `--compare` produces correct
deltas. Slack dry-run includes trend section.

---

## Future Slices (23+, not yet specced)

These are prioritized but not specced — start only after 20–22 are STABLE.

| Slice | Name | Why | Complexity |
|---|---|---|---|
| 23 | dbt integration | Cross-ref dbt schema changes with LookML views; catch drift at source | Medium |
| 24 | Looker Extension panel | Surface cleanup roadmap + cost ledger inside Looker UI | High |
| 25 | Slack governance bot | "What breaks if we drop X?" answered in Slack in real time | Medium |
| 26 | Incremental IR | Re-parse only changed `.lkml` files; critical for repos with 500+ views | High |
| 27 | Content network analysis | Dashboard → explore → view chain; rank dead explores by safe-to-delete score | Medium |
| 28 | Namespace collision detection | Warn when cross-model extends could shadow fields in ambiguous ways | Low |

---

## Agentic Execution Model

Same loop as Track B:
1. Turn 1: `git status -sb && git log -n 5 --oneline && cat conductor/handoff-log.md`
2. Read active slice spec (this document + the slice entry above)
3. Read all files the spec references before touching them
4. Execute → gate → handoff → commit → stop

Stop conditions unchanged: gate fails, spec ambiguous, unexpected state, L0/L1 HTTP call needed.

---

## Verification (sprint complete)

```bash
# All existing gates must still pass
make ci
make ci REPO=tests/lookml/enterprise_mono \
  USAGE=tests/fixtures/enterprise_usage_facts.json \
  SCHEMA=tests/fixtures/enterprise_schema_facts.json

# Slice 20: PR bot
# Push a branch with a LookML change → verify GH comment appears

# Slice 21: Attribution
python scripts/generate_outputs.py --repo tests/lookml/enterprise_mono \
  --usage-fixture tests/fixtures/enterprise_usage_facts.json \
  --schema-fixture tests/fixtures/enterprise_schema_facts.json \
  --out output/enterprise_mono
cat output/enterprise_mono/ownership.json  # must have 6 entries with author fields

# Slice 22: Trending
python scripts/generate_outputs.py --repo tests/lookml/gcs_analytics \
  --usage-fixture tests/fixtures/gcs_usage_facts.json \
  --compare output/prior_gcs/ \
  --out output/gcs_analytics
cat output/gcs_analytics/trend.json  # must show deltas
python scripts/notify.py --artifacts output/enterprise_mono --dry-run  # must include trend + owners
```
