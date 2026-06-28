"""End-to-end tests for the Sprint 7A Opportunity Assistant vertical slice."""

from pathlib import Path

from cios.applications.opportunity_assistant.pipeline import OpportunityPipelineResult, render_console_report, run_pipeline
from cios.applications.opportunity_assistant.rules import detect_rules, score_rule_detections

FIXTURE_DIR = Path(__file__).with_name("fixtures") / "opportunity_assistant"
LOW_VALUE_SIMPLE = FIXTURE_DIR / "low_value_simple_opportunity.json"
NO_COMPETITORS_NO_SECURITY = FIXTURE_DIR / "no_competitors_no_security_opportunity.json"


def _rules_by_name(result: OpportunityPipelineResult):
    return {rule.name: rule for rule in result.rule_matches}


def test_opportunity_assistant_pipeline_executes_complete_vertical_slice() -> None:
    result = run_pipeline()

    assert isinstance(result, OpportunityPipelineResult)
    assert result.evidence
    assert result.ontology.opportunity.name == "Acme Secure Cloud Transformation"
    assert result.graph.nodes
    assert result.graph.edges
    assert len(result.rule_matches) == 6
    assert all(rule.matched for rule in result.rule_matches)
    assert len(result.observations) == 6
    assert len(result.reasoning.signals) == 6
    assert len(result.reasoning.trace.steps) == 6
    assert result.scoring.result.overall_score.value >= 75
    assert result.decision.outcome == "selected"
    assert result.decision.recommendations

    report = render_console_report(result)

    assert "Observations:" in report
    assert "Signals:" in report
    assert "Scores:" in report
    assert "Recommendation:" in report
    assert "Confidence:" in report
    assert "Reasoning Trace Summary:" in report


def test_low_value_simple_opportunity_does_not_fire_absent_rules() -> None:
    result = run_pipeline(LOW_VALUE_SIMPLE)

    rules = _rules_by_name(result)

    assert not rules["High Value Opportunity"].matched
    assert not rules["Oracle Transformation"].matched
    assert not rules["Security Critical"].matched
    assert not rules["Managed Service"].matched
    assert not rules["Long-Term Contract"].matched
    assert not rules["Multi-Competitor"].matched
    assert result.scoring.result.band.name == "Low"


def test_no_competitors_no_security_opportunity_only_fires_present_criteria() -> None:
    result = run_pipeline(NO_COMPETITORS_NO_SECURITY)

    rules = _rules_by_name(result)

    assert rules["High Value Opportunity"].matched
    assert rules["Oracle Transformation"].matched
    assert not rules["Security Critical"].matched
    assert not rules["Managed Service"].matched
    assert rules["Long-Term Contract"].matched
    assert not rules["Multi-Competitor"].matched
    assert result.ontology.competitors == []


def test_rule_detection_is_separate_from_scoring_policy() -> None:
    source = {
        "name": "No Criteria",
        "customer": {"name": "Example"},
        "description": "Basic staff augmentation.",
        "value": 1,
        "duration_months": 1,
        "current_platforms": [],
        "requirements": [],
        "competitors": [],
        "capabilities": [],
    }

    detections = detect_rules(source)
    matches = score_rule_detections(detections)

    assert all(detection.matched is False for detection in detections)
    assert all(match.score > 0 for match in matches)
    assert [detection.name for detection in detections] == [match.name for match in matches]
