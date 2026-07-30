from dataclasses import replace
from cios.applications.flora.blueprint_import.executive_workspace import twin_readiness, _opportunities
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin
from cios.applications.flora.commercial_mission import CommercialMission


def twin(opportunities):
    return assemble_semantic_twin(opportunities)


def incomplete(n=9):
    return twin([{"candidate_record_id": f"o{i}", "candidate_object_class": "opportunity_hypothesis", "payload": {"statement": f"Hypothesis {i}"}} for i in range(n)])


def test_volume_cannot_advance_opportunity_readiness():
    one = next(a for a in twin_readiness(incomplete(1)) if a.key == "commercial-opportunities")
    nine = next(a for a in twin_readiness(incomplete(9)) if a.key == "commercial-opportunities")
    assert one.state == nine.state == "Insufficient"
    assert one.bars == nine.bars == 1
    assert "%" not in str(nine)


def test_not_applicable_is_distinct_and_research_action_is_shared():
    aspect = next(a for a in twin_readiness(incomplete()) if a.key == "mission-alignment")
    assert aspect.state == "Not applicable" and aspect.bars is None
    assert aspect.researcher_action and aspect.next_requirement


def test_only_contract_ready_opportunity_enters_table():
    rows = [{"candidate_record_id": "ready", "candidate_object_class": "opportunity_hypothesis", "payload": {
        "statement": "Modernise payments operations", "affected_enterprises": ["Example Bank"],
        "client_problem": "Legacy payment processing", "evidence_refs": ["E1"], "confidence": "high",
        "procurement_start": "2027-Q1", "procurement_status": "Procurement active", "value_unavailable": True}},
        {"candidate_record_id": "weak", "candidate_object_class": "opportunity_hypothesis", "payload": {"statement": "Weak"}}]
    html = _opportunities(twin(rows), "run", None)
    assert "Customer" in html and "Example Bank" in html and "Not established" in html
    assert "2027-Q1" in html and "Procurement active" in html and ">Weak<" not in html
