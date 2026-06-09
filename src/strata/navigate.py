"""Navigator brief — deterministic ticket-anchor analysis over the IR.

Shared by the CLI (`strata query navigate`) and the MCP tool (`strata_navigate`),
so an agent gets the same brief in one call that the CLI builds in one pass.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from strata.ir.types import IRGraph
from strata.mcp.tools import (
    strata_explore_deps,
    strata_find_field,
    strata_impact,
    strata_view_sources,
)

MAX_EXPLORES = 5


def build_navigate_brief(
    graph: IRGraph,
    anchor: str,
    model: str | None = None,
    ticket: str | None = None,
) -> dict[str, Any]:
    """Classify a ticket anchor, run the right lookups, and return a navigator brief.

    The brief names the views, explores, and fields an anchor touches, infers the change
    type from ticket text, and cites `source_file` + best-effort `source_line` for each
    target so a downstream agent or developer can act without exploring the repo blind.
    """
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
        sources = strata_view_sources(graph, None)
        view_map = {v["name"]: v for v in sources["views"]}
        brief["views"] = [view_map.get(v, {"name": v}) for v in views_hit]

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
        explores_hit = _match_explores(graph, name)

    if anchor_type == "explore" and not explores_hit:
        explores_hit = _match_explores(graph, _anchor_to_name(anchor, anchor_type))

    explore_details = []
    truncated_explores = len(explores_hit) > MAX_EXPLORES
    for ex in explores_hit[:MAX_EXPLORES]:
        model_name, explore_name = ex.split(".", 1)
        deps = strata_explore_deps(graph, explore_name, model_name)
        if "error" not in deps:
            node = graph.get_node(f"explore:{model_name}:{explore_name}")
            source_file = node.source_file if node else None
            explore_details.append(
                {
                    "name": ex,
                    "base_view": deps.get("base_view"),
                    "field_count": deps.get("field_count"),
                    "joins": [j["name"] for j in deps.get("joins", [])],
                    "source_file": source_file,
                    "source_line": _definition_line(graph, source_file, "explore", explore_name),
                }
            )
    if explore_details:
        brief["explores"] = explore_details

    if views_hit and anchor_type != "bq_table":
        sources = strata_view_sources(graph, model)
        view_map = {v["name"]: v for v in sources["views"]}
        brief["backing_tables"] = [view_map[v] for v in views_hit if v in view_map]

    _attach_source_lines(graph, brief)

    if truncated_explores:
        brief["truncated"] = (
            f"Capped at {MAX_EXPLORES} of {len(explores_hit)} explores — pass model= to narrow."
        )

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


def _match_explores(graph: IRGraph, name: str) -> list[str]:
    hits = []
    for node_id in graph.nodes:
        if node_id.startswith("explore:") and name.lower() in node_id.lower():
            parts = node_id.split(":")
            if len(parts) == 3:
                hits.append(f"{parts[1]}.{parts[2]}")
    return hits


def _attach_source_lines(graph: IRGraph, brief: dict[str, Any]) -> None:
    """Best-effort: cite the definition line for each view/field target."""
    for key in ("views", "backing_tables"):
        for v in brief.get(key, []):
            if v.get("source_file") and "source_line" not in v:
                v["source_line"] = _definition_line(graph, v["source_file"], "view", v["name"])
    for m in brief.get("field_matches", []):
        if m.get("source_file"):
            m["source_line"] = _definition_line(graph, m["source_file"], "field", m["field"])


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


_FIELD_KW = "dimension|dimension_group|measure|filter|parameter"


def _definition_line(graph: IRGraph, source_file: str | None, kind: str, name: str) -> int | None:
    """Scan the LookML source for the 1-based line where `name` is defined.

    Line numbers are not preserved by the LookML parser, so this is a best-effort
    text scan. Returns None when the file is missing or no definition matches.
    """
    if not source_file:
        return None
    if kind == "view":
        pattern = rf"^\s*view:\s*{re.escape(name)}\s*\{{"
    elif kind == "explore":
        pattern = rf"^\s*explore:\s*{re.escape(name)}\s*\{{"
    else:
        pattern = rf"^\s*(?:{_FIELD_KW}):\s*{re.escape(name)}\s*\{{"
    return _scan_file(_resolve(graph.repo_path, source_file), pattern)


def _resolve(repo_path: str, source_file: str) -> str:
    p = Path(source_file)
    if p.is_absolute() or p.exists():
        return str(p)
    return str(Path(repo_path) / source_file)


@lru_cache(maxsize=256)
def _scan_file(path: str, pattern: str) -> int | None:
    try:
        with open(path, encoding="utf-8") as fh:
            for i, line in enumerate(fh, start=1):
                if re.search(pattern, line):
                    return i
    except OSError:
        return None
    return None
