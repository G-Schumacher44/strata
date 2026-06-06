# Strata — Claude Agent Rules

See `AGENTS.md` for the full Conductor rules. This file adds Claude-specific guidance.

## Authority Order
1. `AGENTS.md`
2. `intent.md`
3. `conductor/index.md`
4. active `conductor/slice-*.md`
5. `conductor/handoff-log.md` (latest block when resuming)

## Turn 1 Rule
```
git status -sb && git log -n 5 --oneline && cat conductor/handoff-log.md
```

## Key Constraints
- L0–L1 code must never call any LLM or external API
- lkml is vendored in `src/vendor/lkml/` — do not `pip install lkml`
- MCP server is stdio-only; no HTTP transport, no cloud dependency
- Read-only enforcement is non-negotiable

## Build
```bash
python -m pytest
python scripts/validate.py
```
