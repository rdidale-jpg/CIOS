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
    reconciliation_kind: str = ""
    expected_target_fingerprint: str = ""
    source_scope: dict | None = None
    decision_origin: str = "manual"
    source_content_fingerprint: str = ""

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
        return sorted([json.loads(p.read_text(encoding="utf-8")) for p in root.glob("*.json")],key=lambda row:(row.get('created_at',''),row['mapping_id']))

class ImportMappingService:
    def __init__(self, registry=None, repository=None, ledger=None):
        self.registry = registry or BlueprintPackageRegistry(); self.repository = repository or ImportMappingRepository(); self.ledger = ledger or BlueprintImportLedger()
        self._industry = {}
    def record_mapping(self, candidate: dict[str, Any], disposition: MappingDisposition, actor: str, headers: Any, canonical_type: str = "", canonical_id: str = "", rationale: str = "", *, automatic=False) -> ImportMappingRecord:
        package = self.registry.get(str(candidate["source_package_ref"]))
        if not package or not can_review_blueprint_candidate(headers, package.identity.enterprise_id, package.workspace_id):
            raise BlueprintReviewError("Actor is not authorised to create Blueprint mappings")
        if disposition not in MappingDisposition.__args__:
            raise BlueprintReviewError("Unsupported mapping disposition")
        assessment={};scope=None
        if candidate['candidate_object_class']=='evidence' and disposition in {'map_existing','propose_create','propose_update','duplicate','unresolved'}:
            try:
                if package.package_ref not in self._industry: self._industry[package.package_ref]=industry_package(package)
                scope=governed_source_scope(package,record_owner(candidate.get('payload') or {},package),is_industry=self._industry[package.package_ref])
            except BlueprintReviewError as exc:
                assessment=dict(kind='unresolved identity',disposition='unresolved',canonical_id='',reason=str(exc),expected_target_fingerprint='')
            if not assessment: assessment=evidence_reconciliation(candidate,package,canonical_id=canonical_id,disposition=disposition,scope=scope)
            disposition=assessment['disposition'];canonical_id=assessment['canonical_id']
            rationale=rationale or assessment['reason']
        proposed_id = canonical_id or ("proposed-" + sha256_bytes(f"{package.package_ref}\n{candidate['original_source_id']}\n{candidate['candidate_object_class']}".encode())[:20] if disposition == "propose_create" else "")
        rec = ImportMappingRecord("1.0", mapping_id(package.package_ref, str(candidate["original_source_id"]), str(candidate["candidate_object_class"]), disposition, canonical_id), package.package_ref, package.identity.package_version, str(candidate["import_run_id"]), str(candidate["candidate_record_id"]), str(candidate["original_source_id"]), str(candidate["candidate_object_class"]), disposition, canonical_type, canonical_id, proposed_id, rationale, actor, utc_now())
        if assessment:
            rec=ImportMappingRecord(**{**rec.to_dict(),'reconciliation_kind':assessment['kind'],
                'expected_target_fingerprint':assessment['expected_target_fingerprint'],'source_scope':scope,
                'decision_origin':'automatic' if automatic else 'manual',
                'source_content_fingerprint':content_fingerprint(candidate.get('payload') or {}),
                'mapping_id':'bpi-map-'+sha256_bytes(json.dumps([rec.mapping_id,assessment,scope,rationale,automatic,content_fingerprint(candidate.get('payload') or {})],sort_keys=True).encode())[:24]})
        saved = self.repository.save(rec)
        if saved.created_at==rec.created_at: self.ledger.append("import_mapping_recorded", saved.to_dict())
        return saved


def source_payload(payload: dict) -> dict:
    """Exact producer content, excluding importer identity/provenance only."""
    if isinstance(payload.get('source_payload'), dict):
        return payload['source_payload']
    excluded={'evidence_id','canonical_id','enterprise_id','canonical_enterprise_id','blueprint_import_lineage',
              'source_release_provenance','governed_source_scope','source_external_id','source_content_fingerprint',
              'proposed_effect'}
    return {key:value for key,value in payload.items() if key not in excluded}


def content_fingerprint(payload: dict, *, assertion=False) -> str:
    content=source_payload(payload)
    if assertion:
        volatile={'collection_date','collected_at','last_confirmed_date','source_ref','confidence','freshness','access'}
        content={key:value for key,value in content.items() if key not in volatile}
    return sha256_bytes(json.dumps(content,sort_keys=True,separators=(',',':')).encode())


def target_fingerprint(row) -> str:
    content=None if row is None else {key:value for key,value in row.items()
        if key not in {'blueprint_import_lineage','source_release_provenance'}}
    return sha256_bytes(json.dumps(content,sort_keys=True,separators=(',',':')).encode())


def record_owner(payload, package):
    from cios.applications.flora.live.source_registry import canonical_enterprise_id
    owners={canonical_enterprise_id(str(payload[key])) for key in ('enterprise_id','canonical_enterprise_id') if payload.get(key)}
    if len(owners)>1: raise BlueprintReviewError('Conflicting Evidence Enterprise owners')
    return next(iter(owners)) if owners else canonical_enterprise_id(package.identity.enterprise_id)


