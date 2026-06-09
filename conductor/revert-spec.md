# Plan: Revert Benchmark Spec to Balanced Mode

## Objective
Revert `docs/benchmarks/gemma4_spec.md` to its last committed state (balanced mode) after testing "Hard Mode" with the sub-agent.

## Changes
- Run `git restore docs/benchmarks/gemma4_spec.md` to revert the unstaged "Hard Mode" changes.

## Verification
- Run `git status` to ensure the workspace is clean.
- Read `docs/benchmarks/gemma4_spec.md` to confirm it contains the balanced instructions.
