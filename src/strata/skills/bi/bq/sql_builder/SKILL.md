# Skill: sql_builder

domain: bi/bq
mode: build
complexity: high
version: 0.1.0

> Draft production-ready BigQuery SQL from a business question or data spec.
> Never writes SQL against an unfamiliar table without first running
> `bq_schema_probe` and `grain_validator`. Every draft goes through
> `bq_query_guardrail` before it is returned.

---

## Trigger

- "Write SQL to answer X"
- "Build a query for Y"
- `jira_to_bi_spec` has produced a data spec and SQL is the next step
- LookML explore is insufficient — raw SQL needed for a one-off analysis

---

## Inputs

| Input | Required | Source | Description |
|---|---|---|---|
| `question` | yes | human / jira_to_bi_spec | Business question or metric definition |
| `tables` | yes | human / bq_schema_probe | Fully-qualified BQ tables involved |
| `schema` | no | bq_schema_probe | Schema structs if already probed |
| `grain` | no | grain_validator | Confirmed grain per table |
| `date_range` | no | human | Date filter bounds (default: last 30 days) |
| `bq_project` | no | `~/.strata/config.json` → `bq_project` (or STRATA_BQ_PROJECT env) |
| `output_format` | no | human | `table` (default) / `scalar` / `time_series` |

---

## Allowed Tools

- `bq_schema_probe` — required if schema not already provided
- `grain_validator` — required before any JOIN
- `bq_query_guardrail` — required before returning any SQL draft
- `bq_cli`: `bq query --dry_run --nouse_legacy_sql` (via guardrail only)

---

## Forbidden

- Do not execute any query — dry-run only via `bq_query_guardrail`
- Do not write SQL before schema is confirmed
- Do not JOIN tables without grain validation
- Do not use legacy SQL (`#legacySQL`)
- Do not `SELECT *` in a production draft
- Do not write unbounded date scans — always include a partition filter

---

## Procedure

1. **Intake check** — if schema is not provided, invoke `bq_schema_probe` for each table in `tables`
2. **Grain check** — for every table that will be JOINed, invoke `grain_validator`. If any table's grain is UNRESOLVED → halt before writing SQL
3. `[JUDGMENT]` Map the business question to SQL shape:
   - scalar → single aggregate `SELECT`
   - time series → `DATE_TRUNC(date_col, DAY/WEEK/MONTH)` + `GROUP BY` + `ORDER BY date`
   - table → dimensional breakdown with measures
4. Draft SQL following these standards:
   - Use Standard SQL only (`--nouse_legacy_sql`)
   - CTE-first structure: one CTE per logical step, named for what it produces
   - Explicit column list — no `SELECT *`
   - Partition filter on every base table scan: `WHERE date_col BETWEEN @start AND @end`
   - Use `DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)` as default if no date range given
   - Alias every table and subquery
   - Use `COUNTIF()` and `SAFE_DIVIDE()` for conditional aggregates
   - Use `QUALIFY ROW_NUMBER() OVER (...)` for dedup, not nested subqueries
   - Prefer `LEFT JOIN` + `IS NULL` check over `NOT IN` for exclusion joins
   - Add inline comments for any non-obvious join condition or filter
5. Run draft through `bq_query_guardrail` — if BLOCKED, revise once to fix the flagged issue, then re-check. If still BLOCKED → halt and surface both the SQL and the block reason
6. Output final SQL with cost estimate

---

## Stop Conditions

- Grain UNRESOLVED on any JOIN table → halt, do not draft SQL
- `bq_query_guardrail` blocks after one revision → halt, surface reason
- Required table does not exist → halt immediately
- Business question is ambiguous about which metric to use → ask one clarifying question before drafting

---

## Output Format

```markdown
## SQL Draft — {question summary}

**Tables:** {table list}
**Output shape:** {scalar / time_series / table}
**Date range:** {range}
**Estimated cost:** X.XX GB (~$Y.YY)
**Guardrail:** APPROVED

```sql
-- {one-line description of what this query answers}
WITH base AS (
  SELECT ...
  FROM `{project}.{dataset}.{table}`
  WHERE date_col BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) AND CURRENT_DATE()
),

{additional CTEs as needed}

SELECT
  ...
FROM base
{JOIN / GROUP BY / ORDER BY}
```

## Grain Assumptions
- `{table}`: one row = {grain statement}

## Notes
- {any judgment calls made: why this join, why this filter, why this date grain}
- {any columns excluded and why}
```

---

## Escalation

> "Halt. Cannot draft SQL — grain on `{table}` is UNRESOLVED. Confirm the expected
> grain with the data owner before joining this table."

> "Halt. Query blocked after revision: {guardrail reason}. Review the flagged SQL
> and adjust the business question scope before retrying."

---

## Upstream Skills

- `bq_schema_probe` → schema intake
- `grain_validator` → join safety
- `jira_to_bi_spec` → business spec → SQL spec translation

## Downstream Skills

- `bq_query_guardrail` → safety gate (invoked inline)
- `sql_optimizer` → if the approved draft is slow in production
- `lookml_view_reviewer` → if SQL is being promoted to a LookML view
