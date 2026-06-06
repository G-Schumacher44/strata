#!/usr/bin/env python3
"""Import a usage fixture JSON into the Strata L1 time-series store."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from strata.l1.store import import_fixture, store_date_range


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", required=True, help="Path to strata_usage.db (created if absent)")
    parser.add_argument("--fixture", required=True, help="Usage facts JSON to import")
    args = parser.parse_args()

    fixture = Path(args.fixture)
    if not fixture.exists():
        parser.error(f"--fixture does not exist: {fixture}")

    counts = import_fixture(args.store, fixture)
    date_range = store_date_range(args.store)
    range_str = f"{date_range[0]} → {date_range[1]}" if date_range else "no data"

    print(
        f"Imported: {counts['explore_queries']} explore rows, "
        f"{counts['pdt_builds']} PDT rows, "
        f"{counts['content_refs']} content rows"
    )
    print(f"Store range: {range_str}  ({args.store})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
