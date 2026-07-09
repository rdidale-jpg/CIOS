"""Source external ID to canonical ID mapping records for Blueprint imports."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Literal

from cios.applications.flora.storage import atomic_write_json, data_path

from .archive import sha256_bytes
from .ledger import BlueprintImportLedger, utc_now
from .review import BlueprintReviewError, can_review_blueprint_candidate
from .registry import BlueprintPackageRegistry

MappingDisposition = Literal["map_existing", "propose_create", "propose_update", "duplicate", "conflict", "unresolved", "reject", "defer", "quarantine", "unsupported"]

@dataclass(frozen=True)
class ImportMappingRecord:
    schema_version: str
    mapping_id: str
    package_ref: str
    package_version: str
    import_run_id: str
    candidate_id: str
    external_id: str
    record_class: str
    disposition: MappingDisposition
    canonical_type: str = ""
    canonical_id: str = ""
    proposed_canonical_id: str = ""
    rationale: str = ""
    created_by: str = ""
    created_at: str = ""

    def to_dict(self):
        return asdict(self)


def mapping_id(package_ref: str, external_id: str, record_class: str, disposition: str, canonical_id: str = "") -> str:
    return "bpi-map-" + sha256_bytes(f"{package_ref}\n{external_id}\n{record_class}\n{disposition}\n{canonical_id}".encode())[:24]

class ImportMappingRepository:
    def _dir(self, import_run_id: str):
        return data_path("blueprint_import", "mappings", import_run_id)
    def save(self, record: ImportMappingRecord):
        path = self._dir(record.import_run_id) / f"{record.mapping_id}.json"
        if path.exists():
            return ImportMappingRecord(**json.loads(path.read_text(encoding="utf-8")))
        atomic_write_json(path, record.to_dict())
        return record
    def list(self, import_run_id: str) -> list[dict[str, Any]]:
        root = self._dir(import_run_id)
        if not root.exists(): return []
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(root.glob("*.json"))]

class ImportMappingService:
    def __init__(self, registry=None, repository=None, ledger=None):
        self.registry = registry or BlueprintPackageRegistry(); self.repository = repository or ImportMappingRepository(); self.ledger = ledger or BlueprintImportLedger()
    def record_mapping(self, candidate: dict[str, Any], disposition: MappingDisposition, actor: str, headers: Any, canonical_type: str = "", canonical_id: str = "", rationale: str = "") -> ImportMappingRecord:
        package = self.registry.get(str(candidate["source_package_ref"]))
        if not package or not can_review_blueprint_candidate(headers, package.identity.enterprise_id):
            raise BlueprintReviewError("Actor is not authorised to create Blueprint mappings")
        if disposition not in MappingDisposition.__args__:
            raise BlueprintReviewError("Unsupported mapping disposition")
        proposed_id = canonical_id or ("proposed-" + sha256_bytes(f"{package.package_ref}\n{candidate['original_source_id']}\n{candidate['candidate_object_class']}".encode())[:20] if disposition == "propose_create" else "")
        rec = ImportMappingRecord("1.0", mapping_id(package.package_ref, str(candidate["original_source_id"]), str(candidate["candidate_object_class"]), disposition, canonical_id), package.package_ref, package.identity.package_version, str(candidate["import_run_id"]), str(candidate["candidate_record_id"]), str(candidate["original_source_id"]), str(candidate["candidate_object_class"]), disposition, canonical_type, canonical_id, proposed_id, rationale, actor, utc_now())
        saved = self.repository.save(rec)
        self.ledger.append("import_mapping_recorded", saved.to_dict())
        return saved
