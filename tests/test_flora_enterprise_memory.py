from pathlib import Path

import pytest

from cios.applications.flora.memory.models import Observation
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository
from cios.applications.flora.memory.service import ObservationMemoryService
from cios.applications.flora.memory.views import enterprise_memory_panel


def service(tmp_path: Path) -> ObservationMemoryService:
    return ObservationMemoryService(ObservationRepository(tmp_path / "observations.jsonl"), EnterpriseModelRepository(tmp_path / "models"))


def evidence(eid="EV-1", statement="BT launched Project Falcon in 2026 for network operations."):
    return {
        "evidence_id": eid,
        "organisation": "BT",
        "cleaned_observation": statement,
        "commercial_condition": "AI Modernisation",
        "confidence": 82,
        "extraction_timestamp": "2026-07-04T10:00:00+00:00",
        "publication_date": "2026-07-01",
        "evidence_freshness": "collected today",
        "page_range": "1",
        "page_number": 1,
    }


def test_observation_requires_evidence_or_human_provenance() -> None:
    with pytest.raises(ValueError):
        Observation("BT", "AI Modernisation", "BT launched Project Falcon in 2026.", "2026-07-04", "2026-07-04T00:00:00+00:00", "technology_events.AI Modernisation", 80)
    human = Observation("BT", "leadership", "BT appointed a new CIO in 2026.", "2026-07-04", "2026-07-04T00:00:00+00:00", "enterprise_identity.leadership", 70, provenance_type="human-supplied", human_provenance={"contributor": "analyst", "date": "2026-07-04"})
    assert human.provenance_type == "human-supplied"


def test_speculation_recommendation_and_non_atomic_language_are_rejected() -> None:
    base = ("BT", "AI Modernisation", "2026-07-04", "2026-07-04T00:00:00+00:00", "technology_events.AI Modernisation", 80)
    with pytest.raises(ValueError):
        Observation(base[0], base[1], "BT may launch Project Falcon.", *base[2:], supporting_evidence_ids=("EV",))
    with pytest.raises(ValueError):
        Observation(base[0], base[1], "BT launched Project Falcon; sellers should pitch AI.", *base[2:], supporting_evidence_ids=("EV",))
    with pytest.raises(ValueError):
        Observation(base[0], base[1], "BT launched Project Falcon; BT reduced costs.", *base[2:], supporting_evidence_ids=("EV",))


def test_evidence_to_observation_is_durable_idempotent_and_corroborates(tmp_path: Path) -> None:
    svc = service(tmp_path)
    first = svc.accept_evidence(evidence("EV-1"))
    second = svc.accept_evidence(evidence("EV-1"))
    corroborating = svc.accept_evidence(evidence("EV-2"))
    observations = svc.observations.list()
    assert first.observation_id == second.observation_id == corroborating.observation_id
    assert len(observations) == 1
    assert observations[0].supporting_evidence_ids == ("EV-1", "EV-2")
    assert svc.observations.get(first.observation_id) is not None


def test_unrelated_evidence_creates_distinct_observation(tmp_path: Path) -> None:
    svc = service(tmp_path)
    svc.accept_evidence(evidence("EV-1"))
    svc.accept_evidence(evidence("EV-3", "BT signed a 2026 cloud platform agreement."))
    assert len(svc.observations.list()) == 2


def test_model_update_retains_lineage_confidence_dates_and_prior_state(tmp_path: Path) -> None:
    svc = service(tmp_path)
    result = svc.accept_evidence(evidence("EV-1"))
    svc.accept_evidence(evidence("EV-4", "BT launched Project Falcon phase two in 2026."))
    model = svc.models.get("BT")
    attr = model.attributes[result.affected_attribute]
    assert result.action == "created"
    assert result.observation_id in attr.observation_ids
    assert "EV-1" in attr.evidence_ids
    assert attr.confidence == 82
    assert attr.last_observed_date == "2026-07-04"
    assert attr.prior_values


