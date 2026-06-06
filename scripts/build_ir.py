#!/usr/bin/env python3
"""Build and cache the Strata L0 IR for a LookML repo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from strata.ir.store import save_ir
from strata.pipeline import build_graph


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Path to a LookML repo or fixture directory")
    parser.add_argument("--cache", help="SQLite cache path; defaults to <repo>/strata_ir.db")
    parser.add_argument("--usage-fixture", help="Optional L1 fixture facts JSON")
    parser.add_argument("--schema-fixture", help="Optional L1 schema facts JSON")
    parser.add_argument("--json", action="store_true", help="Print a compact status JSON")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists():
        parser.error(f"--repo does not exist: {repo}")
    cache = Path(args.cache).expanduser().resolve() if args.cache else repo / "strata_ir.db"
    graph = build_graph(repo, args.usage_fixture, args.schema_fixture)
    save_ir(graph, cache)
    status = {
        "repo_path": graph.repo_path,
        "built_at": graph.built_at,
        "node_counts": graph.node_counts(),
        "edge_count": len(graph.edges),
        "cache_path": graph.cache_path,
    }
    if args.json:
        print(json.dumps(status, sort_keys=True))
    else:
        print(f"Built Strata IR: {status['node_counts']} nodes, {status['edge_count']} edges")
        print(f"Cache: {graph.cache_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
