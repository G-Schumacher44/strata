# Strata Testing Scenarios

Strata keeps its core gates offline and deterministic. The public scenarios are
designed to prove the three risk surfaces that matter before any live Looker
connection is enabled.

## Structural L0

Purpose: prove LookML parse, graph build, extends/refinement resolution, and
orphan detection.

Gate:

```bash
make ci REPO=tests/fixtures \
  USAGE=tests/fixtures/usage_facts.json \
  SCHEMA=tests/fixtures/schema_facts_drift.json
```

Expected behavior: no resolution errors; validation scope includes the customer
and PDT scope explores; every deterministic verdict has evidence.

## Enrichment L1

Purpose: prove usage fixtures enrich the IR with dead-code evidence, PDT costs,
schema drift, and period metadata without any live dependency.

Gate:

```bash
make ci
```

Expected behavior: `gcs_analytics` produces catalog, usage summary, dead-code,
PDT ledger, schema drift, migration impact, cleanup roadmap, and validation-scope
artifacts under `output/gcs_analytics`.

## Enterprise G4

Purpose: stress cross-model extends, zombie PDT cost visibility, schema drift,
legacy connections, and dead-explore clusters.

Gate:

```bash
make ci REPO=tests/lookml/enterprise_mono \
  USAGE=tests/fixtures/enterprise_usage_facts.json \
  SCHEMA=tests/fixtures/enterprise_schema_facts.json
```

Expected behavior: 34 explores, 6 dead-code records, 5 PDT ledger rows with
`$63,755.94` 30-day cost, and 10 schema-drift records. Three drift records are
known CTE false positives from PDT SQL regex extraction and remain documented
until SQL lineage parsing is deeper than regex.
