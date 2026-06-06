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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(REPO_ROOT / "tests" / "fixtures"))
    parser.add_argument("--usage-fixture", default=str(REPO_ROOT / "tests" / "fixtures" / "usage_facts.json"))
    args = parser.parse_args()

    graph = build_graph(args.repo, args.usage_fixture)
    failures: list[str] = []
    if graph.metadata.get("resolution_errors"):
        failures.append(f"resolution errors: {graph.metadata['resolution_errors']}")
    if not graph.metadata.get("l1", {}).get("dead_code"):
        failures.append("expected at least one dead-code evidence record")
    if not graph.metadata.get("l1", {}).get("pdt_ledger"):
        failures.append("expected at least one PDT ledger record")
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


if __name__ == "__main__":
    raise SystemExit(main())
