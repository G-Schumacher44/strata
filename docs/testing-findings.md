# Strata Testing Findings

Verified: 2026-06-06. All numbers sourced from actual output artifacts.

---

## Playground Matrix

| | thelook | gcs_analytics | enterprise_mono |
|---|---|---|---|
| **Purpose** | Parser + resolver baseline | L1 enrichment + drift | Enterprise stress test |
| **Models** | 1 | 3 | 19 |
| **Explores** | ~9 | 7 | 34 |
| **PDTs** | 0 | 2 | 5 |
| **Connection** | thelook | gcs-automation-project | gcs-automation-project + 2 legacy |
| **Cross-model extends** | No | No | Yes |
| **Schema fixtures** | No | Yes | Yes |
| **Legacy clusters** | No | No | Yes (3 decommissioned models) |
| **Zombie PDTs** | No | No | Yes |

---

## CI Results — All Playgrounds

| Playground | Tests | validate.py | Scenario gates | Replay | Outputs |
|---|---|---|---|---|---|
| thelook | 44 / 44 ✅ | 10 / 10 ✅ | ✅ | ✅ | ✅ |
| gcs_analytics | 44 / 44 ✅ | 10 / 10 ✅ | ✅ | ✅ | ✅ |
| enterprise_mono | 44 / 44 ✅ | 10 / 10 ✅ | ✅ | ✅ | ✅ |

Period: 2026-05-07 → 2026-06-06 (30 days)

---

## L1 Findings — gcs_analytics

### Usage

| Metric | Value |
|---|---|
| Total queries (30d) | 1,975 |
| Active explores | 5 |
| Dead explores | 2 |
| Orphan views | 2 |
| Schema drift hits | 1 |

### Dead Code Register

| Item | Kind | Reason |
|---|---|---|
| `gcs_legacy.legacy_inventory` | explore | 0 queries |
| `gcs_legacy.legacy_orders` | explore | 0 queries |
| `orphaned_demand_forecast` | view | no explore base / join / ancestor |
| `pdt_retention_signals` | view | no explore / content usage |

### PDT Ledger

| PDT | Builds/30d | Cost/30d | Status | Backed by |
|---|---|---|---|---|
| pdt_customer_ltv | 30 | $28.00 | active | gcs_analytics.customers |
| pdt_retention_signals | 30 | $156.00 | **unused** | (no explores) |
| **Total** | | **$184.00** | | |

`pdt_retention_signals` is structurally defined but no explore references it — dead view + running PDT.

---

## L1 Findings — enterprise_mono

### Usage

| Metric | Value |
|---|---|
| Total queries (30d) | 14,242 |
| Active explores | 28 |
| Dead explores | 6 |
| Schema drift hits (real) | 7 |
| Schema drift hits (CTE false positive) | 3 |
| Models | 19 |
| Legacy/decommissioned models | 3 |

### Dead Explore Register

| Explore | Model | Connection | Reason |
|---|---|---|---|
| dead_finance_v2 | em_legacy_v2 | gcs-automation-project | 0 queries (zombie PDT backer) |
| dead_orders_v2 | em_legacy_v2 | gcs-automation-project | 0 queries (zombie PDT backer) |
| legacy_customers | em_legacy_v1 | legacy_redshift | decommissioned |
| legacy_inventory | em_legacy_v1 | legacy_redshift | decommissioned |
| legacy_orders | em_legacy_v1 | legacy_redshift | decommissioned |
| migration_orders | em_legacy_migration | legacy_warehouse_v1 | broken connection |

### PDT Ledger

| PDT | Builds/30d | Bytes | Cost/30d | Status | Backed by |
|---|---|---|---|---|---|
| pdt_attribution_full_funnel | 180 | 7.2 PB | **$45,000.00** | zombie | dead_finance_v2 |
| pdt_customer_value_score | 120 | 3.0 PB | **$18,750.00** | zombie | dead_orders_v2 |
| pdt_regional_kpi | 60 | 192 GB | $1.20 | active | 6 explores |
| pdt_sales_velocity | 90 | 504 GB | $3.15 | active | 3 explores |
| pdt_cohort_retention | 30 | 255 GB | $1.59 | active | customers_ds |

```
Zombie PDT cost (30d):  $63,750.00
Active PDT cost (30d):      $5.94
────────────────────────────────
Zombie annualized:     ~$765,000
```

Both zombie PDTs are backed exclusively by dead explores — the explore was never deleted, so the PDT keeps rebuilding on schedule.

### Schema Drift — Real Hits (7)

