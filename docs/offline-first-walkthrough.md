# Offline-First Walkthrough

Strata can run end-to-end without live Looker access.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make ci
```

Artifacts are written under `output/<repo-name>/`.

## Analyze A Playground

```bash
make ci REPO=tests/lookml/enterprise_mono \
  USAGE=tests/fixtures/enterprise_usage_facts.json \
  SCHEMA=tests/fixtures/enterprise_schema_facts.json
```

Then inspect:

- `usage_summary.json`
- `dead_code_register.json`
- `pdt_ledger.json`
- `schema_drift.json`
- `cleanup_roadmap.json`

## Live Tier

Live Looker is an optional L1 fact source:

```bash
python scripts/strata_auth.py login --looker-url https://your-instance.looker.com
python scripts/generate_outputs.py --repo /path/to/lookml --looker-url https://your-instance.looker.com --out output/live
```

If no token is configured, the live path fails fast and offline fixtures continue
to work.

## Capability Tiers

| Tier | Input | Network | Use |
|---|---|---|---|
| L0 | LookML clone | none | Parse, resolve, dependency graph. |
| Fixture L1 | Usage/schema JSON | none | CI and deterministic review. |
| Replay L1 | Sanitized System Activity rows | none | Provider contract testing. |
| Live L1 | Looker OAuth token | Looker API | Manual smoke and production enrichment. |
