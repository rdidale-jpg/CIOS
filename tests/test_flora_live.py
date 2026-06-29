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


def test_repeated_collection_does_not_increase_evidence_count(tmp_path: Path, monkeypatch) -> None:
    from cios.applications.flora.live import collect as collect_module
    from cios.applications.flora.live.store import DEFAULT_PATH, read_jsonl

    class DummyResult:
        succeeded = True
        status_code = 200
        html = "<html><body><p>BT is investing in network automation and customer experience data.</p></body></html>"
        error = None

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(collect_module, "fetch_html", lambda url: DummyResult())

    first = collect_module.collect("BT")
    first_count = len(read_jsonl(DEFAULT_PATH))
    second = collect_module.collect("BT")
    second_count = len(read_jsonl(DEFAULT_PATH))

    assert first["sources_attempted"] == 3
    assert first["evidence_objects_extracted"] > 0
    assert first["new_evidence_added"] == first_count
    assert first["duplicate_evidence_skipped"] == 0
    assert second["sources_attempted"] == 3
    assert second["evidence_objects_extracted"] == first["evidence_objects_extracted"]
    assert second["new_evidence_added"] == 0
    assert second["duplicate_evidence_skipped"] == first["evidence_objects_extracted"]
    assert second["total_unique_evidence_objects"] == first_count
    assert second_count == first_count


def test_current_status_reports_unique_evidence_objects(tmp_path: Path, monkeypatch) -> None:
    from cios.applications.flora.live.collect import current_status
    from cios.applications.flora.live.store import write_jsonl

    monkeypatch.chdir(tmp_path)
    evidence = {
        "evidence_id": "LIVE-1",
        "organisation": "BT",
        "source_id": "bt-official-newsroom",
        "source_url": "https://newsroom.bt.com/",
        "snippet": "BT mentions AI for network operations.",
        "commercial_condition": "AI Modernisation",
        "likely_capability": "AI use-case discovery",
    }
    write_jsonl([evidence, {**evidence, "evidence_id": "LIVE-2"}])

    status = current_status()

    assert status["evidence_objects_collected"] == 1
    assert status["total_unique_evidence_objects"] == 1


def test_source_diagnostics_categorisation() -> None:
    from cios.applications.flora.live.collect import categorise_failure

    assert categorise_failure(succeeded=False, http_status=403, error="Forbidden", evidence_count=0) == "access_blocked"
    assert categorise_failure(succeeded=False, http_status=None, error="timed out", evidence_count=0) == "timeout"
    assert categorise_failure(succeeded=False, http_status=200, error="non-html content type: application/pdf", evidence_count=0) == "non_html"
    assert categorise_failure(succeeded=True, http_status=200, error=None, evidence_count=0) == "no_relevant_evidence"
    assert categorise_failure(succeeded=True, http_status=200, error=None, evidence_count=1) is None


def test_no_relevant_evidence_is_not_failure(tmp_path: Path, monkeypatch) -> None:
    from cios.applications.flora.live import collect as collect_module

    class DummyResult:
        succeeded = True
        status_code = 200
        html = "<html><body><p>Plain page without configured commercial keywords.</p></body></html>"
        error = None

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(collect_module, "fetch_html", lambda url: DummyResult())
    result = collect_module.collect("BT")

    assert result["sources_failed"] == 0
    assert result["sources_succeeded"] == 3
    assert {d["status"] for d in result["diagnostics"]} == {"no evidence"}
    assert {d["failure_reason"] for d in result["diagnostics"]} == {"no_relevant_evidence"}


def test_source_registry_expanded_organisations() -> None:
    from cios.applications.flora.live.source_registry import SOURCES

    organisations = {source.organisation for source in SOURCES}
    assert {"United Utilities", "SSE", "Sky", "BBC"}.issubset(organisations)
    source_types = {source.source_type for source in SOURCES}
    assert {"official_newsroom", "official_rss_or_feed", "regulator_publications", "investor_results", "annual_report_landing", "strategy_page"}.issubset(source_types)
    for organisation in {"United Utilities", "SSE", "Sky", "BBC"}:
        enabled = [source for source in SOURCES if source.organisation == organisation and source.enabled]
        assert any(source.source_type == "official_newsroom" for source in enabled)
        assert any(source.source_type in {"investor_results", "annual_report_landing"} for source in enabled)
        assert any(source.source_type == "regulator_publications" for source in enabled)


def test_sources_page_route(monkeypatch, tmp_path) -> None:
    from cios.applications.flora.live.views import sources_page

    monkeypatch.chdir(tmp_path)
    html = sources_page()

    assert "Live source coverage" in html
    assert "Recommended action" in html
    assert "united-utilities-news" in html


