from pathlib import Path

from cios.applications.flora.memory.golden_import import load_golden_facts, validate_golden_facts, import_golden_facts
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository
from cios.applications.flora.memory.service import ObservationMemoryService, decompose_factual_claims, validate_factual_claim, FactualClaim
from cios.applications.flora.memory.factual_twin import maturity_for_model, coverage_for_model, automatic_extraction_comparison
from cios.applications.flora.memory.source_contracts import classify_foundation_eligibility, contract_for

GOLDEN = Path("docs/Architecture/experiments/BT_Foundation_Golden_Facts.yaml")

def svc(tmp_path):
    return ObservationMemoryService(ObservationRepository(tmp_path / "obs.jsonl"), EnterpriseModelRepository(tmp_path / "models"))

def test_golden_facts_validate_import_and_render_calibrated_foundation(tmp_path):
    facts = load_golden_facts(GOLDEN)
    assert len(facts) >= 15
    assert {f["domain"] for f in facts} >= {"identity", "structure", "financial_performance", "strategy", "leadership"}
    assert all(f["page"] and f["source_id"] and f["provenance"] == "evidence_curated" for f in facts)
    assert len(validate_golden_facts(GOLDEN)) == len(facts)
    service = svc(tmp_path)
    result = import_golden_facts(GOLDEN, service)
    again = import_golden_facts(GOLDEN, service)
    model = service.models.get("bt-group-plc")
    assert result["rejected_claims"] == []
    assert result["observations_created"] == len(facts)
    assert again["observations_created"] == len(facts)
    assert result["model_attributes_created"] >= 15
    assert maturity_for_model(model) == "Foundation — calibrated"
    assert all(attr.evidence_ids and attr.observation_ids for attr in model.attributes.values())
    assert all(obs.provenance_type == "evidence_curated" for obs in service.observations.list())
    assert coverage_for_model(model)["financial_performance"]["populated_attributes"]

def test_commercial_signal_categories_do_not_enter_factual_claims():
    assert decompose_factual_claims({"evidence_id":"E1","organisation":"BT","commercial_condition":"Customer Trust","snippet":"This collaboration shows how innovation can deliver benefits to customers.","page_range":"1"}) == []
    claim = FactualClaim("bt-group-plc", "Customer Trust", "BT is trusted by customers.", "strategy", "strategy.Customer Trust", "Customer Trust", evidence_id="E1", page_reference="1")
    try:
        validate_factual_claim(claim)
        raised = False
    except ValueError as exc:
        raised = "commercial Signal classification" in str(exc)
    assert raised

def test_source_contracts_and_foundation_eligibility_are_explicit():
    annual = {"source_type":"annual_report","commercial_condition":"financial_metric_reported","snippet":"revenue was £20.4bn"}
    promo = {"source_type":"strategy_page","commercial_condition":"Customer Trust","snippet":"This collaboration shows how innovation can deliver benefits."}
    news = {"source_type":"official_newsroom","commercial_condition":"Customer Trust","snippet":"BT launched a sovereign services platform on 1 July 2026."}
    assert classify_foundation_eligibility(annual)["foundation_eligible"] is True
    assert classify_foundation_eligibility(promo)["evidence_disposition"] == "accepted + context_only"
    assert classify_foundation_eligibility(news)["foundation_eligible"] is False
    assert "strategic_pillar_stated" in contract_for("strategy_page").permitted_claim_types

def test_automatic_extraction_comparison_reports_low_recall(tmp_path):
    facts = load_golden_facts(GOLDEN)
    automatic = [{"affected_attribute": facts[0]["affected_attribute"], "commercial_condition": facts[0]["claim_type"], "cleaned_observation": facts[0]["atomic_statement"], "page_number": facts[0]["page"]}]
    rows = automatic_extraction_comparison(facts, automatic, {facts[0]["affected_attribute"]})
    assert rows[0]["automatically_recovered"] is True
    assert sum(1 for r in rows if r["automatically_recovered"]) == 1
    assert sum(1 for r in rows if not r["automatically_recovered"]) == len(facts) - 1
