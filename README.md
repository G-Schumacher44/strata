# Strata

**GS Analytics // Strata** — a deterministic, governed framework for mapping, auditing,
and protecting a LookML monorepo.

> Do the heavy lifting deterministically; use AI as a thin, cheap garnish.

Parsing, dependency graphing, dead-code detection, and PDT cost analysis are deterministic
problems. They cost zero tokens. The LLM only touches a synthesis layer over pre-digested
structure — cheap model, tiny clean context, competent output. Gets cheaper over time.

## Architecture

```
repo clone (read-only) ──▶ [L0 IR] ──▶ [L1 usage+cost] ──▶ [L2 synthesis]
live instance (RO MCP) ──────────────────▲
                          [Conductor governance wraps L2]
                          [CI gate reuses L0 + validate]
                          [MCP repo-brain exposes L0–L1 to IDE]
```

- **L0 — Deterministic IR:** Parse entire repo → canonical node/edge graph. No LLM.
- **L1 — Usage enrichment:** Join IR against Looker System Activity. No LLM. (Optional; requires live connection)
- **L2 — Synthesis:** One explore = one slice = one cheap-model verdict with evidence.
- **CI gate:** L0 + validate.py as a PR check — flags orphans, broken extends, dead PDTs.
- **MCP repo-brain:** L0–L1 exposed as read-only IDE tools (stdio, local only).

## Brick Status

| Brick | Name | Status |
|---|---|---|
| 0 | Design doc (thesis / intent / outline) | ✅ STABLE |
| 1 | Generic IR extractor (L0) | 🔲 QUEUED |
| 2 | Usage + cost enrichment (L1) | planned |
| 3 | Synthesis skills + Conductor (L2/L3) | planned |
| 4 | CI suite | planned |
| 5 | MCP repo-brain + output artifacts | planned |

## Getting Started

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
python scripts/validate.py
```

## License

Apache 2.0 — see LICENSE (forthcoming via org sanctioned pathway).
