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
