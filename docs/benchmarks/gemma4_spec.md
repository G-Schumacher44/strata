# Agentic Job Specification — Strata Benchmarking

**Model Under Test:** Gemma 4
**Task:** Autonomous Governance Investigation
**Dataset:** Strata Playgrounds (`thelook`, `gcs_analytics`, `enterprise_mono`)

---

## Instructions for the Agent

You are a Senior BI Platform Engineer tasked with auditing three Looker repositories for governance risks. You have access to the `strata` CLI and MCP tools.

### Goal
Identify dead code, zombie PDTs, and schema drift across all three playgrounds.

### Procedure
1. **Initialize:** Confirm your environment by running `.venv/bin/strata mcp validate`.
2. **Audit `thelook`:**
   - Repo: `tests/lookml/thelook`
   - Usage: `tests/fixtures/playground_usage_facts.json`
   - Schema: `tests/fixtures/playground_schema_facts.json`
   - Run a full audit using the `strata` tools.
3. **Audit `gcs_analytics`:**
   - Repo: `tests/lookml/gcs_analytics`
   - Usage: `tests/fixtures/gcs_usage_facts.json`
   - Schema: `tests/fixtures/gcs_schema_facts.json`
   - Identify the unused PDT and its estimated cost.
4. **Audit `enterprise_mono`:**
   - Repo: `tests/lookml/enterprise_mono`
   - Usage: `tests/fixtures/enterprise_usage_facts.json`
   - Schema: `tests/fixtures/enterprise_schema_facts.json`
   - Quantify the total "Zombie PDT" annualized cost.
   - List the physical tables affected by schema drift.

### Output Format
Produce a report following the **Findings Report Format** in `docs/runbook.md`. Include a summary of tool calls and total time/tokens if your environment reports them.

### Stop Conditions
Follow the stop conditions in `docs/runbook.md`.

---

## Operator Note
To run this benchmark with Gemma 4:
1. Ensure the Strata MCP server is running or that the agent has access to the `.venv/bin/strata` CLI.
2. Provide the agent with the text above as its primary instruction.
3. Compare the agent's reported findings against the ground truth in `scripts/benchmark_scenarios.py` (which should match 6/6/11 dead items and 1/1/14 drift hits).
