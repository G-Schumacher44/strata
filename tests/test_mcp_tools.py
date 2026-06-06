from pathlib import Path

from strata.ir.resolver import build_resolved_graph
from strata.mcp.tools import (
    strata_dead_code_register,
    strata_explore_deps,
    strata_impact,
    strata_ir_status,
    strata_list_orphans,
    strata_pdt_costs,
    strata_query_field,
    strata_usage_summary,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_strata_query_field():
    graph = build_resolved_graph(FIXTURES)

    field = strata_query_field(graph, "customer_extended", "email")

    assert field == {
        "sql": "LOWER(${TABLE}.email)",
        "type": "string",
        "tags": ["normalized"],
        "source_file": "customer_extended.view.lkml",
        "resolution_chain": ["base_customer", "customer_extended"],
    }


def test_strata_list_orphans():
    graph = build_resolved_graph(FIXTURES)

    assert strata_list_orphans(graph, "view")[0]["name"] == "orphan_view"
    assert strata_list_orphans(graph, "field") == []


def test_strata_explore_deps():
    graph = build_resolved_graph(FIXTURES)

    deps = strata_explore_deps(graph, "refined_customer", "refined_explore")

    assert deps["base_view"] == "customer_extended"
    assert deps["joins"] == [
        {"name": "simple", "view": "simple", "type": "left_outer"},
        {"name": "chain_final", "view": "chain_final", "type": "left_outer"},
    ]
    assert deps["resolution_chain"] == ["refined_customer", "+refined_customer"]
    assert deps["field_count"] == 16


def test_strata_ir_status():
    graph = build_resolved_graph(FIXTURES)
    graph.cache_path = "/tmp/strata-test.db"

    status = strata_ir_status(graph)

    assert status["repo_path"].endswith("tests/fixtures")
    assert status["node_counts"]["view"] == 9
    assert status["edge_count"] > 0
    assert status["cache_path"] == "/tmp/strata-test.db"


def test_l1_repo_brain_tools():
    from strata.l1.enrich import enrich_graph
    from strata.l1.fixtures import load_usage_facts

    graph = build_resolved_graph(FIXTURES)
    facts = load_usage_facts(FIXTURES / "usage_facts.json")
    enrich_graph(graph, facts["explore_usage"], facts["content_references"], facts["pdt_builds"])

    summary = strata_usage_summary(graph)
    assert summary["total_queries"] == 49
    assert summary["dead_code_count"] >= 2
    assert strata_dead_code_register(graph)
    assert strata_pdt_costs(graph)[0]["status"] == "unused"
    assert strata_impact(graph, "analytics.orders")["views"] == ["pdt_orders", "pdt_scope_orders"]
