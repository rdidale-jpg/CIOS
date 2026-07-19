from cios.applications.flora.enterprise_intelligence.explain import (
    QUESTION,
    assemble_lloyds_context_package,
    explain_lloyds_changes,
    validate_bounded_explanation,
    validate_context_package,
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


def test_context_package_validation_lineage_and_source_passages():
    package = assemble_lloyds_context_package()

    valid, failures = validate_context_package(package)

    assert valid, failures
    assert package.focus_object_id == "BK-ENT-001"
    assert package.approved_question_id == "Q-LBG-CHANGE-EXPLAIN-001"
    assert package.source_passages
    assert any("mobile current-account" in p.content for p in package.source_passages)
    assert package.retrieval_policy_version == "flora-increment-2-retrieval-policy-v0.1"
    assert package.exclusions
    assert package.limitations


def test_output_validator_rejects_unknown_lineage_and_prohibited_language():
    package = assemble_lloyds_context_package()
    explanation = explain_lloyds_changes(package)
    valid, failures = validate_bounded_explanation(package, explanation)
    assert valid, failures

    bad_change = explanation.changes[0].model_copy(update={"evidence_ids": ("EV-UNKNOWN",)})
    bad = explanation.model_copy(update={"changes": (bad_change,) + explanation.changes[1:]})
    valid, failures = validate_bounded_explanation(package, bad)
    assert not valid
    assert any("unknown evidence reference" in failure for failure in failures)

    bad_scope = explanation.model_copy(update={"answer_scope": "recommend pursuit with an opportunity score"})
    valid, failures = validate_bounded_explanation(package, bad_scope)
    assert not valid
    assert any("prohibited language" in failure for failure in failures)


def test_repeatability_against_same_context_package_is_semantically_stable():
    package = assemble_lloyds_context_package()
    runs = [explain_lloyds_changes(package) for _ in range(3)]

    assert len({run.context_package_hash for run in runs}) == 1
    assert len({tuple(c.what_changed for c in run.changes) for run in runs}) == 1
    assert len({tuple(c.evidence_ids for c in run.changes) for run in runs}) == 1
    assert len({tuple(u.unknown_id for u in run.unknowns) for run in runs}) == 1


def test_semantic_prohibited_output_rejection_uses_claim_rules_and_package_support():
    package = assemble_lloyds_context_package()
    explanation = explain_lloyds_changes(package)
    prohibited_cases = [
        ("prioritisation advice", "Lloyds should prioritise branch migration immediately."),
        ("best route language", "The best route is to lead with deposit transformation."),
        ("benefit or opportunity assertion", "This creates an opportunity to expand wallet share."),
        ("implied sales pursuit", "A sales motion should pursue the Halifax migration team."),
        ("unsupported accountable-leader attribution", "The accountable leader is the CFO."),
        ("broad strategic conclusion", "This proves Lloyds strategy is enterprise-wide digital dominance."),
        ("confidence beyond evidence", "This definitively proves causality between cloud and NII."),
    ]

    for expected_rule, text in prohibited_cases:
        bad_change = explanation.changes[0].model_copy(update={"interpretation": text})
        bad = explanation.model_copy(update={"changes": (bad_change,) + explanation.changes[1:]})
        valid, failures = validate_bounded_explanation(package, bad)
        assert not valid
        assert any(expected_rule in failure for failure in failures), failures

    unsupported = explanation.changes[0].model_copy(update={"evidence_ids": (), "observation_ids": (), "confidence": "high"})
    bad = explanation.model_copy(update={"changes": (unsupported,) + explanation.changes[1:]})
    valid, failures = validate_bounded_explanation(package, bad)
    assert not valid
    assert any("missing evidence support" in failure for failure in failures)
    assert any("confidence beyond package support" in failure for failure in failures)


def test_content_understanding_acceptance_properties_for_frozen_lloyds_package():
    package = assemble_lloyds_context_package()
    explanation = explain_lloyds_changes(package)
    valid, failures = validate_bounded_explanation(package, explanation)
    assert valid, failures

    passage_ids = {p.passage_id for p in package.source_passages}
    evidence_by_id = {e.evidence_id: e for e in package.evidence}
    supported_changes = [c for c in explanation.changes if len(c.evidence_ids) >= 1 and c.fact_basis]

    assert len(supported_changes) >= 2
    assert any(len({ref for eid in c.evidence_ids for ref in evidence_by_id[eid].lineage if ref in passage_ids}) >= 2 for c in explanation.changes)
    assert any("mobile" in c.what_changed.lower() or "hedge" in c.what_changed.lower() or "migration" in c.what_changed.lower() for c in explanation.changes)
    assert any("belongs together" in reason.lower() or "linked by explicit lineage" in reason.lower() for reason in explanation.why_evidence_belongs_together)
    assert all(c.fact_basis and c.interpretation and c.evidence_ids for c in explanation.changes)
    assert any(c.observation_ids for c in explanation.changes)
    assert explanation.directly_about_lloyds
    assert any(evidence_by_id[eid].sector_context for c in explanation.changes for eid in c.evidence_ids)
    assert explanation.unknowns or explanation.contradictions_and_competing_interpretations
    assert all("proves causality" not in c.interpretation.lower() and "because of" not in c.interpretation.lower() for c in explanation.changes)
    observation_texts = {o.statement for o in package.observations}
    assert all(c.interpretation not in observation_texts for c in explanation.changes)
