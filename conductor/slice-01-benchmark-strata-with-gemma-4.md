# Slice 01: Benchmark Strata with Gemma 4

Date: 2026-06-09
Status: stable
Phase: 1
Depends: none

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Establish a benchmarking framework for Gemma 4 (and future models) to verify Strata governance capabilities. This includes a deterministic automation script for ground-truth verification and a structured agentic prompt to test autonomous investigation performance.

## Scope

- **L3 (Governance)** — Benchmarking infrastructure and documentation.
- **Scripts** — `scripts/benchmark_scenarios.py` for automated runs.
- **Documentation** — `docs/benchmarks/gemma4_spec.md` for agentic testing.

## Implementation Order

1. **Automation:** Create `scripts/benchmark_scenarios.py` to run `strata check` and `strata outputs` across all three playgrounds (`thelook`, `gcs_analytics`, `enterprise_mono`).
2. **Standardization:** Create `docs/benchmarks/gemma4_spec.md` containing the "Agentic Job Specification" for Gemma 4.
3. **Validation:** Run the automated benchmark to confirm repo-state compatibility with existing findings.

## The Hard Constraint

The deterministic benchmark must reproduce the exact finding counts (6 dead items in thelook, 14 drift hits in enterprise_mono) documented in `docs/testing-findings.md` to ensure the baseline is stable.

## Acceptance Criteria

- [x] Conductor slice active and documented.
- [x] `scripts/benchmark_scenarios.py` correctly runs all 3 playgrounds.
- [x] `docs/benchmarks/gemma4_spec.md` created with clear prompt and stop conditions.
- [x] Deterministic baseline verified against `docs/testing-findings.md`.
- [x] `conductor/handoff-log.md` — STABLE entry with Commit: hash
