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
    dossier = items[0]["evidence_dossier"]
    assert dossier["observed_facts"]
    assert dossier["named_sources"][0]["source_name"]
    assert dossier["interpretation"]
    assert dossier["hypotheses"]
    assert dossier["implications"]
    assert dossier["recommended_actions"]
    assert dossier["richness"]["traceability_score"] >= 80


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
    assert evidence.dossier
    assert evidence.dossier.richness.evidence_richness_score > 0


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


def test_generic_responsible_ai_esg_and_careers_are_not_ai_modernisation() -> None:
    source = enabled_sources("BT")[0]
    html = """<p>Responsible AI child rights modern slavery flexible working rewards & benefits our locations search roles careers.</p>"""
    assert extract_evidence(source, html) == []


def test_navigation_heavy_snippets_are_rejected_with_diagnostics() -> None:
    from cios.applications.flora.live.extractor import extract_evidence_with_diagnostics

    source = enabled_sources("BT")[0]
    html = "<nav>Home About us Investors Newsroom Careers Search Roles Contact us Menu AI network</nav>"
    accepted, rejected = extract_evidence_with_diagnostics(source, html)
    assert accepted == []
    assert rejected
    assert rejected[0]["relevance_level"] in {"LOW", "REJECT"}
    assert rejected[0]["accepted_for_claims"] is False


def test_bt_style_policy_snippets_are_downgraded_or_rejected() -> None:
    from cios.applications.flora.live.extractor import extract_evidence_with_diagnostics

    source = enabled_sources("BT")[0]
    accepted, rejected = extract_evidence_with_diagnostics(
        source,
        "<p>BT Responsible AI policy, child rights, modern slavery statement, flexible working and search roles.</p>",
    )
    assert accepted == []
    assert any(item["relevance_level"] in {"LOW", "REJECT"} for item in rejected)


def test_claims_require_high_or_independent_medium_evidence() -> None:
    from cios.applications.flora.live.aggregation import aggregate_live_evidence

    one_medium = [{"organisation": "BT", "source_id": "s1", "commercial_condition": "AI Modernisation", "likely_capability": "AI use-case discovery", "relevance_level": "MEDIUM", "confidence": 60, "overall_evidence_quality": 60}]
    metrics = aggregate_live_evidence(one_medium)["BT"]
    assert "AI Modernisation" in metrics.insufficient_claims
    assert metrics.condition_counts == {}

    two_medium = [*one_medium, {**one_medium[0], "source_id": "s2"}]
    metrics = aggregate_live_evidence(two_medium)["BT"]
    assert metrics.condition_counts["AI Modernisation"] == 2
    assert metrics.insufficient_claims == []


def test_confidence_falls_when_weak_evidence_is_removed_from_claim_support() -> None:
    from cios.applications.flora.live.aggregation import aggregate_live_evidence
    from cios.applications.flora.portfolio import evidence_confidence

    weak = [{"organisation": "BT", "source_id": "s1", "commercial_condition": "AI Modernisation", "likely_capability": "AI", "relevance_level": "MEDIUM", "confidence": 55, "overall_evidence_quality": 55, "evidence_tier": "tier_1_company"}]
    strong = [{**weak[0], "relevance_level": "HIGH", "confidence": 85, "overall_evidence_quality": 85}]
    assert evidence_confidence(aggregate_live_evidence(weak)["BT"]) < evidence_confidence(aggregate_live_evidence(strong)["BT"])


def test_rejected_evidence_is_visible_in_collection_diagnostics(monkeypatch, tmp_path: Path) -> None:
    from cios.applications.flora.live import collect as collect_module
    from cios.applications.flora.live.fetcher import FetchResult

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(collect_module, "enabled_sources", lambda organisation=None: [enabled_sources("BT")[0]])
    monkeypatch.setattr(collect_module, "fetch_html", lambda url: FetchResult(url=url, succeeded=True, status_code=200, html="<p>Responsible AI child rights modern slavery flexible working search roles.</p>", error=None))
    result = collect_module.collect("BT")
    diag = result["diagnostics"][0]
    assert diag["evidence_count"] == 0
    assert diag["rejected_evidence_count"] > 0
    assert diag["unsupported_interpretations"]


def test_no_llm_database_or_broad_crawling_imports() -> None:
    extractor_source = Path("cios/applications/flora/live/extractor.py").read_text()
    collect_source = Path("cios/applications/flora/live/collect.py").read_text()
    forbidden = ("openai", "anthropic", "sqlite3", "sqlalchemy", "crawl")
    for term in forbidden:
        assert term not in extractor_source.lower()
        assert term not in collect_source.lower()


def test_specificity_gate_rejects_govuk_boilerplate_and_service_menus() -> None:
    from cios.applications.flora.live.extractor import extract_evidence, extract_evidence_with_diagnostics
    from cios.applications.flora.live.source_registry import SourceRecord
    dwp = SourceRecord(source_id="dwp-govuk", organisation="DWP", source_name="DWP GOV.UK", source_type="organisation_landing", url="https://www.gov.uk/government/organisations/department-for-work-pensions", sector="Public", evidence_tier="tier_1_public_body", expected_signal_types=["procurement"], coverage_role="context")
    html = "<p>Complaints modern slavery accessibility jobs and contracts working for DWP contact media enquiries publication scheme procurement.</p>"
    accepted, rejected = extract_evidence_with_diagnostics(dwp, html)
    assert accepted == []
    assert rejected
    assert rejected[0]["evidence_type"] == "Context Only"
    assert not rejected[0]["supports_strategic_signals"]

    supplier = SourceRecord(source_id="supplier-services", organisation="Supplier", source_name="Supplier services", source_type="supplier_service_menu", url="https://example.com/services", sector="Technology", evidence_tier="tier_1_company", expected_signal_types=["AI"], coverage_role="context")
    assert extract_evidence(supplier, "<p>Our services include AI cloud cyber data managed services consulting delivery capability contact us.</p>") == []


