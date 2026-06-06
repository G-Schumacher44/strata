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


def strata_usage_summary(graph: IRGraph) -> dict[str, Any]:
    l1 = graph.metadata.get("l1", {})
    usage = l1.get("explore_usage", {})
    total_queries = sum(item.get("query_count", 0) for item in usage.values())
    return {
        "has_l1": bool(l1),
        "explore_count": len(usage),
        "total_queries": total_queries,
        "dead_code_count": len(l1.get("dead_code", [])),
        "pdt_count": len(l1.get("pdt_ledger", [])),
        "unused_pdt_count": sum(1 for item in l1.get("pdt_ledger", []) if item.get("status") == "unused"),
    }


def strata_dead_code_register(graph: IRGraph) -> list[dict[str, Any]]:
    return list(graph.metadata.get("l1", {}).get("dead_code", []))


def strata_pdt_costs(graph: IRGraph) -> list[dict[str, Any]]:
    return list(graph.metadata.get("l1", {}).get("pdt_ledger", []))


def strata_impact(graph: IRGraph, physical_table: str) -> dict[str, Any]:
    table_id = f"physical_table:{physical_table}"
    views: set[str] = set()
    for edge in graph.edges:
        if edge.target != table_id:
            continue
        if edge.relation == "view→physical_table":
            views.add(edge.source.removeprefix("view:"))
        elif edge.relation == "pdt→upstream":
            pdt = graph.get_node(edge.source)
            if pdt:
                views.add(pdt.name)
    explores: set[str] = set()
    fields: set[str] = set()
    for view in views:
        for edge in graph.edges:
            if edge.target == f"view:{view}" and edge.relation in {"explore→base_view", "explore→joined_view"}:
                node = graph.get_node(edge.source)
                if node:
                    explores.add(f"{node.attrs.get('model')}.{node.name}")
        prefix = f"field:{view}."
        fields.update(node_id.removeprefix("field:") for node_id in graph.nodes if node_id.startswith(prefix))
    return {
        "physical_table": physical_table,
        "views": sorted(views),
        "explores": sorted(explores),
        "fields": sorted(fields),
    }


def _field_count_for_view(graph: IRGraph, view: str) -> int:
    prefix = f"field:{view}."
    return sum(1 for node_id in graph.nodes if node_id.startswith(prefix))