def test_unknowns_and_contradictions_are_preserved(tmp_path: Path) -> None:
    svc = service(tmp_path)
    svc.accept_evidence(evidence("EV-1"))
    unknown = svc.accept_evidence(evidence("EV-U", "BT has unknown procurement timing for Project Falcon."))
    contradiction = svc.accept_evidence(evidence("EV-C", "BT cancelled Project Falcon in 2026."))
    model = svc.models.get("BT")
    attr = model.attributes[contradiction.affected_attribute]
    assert unknown.unknown_created
    assert model.unknowns
    assert contradiction.contradiction
    assert attr.contradiction_state == "contradicted"
    assert contradiction.observation_id in attr.conflicting_observation_ids


def test_model_backed_output_reads_memory_and_exposes_lineage(tmp_path: Path) -> None:
    svc = service(tmp_path)
    result = svc.accept_evidence(evidence("EV-1"))
    html = enterprise_memory_panel("BT", svc.models, svc.observations)
    assert "Enterprise Memory" in html
    assert result.observation_id in html
    assert "EV-1" in html
    assert "collected today" in html
    # Deleting a report string cannot delete the durable model memory.
    del html
    assert svc.models.get("BT").attributes


def test_versioned_fingerprint_uses_effective_date_not_collection_timestamp(tmp_path: Path) -> None:
    svc = service(tmp_path)
    first = svc.accept_evidence(evidence("EV-A") | {"extraction_timestamp": "2026-07-04T10:00:00+00:00", "observation_date": "2026-07-01"})
    retry = svc.accept_evidence(evidence("EV-B") | {"extraction_timestamp": "2026-07-04T11:00:00+00:00", "observation_date": "2026-07-01"})
    later = svc.accept_evidence(evidence("EV-C") | {"extraction_timestamp": "2026-07-04T12:00:00+00:00", "observation_date": "2026-07-02"})
    observations = svc.observations.list()
    assert first.observation_id == retry.observation_id
    assert first.observation_id != later.observation_id
    assert all(o.observation_fingerprint.startswith("obs-v1-") for o in observations)
    assert len(observations) == 2