def test_morning_edition_coverage_summary(tmp_path: Path, monkeypatch) -> None:
    from cios.applications.flora.live.store import DEFAULT_DIAGNOSTICS_PATH, write_jsonl
    from cios.applications.flora.publisher.morning_edition import build_publication_context, render_markdown

    monkeypatch.chdir(tmp_path)
    write_jsonl([
        {"source_id": "bt-official-newsroom", "organisation": "BT", "status": "succeeded", "success": True, "evidence_count": 2, "last_attempted": "2026-06-29T00:00:00+00:00"},
        {"source_id": "sky-official-newsroom", "organisation": "Sky", "status": "no evidence", "success": False, "evidence_count": 0, "last_attempted": "2026-06-29T00:00:00+00:00", "failure_reason": "no_relevant_evidence"},
    ], DEFAULT_DIAGNOSTICS_PATH)

    ctx = build_publication_context()
    markdown = render_markdown(ctx)

    assert ctx["live_coverage_summary"]["sources_attempted"] == 2
    assert ctx["live_coverage_summary"]["sources_produced_evidence"] == 1
    assert "### Live Evidence Coverage" in markdown
    assert "Strongest covered organisations: BT" in markdown
    assert "Uncovered organisations: Sky" in markdown


def test_flora_v07_required_groups_and_metadata() -> None:
    from cios.applications.flora.live.source_registry import SOURCES

    required = {
        "Utilities": {"Thames Water", "United Utilities", "Severn Trent", "Southern Water", "Yorkshire Water", "Anglian Water", "Northumbrian Water", "South West Water / Pennon", "Wessex Water", "Affinity Water", "Portsmouth Water", "SES Water"},
        "Energy": {"National Grid", "SSE", "Centrica", "EDF Energy UK", "Octopus Energy", "ScottishPower", "E.ON UK", "RWE UK", "Drax", "OVO Energy", "UK Power Networks", "SP Energy Networks"},
        "Telecommunications": {"BT", "Vodafone", "Virgin Media O2", "TalkTalk", "Three UK", "Openreach", "CityFibre", "Hyperoptic", "KCOM", "Gamma Communications"},
        "Media": {"Sky", "BBC", "ITV", "Channel 4", "Channel 5 / Paramount UK", "The Guardian", "News UK", "DMG Media", "Reach plc", "Global", "Bauer Media"},
        "Sport": {"Premier League", "The Football Association", "England and Wales Cricket Board", "Rugby Football Union", "Wimbledon / AELTC", "British Olympic Association", "UK Sport", "Sport England", "England Netball", "British Cycling", "Formula 1 / Silverstone"},
        "Public Sector": {"Ministry of Defence", "DWP", "Ministry of Justice", "HMRC", "DEFRA", "Department of Health and Social Care", "NHS England", "Home Office", "Cabinet Office", "Department for Education", "Department for Transport", "DSIT", "DESNZ", "MHCLG", "FCDO", "UKHSA", "Environment Agency", "HM Treasury"},
        "Regulators": {"Ofwat", "Ofgem", "Ofcom", "CMA", "ICO", "National Audit Office", "Infrastructure and Projects Authority", "UK Regulators Network"},
        "Competitors": {"IBM", "Accenture", "Capgemini", "Deloitte", "KPMG", "PwC", "Cognizant", "CGI", "TCS", "Infosys", "Wipro", "Atos / Eviden", "Fujitsu", "Sopra Steria", "DXC Technology", "NTT DATA", "Oracle", "Microsoft", "ServiceNow", "Salesforce", "SAP"},
    }
    by_sector: dict[str, set[str]] = {}
    for source in SOURCES:
        by_sector.setdefault(source.sector, set()).add(source.organisation)
        if source.enabled:
            assert source.source_id and source.organisation and source.source_name and source.source_type and source.url
            assert source.evidence_tier and source.expected_signal_types and source.coverage_role and source.notes
            assert "search" not in str(source.url).lower()
            assert "google." not in str(source.url).lower()
            assert "bing." not in str(source.url).lower()
    for sector, orgs in required.items():
        assert orgs.issubset(by_sector.get(sector, set()))


def test_flora_v07_quality_and_condition_mapping() -> None:
    from cios.applications.flora.live.extractor import extract_evidence
    from cios.applications.flora.live.source_registry import SOURCES

    dwp = next(source for source in SOURCES if source.organisation == "DWP" and source.enabled)
    public = extract_evidence(dwp, "<p>Citizen experience and procurement readiness for legacy technology.</p>")
    assert public[0]["overall_evidence_quality"] > 0
    assert public[0]["commercial_condition"] in {"Citizen Experience", "Cyber Resilience", "Procurement Readiness", "Legacy Technology"}

    ibm = next(source for source in SOURCES if source.organisation == "IBM" and source.enabled)
    competitor = extract_evidence(ibm, "<p>Managed services and cloud modernisation strengthen consulting growth, partnership ecosystem and delivery capability.</p>")
    assert competitor[0]["commercial_condition"] in {"Managed Services", "Consulting Growth", "Partnership Ecosystem", "Delivery Capability", "Technology Debt"}


