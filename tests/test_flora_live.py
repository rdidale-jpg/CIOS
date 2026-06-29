from __future__ import annotations

import ast
import json
from pathlib import Path

from cios.applications.flora.live.extractor import extract_evidence, interpret_keyword, to_commercial_evidence
from cios.applications.flora.live.fetcher import fetch_html
from cios.applications.flora.live.source_registry import enabled_sources
from cios.applications.flora.live.store import write_jsonl
from cios.applications.flora.publisher.morning_edition import build_publication_context, render_markdown


def test_source_registry_construction() -> None:
    sources = enabled_sources("ThamesWater")
    assert len(sources) == 3
    assert {s.organisation for s in sources} == {"Thames Water"}
    assert all(s.evidence_tier.startswith("tier_1_") for s in sources)


def test_fetch_failure_handling() -> None:
    result = fetch_html("http://127.0.0.1:1/not-running", timeout=0.1)
    assert not result.succeeded
    assert result.error


def test_deterministic_extraction_from_sample_html() -> None:
    source = enabled_sources("BT")[0]
    html = "<html><body><h1>AI and automation</h1><p>BT is investing in network automation and customer experience data.</p></body></html>"
    items = extract_evidence(source, html)
    assert items
    assert items[0]["organisation"] == "BT"
    assert items[0]["snippet"]
    assert items[0]["source_url"]


def test_mapping_evidence_to_conditions() -> None:
    condition, capability, relevance, confidence = interpret_keyword("automation")
    assert condition == "Operational Efficiency"
    assert "automation" in capability
    assert "AI reinvention" in relevance
    assert confidence >= 60


def test_commercial_evidence_compatible_mapping() -> None:
    source = enabled_sources("Vodafone")[0]
    item = extract_evidence(source, "<p>Vodafone network efficiency and data modernisation.</p>")[0]
    evidence = to_commercial_evidence(item)
    assert evidence.evidence_id == item["evidence_id"]
    assert evidence.extracted_observation == item["snippet"]
    assert evidence.capability_tags


def test_live_evidence_jsonl_writing(tmp_path: Path) -> None:
    path = tmp_path / "live_evidence.jsonl"
    output = write_jsonl([{"evidence_id": "LIVE-1", "organisation": "BT"}], path)
    assert output == path
    assert json.loads(path.read_text().strip())["evidence_id"] == "LIVE-1"


def test_morning_edition_live_and_fallback_banner(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    fallback = render_markdown(build_publication_context())
    assert "NO LIVE EVIDENCE AVAILABLE — use /live/collect to attempt collection" in fallback
    write_jsonl([{
        "evidence_id": "LIVE-1", "organisation": "BT", "source_name": "BT newsroom", "source_url": "https://newsroom.bt.com/", "source_type": "company_newsroom", "snippet": "BT mentions AI for network operations.", "extraction_timestamp": "2026-06-29T00:00:00+00:00", "commercial_condition": "AI Modernisation", "missing_evidence": ["budget"], "evidence_tier": "tier_1_company",
    }])
    live = render_markdown(build_publication_context())
    assert "LIVE EVIDENCE USED" in live
    assert "BT mentions AI for network operations" in live


def test_no_llm_or_database_imports_in_flora() -> None:
    forbidden = {"openai", "anthropic", "langchain", "llama_index", "sqlalchemy", "sqlite", "sqlite3", "pymongo", "psycopg", "psycopg2"}
    for path in Path("cios/applications/flora").rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported = {node.module.split(".")[0]}
            else:
                continue
            assert forbidden.isdisjoint(imported), f"{path} imports {forbidden & imported}"


def test_source_diagnostics_are_written(tmp_path: Path, monkeypatch) -> None:
    from cios.applications.flora.live import collect as collect_module
    from cios.applications.flora.live.store import DEFAULT_DIAGNOSTICS_PATH, read_jsonl

    class DummyResult:
        succeeded = False
        status_code = 403
        html = ""
        error = "HTTP 403: Forbidden"

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(collect_module, "fetch_html", lambda url: DummyResult())
    result = collect_module.collect("BT")
    diagnostics = read_jsonl(DEFAULT_DIAGNOSTICS_PATH)
    assert result["sources_failed"] == 3
    assert diagnostics
    assert diagnostics[0]["source_id"]
    assert diagnostics[0]["success"] is False
    assert diagnostics[0]["http_status"] == 403


def test_collection_failures_display_clearly(tmp_path: Path, monkeypatch) -> None:
    from cios.applications.flora.live import collect as collect_module
    from cios.applications.flora.live.views import collection_result

    class DummyResult:
        succeeded = False
        status_code = None
        html = ""
        error = "tunnel 403"

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(collect_module, "fetch_html", lambda url: DummyResult())
    html = collection_result(collect_module.collect("BT"))
    assert "failed 3" in html
    assert "tunnel 403" in html