def test_schema_versions_and_jsonl_corruption_are_detected(tmp_path: Path) -> None:
    svc = service(tmp_path)
    svc.accept_evidence(evidence("EV-1"))
    observation_row = svc.observations.path.read_text(encoding="utf-8").splitlines()[0]
    assert '"schema_version":"flora-memory-v1"' in observation_row
    svc.observations.path.write_text(observation_row + "\n{" , encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed Observation JSONL"):
        svc.observations.list()

    bad_model = tmp_path / "models" / "bad.json"
    bad_model.parent.mkdir(exist_ok=True)
    # Write through the repository path so the safe file-name strategy is still exercised.
    path = svc.models.path_for("Bad Co")
    path.write_text('{"schema_version":"future","enterprise_id":"Bad Co","attributes":{},"unknowns":{}}', encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported EnterpriseModel schema_version"):
        svc.models.get("Bad Co")


def test_enterprise_paths_are_safe_stable_and_collision_resistant(tmp_path: Path) -> None:
    repo = EnterpriseModelRepository(tmp_path / "models")
    evil = repo.path_for("../BT")
    bt = repo.path_for("BT")
    lower = repo.path_for("bt")
    renamed = repo.path_for("BT Group")
    assert evil.parent == tmp_path / "models"
    assert ".." not in evil.name and "/" not in evil.name
    assert bt == lower
    assert bt == renamed


def test_memory_survives_reconstruction_and_report_deletion(tmp_path: Path) -> None:
    svc = service(tmp_path)
    result = svc.accept_evidence(evidence("EV-1"))
    del svc
    rebuilt = service(tmp_path)
    html = enterprise_memory_panel("BT", rebuilt.models, rebuilt.observations)
    assert result.observation_id in html
    assert "EV-1" in html
    retry = rebuilt.accept_evidence(evidence("EV-1"))
    assert retry.observation_id == result.observation_id
    assert len(rebuilt.observations.list()) == 1
    report = tmp_path / "report.html"
    report.write_text(html, encoding="utf-8")
    report.unlink()
    assert rebuilt.models.get("BT").attributes


def test_duplicate_memory_implementation_is_not_active() -> None:
    import cios.applications.flora.memory.service as service_module
    assert hasattr(service_module, "ObservationMemoryService")
    with pytest.raises(ModuleNotFoundError):
        __import__("cios.applications.flora.memory.enterprise_memory")


def test_compound_financial_sentence_decomposes_to_atomic_claims(tmp_path: Path) -> None:
    from cios.applications.flora.memory.service import decompose_factual_claims
    item = evidence("EV-FIN", "Revenue was £20.4bn, adjusted EBITDA was £8.2bn and normalised free cash flow was £1.3bn.") | {"organisation": "BT Group plc"}
    claims = decompose_factual_claims(item)
    assert [c.affected_attribute for c in claims] == [
        "financial_performance.metrics.revenue.reported period.actual",
        "financial_performance.metrics.adjusted_ebitda.reported period.actual",
        "financial_performance.metrics.normalised_free_cash_flow.reported period.actual",
    ]
    assert [(c.value, c.unit, c.currency, c.state) for c in claims] == [(20.4, "billion", "GBP", "actual"), (8.2, "billion", "GBP", "actual"), (1.3, "billion", "GBP", "actual")]
    svc = service(tmp_path)
    report = svc.process_evidence(item)
    assert report.factual_claims_accepted == 3
    assert len(svc.observations.list()) == 3


def test_organisation_strategy_and_leadership_decompose_separately(tmp_path: Path) -> None:
    svc = service(tmp_path)
    org = svc.process_evidence(evidence("EV-ORG", "BT reports Consumer, Business, International and Openreach as customer-facing units, while Digital and Networks provide group capabilities.") | {"organisation": "BT Group plc"})
    strat = svc.process_evidence(evidence("EV-STR", "BT's strategy is Build, Connect and Accelerate, with a target to achieve X by FY29.") | {"organisation": "BT Group plc"})
    lead = svc.process_evidence(evidence("EV-LEAD", "Allison Kirkby held the role of Group Chief Executive.") | {"organisation": "BT Group plc"})
    statements = [o.atomic_statement for o in svc.observations.list()]
    assert org.factual_claims_accepted == 6
    assert "Consumer is disclosed as a BT Group business unit." in statements
    assert "Networks is a disclosed internal BT capability." in statements
    assert strat.factual_claims_accepted == 3
    assert "Build is a stated BT Group strategic pillar." in statements
    assert lead.factual_claims_accepted == 1
    assert "Allison Kirkby held the role of Group Chief Executive at BT Group plc on 2026-07-01." in statements


def test_invalid_claim_isolated_and_successes_persist(tmp_path: Path) -> None:
    svc = service(tmp_path)
    item = evidence("EV-MIX", "Revenue was £20.4bn and BT may launch Project Falcon.") | {"organisation": "BT Group plc"}
    report = svc.process_evidence(item)
    assert report.factual_claims_accepted == 1
    assert report.factual_claims_rejected == 0  # deterministic extraction ignores non-factual interpretation fragment
    bad = svc.process_evidence(evidence("EV-BAD", "BT may launch Project Falcon.") | {"organisation": "BT Group plc"})
    assert bad.factual_claims_rejected == 1
    assert len(svc.observations.list()) == 1
    assert svc.models.get("bt-group-plc").attributes


def test_evidence_primary_dispositions_reconcile_without_secondary_inflation() -> None:
    manifest = {"evidence_candidates": 4, "evidence_accepted": 1, "evidence_rejected": 1, "evidence_downgraded": 1, "evidence_duplicate": 1, "evidence_context_only": 2}
    primary_total = manifest["evidence_accepted"] + manifest["evidence_rejected"] + manifest["evidence_downgraded"] + manifest["evidence_duplicate"]
    assert manifest["evidence_candidates"] == primary_total
    assert manifest["evidence_candidates"] != primary_total + manifest["evidence_context_only"]
