"""End-to-end tests for the Sprint 7A Opportunity Assistant vertical slice."""

from cios.applications.opportunity_assistant.pipeline import render_console_report, run_pipeline


def test_opportunity_assistant_pipeline_executes_complete_vertical_slice() -> None:
    result = run_pipeline()

    assert result["evidence"]
    assert result["ontology"]["opportunity"].name == "Acme Secure Cloud Transformation"
    assert result["graph"].nodes
    assert result["graph"].edges
    assert len(result["rule_matches"]) == 6
    assert all(rule.matched for rule in result["rule_matches"])
    assert len(result["observations"]) == 6
    assert len(result["reasoning"]["signals"]) == 6
    assert len(result["reasoning"]["trace"].steps) == 6
    assert result["scoring"]["result"].overall_score.value >= 75
    assert result["decision"].outcome == "selected"
    assert result["decision"].recommendations

    report = render_console_report(result)

    assert "Observations:" in report
    assert "Signals:" in report
    assert "Scores:" in report
    assert "Recommendation:" in report
    assert "Confidence:" in report
    assert "Reasoning Trace Summary:" in report
