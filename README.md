# Strata

Strata is a deterministic, governed framework for mapping, auditing, and
protecting a LookML monorepo.

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
- **L1 — Usage enrichment:** Join IR against fixture-backed or live read-only facts. No LLM.
- **L2 — Synthesis:** One explore = one slice = one verdict with evidence.
- **CI gate:** Offline scenario gates — flags broken extends, missing evidence, and dead PDTs.
- **MCP repo-brain:** L0–L1 exposed as read-only IDE tools (stdio, local only).

## Getting Started

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
make ci
```

## Outputs

`make ci` writes JSON artifacts under `output/<repo-name>/`: catalog, dead-code
register, PDT ledger, schema drift, cleanup roadmap, migration impact, validation
scope, and usage summary.

## Live Looker

Offline fixtures are the default. Live Looker/System Activity is opt-in:

```bash
python scripts/strata_auth.py login --looker-url https://your-instance.looker.com
python scripts/generate_outputs.py --repo /path/to/lookml --looker-url https://your-instance.looker.com --out output/live
```

Missing live config fails fast; ordinary CI has no live dependency.

## License

Apache 2.0 intended; see `docs/CONTRIBUTING.md`.
