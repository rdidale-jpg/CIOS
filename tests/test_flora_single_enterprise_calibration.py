from pathlib import Path

from cios.applications.flora.live.source_registry import canonical_enterprise_id, collection_scope, enabled_sources
from cios.applications.flora.memory.calibration import archive_and_reset_enterprise, inspection_rows
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository
from cios.applications.flora.memory.service import ObservationMemoryService


def svc(tmp_path: Path) -> ObservationMemoryService:
    return ObservationMemoryService(ObservationRepository(tmp_path / "obs.jsonl"), EnterpriseModelRepository(tmp_path / "models"))


def evidence(eid="EV-1", org="BT"):
    return {"evidence_id": eid, "enterprise_id": org, "organisation": org, "cleaned_observation": "BT reports Consumer as a customer-facing unit.", "commercial_condition": "Organisation", "publication_date": "2026-05-14", "confidence": 88, "evidence_freshness": "current", "source_provenance": "live", "page_range": "1", "page_number": 1}


def test_bt_aliases_resolve_to_one_canonical_enterprise_id():
    assert canonical_enterprise_id("BT") == "bt-group-plc"
    assert canonical_enterprise_id("BT Group") == "bt-group-plc"
    assert canonical_enterprise_id("BT Group plc") == "bt-group-plc"


def test_bt_profile_scopes_only_bt_sources_and_exact_targets():
    scope = collection_scope("bt-group-plc", run_id="run-1")
    sources = enabled_sources(profile_id="bt-group-plc")
    assert scope.canonical_enterprise_id == "bt-group-plc"
    assert scope.collection_mode == "live_authoritative"
    assert sources and {s.canonical_enterprise_id for s in sources} == {"bt-group-plc"}
    assert {s.source_id for s in sources} == set(scope.permitted_source_ids)
    assert all(str(s.url).startswith("https://") and s.authority_tier for s in sources)


def test_accepted_evidence_uses_canonical_id_and_recollection_is_idempotent(tmp_path: Path):
    service = svc(tmp_path)
    first = service.accept_evidence(evidence("EV-1", "BT Group"))
    second = service.accept_evidence(evidence("EV-2", "BT Group plc"))
    assert first.observation_id == second.observation_id
    observations = service.observations.list()
    assert len(observations) == 1
    assert observations[0].enterprise_id == "bt-group-plc"
    assert set(observations[0].supporting_evidence_ids) == {"EV-1", "EV-2"}
    assert service.models.get("BT").enterprise_id == "bt-group-plc"
    assert service.models.get("BT Group plc").attributes


def test_aliases_do_not_create_separate_models(tmp_path: Path):
    service = svc(tmp_path)
    service.accept_evidence(evidence("EV-1", "BT"))
    service.accept_evidence(evidence("EV-2", "BT Group plc"))
    assert service.models.path_for("BT") == service.models.path_for("BT Group plc")


def test_memory_inspection_and_bt_only_reset_preserve_other_enterprise(tmp_path: Path):
    service = svc(tmp_path)
    service.accept_evidence(evidence("EV-1", "BT"))
    service.accept_evidence({**evidence("EV-X", "Other Co"), "cleaned_observation": "Other Co reports Consumer as a customer-facing unit."})
    rows = inspection_rows("BT", service.observations, service.models)
    assert rows[0]["enterprise_id"] == "bt-group-plc"
    assert rows[0]["update_result"] == "projected"
    audit = archive_and_reset_enterprise("BT", confirm="reset bt-group-plc", observations=service.observations, models=service.models, archive_root=tmp_path / "archive")
    assert audit["archived_observations"] == 1
    assert not service.models.get("BT").attributes
    assert service.models.get("Other Co").attributes
