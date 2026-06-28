"""End-to-end tests for the Sprint 7A Opportunity Assistant vertical slice."""

import ast
import importlib
import json
from pathlib import Path

from cios.applications.opportunity_assistant.pipeline import (
    OpportunityPipelineResult,
    run_pipeline,
)
from cios.applications.opportunity_assistant.reporting import render_console_report
from cios.memory import InMemoryRepository
from cios.applications.opportunity_assistant.rules import (
    HIGH_VALUE_RULE_ID,
    LONG_TERM_CONTRACT_RULE_ID,
    ORACLE_TRANSFORMATION_RULE_ID,
    SECURITY_CRITICAL_RULE_ID,
    detect_rules,
)
from cios.applications.opportunity_assistant.reasoning_mapping import create_reasoning
from cios.applications.opportunity_assistant.scoring_policy import (
    OpportunityScoringPolicy,
    create_scoring,
    score_rule_detections,
)
from cios.applications.opportunity_assistant.explainability import (
    create_explainability_report,
)
from cios.applications.opportunity_assistant.decision_policy import (
    OpportunityDecisionPolicy,
)

FIXTURE_DIR = Path(__file__).with_name("fixtures") / "opportunity_assistant"
LOW_VALUE_SIMPLE = FIXTURE_DIR / "low_value_simple_opportunity.json"
NO_COMPETITORS_NO_SECURITY = FIXTURE_DIR / "no_competitors_no_security_opportunity.json"


def _rules_by_name(result: OpportunityPipelineResult):
    return {rule.name: rule for rule in result.rule_matches}


