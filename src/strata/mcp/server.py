"""Thin stdio MCP server for Strata repo-brain tools."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from strata.ir.store import cache_age_seconds, load_ir, save_ir
from strata.ir.types import IRGraph
from strata.pipeline import build_graph
from strata.mcp.tools import (
    strata_dead_code_register as query_dead_code_register,
    strata_explore_deps as query_explore_deps,
    strata_impact as query_impact,
    strata_ir_status as query_ir_status,
    strata_list_orphans as query_list_orphans,
    strata_pdt_costs as query_pdt_costs,
    strata_query_field as query_field,
    strata_schema_drift as query_schema_drift,
    strata_usage_summary as query_usage_summary,
)

CACHE_MAX_AGE_SECONDS = 300


def load_configured_graph() -> IRGraph:
    repo_path = _repo_path()
    cache_path = _cache_path(repo_path)
    age = cache_age_seconds(cache_path)
    if age is not None and age < CACHE_MAX_AGE_SECONDS:
        return load_ir(cache_path)
    graph = build_graph(repo_path, _usage_fixture(), _schema_fixture())
    save_ir(graph, cache_path)
    return graph


def create_server(graph: IRGraph | None = None) -> FastMCP:
    ir_graph = graph or load_configured_graph()
    server = FastMCP("strata")

    @server.tool()
    def strata_query_field(view: str, field: str) -> dict[str, Any]:
        return query_field(ir_graph, view, field)

    @server.tool()
    def strata_list_orphans(kind: str = "all") -> list[dict[str, Any]]:
        return query_list_orphans(ir_graph, kind)

    @server.tool()
    def strata_explore_deps(explore: str, model: str) -> dict[str, Any]:
        return query_explore_deps(ir_graph, explore, model)

    @server.tool()
    def strata_ir_status() -> dict[str, Any]:
        return query_ir_status(ir_graph)

    @server.tool()
    def strata_usage_summary() -> dict[str, Any]:
        return query_usage_summary(ir_graph)

    @server.tool()
    def strata_dead_code_register() -> list[dict[str, Any]]:
        return query_dead_code_register(ir_graph)

    @server.tool()
    def strata_pdt_costs() -> list[dict[str, Any]]:
        return query_pdt_costs(ir_graph)

    @server.tool()
    def strata_schema_drift() -> list[dict[str, Any]]:
        return query_schema_drift(ir_graph)

    @server.tool()
    def strata_impact(physical_table: str) -> dict[str, Any]:
        return query_impact(ir_graph, physical_table)

    return server


def main() -> None:
    create_server().run(transport="stdio")


def _repo_path() -> Path:
    env_path = os.environ.get("STRATA_REPO_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()
    config_path = Path.home() / ".strata" / "config.json"
    if config_path.exists():
        data = json.loads(config_path.read_text(encoding="utf-8"))
        if data.get("repo_path"):
            return Path(data["repo_path"]).expanduser().resolve()
    return Path.cwd().resolve()


def _cache_path(repo_path: Path) -> Path:
    env_path = os.environ.get("STRATA_CACHE_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return repo_path / "strata_ir.db"


def _usage_fixture() -> Path | None:
    env_path = os.environ.get("STRATA_USAGE_FIXTURE")
    if not env_path:
        return None
    return Path(env_path).expanduser().resolve()


def _schema_fixture() -> Path | None:
    env_path = os.environ.get("STRATA_SCHEMA_FIXTURE")
    if not env_path:
        return None
    return Path(env_path).expanduser().resolve()


if __name__ == "__main__":
    main()
