from cios.applications.flora.enterprise_intelligence.explain import (
    QUESTION,
    assemble_lloyds_context_package,
    explain_lloyds_changes,
)


def test_context_package_is_bounded_inspectable_and_immutable():
    package = assemble_lloyds_context_package()

    assert package.focus_object == "Lloyds Banking Group"
    assert package.approved_question == QUESTION
    assert package.baseline_commit == "e7dca8e"
    assert package.package_hash
    assert package.evidence
    assert package.observations
    assert package.unknowns
    assert package.tensions

    try:
        package.focus_object = "Other"
    except Exception:
        pass
    else:
        raise AssertionError("context package must be immutable")


def test_bounded_explanation_separates_facts_interpretations_unknowns_and_limits():
    package = assemble_lloyds_context_package()
    explanation = explain_lloyds_changes(package)

    assert explanation.context_package_hash == package.package_hash
    assert "no recommendations" in explanation.answer_scope.lower()
    assert len(explanation.changes) >= 4
    assert explanation.unknowns
    assert explanation.contradictions_and_competing_interpretations
    assert "EV-LBG-006" in explanation.directly_about_lloyds
    assert not explanation.sector_context_only
    assert any("Digital engagement is not equivalent" in limit for limit in explanation.confidence_limits)
    assert "recommendation" in explanation.prohibited_outputs

    hedge = next(c for c in explanation.changes if c.change_id == "CHG-LBG-002")
    assert hedge.confidence == "medium-high"
    assert hedge.evidence_ids == ("EV-LBG-003",)
    assert hedge.observation_ids == ("OBS-LBG-002",)
    assert hedge.limits


def test_sector_context_is_related_only_through_lloyds_usage():
    package = assemble_lloyds_context_package()
    ctp_evidence = next(e for e in package.evidence if e.evidence_id == "EV-LBG-006")

    assert ctp_evidence.lloyds_direct is True
    assert ctp_evidence.sector_context is True
    explanation = explain_lloyds_changes(package)
    assert any("Google Cloud" in reason for reason in explanation.why_evidence_belongs_together)
