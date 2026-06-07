"""strata query — field-level LookML inspection from the terminal."""

from __future__ import annotations

import json
from pathlib import Path

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
    "--repo", default=None, envvar="STRATA_REPO_PATH", show_envvar=True, help="LookML repo path (overrides config)"
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
