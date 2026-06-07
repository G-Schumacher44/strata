# Playground Guide

Strata ships with offline playgrounds so agents can validate behavior without
Looker, BigQuery, or organization-specific repositories.

## Fixtures

`tests/fixtures` is the smallest structural playground. Use it for parser,
resolver, validation-scope, and verdict-evidence changes.

## gcs_analytics

`tests/lookml/gcs_analytics` is the default playground. It exercises L1
usage, PDT, schema drift, dashboard artifact, and migration-impact surfaces.

Run:

```bash
strata check \
  --repo tests/lookml/gcs_analytics \
  --usage-fixture tests/fixtures/gcs_usage_facts.json \
  --schema-fixture tests/fixtures/gcs_schema_facts.json
```

## enterprise_mono

`tests/lookml/enterprise_mono` is the broadest productionization playground. It
contains 19 models, 34 explores, cross-model extends, legacy clusters, zombie
PDT costs, and schema drift.

Run:

```bash
strata check \
  --repo tests/lookml/enterprise_mono \
  --usage-fixture tests/fixtures/enterprise_usage_facts.json \
  --schema-fixture tests/fixtures/enterprise_schema_facts.json
```

## Live Looker

Live Looker is opt-in. Authenticate first:

```bash
strata auth login --looker-url https://your-instance.looker.com
```

Then run outputs with `--looker-url`. Offline CI must keep passing without this
configuration.

---

[← Strata README](../README.md) · [Docs index](./README.md)
