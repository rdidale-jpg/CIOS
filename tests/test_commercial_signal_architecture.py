from cios.applications.flora.observatory.engine import (
    build_commercial_arguments,
    build_commercial_insights,
    build_commercial_signals,
    build_executive_recommendations,
    build_observatory,
)
from cios.applications.flora.observatory.models import ObservatoryEvidence
from cios.applications.flora.observatory.views import organisation_observatory_page


def _bt_evidence(snippet: str = "BT has joined Project Glasswing to strengthen cyber defences with frontier AI.") -> ObservatoryEvidence:
    return ObservatoryEvidence(
        "LIVE-565DABAF4844", "official announcement", "High", "2026-06-30", "BT", "Telecommunications",
        "AI cyber modernisation", "AI Readiness", "Why AI?", snippet, "BT newsroom", "https://example.com/bt",
        82, ("budget", "executive sponsor"), ("test",), source_type="official_newsroom", mapped_condition="AI Modernisation",
        mapped_capability="cyber capability", extraction_timestamp="2026-06-30T00:00:00+00:00", is_live=True,
    )


def test_commercial_signal_creation_from_accepted_evidence() -> None:
    signals = build_commercial_signals((_bt_evidence(),))
    assert signals[0].signal_id == "SIG-BT-001"
    assert signals[0].supporting_evidence_ids == ("LIVE-565DABAF4844",)
    assert len(signals[0].observation.split()) <= 75


def test_commercial_signal_excludes_unsupported_extrapolation_and_lists_boundaries() -> None:
    signal = build_commercial_signals((_bt_evidence(),))[0]
    assert "enterprise-wide AI transformation" not in signal.supports
    assert "enterprise-wide AI transformation" in signal.does_not_support
    assert signal.supports
    assert signal.does_not_support


def test_insights_require_multiple_signals_or_single_signal_label() -> None:
    one = build_commercial_insights(build_commercial_signals((_bt_evidence(),)))[0]
    assert one.hypothesis_type == "single-signal hypothesis"
    two = build_commercial_insights(build_commercial_signals((_bt_evidence(), _bt_evidence("BT Business launched Mission Boost as the first capability in a new portfolio."))))[0]
    assert two.hypothesis_type == "multi-signal insight"


def test_arguments_and_recommendations_reference_layers_not_raw_evidence() -> None:
    signals = build_commercial_signals((_bt_evidence(), _bt_evidence("BT Business launched Mission Boost as the first capability in a new portfolio.")))
    insights = build_commercial_insights(signals)
    arguments = build_commercial_arguments(insights, signals)
    recommendations = build_executive_recommendations(arguments)
    assert arguments[0].supporting_insight_ids
    assert arguments[0].supporting_signal_ids
    assert "Project Glasswing" not in arguments[0].claim
    assert recommendations[0].supporting_argument_ids == (arguments[0].argument_id,)


def test_bt_project_glasswing_does_not_prove_enterprise_wide_transformation() -> None:
    signal = build_commercial_signals((_bt_evidence(),))[0]
    insight = build_commercial_insights((signal,))[0]
    assert "does not prove enterprise-wide AI transformation" in insight.summary
    assert "enterprise-wide AI transformation" in signal.does_not_support


def test_raw_boilerplate_does_not_appear_in_executive_sections_and_drilldown_remains() -> None:
    signal = build_commercial_signals((_bt_evidence("Skip to content | Careers | Cookie notice | BT has joined Project Glasswing to strengthen cyber defences with frontier AI."),))[0]
    assert "Skip to content" not in signal.observation
    html = organisation_observatory_page("BT")
    assert "Executive Snapshot" in html
    assert "Evidence Drill-down" in html


def test_knowledge_graph_links_full_commercial_chain() -> None:
    obs = build_observatory()
    relationships = {edge.relationship for edge in obs.graph_edges}
    assert {"supports_signal", "supports_insight", "supports_argument", "supports_recommendation"} <= relationships
    assert "contradicts_signal" in relationships


def test_no_llm_database_or_broad_crawling_imports_for_pipeline() -> None:
    from pathlib import Path
    text = "\n".join(Path(p).read_text(encoding="utf-8") for p in ["cios/applications/flora/observatory/engine.py", "cios/applications/flora/observatory/views.py"])
    forbidden = ["openai", "langchain", "sqlalchemy", "sqlite3", "psycopg", "crawl"]
    assert not any(term in text.lower() for term in forbidden)