def test_rules_module_contains_no_scoring_policy_responsibilities() -> None:
    module = importlib.import_module("cios.applications.opportunity_assistant.rules")
    source = Path(module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    defined_names = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assigned_names = {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }

    assert "RuleScore" not in defined_names
    assert "RuleMatch" not in defined_names
    assert "score_rule_detections" not in defined_names
    assert "DEFAULT_SCORING_POLICY" not in assigned_names
    assert all(
        "score" not in field for field in module.RuleDetection.__dataclass_fields__
    )


def test_scoring_policy_owns_numeric_rule_scoring() -> None:
    source = {
        "name": "Scoring Ownership",
        "customer": {"name": "Example"},
        "description": "Oracle migration with security needs.",
        "value": 10_000_000,
        "duration_months": 36,
        "current_platforms": ["Oracle"],
        "requirements": ["security"],
        "competitors": ["A", "B", "C"],
        "capabilities": ["managed service"],
    }
    policy = OpportunityScoringPolicy()

    detections = detect_rules(source)
    matches = policy.score_rule_detections(detections)

    assert all(not hasattr(detection, "score") for detection in detections)
    assert [match.score for match in matches] == [
        (
            policy.rule_scores[detection.rule_id].matched_score
            if detection.matched
            else policy.rule_scores[detection.rule_id].absent_score
        )
        for detection in detections
    ]


def test_scoring_policy_can_be_inspected_independently() -> None:
    policy = OpportunityScoringPolicy()

    assert policy.model_name == "Sprint 7A Deterministic Opportunity Score"
    assert [(band.name, band.minimum, band.maximum) for band in policy.bands] == [
        ("Low", 0.0, 49.0),
        ("Medium", 50.0, 74.0),
        ("High", 75.0, 100.0),
    ]
    assert (
        policy.transformation_pressure_mapping.urgency_rule_id
        == LONG_TERM_CONTRACT_RULE_ID
    )
    assert (
        policy.transformation_pressure_mapping.strategic_importance_rule_id
        == HIGH_VALUE_RULE_ID
    )
    assert (
        policy.transformation_pressure_mapping.change_pressure_rule_id
        == ORACLE_TRANSFORMATION_RULE_ID
    )
    assert (
        policy.transformation_pressure_mapping.capability_gap_rule_id
        == SECURITY_CRITICAL_RULE_ID
    )


def test_decision_policy_can_be_inspected_independently() -> None:
    policy = OpportunityDecisionPolicy()

    assert policy.question == "Should this opportunity be qualified for active pursuit?"
    assert policy.option_title == "Qualify for active pursuit"
    assert policy.status.value == "approved"
    assert policy.confidence.value == "high"
    assert [(criterion.name, criterion.weight) for criterion in policy.criteria] == [
        ("Commercial attractiveness", 0.4),
        ("Strategic fit", 0.3),
        ("Delivery confidence", 0.3),
    ]
    assert policy.option_actions == [
        "Build an Oracle transformation win theme.",
        "Validate security accreditation evidence.",
        "Prepare managed-service operating model proof points.",
        "Create competitor differentiation plan.",
    ]


def test_pipeline_output_remains_unchanged_with_explicit_policy_interfaces() -> None:
    default_result = run_pipeline()
    explicit_result = run_pipeline(
        scoring_policy=OpportunityScoringPolicy(),
        decision_policy=OpportunityDecisionPolicy(),
    )

    assert (
        explicit_result.scoring.result.overall_score.value
        == default_result.scoring.result.overall_score.value
    )
    assert (
        explicit_result.scoring.result.band.name
        == default_result.scoring.result.band.name
    )
    assert [
        component.name for component in explicit_result.scoring.result.components
    ] == [component.name for component in default_result.scoring.result.components]
    assert explicit_result.decision.status == default_result.decision.status
    assert explicit_result.decision.outcome == default_result.decision.outcome
    assert (
        explicit_result.decision.recommendations[0].title
        == default_result.decision.recommendations[0].title
    )
    assert (
        explicit_result.decision.recommendations[0].actions
        == default_result.decision.recommendations[0].actions
    )


def test_policy_traceability_ids_flow_through_scoring_and_decision() -> None:
    result = run_pipeline(
        scoring_policy=OpportunityScoringPolicy(),
        decision_policy=OpportunityDecisionPolicy(),
    )

    evidence_ids = [item.id for item in result.evidence]
    rule_ids = [rule.rule_id for rule in result.rule_matches]

    assert [
        component.metadata["rule_id"] for component in result.scoring.result.components
    ] == rule_ids
    assert all(
        component.score.evidence_ids == evidence_ids
        for component in result.scoring.result.components
    )
    assert result.decision.assessments[0].evidence_ids == evidence_ids
    assert result.decision.assessments[0].reasoning_trace_ids == [
        result.reasoning.trace.id
    ]
    assert result.decision.assessments[0].scoring_result_ids == [
        result.scoring.result.id
    ]
    assert result.decision.rationales[0].reasoning_result_ids == [
        result.reasoning.result.id
    ]
    assert result.decision.rationales[0].score_ids == [
        result.scoring.result.overall_score.id
    ]
    assert result.decision.recommendations[0].evidence_ids == evidence_ids


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


def test_opportunity_assistant_pipeline_runs_without_memory_repository() -> None:
    result = run_pipeline()

    assert isinstance(result, OpportunityPipelineResult)
    assert result.evidence
    assert result.decision.recommendations


def test_opportunity_assistant_pipeline_persists_vertical_slice_to_memory() -> None:
    repository = InMemoryRepository()

    result = run_pipeline(memory_repository=repository)

    records = repository.list()
    assert isinstance(result, OpportunityPipelineResult)
    assert {record.record_type for record in records} == {
        "evidence",
        "assessment",
        "decision",
    }
    assert len(repository.find_by_record_type("evidence")) == 1
    assert len(repository.find_by_record_type("assessment")) == len(
        result.decision.assessments
    )
    assert len(repository.find_by_record_type("decision")) == 1

    evidence_record = repository.find_by_record_type("evidence")[0]
    assessment_record = repository.find_by_record_type("assessment")[0]
    decision_record = repository.find_by_record_type("decision")[0]

    assert evidence_record.subject_id == result.ontology.opportunity.id
    assert evidence_record.evidence_ids == [item.id for item in result.evidence]
    assert evidence_record.payload["evidence_count"] == len(result.evidence)
    assert assessment_record.subject_id == result.ontology.opportunity.id
    assert assessment_record.evidence_ids == [item.id for item in result.evidence]
    assert assessment_record.graph_record_ids == [result.graph.id]
    assert decision_record.subject_id == result.ontology.opportunity.id
    assert decision_record.evidence_ids == [item.id for item in result.evidence]
    assert decision_record.decision_id == result.decision.id
    assert decision_record.decision_payload["id"] == result.decision.id

    assert repository.get(evidence_record.id) == evidence_record
    assert repository.get(assessment_record.id) == assessment_record
    assert repository.get(decision_record.id) == decision_record


def test_opportunity_assistant_memory_integration_does_not_add_forbidden_imports() -> (
    None
):
    module = importlib.import_module("cios.memory.repository")
    source = Path(module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    forbidden_roots = {
        "cios.reasoning",
        "cios.scoring",
        "cios.decision_engine",
        "cios.agents",
        "cios.applications",
    }

    assert not any(
        imported == root or imported.startswith(f"{root}.")
        for imported in imported_modules
        for root in forbidden_roots
    )


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
    assert [detection.name for detection in detections] == [
        match.name for match in matches
    ]


def test_explainability_report_is_produced_for_each_recommendation() -> None:
    result = run_pipeline()

    report = result.explainability_report

    assert report.decision_id == result.decision.id
    assert report.opportunity_id == result.ontology.opportunity.id
    assert len(report.recommendation_explanations) == len(
        result.decision.recommendations
    )


def test_every_recommendation_has_supporting_reason() -> None:
    result = run_pipeline()

    for explanation in result.explainability_report.recommendation_explanations:
        assert explanation.supporting_observations
        assert explanation.supporting_observation_ids
        assert explanation.evidence_ids
        assert explanation.scores_used
        assert explanation.reasoning_trace_ids
        assert explanation.reasoning_step_ids
        assert explanation.confidence == result.decision.confidence


def test_rule_traceability_metadata_uses_stable_rule_ids() -> None:
    result = run_pipeline()

    rule_ids = [rule.rule_id for rule in result.rule_matches]

    assert len(rule_ids) == len(set(rule_ids))
    assert [detection.rule_id for detection in result.rule_detections] == rule_ids
    assert [
        observation.metadata["rule_id"] for observation in result.observations
    ] == rule_ids
    assert [
        signal.metadata["rule_id"] for signal in result.reasoning.signals
    ] == rule_ids
    assert [
        inference.metadata["rule_id"] for inference in result.reasoning.inferences
    ] == rule_ids
    assert [
        step.metadata["rule_id"] for step in result.reasoning.trace.steps
    ] == rule_ids
    assert [
        component.metadata["rule_id"] for component in result.scoring.result.components
    ] == rule_ids
    assert [
        component.score.metadata["rule_id"]
        for component in result.scoring.result.components
    ] == rule_ids

    for explanation in result.explainability_report.recommendation_explanations:
        assert explanation.triggered_rule_ids == rule_ids


def test_rule_traceability_survives_reordered_pipeline_lists() -> None:
    result = run_pipeline()

    reversed_rules = list(reversed(result.rule_matches))
    reversed_observations = list(reversed(result.observations))
    reasoning = create_reasoning(reversed_rules, reversed_observations)
    scoring = create_scoring(reversed_rules, reasoning.trace, result.evidence)
    report = create_explainability_report(
        result.ontology,
        result.evidence,
        reversed_rules,
        reversed_observations,
        reasoning,
        scoring,
        result.decision,
    )

    observations_by_rule_id = {
        observation.metadata["rule_id"]: observation
        for observation in reversed_observations
    }
    for rule, signal, inference, step, component in zip(
        reversed_rules,
        reasoning.signals,
        reasoning.inferences,
        reasoning.trace.steps,
        scoring.result.components,
    ):
        assert signal.metadata["rule_id"] == rule.rule_id
        assert signal.source_ids == [observations_by_rule_id[rule.rule_id].id]
        assert inference.metadata["rule_id"] == rule.rule_id
        assert observations_by_rule_id[rule.rule_id].id in inference.premise_ids
        assert step.metadata["rule_id"] == rule.rule_id
        assert step.input_ids == [observations_by_rule_id[rule.rule_id].id]
        assert component.metadata["rule_id"] == rule.rule_id

    assert (
        scoring.transformation_pressure.strategic_importance_score.name
        == "High Value Opportunity"
    )
    assert scoring.transformation_pressure.urgency_score.name == "Long-Term Contract"
    assert report.recommendation_explanations[0].triggered_rule_ids == [
        rule.rule_id for rule in reversed_rules
    ]


def test_json_output_is_valid(capsys) -> None:
    from cios.applications.opportunity_assistant import main as cli

    import sys

    previous_argv = sys.argv
    try:
        sys.argv = ["opportunity-assistant", "--json"]
        cli.main()
    finally:
        sys.argv = previous_argv

    payload = json.loads(capsys.readouterr().out)

    assert "explainability_report" in payload
    assert payload["explainability_report"]["recommendation_explanations"]


def test_console_output_still_works(capsys) -> None:
    from cios.applications.opportunity_assistant import main as cli

    import sys

    previous_argv = sys.argv
    try:
        sys.argv = ["opportunity-assistant"]
        cli.main()
    finally:
        sys.argv = previous_argv

    output = capsys.readouterr().out

    assert "Observations:" in output
    assert "Recommendation:" in output
    assert "explainability_report" not in output
