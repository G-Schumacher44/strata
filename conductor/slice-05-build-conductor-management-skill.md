# Slice 05: Build Conductor Management Skill

Date: 2026-06-09
Status: stable
Phase: Governance Tooling
Depends: slice-04

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Currently, AI agents use the CLI to generate slices but lack formal instructions on *how to think* about composing those slices or managing the Conductor workflow (e.g., scoping, implementation ordering, updating `index.md`, when to use master plans). This slice creates a formal `conductor_manager` skill to give agents a rigorous playbook for executing governance tasks.

## Scope

- New skill directory: `src/strata/skills/governance/conductor_manager/`
- New skill file: `src/strata/skills/governance/conductor_manager/SKILL.md`

## Implementation Order

1. **Create Skill Scaffold**: Create the directory and `SKILL.md` using the standard `SKILL_TEMPLATE.md`.
2. **Define Triggers**: Specify triggers like "Start a new slice for...", "Update the active slice", or "Help me plan a cross-cutting change".
3. **Define Procedure**: Document the step-by-step process for an agent to:
   - Use `strata conductor new-slice`
   - Apply `[JUDGMENT]` to bound the scope strictly to one architectural layer.
   - Define a Hard Constraint for correctness.
   - Update `conductor/index.md` active pointers and Phase (formerly Brick) tracking tables.
4. **Define Outputs**: Structure how the agent should present the drafted slice back to the user for review before considering the spec "stable".

## The Hard Constraint

The skill must explicitly instruct the agent to enforce the "Spec Before Build" rule. The agent must never write code to implement a slice in the same conversational turn that it drafts the slice.

## Acceptance Criteria

- [x] `src/strata/skills/governance/conductor_manager/SKILL.md` exists and follows the exact template format.
- [x] The skill procedure explicitly covers slices, phases, and master-plans.
- [x] The skill explicitly mandates updating `conductor/index.md`.
- [x] `conductor/handoff-log.md` — STABLE entry with Commit: hash
