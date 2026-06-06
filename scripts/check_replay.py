#!/usr/bin/env python3
"""Validate sanitized replay L1 facts without network or secrets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from strata.l1.provider import UsageFacts
from strata.l1.replay import ReplayLookerUsageProvider


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", default=str(REPO_ROOT / "tests" / "fixtures" / "replay_facts.json"))
    args = parser.parse_args()

    facts = UsageFacts.from_provider(ReplayLookerUsageProvider(args.replay))
    summary = {
        "explore_usage_count": len(facts.explore_usage),
        "content_reference_count": len(facts.content_references),
        "pdt_build_count": len(facts.pdt_builds),
        "total_queries": sum(item.query_count for item in facts.explore_usage),
        "total_pdt_cost_usd": round(sum(item.estimated_cost_usd for item in facts.pdt_builds), 6),
    }
    print(json.dumps(summary, sort_keys=True))
    if summary["explore_usage_count"] == 0:
        print("FAIL: replay has no explore usage rows after normalization", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
