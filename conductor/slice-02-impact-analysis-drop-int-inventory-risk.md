# Slice 02: Impact Analysis: Drop int_inventory_risk

Date: 2026-06-09
Status: active
Brick: 2
Depends: none

```yaml
conductor_mode: slice
context_budget: low
handoff_required: true
stable_tag_required: false
```

## Objective

Assess the blast radius of dropping the `gcs-automation-project.silver.int_inventory_risk` BigQuery table.

## Scope

- **L3 (Governance)** — Impact assessment.

## Findings

The `strata_impact` tool identified the following downstream dependencies for `gcs-automation-project.silver.int_inventory_risk`:

### Views Affected (2)
- `int_inventory_risk`
- `legacy_inventory_snapshot`

### Explores Affected (4)
- `em_legacy_v1.legacy_inventory`
- `em_ops_reporting.products_ops`
- `em_products_base.products`
- `em_products_base.sales_ops`

### Fields Affected (20)
Total of 20 fields across the two views, including `avg_attention_score`, `total_locked_capital`, and `risk_tier`.

## Recommendation

The table should not be dropped until the legacy views and the corresponding explores are decommissioned or updated to a new source.

## Acceptance Criteria

- [x] Blast radius identified using `strata_impact`.
- [x] Affected nodes listed in slice.
- [x] Handoff written.
- [ ] `conductor/handoff-log.md` — STABLE entry with Commit: hash
