"""Fixture-backed L1 facts for deterministic offline enrichment."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any

from strata.l1.types import ContentReference, ExploreUsage, PDTBuild


def _coerce(cls: type, item: dict[str, Any]) -> Any:
    known = {f.name for f in dataclasses.fields(cls)}
    return cls(**{k: v for k, v in item.items() if k in known})


def load_usage_facts(path: str | Path) -> dict[str, list[Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        "explore_usage": [_coerce(ExploreUsage, item) for item in data.get("explore_usage", [])],
        "content_references": [_coerce(ContentReference, item) for item in data.get("content_references", [])],
        "pdt_builds": [_coerce(PDTBuild, item) for item in data.get("pdt_builds", [])],
    }