| View | Table | Dropped Column | Fields Affected |
|---|---|---|---|
| legacy_order_detail | silver.int_attributed_purchases | unit_cost_usd | regional_gross_margin, total_unit_cost, unit_cost |
| legacy_customer_profile | silver.int_customer_retention_signals | customer_status_v1 | legacy_status |
| legacy_customer_profile | silver.int_customer_retention_signals | segment_score_v1 | segment_score |
| legacy_inventory_snapshot | silver.int_inventory_risk | reorder_threshold | reorder_threshold |
| legacy_inventory_snapshot | silver.int_inventory_risk | warehouse_zone | warehouse_zone |

### Schema Drift — Known False Positives (3)

| Record | Kind | Source | Why |
|---|---|---|---|
| clv_base | missing_table | pdt_customer_value_score | CTE name picked up by `_sql_upstreams()` regex |
| enriched | missing_table | pdt_customer_value_score | CTE name picked up by `_sql_upstreams()` regex |
| scored | missing_table | pdt_customer_value_score | CTE name picked up by `_sql_upstreams()` regex |

**Root cause:** `_sql_upstreams()` uses a regex over raw PDT SQL to extract `FROM` / `JOIN` targets. Nested CTEs satisfy the pattern but are not physical tables. Fix requires SQL AST parsing; documented as known limitation until lineage parsing is deeper than regex.

### Cross-Model Extends — Verified

| Extends chain | resolution_chain | Errors |
|---|---|---|
| customers_us (em_analytics_us) | `['customers', 'customers_us']` | 0 |
| finance_eu (em_analytics_eu) | `['finance', 'finance_eu']` | 0 |
| 32 other extends | correct | 0 |

34 explores across 19 models. 0 resolution errors. Extends chains resolve correctly via `rglob("*.lkml")` across all model files.

---

## Output Artifacts (per playground run)

| Artifact | Content |
|---|---|
| catalog.json | Full explore/view/field inventory |
| usage_summary.json | Query counts, dead/active totals, period metadata |
| dead_code_register.json | Dead explores + orphan views with dual evidence |
| pdt_ledger.json | All PDTs, build counts, costs, explore backers, status |
| schema_drift.json | Missing column/table hits with field → table → source traceability |
| migration_impact.json | Blast radius per explore (fields, joins, content) |
| cleanup_roadmap.json | Prioritized cleanup steps with cost/risk labels |
| validation_scope.json | What was and wasn't validated, offline tier, fixture period |

8 artifacts per run. All deterministic — same fixtures produce identical output.

---

## Agentic Haiku Test

Haiku (`claude-haiku-4-5`) was given only: working directory, task description, and a pointer to the runbook. No step-by-step instructions embedded in the prompt.

| Playground | Tokens | Tool Calls | Wall Time | Result |
|---|---|---|---|---|
| gcs_analytics | 14,741 | 3 | 14s | PASS |
| thelook | 15,748 | 4 | 19s | PASS |
| enterprise_mono | 15,095 | 4 | 22s | PASS |
| **Total (parallel)** | **45,584** | **11** | **22s** | **3 / 3** |

Haiku read the runbook, self-navigated the make targets and fixture paths, and reported results correctly. The conductor docs are clear enough for the smallest model to operate autonomously.

**Token breakdown estimate per run:**
```
Runbook read:        ~3,000
make ci output:      ~8,000
check_strata output: ~2,000
Response format:     ~2,000
─────────────────────────
Total per agent:    ~15,000
```

If runbook read is skipped (pure CI mode), ~12K tokens per playground is achievable.

---

## Risk Surface Coverage

| Risk | thelook | gcs_analytics | enterprise_mono |
|---|---|---|---|
| Parse + resolve (L0) | ✅ | ✅ | ✅ |
| Extends chain resolution | partial | partial | ✅ cross-model |
| Orphan view detection | — | ✅ | — |
| Dead explore detection | — | ✅ | ✅ (6) |
| PDT cost tracking | — | ✅ | ✅ |
| Zombie PDT detection | — | partial | ✅ |
| Schema drift (column) | — | ✅ | ✅ (7 real) |
| Schema drift (CTE FP) | — | — | ✅ documented |
| Cross-model extends | — | — | ✅ |
| Legacy connection clusters | — | — | ✅ |
| Decommissioned model detection | — | — | ✅ |
| Multi-model namespace collision risk | — | — | ✅ |

---

## Known Gaps

| Gap | Status | Mitigation |
|---|---|---|
| CTE false positives in schema drift | documented | SQL AST parsing needed; 3 FPs clearly labeled `missing_table` not `missing_column` |
| Live Looker smoke | external gate pending | OAuth client registration + test instance URL required |
| `pdt_retention_signals` — unused flag vs. dead flag | correct behavior | PDT is defined but view has no explore backer; surfaces as unused PDT + dead view independently |
| thelook has no schema fixture | by design | thelook is a structural-only playground; L1 schema drift not exercised there |
