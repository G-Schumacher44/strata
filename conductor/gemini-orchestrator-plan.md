# Gemini Orchestrator Test Plan

## Objective
Orchestrate a multi-agent governance test of the Strata codebase across three different playgrounds (`thelook`, `gcs_analytics`, `enterprise_mono`), aggregate the results, and validate them against expected baselines.

## Background & Motivation
This test validates the ability of highly constrained ("dumb") agents to execute specific workflow scripts without deviation and report precise metrics. The orchestrator (Gemini CLI) is responsible for delegating the tasks, collecting the outputs, and evaluating the final state against the truth values provided in the prompt.

## Scope & Impact
- The operation is entirely read-only regarding source code (no edits will be made).
- Three parallel sub-agents (`generalist`) will be spawned to run the validation scripts.
- A new git branch will be created locally.
- The `.venv` is assumed to be ready, avoiding installation steps.

## Implementation Steps

### Phase 1: Environment Setup
1. Exit Plan Mode.
2. Ensure the working directory is on the `main` branch.
3. Create and check out a new branch: `test/gemini-flash-$(date +%Y%m%d)`.

### Phase 2: Parallel Agent Execution
Spawn three parallel `generalist` sub-agents using the `invoke_agent` tool. Each agent will be provided with the strict ruleset defined in the prompt.

**Agent 1: thelook**
- Playground: `thelook`
- Schema Flag: (omitted)

**Agent 2: gcs_analytics**
- Playground: `gcs_analytics`
- Schema Flag: `--existing tests/fixtures/gcs_schema_facts.json`

**Agent 3: enterprise_mono**
- Playground: `enterprise_mono`
- Schema Flag: `--existing tests/fixtures/enterprise_schema_facts.json`

**Agent Prompt Template:**
```text
Working dir: /Volumes/t9/dev/tools/strata
Environment: .venv is already set up — use .venv/bin/python directly, no install step needed.

Rules:
- Read ONLY skills/strata_schema_refresh.md (Agentic Loop section)
- Run ONLY the two commands listed below
- Do NOT read any other files
- Do NOT explore the codebase
- Do NOT run any command not listed here
- Return numbers only — no creative problem solving

1. Run dry-run schema refresh:
     .venv/bin/python scripts/generate_schema_facts.py \
       --repo tests/lookml/[PLAYGROUND] \
       --out /tmp/[PLAYGROUND]_schema.json \
       [SCHEMA_FLAG] \
       --dry-run
2. Run full governance loop:
     .venv/bin/python scripts/test_mcp_live.py --playground [PLAYGROUND]
3. Report back:
     - Physical table count (total / queryable / skipped)
     - Dead code count and kinds (explore vs view)
     - Schema drift count
     - PASS or FAIL
     - Note the start and end time of your execution to provide Wall clock time if token counts unavailable.
```

### Phase 3: Collection and Validation
1. Await the results from all three sub-agents.
2. Aggregate the reports into a final summary.
3. Compare the reported numbers against the expected baselines:
   - **thelook**: Physical (1 CTE-only, 0 queryable), Dead code (5), Schema drift (0)
   - **gcs_analytics**: Physical (11 all queryable), Dead code (4), Schema drift (1)
   - **enterprise_mono**: Physical (12 all queryable), Dead code (11), Schema drift (14)
4. Flag any anomalies or deviations from the expected counts.
5. Generate the final report detailing pass/fail status per playground, the overall verdict, and any observed issues.

## Verification
- The final report will be presented to the user in the chat interface.
- No files will be modified, ensuring safety constraints are met.
