# Playground Guide

Strata ships with offline playgrounds so agents can validate behavior without
Looker, BigQuery, or organization-specific repositories.

## Fixtures

`tests/fixtures` is the smallest structural playground. Use it for parser,
resolver, validation-scope, and verdict-evidence changes.

## gcs_analytics

`tests/lookml/gcs_analytics` is the default Makefile target. It exercises L1
usage, PDT, schema drift, dashboard artifact, and migration-impact surfaces.

Run:

```bash
make ci
```

## enterprise_mono

`tests/lookml/enterprise_mono` is the broadest productionization playground. It
contains 19 models, 34 explores, cross-model extends, legacy clusters, zombie
PDT costs, and schema drift.

Run:

```bash
make ci REPO=tests/lookml/enterprise_mono \
  USAGE=tests/fixtures/enterprise_usage_facts.json \
  SCHEMA=tests/fixtures/enterprise_schema_facts.json
```

## Live Looker

Live Looker is opt-in. Authenticate first:

```bash
python scripts/strata_auth.py login --looker-url https://your-instance.looker.com
```

Then run outputs with `--looker-url`. Offline CI must keep passing without this
configuration.
