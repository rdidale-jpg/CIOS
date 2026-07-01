from cios.applications.flora.opportunity_shaping import build_opportunity_report
from cios.applications.flora.seed_data import sample_signals, sample_watchlist


def _report(name: str):
    account = next(a for a in sample_watchlist() if a.organisation_name == name)
    signals = [s for s in sample_signals() if s.organisation == name]
    return build_opportunity_report(account, signals)


def test_eose_generates_enterprise_specific_outputs_without_named_people():
    bt = _report("BT")
    dwp = _report("DWP")
    grid = _report("National Grid")

    assert bt.enterprise_dna.sector == "Telecommunications"
    assert dwp.enterprise_dna.sector == "Public Sector"
    assert grid.enterprise_dna.sector == "Energy"
    assert "Ofcom" in bt.source_profile
    assert "GOV.UK" in dwp.source_profile
    assert "NESO" in grid.source_profile
    assert bt.hypotheses[0].transformation_theme != dwp.hypotheses[0].transformation_theme
    assert all("conversation" in h.recommended_conversation.lower() for h in bt.hypotheses + dwp.hypotheses + grid.hypotheses)


def test_eose_preserves_traceability_and_qualification_ladder():
    report = _report("DWP")
    hypothesis = report.hypotheses[0]

    assert hypothesis.supporting_commercial_arguments
    assert hypothesis.supporting_commercial_insights
    assert hypothesis.supporting_strategic_signals
    assert hypothesis.evidence_trace
    trace = hypothesis.evidence_trace[0]
    assert trace.commercial_argument
    assert trace.commercial_insight
    assert trace.strategic_signal_id
    assert trace.raw_evidence
    assert trace.source
    assert hypothesis.issue_qualification_ladder["validation_required"]
    assert hypothesis.issue_qualification_ladder["disqualifiers"]
    assert len(hypothesis.discovery_questions) >= 6
