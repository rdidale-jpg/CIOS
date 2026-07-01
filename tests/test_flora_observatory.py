from cios.applications.flora.observatory.engine import build_observatory
from cios.applications.flora.observatory.models import HypothesisStatus


def test_observatory_builds_three_board_usable_cases() -> None:
    obs = build_observatory()
    assert obs.critique_path.endswith("Enterprise_Transformation_Observatory_Architectural_Critique.md")
    assert len(obs.organisations) == 3
    assert all(org.case_for_change.why_act for org in obs.organisations)
    assert all(org.case_for_change.supporting_evidence_ids for org in obs.organisations)
    assert all(org.case_for_change.conversation_level in {"Operational", "Business", "Executive", "Board"} for org in obs.organisations)


def test_genome_dimensions_are_explainable_not_hidden_scores() -> None:
    obs = build_observatory()
    dimension_names = {dimension.name for org in obs.organisations for dimension in org.genome}
    assert "Transformation Inevitability Index (TII)" in dimension_names
    for org in obs.organisations:
        for dimension in org.genome:
            assert dimension.reasoning
            assert dimension.unknowns
            assert dimension.evidence_quality
            assert isinstance(dimension.confidence, int)


def test_research_notebook_retains_hypothesis_status_and_evidence() -> None:
    obs = build_observatory()
    assert {h.status for h in obs.hypotheses} >= {HypothesisStatus.STRENGTHENING, HypothesisStatus.NEEDS_MORE_EVIDENCE}
    assert all(h.supporting_evidence_ids for h in obs.hypotheses)
    assert all(h.commercial_implications for h in obs.hypotheses)


def test_knowledge_graph_edges_separate_observed_and_inferred_relationships() -> None:
    obs = build_observatory()
    assert any(not edge.inferred for edge in obs.graph_edges)
    assert any(edge.inferred for edge in obs.graph_edges)
    assert all(edge.evidence_ids for edge in obs.graph_edges)


def test_seeded_commercial_evidence_includes_structured_dossiers() -> None:
    from cios.applications.flora.intelligence.evidence_engine import evidence_for_organisation

    evidence = evidence_for_organisation("BT")
    assert evidence
    dossier = evidence[0].dossier
    assert dossier is not None
    assert dossier.observed_facts
    assert dossier.quantitative_facts
    assert dossier.named_sources
    assert dossier.strategic_messages
    assert dossier.competitor_comparisons
    assert dossier.sector_benchmarks
    assert dossier.transformation_timeline
    assert dossier.interpretation
    assert dossier.hypotheses
    assert dossier.implications
    assert dossier.recommended_actions
    assert dossier.richness.evidence_richness_score > 0


def test_cross_sector_observations_are_not_character_split() -> None:
    from cios.applications.flora.observatory.views import observatory_page

    html = observatory_page()
    assert "<li>T</li><li>r</li>" not in html
    assert "Transformation is most commercially useful" in html


def test_observatory_prefers_live_evidence_and_renders_receipts(monkeypatch, tmp_path) -> None:
    from cios.applications.flora.live import store
    from cios.applications.flora.observatory import engine
    from cios.applications.flora.observatory.views import organisation_observatory_page

    evidence_path = tmp_path / "live_evidence.jsonl"
    rows = [
        {"evidence_id": "DWP-LIVE-1", "source_id": "dwp-annual", "organisation": "DWP", "sector": "Public Sector", "source_name": "DWP annual report", "source_url": "https://example.gov.uk/dwp-annual", "source_type": "annual_report", "snippet": "DWP served 20 million citizens and references £240 billion of payments in 2026.", "extraction_timestamp": "2026-06-30T00:00:00+00:00", "commercial_condition": "Citizen Experience", "likely_capability": "casework intelligence", "confidence": 92, "overall_evidence_quality": 90, "evidence_tier": "tier_1_public_body"},
        {"evidence_id": "BT-LIVE-1", "source_id": "bt-news", "organisation": "BT", "sector": "Telecommunications", "source_name": "BT newsroom", "source_url": "https://example.com/bt", "source_type": "official_newsroom", "snippet": "BT expands AI network operations in 2026.", "extraction_timestamp": "2026-06-29T00:00:00+00:00", "commercial_condition": "AI Modernisation", "likely_capability": "network intelligence", "confidence": 88, "overall_evidence_quality": 86, "evidence_tier": "tier_1_company"},
        {"evidence_id": "NG-LIVE-1", "source_id": "ng-report", "organisation": "National Grid", "sector": "Energy", "source_name": "National Grid report", "source_url": "https://example.com/ng", "source_type": "annual_report", "snippet": "National Grid announced 2026 grid connection reforms.", "extraction_timestamp": "2026-06-28T00:00:00+00:00", "commercial_condition": "Operational Resilience", "likely_capability": "grid forecasting", "confidence": 86, "overall_evidence_quality": 84, "evidence_tier": "tier_1_company"},
    ]
    store.write_jsonl(rows, evidence_path)
    monkeypatch.setattr(engine, "DEFAULT_PATH", evidence_path)

    obs = engine.build_observatory()
    assert any(e.evidence_id == "DWP-LIVE-1" and e.is_live for e in obs.evidence)
    assert not any(e.evidence_id.startswith("ETO-EV-") for e in obs.evidence)
    html = organisation_observatory_page("DWP")
    assert "DWP-LIVE-1" in html
    assert "DWP annual report" in html
    assert "https://example.gov.uk/dwp-annual" in html
    assert "Citizen Experience" in html
    assert "casework intelligence" in html
    assert "Key Facts &amp; Figures" in html
    assert "20 million" in html
    assert "£240 billion" in html
    assert "Evidence strength metrics" in html
    assert "Transformation Timeline" in html
    assert "Operational cost/risk" in html
    assert "Possible counterarguments" in html


def test_seeded_observatory_evidence_is_clearly_labelled(monkeypatch, tmp_path) -> None:
    from cios.applications.flora.observatory import engine

    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    monkeypatch.setattr(engine, "DEFAULT_PATH", empty)
    obs = engine.build_observatory()
    assert any(e.evidence_id.startswith("ETO-EV-") for e in obs.evidence)
    assert all("SEEDED / SYNTHETIC / FALLBACK" in e.evidence_class or "SEEDED / SYNTHETIC / FALLBACK" in e.summary for e in obs.evidence)


def test_observatory_no_llm_database_or_broad_crawling_imports() -> None:
    from pathlib import Path

    text = "\n".join(Path(p).read_text(encoding="utf-8") for p in ["cios/applications/flora/observatory/engine.py", "cios/applications/flora/observatory/views.py"])
    forbidden = ["openai", "anthropic", "langchain", "sqlalchemy", "sqlite3", "psycopg", "crawl"]
    assert not any(term in text.lower() for term in forbidden)
