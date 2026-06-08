# Skill: lookml_ticket_navigator

domain: bi/lookml
mode: navigate
complexity: low
version: 0.1.0

> Given a ticket anchor (BQ table, field name, explore, view, or .lkml file), build a
> complete navigator brief in one pass — the structured context a downstream skill or
> developer needs to act without exploring the repo blind.

---

## Trigger

- Starting a ticket that touches LookML or a BQ table
- "Where does X live in the repo?"
- "What already exists for field / table / explore Y?"
- Before running `lookml_view_reviewer` or `lookml_explore_join_reviewer`
- Any time an agent would otherwise explore `.lkml` files blind

---

## Inputs

| Input | Required | Source | Description |
|---|---|---|---|
| `anchor` | yes | human | BQ table name, field name, explore name, view name, or `.lkml` filename |
| `ticket_text` | no | human | Jira/GitHub ticket description — used to infer change type |
| `model` | no | human | Model name to narrow scope (omit to search full repo) |

---

## Allowed Tools

- `strata_mcp.strata_find_field` — cross-view field search by name/SQL/tag
- `strata_mcp.strata_view_sources` — view → physical BQ table map
- `strata_mcp.strata_impact` — BQ table → all views/explores/fields that reference it
- `strata_mcp.strata_explore_deps` — explore join graph + base view
- `strata_mcp.strata_query_field` — single field definition (sql, type, tags)
- `strata_mcp.strata_ir_status` — confirm IR loaded, get node counts
- file read: `.lkml` source files named in results (targeted, read-only)

---

## Forbidden

- Do not modify any LookML file
- Do not execute any BQ queries
- Do not call `bq_schema_probe` — that belongs to the downstream skill
- Do not call `lookml_view_reviewer` or `lookml_explore_join_reviewer` — hand off to those

---

## Procedure

**Step 1 — Classify the anchor**

Determine anchor type from its shape:
- Contains `.` and no spaces, matches `project.dataset.table` pattern → `bq_table`
- Ends in `.view.lkml`, `.model.lkml`, `.explore.lkml` → `file`
- Matches `view_name.field_name` (single dot, no slashes) → `field`
- No dots, no slashes, matches a known explore pattern → `explore`
- No dots, no slashes → `view` (default — could be view or explore name)

**Step 2 — Primary lookup (route by anchor type)**

| Anchor type | Primary tool | What it tells you |
|---|---|---|
| `bq_table` | `strata_impact(anchor)` | All views, explores, fields touching this table |
| `field` | `strata_find_field(anchor)` | All views that define a matching field |
| `explore` | `strata_explore_deps(anchor, model)` | Join graph, base view, field count |
| `view` | `strata_view_sources(model=model)` filtered | Physical table, field count |
| `file` | Infer name from filename, then route as view/explore | As above |

If anchor not found → halt and report: "Anchor `{anchor}` not found in IR. Check spelling or run `strata query status` to confirm repo parsed."

**Step 3 — Expand surface area**

For each view surfaced in Step 2:
- Get physical table and field count from `strata_view_sources`
- If field anchor: call `strata_query_field(view, field)` for the top match to get full definition

For each explore surfaced in Step 2:
- Call `strata_explore_deps(explore, model)` to get join graph

Cap at 5 explores and 10 views — flag if truncated.

**Step 4 — Infer change type (if ticket_text provided)**

Scan ticket_text for keywords:
- "add field / add dimension / add measure" → `add_field`
- "add join / join to / new relationship" → `add_join`
- "new view / create view / new derived table" → `new_view`
- "rename / move / migrate" → `rename`
- "remove / drop / delete / deprecate" → `drop`
- No match → `unknown`

**Step 5 — Produce "What to Touch" list**

| Change type | What to touch |
|---|---|
| `add_field` | The view file where the field's source table is already joined |
| `add_join` | The explore's `.model.lkml` or explore file; check if view already exists |
| `new_view` | New `.view.lkml` file + add to relevant explore joins |
| `rename` | The view/field definition + all `${view_name.field_name}` references |
| `drop` | Check dead code register first — use `lookml_explore_join_reviewer` on parent explore |
| `unknown` | List all surfaced files as candidates |

**Step 6 — Emit navigator brief**

---

## Output Format

```markdown
## Navigator Brief — `{anchor}`

**Anchor type:** {bq_table | field | explore | view | file}
**Change type:** {add_field | add_join | new_view | rename | drop | unknown}

## Relevant LookML Nodes

| Node | Kind | File | Physical Table |
|---|---|---|---|
| `orders` | view | `views/orders.view.lkml` | `project.dataset.orders` |
| `order_items` | explore | `models/ecommerce.model.lkml` | — |

## Join Graph (affected explores)

- `order_items` (ecommerce): base=`orders` → joined: [order_facts, users, inventory_items]

## Field Matches (field anchor only)

- `orders.lifetime_value` — measure, `SUM(${TABLE}.revenue)`, tags: [finance]
  source: `views/orders.view.lkml`

## What to Touch

1. **{action}** → `{file}` — {reason}
2. ...

## Hand-off

→ `lookml_view_reviewer` on `{view}` — before deploying any field change
→ `lookml_explore_join_reviewer` on `{explore}` — if a join is new or modified
→ `bq_schema_probe` on `{physical_table}` — if you need schema/grain info

## Truncation Warning (if applicable)

> Results capped at 5 explores / 10 views. Pass `model=` to narrow scope.
```

---

## Stop Conditions

- Anchor not found in IR → halt, report with suggested fix
- IR status shows 0 nodes → halt: "IR appears empty — run `strata build` first"

---

## Examples

See `examples/` for sample inputs and outputs.

---

## Escalation

> "Halt. Anchor `{anchor}` matches {n} explores across {m} models — scope is too broad
> for a safe navigator brief. Provide a `model=` filter or a more specific anchor."
> (Threshold: >5 explores without a model filter)
