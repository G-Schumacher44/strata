"""Fixture-backed L1 facts for deterministic offline enrichment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from strata.l1.types import ContentReference, ExploreUsage, PDTBuild


def load_usage_facts(path: str | Path) -> dict[str, list[Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        "explore_usage": [ExploreUsage(**item) for item in data.get("explore_usage", [])],
        "content_references": [ContentReference(**item) for item in data.get("content_references", [])],
        "pdt_builds": [PDTBuild(**item) for item in data.get("pdt_builds", [])],
    }
