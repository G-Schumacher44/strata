"""strata query — field-level LookML inspection from the terminal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click

from strata.config import load_repo_path


@click.group()
def query() -> None:
    """Inspect the LookML IR from the terminal (no AI client needed).

    These are the same tools the MCP server exposes to AI clients —
    available here for scripting, debugging, or quick lookups.

    Repo is resolved from STRATA_REPO_PATH, ~/.strata/config.json, or cwd.
    Pass --usage-fixture to get query counts and PDT cost data.
    """


def _build(
    repo: str | None,
    usage_fixture: str | None,
    schema_fixture: str | None,
):
    from strata.pipeline import build_graph

    _repo = Path(repo).expanduser().resolve() if repo else _repo_path()
    return build_graph(str(_repo), usage_fixture, schema_fixture)


def _repo_path() -> Path:
    return load_repo_path()


_repo_opt = click.option(
    "--repo",
    default=None,
    envvar="STRATA_REPO_PATH",
    show_envvar=True,
    help="LookML repo path (overrides config)",
)
_usage_opt = click.option(
    "--usage-fixture",
    default=None,
    envvar="STRATA_USAGE_FIXTURE",
    show_envvar=True,
    help="Usage facts JSON for query counts + PDT costs",
)
_schema_opt = click.option(
    "--schema-fixture",
    default=None,
    envvar="STRATA_SCHEMA_FIXTURE",
    show_envvar=True,
    help="Schema facts JSON for drift detection",
)


@query.command("field")
@click.argument("view")
@click.argument("field")
@_repo_opt
@_usage_opt
@_schema_opt
def query_field(
    view: str, field: str, repo: str | None, usage_fixture: str | None, schema_fixture: str | None
) -> None:
    """Show a field's full definition: type, SQL, tags, and usage.

    \b
    Example:
      strata query field orders total_revenue
    """
    graph = _build(repo, usage_fixture, schema_fixture)
    from strata.mcp.tools import strata_query_field

    result = strata_query_field(graph, view, field)
    click.echo(json.dumps(result, indent=2, default=str))


@query.command("explore")
@click.argument("explore")
@click.argument("model")
@_repo_opt
@_usage_opt
@_schema_opt
def query_explore(
    explore: str,
    model: str,
    repo: str | None,
    usage_fixture: str | None,
    schema_fixture: str | None,
) -> None:
    """Show an explore's join graph, base view, and field count.

    \b
    Example:
      strata query explore orders enterprise
    """
    graph = _build(repo, usage_fixture, schema_fixture)
    from strata.mcp.tools import strata_explore_deps

    result = strata_explore_deps(graph, explore, model)
    click.echo(json.dumps(result, indent=2, default=str))


@query.command("orphans")
@click.option(
    "--kind",
    default="all",
    type=click.Choice(["all", "explore", "view", "field"]),
    show_default=True,
    help="Filter by node kind",
)
@_repo_opt
@_usage_opt
@_schema_opt
def query_orphans(
    kind: str, repo: str | None, usage_fixture: str | None, schema_fixture: str | None
) -> None:
    """List orphaned explores, views, or fields with no live dependencies."""
    graph = _build(repo, usage_fixture, schema_fixture)
    from strata.mcp.tools import strata_list_orphans

    result = strata_list_orphans(graph, kind)
    click.echo(json.dumps(result, indent=2, default=str))


@query.command("impact")
@click.argument("physical_table")
@_repo_opt
@_usage_opt
@_schema_opt
def query_impact(
    physical_table: str, repo: str | None, usage_fixture: str | None, schema_fixture: str | None
) -> None:
    """Show every view, explore, and field affected by a physical table change.

    Use before dropping a BQ column or renaming a table.

    \b
    Example:
      strata query impact acme-data.analytics.orders
    """
    graph = _build(repo, usage_fixture, schema_fixture)
    from strata.mcp.tools import strata_impact

    result = strata_impact(graph, physical_table)
    click.echo(json.dumps(result, indent=2, default=str))


@query.command("scope")
@click.argument("files", nargs=-1, required=True)
@_repo_opt
@_usage_opt
@_schema_opt
def query_scope(
    files: tuple[str, ...], repo: str | None, usage_fixture: str | None, schema_fixture: str | None
) -> None:
    """Show which explores are impacted by a set of changed .lkml files.

    Use before merging a PR to know what needs revalidation.

    \b
    Example:
      strata query scope views/orders.view.lkml views/users.view.lkml
    """
    graph = _build(repo, usage_fixture, schema_fixture)
    from strata.mcp.tools import strata_validation_scope

    def _file_to_changed(f: str) -> str:
        stem = Path(f).name
        if ".view." in stem:
            return f"view:{stem.split('.view.')[0]}"
        if ".model." in stem:
            return f"model:{stem.split('.model.')[0]}"
        if ".explore." in stem:
            return f"explore:{stem.split('.explore.')[0]}"
        return f"view:{Path(f).stem}"

    result = strata_validation_scope(graph, [_file_to_changed(f) for f in files])
    click.echo(json.dumps(result, indent=2, default=str))


@query.command("find-field")
@click.argument("query")
@click.option(
    "--kind",
    default="all",
    type=click.Choice(["all", "dimension", "measure", "filter", "parameter"]),
    show_default=True,
    help="Restrict results to a specific field kind",
)
@_repo_opt
@_usage_opt
@_schema_opt
def query_find_field(
    query: str,
    kind: str,
    repo: str | None,
    usage_fixture: str | None,
    schema_fixture: str | None,
) -> None:
    """Search all views for fields matching a name, SQL fragment, or tag.

    Use before adding a field to check if it already exists somewhere in the repo.

    \b
    Example:
      strata query find-field "lifetime_value"
      strata query find-field "orders" --kind measure
    """
    graph = _build(repo, usage_fixture, schema_fixture)
    from strata.mcp.tools import strata_find_field

    result = strata_find_field(graph, query, kind)
    click.echo(json.dumps(result, indent=2, default=str))


@query.command("view-sources")
@click.option("--model", default=None, help="Restrict to views reachable from a specific model")
@_repo_opt
@_usage_opt
@_schema_opt
def query_view_sources(
    model: str | None,
    repo: str | None,
    usage_fixture: str | None,
    schema_fixture: str | None,
) -> None:
    """List all views with their physical BQ table and field counts.

    Use to find which view wraps a given BQ table, or to get a full view inventory.

    \b
    Example:
      strata query view-sources
      strata query view-sources --model ecommerce
    """
    graph = _build(repo, usage_fixture, schema_fixture)
    from strata.mcp.tools import strata_view_sources

    result = strata_view_sources(graph, model)
    click.echo(json.dumps(result, indent=2, default=str))


@query.command("navigate")
@click.argument("anchor")
@click.option("--model", default=None, help="Narrow scope to a specific model")
@click.option("--ticket", default=None, help="Ticket description — infers change type")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Emit structured JSON instead of formatted text",
)
@_repo_opt
@_usage_opt
@_schema_opt
def query_navigate(
    anchor: str,
    model: str | None,
    ticket: str | None,
    as_json: bool,
    repo: str | None,
    usage_fixture: str | None,
    schema_fixture: str | None,
) -> None:
    """Build a navigator brief for a ticket anchor — no agent needed.

    Classifies the anchor (BQ table, field, view, explore, or .lkml file),
    runs the right lookups, and prints a readable brief showing what exists
    and what to touch.

    \b
    Examples:
      strata query navigate "revenue"
      strata query navigate "project.dataset.orders"
      strata query navigate "orders" --model ecommerce
      strata query navigate "user_id" --ticket "add user region dimension"
    """
    from strata.mcp.tools import (
        strata_explore_deps,
        strata_find_field,
        strata_impact,
        strata_view_sources,
    )

    graph = _build(repo, usage_fixture, schema_fixture)
    brief = _build_navigate_brief(
        graph,
        anchor,
        model,
        ticket,
        strata_find_field,
        strata_impact,
        strata_view_sources,
        strata_explore_deps,
    )

    if as_json:
        click.echo(json.dumps(brief, indent=2, default=str))
        return

    if "error" in brief:
        click.echo(f"Not found: {brief['error']}")
        return

    click.echo(f"\nNavigator Brief — {anchor!r}")
    click.echo(f"Anchor type: {brief['anchor_type']}\n")

    if brief.get("field_matches"):
        click.echo(f"Field matches ({len(brief['field_matches'])}):")
        for m in brief["field_matches"][:15]:
            label = f"  [{m['label']}]" if m.get("label") else ""
            click.echo(
                f"  {m['view']}.{m['field']:<30}  {m['type']:<12}  {m['source_file']}{label}"
            )

    if brief.get("bq_fields"):
        fields = brief["bq_fields"]
        click.echo(f"Fields ({min(len(fields), 10)} of {len(fields)}):")
        for f in fields[:10]:
            click.echo(f"  {f}")

    if brief.get("views"):
        click.echo(f"\nViews ({len(brief['views'])}):")
        for v in brief["views"]:
            pt = v.get("physical_table") or "—"
            click.echo(f"  {v['name']:<30}  →  {pt}  ({v.get('field_count', '?')} fields)")
            if v.get("source_file"):
                click.echo(f"    {v['source_file']}")

    if brief.get("explores"):
        click.echo(f"\nExplores ({len(brief['explores'])}):")
        for ex in brief["explores"][:5]:
            joins = ", ".join(ex.get("joins", []))
            click.echo(f"  {ex['name']:<40}  base={ex['base_view']}  fields={ex['field_count']}")
            if joins:
                click.echo(f"    joins: {joins}")
        if len(brief["explores"]) > 5:
            click.echo(f"  ... ({len(brief['explores']) - 5} more — pass --model to narrow)")

    if brief.get("backing_tables"):
        click.echo(f"\nBacking tables ({len(brief['backing_tables'])}):")
        for v in brief["backing_tables"][:10]:
            click.echo(f"  {v['name']:<30}  →  {v.get('physical_table') or '—'}")

    if ticket and brief.get("change_type"):
        change_type = brief["change_type"]
        click.echo(f"\nChange type ({ticket!r}):")
        click.echo(f"  {change_type}")
        for action in brief.get("what_to_touch", []):
            click.echo(f"  → {action}")

    click.echo("")


def _build_navigate_brief(
    graph: Any,
    anchor: str,
    model: str | None,
    ticket: str | None,
    strata_find_field: Any,
    strata_impact: Any,
    strata_view_sources: Any,
    strata_explore_deps: Any,
) -> dict[str, Any]:
    anchor_type = _classify_anchor(anchor)
    brief: dict[str, Any] = {"anchor": anchor, "anchor_type": anchor_type}

    views_hit: list[str] = []
    explores_hit: list[str] = []

    if anchor_type == "bq_table":
        result = strata_impact(graph, anchor)
        if "error" in result:
            return {"error": result["error"]}
        views_hit = result.get("views", [])
        explores_hit = result.get("explores", [])
        brief["bq_fields"] = result.get("fields", [])
        brief["views"] = [{"name": v} for v in views_hit]

    elif anchor_type == "field":
        result = strata_find_field(graph, anchor, "all")
        matches = result.get("matches", [])
        if not matches:
            return {"error": f"No fields matching {anchor!r} found in IR"}
        brief["field_matches"] = matches
        views_hit = list({m["view"] for m in matches})

    else:
        name = _anchor_to_name(anchor, anchor_type)
        sources = strata_view_sources(graph, model)
        matched = [v for v in sources["views"] if name.lower() in v["name"].lower()]
        brief["views"] = matched
        views_hit = [v["name"] for v in matched]
        for node_id in graph.nodes:
            if node_id.startswith("explore:") and name.lower() in node_id.lower():
                parts = node_id.split(":")
                if len(parts) == 3:
                    explores_hit.append(f"{parts[1]}.{parts[2]}")

    if anchor_type == "explore" and not explores_hit:
        name = _anchor_to_name(anchor, anchor_type)
        for node_id in graph.nodes:
            if node_id.startswith("explore:") and name.lower() in node_id.lower():
                parts = node_id.split(":")
                if len(parts) == 3:
                    explores_hit.append(f"{parts[1]}.{parts[2]}")

    explore_details = []
    for ex in explores_hit[:5]:
        model_name, explore_name = ex.split(".", 1)
        deps = strata_explore_deps(graph, explore_name, model_name)
        if "error" not in deps:
            explore_details.append(
                {
                    "name": ex,
                    "base_view": deps.get("base_view"),
                    "field_count": deps.get("field_count"),
                    "joins": [j["name"] for j in deps.get("joins", [])],
                }
            )
    if explore_details:
        brief["explores"] = explore_details

    if views_hit and anchor_type != "bq_table":
        sources = strata_view_sources(graph, model)
        view_map = {v["name"]: v for v in sources["views"]}
        brief["backing_tables"] = [view_map[v] for v in views_hit if v in view_map]

    if ticket:
        change_type = _infer_change_type(ticket)
        brief["change_type"] = change_type
        what: list[str] = []
        if change_type == "add_field" and views_hit:
            what.append(f"Edit view file for: {views_hit[0]}")
        elif change_type == "add_join" and explores_hit:
            what.append(f"Edit explore in model: {explores_hit[0].split('.')[0]}")
        elif change_type == "new_view":
            what.append("Create new .view.lkml file, then add join to relevant explore")
        brief["what_to_touch"] = what

    return brief


def _classify_anchor(anchor: str) -> str:
    if anchor.endswith((".view.lkml", ".model.lkml", ".explore.lkml")):
        return "file"
    parts = anchor.split(".")
    if len(parts) >= 3 and not anchor.endswith(".lkml"):
        return "bq_table"
    if len(parts) == 2:
        return "field"
    return "view"


def _anchor_to_name(anchor: str, anchor_type: str) -> str:
    if anchor_type == "file":
        for suffix in (".view.lkml", ".model.lkml", ".explore.lkml"):
            if anchor.endswith(suffix):
                return Path(anchor).name.replace(suffix, "")
    return anchor


def _infer_change_type(ticket: str) -> str:
    import re

    t = ticket.lower()
    if re.search(r"\b(add|new|create)\b.{0,30}\b(field|dimension|measure|metric|column)\b", t):
        return "add_field"
    if re.search(r"\b(add|new|create)\b.{0,20}\b(join|relationship)\b", t):
        return "add_join"
    if re.search(r"\b(add|new|create)\b.{0,20}\b(view|derived table|cte)\b", t):
        return "new_view"
    if re.search(r"\b(rename|move|migrate|refactor)\b", t):
        return "rename"
    if re.search(r"\b(remove|drop|delete|deprecate|clean up)\b", t):
        return "drop"
    return "unknown"


@query.command("status")
@_repo_opt
@_usage_opt
@_schema_opt
def query_status(repo: str | None, usage_fixture: str | None, schema_fixture: str | None) -> None:
    """Show IR summary: node counts, edge count, and cache age.

    Quick sanity check that the repo parsed cleanly and the graph has the
    expected number of explores, views, and fields.

    \b
    $ strata query status --repo tests/lookml/enterprise_mono \\
        --usage-fixture tests/fixtures/enterprise_usage_facts.json
    {
      "node_counts": {"explore": 34, "view": 20, "field": 196, "pdt": 5},
      "edge_count": 378
    }
    """
    graph = _build(repo, usage_fixture, schema_fixture)
    from strata.mcp.tools import strata_ir_status

    result = strata_ir_status(graph)
    click.echo(json.dumps(result, indent=2, default=str))
