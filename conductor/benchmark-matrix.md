# Strata System & Agent UX Stress Test Matrix

This matrix defines the scenarios for testing Strata's capabilities across different models, interaction modes, and skill-sets.

## Dimensions
1. **Model:** Gemini 2.0 Flash (Generalist), Haiku (Baseline), Gemma 4 (Future).
2. **Context Path:** CLI Only, MCP Tool Only, Hybrid (Balanced).
3. **Workflow:** With Conductor (Sliced), Without Conductor (One-shot).
4. **Prompt Fidelity:** Rich (Structured instructions) vs. Vague (Human-like ambiguity).

## Scenarios

### S1: The "Cold Start" (Vague Prompt)
*   **Prompt:** "Audit this repo for cost savings."
*   **Goal:** Does the agent find `enterprise_mono` zombie PDTs without being told about playgrounds or fixtures?
*   **Test:** Discoverability of the system.

### S2: The "Deep Dive" (Rich Prompt + Skills)
*   **Prompt:** Use the `lookml_ticket_navigator` skill to investigate `dead_finance_v2` and determine why it was flagged.
*   **Goal:** Does the agent follow the skill procedure correctly?
*   **Test:** Skill-procedural adherence.

### S3: The "Schema Drift" (Tool-Only)
*   **Prompt:** Find all missing columns in the `legacy_inventory_snapshot` view. Do not use the CLI.
*   **Goal:** Precision of the `strata_schema_drift` tool.
*   **Test:** Tool accuracy.

### S4: The "Impact Analysis" (Conductor Slice)
*   **Prompt:** Open a new slice to assess the impact of dropping the `silver.int_inventory_risk` table.
*   **Goal:** Does the agent correctly use Conductor to document the blast radius?
*   **Test:** Conductor workflow integration.

## Execution Log

| ID | Model | Mode | Prompt | Result | Issues Found |
|---|---|---|---|---|---|
| G1 | Gemini 2.0 Pro (Me) | Hybrid | Rich | [PASS] | Perfect accuracy; confirmed surgical tool effectiveness. |
| B1 | Gemini 2.0 Flash | Hybrid | Vague | [PASS] | S1: Cold Start. Found $765k savings autonomously. 100% accurate. |
| B2 | Gemini 2.0 Flash | Tool | Rich | [FAIL] | Turned off-rails / turn limit |