def test_flora_v07_sources_page_and_morning_summary() -> None:
    from cios.applications.flora.live.views import sources_page
    from cios.applications.flora.publisher.morning_edition import build_publication_context, render_markdown

    html = sources_page()
    assert "Total organisations configured" in html
    assert "Sources by sector" in html
    assert "Sources by source_type" in html
    ctx = build_publication_context()
    summary = ctx["live_coverage_summary"]
    assert summary["organisations_configured"] >= 100
    assert "failed_source_count" in summary
    assert "source_coverage_health" in summary
    assert "Uncovered priority organisations" in render_markdown(ctx)


def test_flora_v08_portfolio_radar_and_source_effectiveness(monkeypatch, tmp_path) -> None:
    from cios.applications.flora.live import store
    monkeypatch.setattr(store, "DEFAULT_PATH", tmp_path / "evidence.jsonl")
    monkeypatch.setattr(store, "DEFAULT_DIAGNOSTICS_PATH", tmp_path / "diagnostics.jsonl")
    monkeypatch.setattr("cios.applications.flora.portfolio.DEFAULT_PATH", tmp_path / "evidence.jsonl")
    monkeypatch.setattr("cios.applications.flora.portfolio.DEFAULT_DIAGNOSTICS_PATH", tmp_path / "diagnostics.jsonl")
    monkeypatch.setattr("cios.applications.flora.live.views.DEFAULT_PATH", tmp_path / "evidence.jsonl")
    monkeypatch.setattr("cios.applications.flora.live.collect.DEFAULT_DIAGNOSTICS_PATH", tmp_path / "diagnostics.jsonl")
    monkeypatch.setattr("cios.applications.flora.live.collect.read_jsonl", store.read_jsonl)
    store.write_jsonl([
        {"source_id": "bt-official-newsroom", "organisation": "BT", "source_name": "BT newsroom", "source_url": "https://example.com", "source_type": "official_newsroom", "snippet": "BT AI network operations", "extraction_timestamp": "2026-06-29T00:00:00+00:00", "commercial_condition": "AI Modernisation", "likely_capability": "network intelligence", "confidence": 90, "overall_evidence_quality": 88, "evidence_tier": "tier_1_company"},
    ], tmp_path / "evidence.jsonl")
    store.write_jsonl([
        {"source_id": "bt-official-newsroom", "organisation": "BT", "status": "succeeded", "success": True, "evidence_count": 1, "last_attempted": "2026-06-29T00:00:00+00:00"},
        {"source_id": "sky-official-newsroom", "organisation": "Sky", "status": "no evidence", "success": False, "evidence_count": 0, "last_attempted": "2026-06-29T00:00:00+00:00", "failure_reason": "no_relevant_evidence"},
    ], tmp_path / "diagnostics.jsonl")

    from cios.applications.flora.portfolio import build_radar_rows, evidence_confidence, quadrant_for, source_effectiveness_rows
    from cios.applications.flora.seed_data import sample_watchlist
    from cios.applications.flora.workspace.views import radar_page
    from cios.applications.flora.live.views import source_effectiveness_page, sources_page
    from cios.applications.flora.publisher.morning_edition import render_markdown, build_publication_context

    assert quadrant_for(80, 80) == "Priority Pursuits"
    rows = build_radar_rows()
    assert len(rows) == len(sample_watchlist())
    bt = next(row for row in rows if row.organisation == "BT")
    assert bt.evidence_confidence > 0
    assert evidence_confidence(None) == 0
    assert "base score" in bt.rank_change_reason.lower() or "Live evidence improved rank" in bt.rank_change_reason
    radar_html = radar_page()
    assert "Flora Portfolio Radar" in radar_html
    assert "rank_change_reason" in radar_html
    assert "Base score" in radar_html or "Base Score" in radar_html
    assert "Live uplift" in radar_html or "Live Uplift" in radar_html
    assert all(account.organisation_name in radar_html for account in sample_watchlist())

    effectiveness = source_effectiveness_rows()
    assert effectiveness
    assert any(row.source_id == "bt-official-newsroom" and row.unique_evidence_count == 1 for row in effectiveness)
    assert "Source effectiveness" in source_effectiveness_page()
    sources_html = sources_page()
    assert "succeeded with evidence" in sources_html
    assert "succeeded but no evidence" in sources_html

    md = render_markdown(build_publication_context())
    assert "Portfolio Radar Summary" in md
