# Offline-First Walkthrough

Strata can run end-to-end without live Looker access.

## Local Setup

```bash
pip install -e ".[dev]"
strata check \
  --repo tests/lookml/gcs_analytics \
  --usage-fixture tests/fixtures/gcs_usage_facts.json \
  --schema-fixture tests/fixtures/gcs_schema_facts.json
```

Artifacts are written under `output/<repo-name>/`.

## Analyze A Playground

```bash
strata outputs \
  --repo tests/lookml/enterprise_mono \
  --usage-fixture tests/fixtures/enterprise_usage_facts.json \
  --schema-fixture tests/fixtures/enterprise_schema_facts.json \
  --out output/enterprise_mono
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
strata auth login --looker-url https://your-instance.looker.com
strata outputs --repo /path/to/lookml --looker-url https://your-instance.looker.com --out output/live
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

---

[← Strata README](../README.md) · [Docs index](./README.md)
