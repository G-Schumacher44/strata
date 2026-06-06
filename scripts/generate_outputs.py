#!/usr/bin/env python3
"""Generate offline Strata review artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from strata.outputs import write_artifacts
from strata.pipeline import build_graph


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--usage-fixture", help="Fixture JSON")
    parser.add_argument("--schema-fixture")
    parser.add_argument("--validation-scope-fixture")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    graph = build_graph(args.repo, args.usage_fixture, args.schema_fixture)
    if args.validation_scope_fixture:
        graph.metadata["validation_scope_inputs"] = json.loads(
            Path(args.validation_scope_fixture).read_text(encoding="utf-8")
        ).get("changed", [])
    written = write_artifacts(graph, args.out)
    print(json.dumps(written, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
