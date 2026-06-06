"""Shared offline build pipeline for IR, L1 enrichment, synthesis, and outputs."""

from __future__ import annotations

from pathlib import Path

from strata.ir.resolver import build_resolved_graph
from strata.ir.types import IRGraph
from strata.l1.enrich import enrich_graph
from strata.l1.fixtures import load_usage_facts
from strata.l1.provider import UsageFacts, UsageProvider


def build_graph(repo_path: str | Path, usage_fixture: str | Path | None = None) -> IRGraph:
    graph = build_resolved_graph(repo_path)
    if usage_fixture:
        facts = load_usage_facts(usage_fixture)
        graph = enrich_graph(graph, **facts)
    return graph


def build_graph_with_provider(repo_path: str | Path, provider: UsageProvider) -> IRGraph:
    graph = build_resolved_graph(repo_path)
    facts = UsageFacts.from_provider(provider)
    return enrich_graph(graph, **facts.to_mapping())
