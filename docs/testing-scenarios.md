# Strata Testing Scenarios

Three public scenarios prove the risk surfaces that matter before any live Looker
connection is enabled. All run fully offline — no Looker instance, no BQ credentials.

Full numbers, artifacts, and known gaps: [`docs/testing-findings.md`](./testing-findings.md)

---

## Scenario 1 — Structural (L0)

**What it proves:** LookML parse, graph build, extends/refinement resolution, orphan detection.

```bash
make ci REPO=tests/lookml/thelook \
  USAGE=tests/fixtures/playground_usage_facts.json \
  SCHEMA=tests/fixtures/playground_schema_facts.json
```

**Expected:** 0 resolution errors. Every deterministic verdict has evidence. Validation scope
correctly reports offline tier.

---

## Scenario 2 — Enrichment (L1)

**What it proves:** usage fixtures enrich the IR with dead-code evidence, PDT costs, schema
drift, and period metadata without any live dependency.

```bash
make ci
# default target = gcs_analytics + gcs usage/schema fixtures
```

**Expected:** 8 output artifacts under `output/gcs_analytics/`:
`catalog`, `usage_summary`, `dead_code_register`, `pdt_ledger`, `schema_drift`,
`migration_impact`, `cleanup_roadmap`, `validation_scope`.

4 dead items (2 explores, 2 orphan views), 1 unused PDT ($156/30d), 1 schema drift hit.

---

## Scenario 3 — Enterprise G4

**What it proves:** cross-model extends chains, zombie PDT cost visibility, schema drift
across legacy views, legacy connection clusters, and dead-explore detection at scale.

```bash
make ci REPO=tests/lookml/enterprise_mono \
  USAGE=tests/fixtures/enterprise_usage_facts.json \
  SCHEMA=tests/fixtures/enterprise_schema_facts.json
```

**Expected:**
- 34 explores across 19 models, 0 resolution errors
- 6 dead explores (3 legacy_redshift + 2 zombie-backer + 1 broken connection)
- Zombie PDTs: $63,750/30d (~$765K/year), backed by dead explores
- 7 real schema drift hits across 3 legacy views
- 3 known CTE false positives labeled `missing_table` (not `missing_column`)

Run scenario assertions directly:
```bash
python scripts/check_strata.py \
  --repo tests/lookml/enterprise_mono \
  --usage-fixture tests/fixtures/enterprise_usage_facts.json \
  --schema-fixture tests/fixtures/enterprise_schema_facts.json
```
