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


def _weak_bt_evidence() -> ObservatoryEvidence:
    return ObservatoryEvidence(
        "LIVE-WEAK", "unknown blog", "Low", "Unknown", "BT", "Telecommunications",
        "Operational topic", "Operations", "Why now?", "BT mentions a possible future operational topic.",
        "Unknown source", "https://example.com/weak", 45, ("specific evidence", "source corroboration"), ("test",),
        source_type="unknown", mapped_condition="Unmapped", mapped_capability="operations", is_live=False,
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


def test_raw_agm_share_price_navigation_never_appears_in_top_commercial_signals() -> None:
    html = organisation_observatory_page("BT")
    top = html.split("<section class='card'><h2>Top Commercial Signals</h2>", 1)[1].split("<section class='card'><h2>Commercial Insights</h2>", 1)[0]
    forbidden = ("ANNUAL GENERAL MEETING", "share price details", "Skip to content", "Careers", "Cookie notice")
    assert not any(fragment.lower() in top.lower() for fragment in forbidden)


def test_bt_investor_snippet_supports_mission_criticality_not_ai_adoption() -> None:
    signal = build_commercial_signals((_bt_evidence("BT is a leading UK telecommunications and network provider with a vital role in the lives of our customers and the nation."),))[0]
    assert signal.title == "BT positions itself as nationally important telecoms infrastructure"
    assert "mission-criticality" in signal.supports
    assert "network importance" in signal.supports
    assert "AI adoption" not in signal.supports
    assert "AI adoption" in signal.does_not_support


def test_bt_project_glasswing_supports_ai_enabled_cyber_not_enterprise_transformation() -> None:
    signal = build_commercial_signals((_bt_evidence(),))[0]
    assert signal.title == "BT joins Anthropic Project Glasswing"
    assert signal.evidence_quote == "strengthen cyber defences with frontier AI"
    assert "AI-enabled cyber capability" in signal.supports
    assert "enterprise-wide AI transformation" in signal.does_not_support


def test_weak_signals_are_excluded_from_strong_insights() -> None:
    weak_signal = build_commercial_signals((_weak_bt_evidence(),))[0]
    insights = build_commercial_insights((weak_signal,))
    assert weak_signal.signal_quality_score < 70
    assert insights[0].summary == "insufficient signal quality"
    assert insights[0].hypothesis_type == "weak/single-signal hypothesis"


def test_average_signal_quality_appears_on_bt_page() -> None:
    html = organisation_observatory_page("BT")
    assert "Signal Quality" in html
    assert "Average signal quality" in html


def test_no_recommendation_uses_low_quality_signal_as_primary_support() -> None:
    weak_signal = build_commercial_signals((_weak_bt_evidence(),))[0]
    insights = build_commercial_insights((weak_signal,))
    arguments = build_commercial_arguments(insights, (weak_signal,))
    recommendations = build_executive_recommendations(arguments)
    assert weak_signal.signal_quality_score < 70
    assert recommendations == ()


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
