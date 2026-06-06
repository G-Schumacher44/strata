import json
import subprocess
import sys
from pathlib import Path

import pytest

from strata.l1.fixtures import FixtureUsageProvider
from strata.l1.provider import UsageFacts
from strata.l1.replay import ReplayLookerUsageProvider
from strata.pipeline import build_graph_with_provider

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "provider",
    [
        FixtureUsageProvider(FIXTURES / "usage_facts.json"),
        ReplayLookerUsageProvider(FIXTURES / "replay_facts.json"),
    ],
)
def test_usage_provider_contract(provider):
    facts = UsageFacts.from_provider(provider)

    usage_by_key = {item.key: item for item in facts.explore_usage}
    assert usage_by_key["test_model.customer"].query_count == 42
    assert usage_by_key["test_model.customer"].last_queried_at
    assert usage_by_key["test_model.orphan_explore"].query_count == 0
    assert facts.content_references[0].content_id == "dash_1"
    assert facts.pdt_builds[0].view == "pdt_orders"
    assert facts.pdt_builds[0].build_count == 30
    assert facts.pdt_builds[0].estimated_cost_usd == 6.5


def test_replay_provider_aggregates_raw_rows():
    facts = UsageFacts.from_provider(ReplayLookerUsageProvider(FIXTURES / "replay_facts.json"))
    usage_by_key = {item.key: item for item in facts.explore_usage}

    assert usage_by_key["test_model.customer"].query_count == 42
    assert usage_by_key["test_model.customer"].last_queried_at == "2026-06-02T12:00:00Z"
    assert facts.pdt_builds[0].bytes_processed == 1200000000


def test_replay_provider_fails_fast_on_missing_required_fields(tmp_path):
    replay = tmp_path / "bad_replay.json"
    replay.write_text(json.dumps({"query_history_rows": [{"model": "test_model"}]}), encoding="utf-8")

    with pytest.raises(ValueError, match="explore"):
        ReplayLookerUsageProvider(replay).explore_usage()


def test_build_graph_with_replay_provider_matches_l1_contract():
    graph = build_graph_with_provider(FIXTURES, ReplayLookerUsageProvider(FIXTURES / "replay_facts.json"))

    assert graph.metadata["l1"]["explore_usage"]["test_model.customer"]["query_count"] == 42
    assert {item["name"] for item in graph.metadata["l1"]["dead_code"]} >= {
        "orphan_view",
        "pdt_orders",
        "test_model.orphan_explore",
    }
    assert graph.metadata["l1"]["pdt_ledger"][0]["estimated_cost_usd"] == 6.5


def test_check_replay_cli():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_replay.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert '"total_queries": 49' in result.stdout
