"""strata skill run — execute a skill via the Anthropic API (requires strata[ai])."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import click

from strata.config import load_repo_path

_MODEL_MAP = {
    "low": "claude-haiku-4-5-20251001",
    "medium": "claude-sonnet-4-6",
    "high": "claude-sonnet-4-6",
}

_TOOL_REGISTRY: dict[str, Any] = {}


def _get_tools() -> dict[str, Any]:
    if not _TOOL_REGISTRY:
        from strata.mcp import tools as t

        _TOOL_REGISTRY.update(
            {
                "strata_find_field": t.strata_find_field,
                "strata_view_sources": t.strata_view_sources,
                "strata_impact": t.strata_impact,
                "strata_explore_deps": t.strata_explore_deps,
                "strata_query_field": t.strata_query_field,
                "strata_ir_status": t.strata_ir_status,
                "strata_list_orphans": t.strata_list_orphans,
                "strata_usage_summary": t.strata_usage_summary,
                "strata_dead_code_register": t.strata_dead_code_register,
                "strata_pdt_costs": t.strata_pdt_costs,
                "strata_schema_drift": t.strata_schema_drift,
            }
        )
    return _TOOL_REGISTRY


# Anthropic tool schemas for each strata tool
_TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "strata_find_field",
        "description": "Search all views for fields matching a name fragment, SQL substring, label, description, or tag.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term"},
                "kind": {
                    "type": "string",
                    "enum": ["all", "dimension", "measure", "filter", "parameter"],
                    "description": "Field kind filter (default: all)",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "strata_view_sources",
        "description": "List all views with their physical BQ table backing and field counts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "Restrict to views reachable from this model (optional)",
                }
            },
        },
    },
    {
        "name": "strata_impact",
        "description": "Show every view, explore, and field that references a physical BQ table.",
        "input_schema": {
            "type": "object",
            "properties": {
                "physical_table": {
                    "type": "string",
                    "description": "BQ table name (project.dataset.table)",
                }
            },
            "required": ["physical_table"],
        },
    },
    {
        "name": "strata_explore_deps",
        "description": "Show an explore's join graph, base view, and field count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "explore": {"type": "string", "description": "Explore name"},
                "model": {"type": "string", "description": "Model name"},
            },
            "required": ["explore", "model"],
        },
    },
    {
        "name": "strata_query_field",
        "description": "Show a single field's full definition: type, SQL, tags, resolution chain.",
        "input_schema": {
            "type": "object",
            "properties": {
                "view": {"type": "string", "description": "View name"},
                "field": {"type": "string", "description": "Field name"},
            },
            "required": ["view", "field"],
        },
    },
    {
        "name": "strata_ir_status",
        "description": "Show IR summary: node counts, edge count, and cache age.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


def _parse_skill_complexity(skill_md: str) -> str:
    m = re.search(r"^complexity:\s*(\w+)", skill_md, re.MULTILINE | re.IGNORECASE)
    return m.group(1).strip().lower() if m else "medium"


def _resolve_model(complexity: str, override: str | None) -> str:
    if override:
        aliases = {
            "haiku": "claude-haiku-4-5-20251001",
            "sonnet": "claude-sonnet-4-6",
            "opus": "claude-opus-4-8",
        }
        return aliases.get(override.lower(), override)
    return _MODEL_MAP.get(complexity, "claude-sonnet-4-6")


def _run_tool(graph: Any, name: str, inputs: dict[str, Any]) -> Any:
    registry = _get_tools()
    fn = registry.get(name)
    if fn is None:
        return {"error": f"tool not found: {name}"}
    return fn(graph, **inputs)


@click.group("skill")
def skill() -> None:
    """Execute skills via the Anthropic API."""


@skill.command("run")
@click.argument("skill_name")
@click.argument("anchor")
@click.option(
    "--model",
    default=None,
    type=click.Choice(["haiku", "sonnet", "opus"]),
    help="Model to use (default: from skill complexity — low→haiku, medium/high→sonnet)",
)
@click.option("--repo", default=None, envvar="STRATA_REPO_PATH", show_envvar=True)
@click.option("--usage-fixture", default=None, envvar="STRATA_USAGE_FIXTURE", show_envvar=True)
@click.option("--schema-fixture", default=None, envvar="STRATA_SCHEMA_FIXTURE", show_envvar=True)
@click.option(
    "--system-extra", default=None, help="Extra instructions appended to the skill prompt"
)
def skill_run(
    skill_name: str,
    anchor: str,
    model: str | None,
    repo: str | None,
    usage_fixture: str | None,
    schema_fixture: str | None,
    system_extra: str | None,
) -> None:
    """Execute a skill against an anchor using the Anthropic API.

    SKILL_NAME is the skill directory name (e.g. lookml_ticket_navigator).
    ANCHOR is the entry point: a BQ table, field name, view, explore, or .lkml file.

    Requires ANTHROPIC_API_KEY and: pip install 'strata[ai]'

    \b
    Examples:
      strata skill run lookml_ticket_navigator "revenue"
      strata skill run lookml_ticket_navigator "project.dataset.orders" --model sonnet
      strata skill run lookml_ticket_navigator "orders" --model haiku \\
        --repo tests/lookml/thelook
    """
    try:
        import anthropic
    except ImportError as exc:
        raise click.ClickException(
            "anthropic package not installed. Run: pip install 'strata[ai]'"
        ) from exc

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise click.ClickException("ANTHROPIC_API_KEY environment variable not set.")

    from strata.mcp.tools import strata_skill
    from strata.pipeline import build_graph

    # Resolve paths
    skills_dir = Path(__file__).resolve().parent.parent / "skills"
    skill_md = strata_skill(skills_dir, skill_name)
    if skill_md.startswith("error:"):
        raise click.ClickException(skill_md)

    repo_path = Path(repo).expanduser().resolve() if repo else load_repo_path()
    graph = build_graph(str(repo_path), usage_fixture, schema_fixture)

    complexity = _parse_skill_complexity(skill_md)
    model_id = _resolve_model(complexity, model)

    system = (
        f"You are executing the following strata skill. Follow its procedure exactly.\n\n{skill_md}"
    )
    if system_extra:
        system += f"\n\nAdditional instructions: {system_extra}"

    user_msg = f"Anchor: {anchor}"
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_msg}]

    click.echo(f"Running {skill_name!r} on {anchor!r} with {model_id} …\n", err=True)

    client = anthropic.Anthropic(api_key=api_key)

    # Agentic tool-use loop
    while True:
        response = client.messages.create(
            model=model_id,
            max_tokens=4096,
            system=system,
            tools=_TOOL_SCHEMAS,  # type: ignore[arg-type]
            messages=messages,
        )

        # Collect text output and tool calls from this turn
        text_parts = []
        tool_uses = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_uses.append(block)

        if text_parts:
            click.echo("\n".join(text_parts))

        if response.stop_reason == "end_turn" or not tool_uses:
            break

        # Execute tool calls and append results
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for tu in tool_uses:
            result = _run_tool(graph, tu.name, tu.input)
            click.echo(
                f"  [tool] {tu.name}({list(tu.input.keys())}) → {len(str(result))} chars", err=True
            )
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": json.dumps(result, default=str),
                }
            )
        messages.append({"role": "user", "content": tool_results})
