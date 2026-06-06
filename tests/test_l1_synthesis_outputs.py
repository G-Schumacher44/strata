import json
import subprocess
import sys
from pathlib import Path

from strata.l1.enrich import enrich_graph
from strata.l1.fixtures import load_usage_facts
from strata.outputs import build_artifacts, write_artifacts
from strata.pipeline import build_graph
from strata.synthesis.slices import build_explore_slice
from strata.synthesis.verdicts import SynthesisVerdict, deterministic_verdict, validate_verdict

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[1]


def test_l1_enrichment_static_usage_intersection_and_pdt_ledger():
    graph = build_graph(FIXTURES)
    facts = load_usage_facts(FIXTURES / "usage_facts.json")

    enrich_graph(graph, facts["explore_usage"], facts["content_references"], facts["pdt_builds"])

    dead_names = {record["name"] for record in graph.metadata["l1"]["dead_code"]}
    assert {"orphan_view", "pdt_orders", "test_model.orphan_explore"} <= dead_names
    pdt = graph.metadata["l1"]["pdt_ledger"][0]
    assert pdt["view"] == "pdt_orders"
    assert pdt["estimated_cost_usd"] == 6.5
    assert pdt["status"] == "unused"


def test_synthesis_slice_and_evidence_validation():
    graph = build_graph(FIXTURES, FIXTURES / "usage_facts.json")

    explore_slice = build_explore_slice(graph, "test_model", "orphan_explore")
    verdict = deterministic_verdict(explore_slice)

    assert verdict.verdict == "deprecate"
    assert validate_verdict(verdict, explore_slice["evidence_ids"]) == []
    bad = SynthesisVerdict(explore_slice["id"], "kill", "missing trail", [])
    assert validate_verdict(bad, explore_slice["evidence_ids"])


def test_output_artifacts_are_deterministic(tmp_path):
    graph = build_graph(FIXTURES, FIXTURES / "usage_facts.json")

    artifacts = build_artifacts(graph)
    written = write_artifacts(graph, tmp_path)

    assert {"catalog", "dead_code_register", "pdt_ledger", "cleanup_roadmap", "migration_impact"} <= set(artifacts)
    assert Path(written["dead_code_register"]).exists()
    loaded = json.loads(Path(written["pdt_ledger"]).read_text(encoding="utf-8"))
    assert loaded[0]["view"] == "pdt_orders"


def test_strata_gate_script_and_output_cli(tmp_path):
    gate = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_strata.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert gate.returncode == 0, gate.stderr

    out = tmp_path / "artifacts"
    generated = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "generate_outputs.py"),
            "--repo",
            str(FIXTURES),
            "--usage-fixture",
            str(FIXTURES / "usage_facts.json"),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert generated.returncode == 0, generated.stderr
    assert (out / "cleanup_roadmap.json").exists()
