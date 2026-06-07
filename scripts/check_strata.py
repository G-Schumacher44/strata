#!/usr/bin/env python3
"""Run offline Strata scenario gates for CI and local review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from strata.pipeline import build_graph
from strata.synthesis.slices import build_explore_slice
from strata.synthesis.verdicts import deterministic_verdict, validate_verdict
from strata.validation import validation_scope


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(REPO_ROOT / "tests" / "fixtures"))
    parser.add_argument("--usage-fixture", default=str(REPO_ROOT / "tests" / "fixtures" / "usage_facts.json"))
    parser.add_argument("--schema-fixture", default=str(REPO_ROOT / "tests" / "fixtures" / "schema_facts_drift.json"))
    args = parser.parse_args()

    graph = build_graph(args.repo, args.usage_fixture, args.schema_fixture)
    failures: list[str] = []
    if graph.metadata.get("resolution_errors"):
        failures.append(f"resolution errors: {graph.metadata['resolution_errors']}")
    if not graph.metadata.get("l1", {}).get("dead_code"):
        failures.append("expected at least one dead-code evidence record")
    if not graph.metadata.get("l1", {}).get("pdt_ledger"):
        failures.append("expected at least one PDT ledger record")
    if not graph.metadata.get("l1", {}).get("schema_drift"):
        failures.append("expected at least one schema-drift evidence record")
    repo_name = Path(args.repo).name
    if repo_name == "enterprise_mono":
        failures.extend(_enterprise_assertions(graph))
    elif repo_name == "fixtures":
        scope = validation_scope(
            graph,
            [
                {"kind": "view", "name": "customer_extended"},
                {"kind": "physical_table", "name": "analytics.orders"},
            ],
        )
        scoped = {(item["model"], item["explore"]) for item in scope["explores"]}
        if ("test_model", "customer") not in scoped or ("pdt_validation", "pdt_scope") not in scoped:
            failures.append("expected validation scope to include customer and pdt_scope explores")
    for node in graph.nodes_by_kind("explore"):
        explore_slice = build_explore_slice(graph, node.attrs["model"], node.name)
        verdict = deterministic_verdict(explore_slice)
        failures.extend(validate_verdict(verdict, explore_slice["evidence_ids"]))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("Strata scenario gates passed")
    return 0


def _enterprise_assertions(graph) -> list[str]:
    failures: list[str] = []
    l1 = graph.metadata.get("l1", {})
    dead = l1.get("dead_code", [])
    pdt = l1.get("pdt_ledger", [])
    drift = l1.get("schema_drift", [])
    dead_names = {item["name"] for item in dead}
    pdt_cost = round(sum(float(item.get("estimated_cost_usd", 0)) for item in pdt), 2)
    if len(graph.nodes_by_kind("explore")) != 34:
        failures.append("enterprise_mono expected 34 explores")
    if len(dead) != 11:
        failures.append(f"enterprise_mono expected 11 dead-code records (6 dead explores + 5 zombie views), got {len(dead)}")
    for name in {"em_legacy_v2.dead_orders_v2", "em_legacy_v2.dead_finance_v2"}:
        if name not in dead_names:
            failures.append(f"enterprise_mono missing dead explore: {name}")
    for name in {"legacy_customer_profile", "legacy_inventory_snapshot", "legacy_order_detail"}:
        if name not in dead_names:
            failures.append(f"enterprise_mono missing zombie view: {name}")
    if len(pdt) != 5 or pdt_cost != 63755.94:
        failures.append(f"enterprise_mono expected 5 PDT records and $63755.94 cost, got {len(pdt)} and ${pdt_cost}")
    if len(drift) != 14:
        failures.append(f"enterprise_mono expected 14 schema-drift records (7 fixture + 7 real int_inventory_risk migration), got {len(drift)}")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
