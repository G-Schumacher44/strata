"""SQLite time-series store for L1 usage facts.

Stores daily-granularity rows so any time window can be queried after
a single import. Separate from strata_ir.db (IR cache).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from strata.l1.types import ContentReference, ExploreUsage, PDTBuild

_SCHEMA = """
CREATE TABLE IF NOT EXISTS explore_queries (
    model       TEXT    NOT NULL,
    explore     TEXT    NOT NULL,
    query_date  TEXT    NOT NULL,
    query_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (model, explore, query_date)
);
CREATE TABLE IF NOT EXISTS pdt_builds (
    view            TEXT    NOT NULL,
    build_date      TEXT    NOT NULL,
    bytes_processed INTEGER NOT NULL DEFAULT 0,
    cost_usd        REAL    NOT NULL DEFAULT 0,
    PRIMARY KEY (view, build_date)
);
CREATE TABLE IF NOT EXISTS content_refs (
    content_id    TEXT NOT NULL,
    content_type  TEXT NOT NULL,
    model         TEXT NOT NULL,
    explore       TEXT NOT NULL,
    title         TEXT,
    recorded_date TEXT NOT NULL,
    PRIMARY KEY (content_id, recorded_date)
);
"""


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)


def store_exists(store_path: str | Path) -> bool:
    return Path(store_path).exists()


def store_date_range(store_path: str | Path) -> tuple[str, str] | None:
    """Return (earliest_date, latest_date) across all explore_queries rows, or None."""
    if not store_exists(store_path):
        return None
    with sqlite3.connect(store_path) as conn:
        row = conn.execute(
            "SELECT MIN(query_date), MAX(query_date) FROM explore_queries"
        ).fetchone()
    if not row or row[0] is None:
        return None
    return (row[0], row[1])


def import_fixture(store_path: str | Path, fixture_path: str | Path) -> dict[str, int]:
    """Import a usage fixture JSON into the store.

    Distributes aggregated counts evenly across each day in the fixture's
    declared period. ON CONFLICT replaces existing rows (re-import is safe).
    Returns counts of rows written per table.
    """
    store_path = Path(store_path)
    store_path.parent.mkdir(parents=True, exist_ok=True)

    raw: dict[str, Any] = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    period = raw.get("period", {})
    days = max(int(period.get("days", 1)), 1)
    end_str = period.get("end") or date.today().isoformat()
    end_d = date.fromisoformat(end_str)
    start_d = end_d - timedelta(days=days - 1)
    date_range = [(start_d + timedelta(days=i)).isoformat() for i in range(days)]

    counts = {"explore_queries": 0, "pdt_builds": 0, "content_refs": 0}

    with sqlite3.connect(store_path) as conn:
        _ensure_schema(conn)

        for item in raw.get("explore_usage", []):
            total = int(item.get("query_count", 0))
            base = total // days
            remainder = total % days
            for i, d in enumerate(date_range):
                daily = base + (remainder if i == len(date_range) - 1 else 0)
                conn.execute(
                    """
                    INSERT INTO explore_queries (model, explore, query_date, query_count)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(model, explore, query_date)
                        DO UPDATE SET query_count = excluded.query_count
                    """,
                    (item["model"], item["explore"], d, daily),
                )
                counts["explore_queries"] += 1

        for item in raw.get("pdt_builds", []):
            build_count = max(int(item.get("build_count", days)), 1)
            actual_days = min(build_count, days)
            build_dates = date_range[-actual_days:]
            total_bytes = int(item.get("bytes_processed", 0))
            total_cost = float(item.get("estimated_cost_usd", 0))
            per_bytes = total_bytes // actual_days
            per_cost = total_cost / actual_days
            for j, d in enumerate(build_dates):
                is_last = j == len(build_dates) - 1
                b = per_bytes + (total_bytes % actual_days if is_last else 0)
                c = round(total_cost - per_cost * (actual_days - 1) if is_last else per_cost, 6)
                conn.execute(
                    """
                    INSERT INTO pdt_builds (view, build_date, bytes_processed, cost_usd)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(view, build_date)
                        DO UPDATE SET bytes_processed = excluded.bytes_processed,
                                      cost_usd = excluded.cost_usd
                    """,
                    (item["view"], d, b, c),
                )
                counts["pdt_builds"] += 1

        for item in raw.get("content_references", []):
            conn.execute(
                """
                INSERT INTO content_refs
                    (content_id, content_type, model, explore, title, recorded_date)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(content_id, recorded_date)
                    DO UPDATE SET model = excluded.model, explore = excluded.explore
                """,
                (
                    item.get("content_id", ""),
                    item.get("content_type", ""),
                    item.get("model", ""),
                    item.get("explore", ""),
                    item.get("title", ""),
                    end_str,
                ),
            )
            counts["content_refs"] += 1

    return counts


def query_window(store_path: str | Path, days: int = 30) -> dict[str, Any]:
    """Return aggregated L1 facts for the last N days in the store.

    Uses the store's own max date as the window end (not wall-clock time),
    so the window is stable regardless of when you query.
    Returns a dict in the same shape as load_usage_facts() — drop-in replacement.
    """
    store_path = Path(store_path)
    if not store_path.exists():
        return {"explore_usage": [], "content_references": [], "pdt_builds": [], "period": None}

    with sqlite3.connect(store_path) as conn:
        _ensure_schema(conn)
        end_row = conn.execute(
            "SELECT MAX(query_date) FROM explore_queries"
        ).fetchone()
        if not end_row or end_row[0] is None:
            return {"explore_usage": [], "content_references": [], "pdt_builds": [], "period": None}

        end_str = end_row[0]
        end_d = date.fromisoformat(end_str)
        start_d = end_d - timedelta(days=days - 1)
        start_str = start_d.isoformat()

        eu_rows = conn.execute(
            """
            SELECT model, explore, SUM(query_count), MAX(query_date)
            FROM explore_queries
            WHERE query_date >= ? AND query_date <= ?
            GROUP BY model, explore
            """,
            (start_str, end_str),
        ).fetchall()
        explore_usage = [
            ExploreUsage(
                model=r[0],
                explore=r[1],
                query_count=r[2],
                last_queried_at=r[3] + "T00:00:00Z",
            )
            for r in eu_rows
        ]

        pdt_rows = conn.execute(
            """
            SELECT view, COUNT(build_date), MAX(build_date),
                   SUM(bytes_processed), SUM(cost_usd)
            FROM pdt_builds
            WHERE build_date >= ? AND build_date <= ?
            GROUP BY view
            """,
            (start_str, end_str),
        ).fetchall()
        pdt_builds = [
            PDTBuild(
                view=r[0],
                build_count=r[1],
                last_built_at=r[2] + "T00:00:00Z",
                bytes_processed=r[3],
                estimated_cost_usd=round(r[4], 2),
            )
            for r in pdt_rows
        ]

        ref_rows = conn.execute(
            """
            SELECT content_id, content_type, model, explore, title
            FROM content_refs
            WHERE recorded_date >= ? AND recorded_date <= ?
            GROUP BY content_id
            """,
            (start_str, end_str),
        ).fetchall()
        content_references = [
            ContentReference(
                content_id=r[0],
                content_type=r[1],
                model=r[2],
                explore=r[3],
                title=r[4] or "",
            )
            for r in ref_rows
        ]

    period = {"start": start_str, "end": end_str, "days": days}
    return {
        "explore_usage": explore_usage,
        "content_references": content_references,
        "pdt_builds": pdt_builds,
        "period": period,
    }
