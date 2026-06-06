"""Read-only MCP tool implementations over a resolved IRGraph."""

from __future__ import annotations

from typing import Any

from strata.ir.types import IRGraph


def strata_query_field(graph: IRGraph, view: str, field: str) -> dict[str, Any]:
    node = graph.get_node(f"field:{view}.{field}")
    if node is None:
        raise KeyError(f"field not found: {view}.{field}")
    return {
        "sql": node.attrs.get("sql"),
        "type": node.attrs.get("type"),
        "tags": node.attrs.get("tags", []),
        "source_file": node.source_file,
        "resolution_chain": node.attrs.get("resolution_chain", []),
    }


def strata_list_orphans(graph: IRGraph, kind: str = "all") -> list[dict[str, Any]]:
    if kind not in {"all", "view", "explore", "field"}:
        raise ValueError("kind must be one of: all, view, explore, field")
    orphans = graph.metadata.get("orphans", [])
    if kind == "all":
        return list(orphans)
    return [orphan for orphan in orphans if orphan.get("kind") == kind]


def strata_explore_deps(graph: IRGraph, explore: str, model: str) -> dict[str, Any]:
    node = graph.get_node(f"explore:{model}:{explore}")
    if node is None:
        raise KeyError(f"explore not found: {model}.{explore}")
    joins = [
        {
            "name": join["name"],
            "view": join.get("from") or join["name"],
            "type": join.get("type"),
        }
        for join in node.attrs.get("joins", [])
    ]
    view_names = [node.attrs.get("base_view")] + [join["view"] for join in joins]
    field_count = sum(_field_count_for_view(graph, view_name) for view_name in view_names if view_name)
    return {
        "base_view": node.attrs.get("base_view"),
        "joins": joins,
        "resolution_chain": node.attrs.get("resolution_chain", []),
        "field_count": field_count,
    }


def strata_ir_status(graph: IRGraph) -> dict[str, Any]:
    return {
        "repo_path": graph.repo_path,
        "built_at": graph.built_at,
        "node_counts": graph.node_counts(),
        "edge_count": len(graph.edges),
        "cache_path": graph.cache_path,
    }


def _field_count_for_view(graph: IRGraph, view: str) -> int:
    prefix = f"field:{view}."
    return sum(1 for node_id in graph.nodes if node_id.startswith(prefix))