def industry_package(package):
    from .candidates import CandidateStagingRepository
    from .twin_governance import project_twin_identity
    return (project_twin_identity(package).twin_type=='industry'
            or package.package_inspection.get('contract_type')=='Governed Industry Twin Package'
            or any(c['candidate_object_class']=='industry_twin' for c in CandidateStagingRepository().list_candidates(package.import_run_id)))


def governed_source_scope(package, owner, *, is_industry=None):
    from .twin_governance import project_twin_identity
    identity=project_twin_identity(package)
    is_industry=industry_package(package) if is_industry is None else is_industry
    if is_industry and (identity.status!='recognised' or identity.twin_type!='industry' or identity.primary_subject_class!='industry'):
        raise BlueprintReviewError('Explicit governed Industry Twin identity decision required')
    scope={'access_owner':record_owner({},package),'workspace_id':package.workspace_id,'enterprise_id':owner}
    if identity.status=='recognised':
        scope.update({key:getattr(identity,key) for key in ('twin_id','twin_type','primary_subject_id','primary_subject_class','canonical_owner','governed_scope')})
    return scope


def evidence_is_current(row):
    from .material_pressure import _active
    from datetime import datetime,timezone
    # Import acceptance is a lifecycle check. Full citation/date/support
    # qualification remains with ClaimValidator and ADR-026 unchanged.
    lifecycle_keys={'status','lifecycle_state','acceptance_state','validation_status','truth_status','truth_class','retired_at','freshness','evidence_freshness'}
    return row is not None and _active({key:value for key,value in row.items() if key in lifecycle_keys},datetime.now(timezone.utc).date().isoformat())


def evidence_reconciliation(candidate, package, *, canonical_id='', disposition='', scope=None):
    """Resolve source identity conservatively; no URL/word similarity merging."""
    from cios.applications.flora.memory.repository import EvidenceRepository
    payload=candidate.get('payload') or {};repo=EvidenceRepository();external=str(candidate['original_source_id'])
    try: scope=scope or governed_source_scope(package,record_owner(payload,package))
    except BlueprintReviewError as exc:
        return {'kind':'unresolved identity','disposition':'unresolved','canonical_id':'','reason':str(exc),'expected_target_fingerprint':''}
    all_rows=repo.list()
    if payload.get('contradicts_evidence_id') or payload.get('contradiction_state') in {'open','unresolved','conflict'}:
        return {'kind':'contradictory','disposition':'conflict','canonical_id':canonical_id,'reason':'Explicit source contradiction requires governed resolution','expected_target_fingerprint':''}
    matches=[row for row in all_rows if row.get('governed_source_scope')==scope and (row.get('source_external_id')==external or any(link.get('original_external_id')==external for link in row.get('source_release_provenance',[])))]
    explicit=bool(canonical_id)
    if not explicit and len(matches)>1:
        return {'kind':'unresolved identity','disposition':'unresolved','canonical_id':'','reason':'Multiple canonical targets for the same governed source identity','expected_target_fingerprint':''}
    prior=repo.get(canonical_id) if explicit else (matches[0] if matches else None)
    if explicit and prior:
        if record_owner(prior,package)!=scope['enterprise_id'] or (prior.get('governed_source_scope') and prior['governed_source_scope']!=scope):
            raise BlueprintReviewError('Evidence mapping crosses Enterprise or governed source scope')
    if prior:
        target=prior['evidence_id'];snapshot=target_fingerprint(prior)
        if not evidence_is_current(prior):
            kind,disp,reason='unresolved identity','unresolved','Canonical Evidence target is not current accepted support'
        elif content_fingerprint(prior)==content_fingerprint(payload):
            kind,disp,reason='unchanged','map_existing','Exact unchanged source content within approved scope'
        elif content_fingerprint(prior,assertion=True)==content_fingerprint(payload,assertion=True):
            kind,disp,reason='corroborating','propose_update','Same source assertion; collection/assurance metadata changed'
        elif disposition=='propose_update' and explicit:
            kind,disp,reason='updated','propose_update','Explicit owner-reviewed source content update; prior version retained'
        else:
            kind,disp,reason='unresolved identity','unresolved','Changed source assertion requires explicit owner update or conflict resolution'
        return dict(kind=kind,disposition=disp,canonical_id=target,reason=reason,expected_target_fingerprint=snapshot)
    if explicit and disposition in {'map_existing','propose_update','duplicate'}:
        raise BlueprintReviewError('Canonical Evidence mapping target does not exist')
    target=canonical_id or external
    collision=repo.get(target)
    if collision:
        if record_owner(collision,package)==scope['enterprise_id'] and not collision.get('governed_source_scope'):
            return {'kind':'unresolved identity','disposition':'unresolved','canonical_id':target,'reason':'Legacy Evidence scope requires explicit owner mapping','expected_target_fingerprint':target_fingerprint(collision)}
        target='EVID-'+sha256_bytes(json.dumps([scope,external],sort_keys=True).encode())[:24].upper()
        if repo.get(target): raise BlueprintReviewError('Scoped Evidence identifier collision; explicit mapping required')
    return dict(kind='new',disposition='propose_create',canonical_id=target,
        reason='New scoped Evidence'+(' — source-ID collision rebound to scoped target' if target!=external else ''),expected_target_fingerprint=target_fingerprint(None))
