from cios.applications.flora.blueprint_import.intelligence_projection import executive_assessments
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin


def _twin(*rows):
    return assemble_semantic_twin(list(rows))


def test_legacy_records_cannot_infer_readiness_from_volume_or_weighted_maturity():
    records = [
        {"candidate_record_id": f"i-{i}", "candidate_object_class": "executive_intelligence", "payload": {"statement": "Insight", "subject": "Market"}}
        for i in range(20)
    ]
    records.append({"candidate_record_id": "m", "candidate_object_class": "maturity_assessment", "payload": {
        "id": "legacy", "overall_maturity_percent": 100, "mission_outcome": "COMPLETE",
        "dimensions": [{"dimension": "industry structure", "score": 100}],
    }})
    results = executive_assessments(_twin(*records))
    assert all(result.state == "legacy_unassessed" for result in results)
    assert all(result.owner_result_id == "" for result in results)
    assert "20 insight record(s)" in results[0].inventory_summary


def test_projection_copies_complete_owner_output_without_scoring_it():
    dimensions = [
        "Industry Fidelity", "Temporal Fidelity", "Evidence Maturity", "Source Diversity",
        "Enterprise Intelligence Density", "Financial Intelligence", "Relationship and Graph Integrity",
        "Market Participant Intelligence Density", "Capability and Offer Intelligence",
        "Opportunity Completeness", "Commercial Reasoning Lineage", "Decision Maturity",
        "Observation and Explanation Maturity",
    ]
    twin = _twin({"candidate_record_id": "assessment", "original_source_id": "IT001-A-1",
        "candidate_object_class": "high_fidelity_completeness_assessment", "source_file": "assessment.json",
        "payload": {"state": "conditionally_complete", "dimensions": [
            {"dimension": name, "deficiencies": ["DEF-1"] if name == "Industry Fidelity" else []}
            for name in dimensions
        ]}})
    results = executive_assessments(twin)
    assert all(result.state == "conditionally_complete" for result in results)
    assert all(result.owner_result_id == "IT001-A-1" for result in results)
    assert results[0].deficiencies == ("DEF-1",)
    assert not any(hasattr(result, "score") for result in results)