def test_specificity_gate_accepts_named_date_quantified_and_report_facts() -> None:
    from cios.applications.flora.live.extractor import extract_evidence
    from cios.applications.flora.live.source_registry import SourceRecord
    src = SourceRecord(source_id="nhs-news", organisation="NHS England", source_name="NHS announcement", source_type="official_newsroom", url="https://www.england.nhs.uk/news/example", sector="Health", evidence_tier="tier_1_public_body", expected_signal_types=["AI"], coverage_role="primary")
    item = extract_evidence(src, "<p>On 12 June 2026 NHS England announced the Federated Data Platform rollout to 40 trusts with AI technology supplier support.</p>")[0]
    assert item["accepted_for_claims"]
    assert item["evidence_type"] in {"Primary Evidence", "Secondary Evidence"}
    assert item["cleaned_observation"].startswith("On 12 June 2026")

    report = SourceRecord(source_id="bt-ar", organisation="BT", source_name="BT annual report", source_type="annual_report_landing", url="https://www.bt.com/annual-report", sector="Telecoms", evidence_tier="tier_1_company", expected_signal_types=["investment"], coverage_role="primary")
    fact = extract_evidence(report, "<p>The annual report states capital investment was £4.8bn in 2026 and the cost savings target is £3bn.</p>")[0]
    assert fact["evidence_type"] == "Primary Evidence"
    assert fact["confidence"] >= 70


def test_context_only_evidence_does_not_support_signals_and_coverage_dampens_scores() -> None:
    from cios.applications.flora.live.aggregation import adjust_score, aggregate_live_evidence
    context = [{"organisation": "DWP", "source_id": "s1", "source_type": "organisation_landing", "commercial_condition": "Procurement Readiness", "evidence_type": "Context Only", "supports_strategic_signals": False, "relevance_level": "LOW", "confidence": 50, "overall_evidence_quality": 40}]
    metrics = aggregate_live_evidence(context)["DWP"]
    assert metrics.condition_relevance == 0
    assert not metrics.coverage_sufficient
    assert adjust_score("DWP", 80, metrics).live_evidence_score < 50


def test_bt_profile_selection_reaches_collection_service_from_web(monkeypatch, tmp_path) -> None:
    from cios.applications.flora.web.app import FloraWebHandler
    import http.client
    from http.server import ThreadingHTTPServer

    calls = []
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("cios.applications.flora.web.app.collect", lambda organisation, **kwargs: calls.append((organisation, kwargs)) or None)
    server = ThreadingHTTPServer(("127.0.0.1", 0), FloraWebHandler)
    try:
        import threading
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        body = "enterprise_display_name=BT+Group+plc&canonical_enterprise_id=bt-group-plc&profile_id=bt-group-plc&collection_mode=live_authoritative&collection_pass=baseline"
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
        conn.request("POST", "/live/collect/start", body, {"Content-Type": "application/x-www-form-urlencoded"})
        resp = conn.getresponse(); resp.read()
    finally:
        server.shutdown(); server.server_close()
    assert calls == [("BT Group plc", {"profile_id": "bt-group-plc", "collection_mode": "live_authoritative", "passes": ["baseline"]})]


def test_bt_profile_sources_are_scoped_and_exclude_sap() -> None:
    from cios.applications.flora.live.source_registry import enabled_sources
    sources = enabled_sources("BT Group plc", profile_id="bt-group-plc", passes=["baseline"])
    assert sources
    assert {s.canonical_enterprise_id for s in sources} == {"bt-group-plc"}
    assert all("sap" not in s.source_id.lower() and "vodafone" not in s.source_id.lower() for s in sources)


def test_bt_profile_run_manifest_identity_counts_and_memory_chain(tmp_path, monkeypatch) -> None:
    from cios.applications.flora.live import collect as collect_module

    class DummyResult:
        succeeded = True
        status_code = 200
        html = "<html><body><p>BT is investing in network automation and customer experience data in 2026.</p></body></html>"
        error = None

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(collect_module, "fetch_html", lambda url: DummyResult())
    result = collect_module.collect("BT Group plc", profile_id="bt-group-plc", collection_mode="live_authoritative", passes=["baseline"])
    manifest = result["collection_manifest"]
    assert manifest["run_id"]
    assert manifest["started_at"] and manifest["completed_at"]
    assert manifest["canonical_enterprise_id"] == "bt-group-plc"
    assert len(manifest["sources_attempted"]) == len(manifest["sources_retrieved"]) + len(manifest["sources_failed"])
    assert manifest["evidence_candidates"] >= manifest["evidence_accepted"] + manifest["evidence_rejected"] + manifest["evidence_downgraded"]
    assert manifest["evidence_accepted"] >= 1
    assert manifest["observations_created"] >= 1
    assert manifest["model_attributes_created"] >= 1
    assert result["collection_mode"] == "live_authoritative"


def test_zero_accepted_bt_run_is_not_successful(tmp_path, monkeypatch) -> None:
    from cios.applications.flora.live import collect as collect_module

    class DummyResult:
        succeeded = True
        status_code = 200
        html = "<html><body><p>Plain page without governed signal keywords.</p></body></html>"
        error = None

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(collect_module, "fetch_html", lambda url: DummyResult())
    result = collect_module.collect("BT Group plc", profile_id="bt-group-plc", collection_mode="live_authoritative", passes=["baseline"])
    assert result["accepted_evidence_count"] == 0
    assert result["result_state"] != "completed successfully"
