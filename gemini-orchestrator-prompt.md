# Gemini Orchestrator — Strata Flash Agent Test

You are orchestrating a multi-agent governance test of the Strata codebase.

Repo: clone from main branch of this repo.

---

## Step 1 — Create a test branch

```bash
git checkout main
git checkout -b test/gemini-flash-$(date +%Y%m%d)
```

---

## Step 2 — Spawn 3 parallel agents

Use your cheapest/fastest available model. One agent per playground.
Agents do NOT communicate with each other.

**Agent task template** (fill in PLAYGROUND and SCHEMA_FLAG per assignment below):

```
Working dir: <repo root>
Environment: .venv is already set up — use .venv/bin/python directly, 
no install step needed.

Rules:
- Read ONLY skills/strata_schema_refresh.md (Agentic Loop section)
- Run ONLY the two commands listed below
- Do NOT read any other files
- Do NOT explore the codebase
- Do NOT run any command not listed here
- Return numbers only — no creative problem solving

1. Run dry-run schema refresh:
     .venv/bin/python scripts/generate_schema_facts.py \
       --repo tests/lookml/PLAYGROUND \
       --out /tmp/PLAYGROUND_schema.json \
       SCHEMA_FLAG \
       --dry-run
2. Run full governance loop:
     .venv/bin/python scripts/test_mcp_live.py --playground PLAYGROUND
3. Report back:
     - Physical table count (total / queryable / skipped)
     - Dead code count and kinds (explore vs view)
     - Schema drift count
     - PASS or FAIL
     - Wall clock time if token counts unavailable
```

**Playground assignments:**

| Agent | PLAYGROUND | SCHEMA_FLAG |
|---|---|---|
| 1 | thelook | *(omit — no schema fixture)* |
| 2 | gcs_analytics | `--existing tests/fixtures/gcs_schema_facts.json` |
| 3 | enterprise_mono | `--existing tests/fixtures/enterprise_schema_facts.json` |

---

## Step 3 — Collect and validate

Aggregate all 3 agent reports. Compare against expected baselines:

| Playground | Physical tables | Dead code | Schema drift |
|---|---|---|---|
| thelook | 1 (CTE-only, 0 queryable) | 6 | 1 |
| gcs_analytics | 11 (all queryable) | 6 | 1 |
| enterprise_mono | 12 (all queryable) | 11 | 14 |

Flag any deviation from expected counts as an anomaly.

Report:
- Token count and tool calls per agent (if available)
- Per-playground pass/fail
- Overall verdict
- Any navigation issues or unexpected agent behavior

---

## Constraints

- Do not push the branch
- Do not modify any source files
- Agents read skills and run scripts only — no editing
