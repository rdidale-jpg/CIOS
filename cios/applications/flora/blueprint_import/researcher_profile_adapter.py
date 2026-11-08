"""Reusable Researcher profile to canonical candidate-field adapter.

The adapter is driven by the versioned machine-readable Twin Object Profile
contract in :mod:`cios.contracts.twin_object_profiles` so Flora does not carry a
second prose-only semantic contract for Researcher packages.
"""
from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from typing import Any


def _contract_resource():
    return files("cios.contracts.twin_object_profiles").joinpath("researcher_v1.json")


def _contract() -> dict[str, Any]:
    return json.loads(_contract_resource().read_text())


def contract_checksum() -> str:
    """Return the SHA-256 checksum for the loaded Researcher Twin Object Profile."""
    return hashlib.sha256(_contract_resource().read_bytes()).hexdigest()


CONTRACT = _contract()
_CLASS_ALIASES = {k: v["canonical_class"] for k, v in CONTRACT["profiles"].items() if "canonical_class" in v}


def adapt_researcher_payload(record_class: str, source: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Return the governed canonical owner class and a lossless payload."""
    canonical_class = _CLASS_ALIASES.get(record_class, record_class)
    profile = CONTRACT["profiles"].get(canonical_class, {})
    p = dict(source)
    p["source_payload"] = dict(source)
    p["transformation_adapter"] = CONTRACT["document_id"]

    aliases: dict[str, Any] = {}
    for target, selectors in CONTRACT["common_fields"].items():
        value = _first_value(source, selectors)
        if value not in (None, "", [], {}):
            aliases[target] = value
    for target, selectors in profile.get("fields", {}).items():
        value = _first_value(source, selectors)
        if value not in (None, "", [], {}):
            aliases[target] = value

    p.update(aliases)
    consumed = set(_flatten_selectors(CONTRACT["common_fields"].values())) | set(_flatten_selectors(profile.get("fields", {}).values()))
    p["mapping_diagnostics"] = {
        "contract_id": CONTRACT["document_id"],
        "contract_status": CONTRACT["status"],
        "contract_version": CONTRACT.get("profile_version", ""),
        "contract_checksum": contract_checksum(),
        "source_fields": sorted(source),
        "mapped_fields": sorted(aliases),
        "unmapped_fields": sorted(set(source) - {field.split('.', 1)[0] for field in consumed if field != "$self"}),
    }
    return canonical_class, p


def _first_value(source: dict[str, Any], selectors: list[Any]) -> Any:
    for selector in selectors:
        if selector == "$self":
            return source
        if isinstance(selector, str):
            value = _path_value(source, selector)
        elif isinstance(selector, list):
            values = [_path_value(source, item) for item in selector]
            value = [item for item in values if item not in (None, "", [], {})]
        elif isinstance(selector, dict):
            value = {key: _path_value(source, path) for key, path in selector.items()}
            value = {key: item for key, item in value.items() if item not in (None, "", [], {})}
        else:
            value = None
        if value not in (None, "", [], {}):
            return value
    return None


def _path_value(source: dict[str, Any], path: str) -> Any:
    value: Any = source
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _flatten_selectors(groups) -> list[str]:
    out: list[str] = []
    for selectors in groups:
        for selector in selectors:
            if isinstance(selector, str):
                out.append(selector)
            elif isinstance(selector, list):
                out.extend(str(item) for item in selector)
            elif isinstance(selector, dict):
                out.extend(str(item) for item in selector.values())
    return out


# A reviewed handoff of producer-written claims, not a prose extraction engine.
HANDOFF_TYPES = ('enterprise_event_announced', 'partnership_announced',
                 'executive_appointment_announced', 'leadership_change_announced')


def handoff_offers(candidates):
    """Inspect explicit dossier Evidence links; never turn dossier prose into facts."""
    from .atomicity import validate_atomic_statement
    by_id = {c['original_source_id']: c for c in candidates
             if c['candidate_object_class'] == 'evidence'}
    offers = []
    for wrapper in candidates:
        if wrapper['candidate_object_class'] != 'enterprise_twin':
            continue
        source = wrapper['payload'].get('source_payload') or {}
        for ref in source.get('evidence', []):
            evidence = by_id.get(ref)
            raw = (evidence or {}).get('payload', {}).get('source_payload') or {}
            statement = raw.get('supported_claim')
            from .mapping import evidence_is_current
            reason = ''
            if raw.get('contradiction_state') not in (None,'','none') or raw.get('contradicts_evidence_id'):
                reason='Unresolved source contradiction'
            elif not evidence_is_current(raw) or not evidence_is_current((evidence or {}).get('payload',{})):
                reason='Evidence is not current accepted support'
            elif not evidence or evidence.get('validation_status') != 'accepted':
                reason = 'Missing or ineligible staged Evidence'
            elif not isinstance(statement, str) or not statement.strip():
                reason = 'No explicit producer supported_claim'
            elif not validate_atomic_statement(statement).atomic:
                reason = 'Unsupported, speculative or compound producer claim'
            else:
                try:
                    _handoff_dates(raw)
                    from cios.applications.flora.memory.models import Observation
                    Observation('preview', HANDOFF_TYPES[0], statement, raw['publication_date'],
                                raw['collection_date'], 'events.preview', 50, (ref,))
                except (ValueError, TypeError):
                    reason = 'Incomplete/future dates, unverified source or invalid Observation contract'
            offers.append({'wrapper_id': wrapper['candidate_record_id'],
                           'enterprise_source_id': wrapper['original_source_id'],
                           'enterprise_name': source.get('name', ''), 'evidence_source_id': ref,
                           'statement': statement or '', 'reason': reason,
                           'status': 'deferred' if reason else 'owner_review_required'})
    return offers


def _handoff_dates(raw):
    from datetime import date
    if raw.get('verified') is False or str(raw.get('verification_status','')).casefold() in {'unverified','rejected','disputed'}:
        raise ValueError('Explicitly unverified source remains candidate material')
    for key in ('publication_date', 'collection_date', *(['effective_date'] if raw.get('effective_date') else [])):
        value = raw.get(key)
        if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
            raise ValueError('Handoff requires complete ISO publication and collection dates')
        if date.fromisoformat(value) > date.today():
            raise ValueError('Future source dates are not current support')


def stage_observation_handoff(import_run_id, wrapper_id, evidence_source_id,
                              enterprise_id, observation_type, attribute,
                              actor, rationale, headers, *, selected_subset=False):
    """Owner-confirmed pre-acceptance handoff into the existing staged objects.

    selected_subset is an explicit operator decision to defer other records.
    No accepted canonical Evidence is reassigned or copied by this function.
    """
    from .candidates import CandidateImportRecord, ValidationFinding, candidate_id, CandidateStagingRepository
    from .registry import BlueprintPackageRegistry
    from .lifecycle import ImportLifecycleService
    from .promotion import can_approve_blueprint_promotion, _as_confidence
    from .mapping import ImportMappingService, evidence_is_current, content_fingerprint
    from .review import CandidateReviewService
    from .ledger import BlueprintImportLedger, utc_now
    from cios.applications.flora.live.source_registry import canonical_enterprise_id
    from cios.applications.flora.memory.models import Observation
    from cios.applications.flora.memory.service import CLAIM_VOCABULARY
    from cios.applications.flora.memory.repository import EvidenceRepository

    staging = CandidateStagingRepository()
    rows = staging.list_candidates(import_run_id)
    package = next((p for p in BlueprintPackageRegistry().list() if p.import_run_id == import_run_id), None)
    target = canonical_enterprise_id(enterprise_id)
    if not package or not target or not can_approve_blueprint_promotion(headers, package.identity.enterprise_id) or not can_approve_blueprint_promotion(headers, target):
        raise PermissionError('Handoff requires owner promotion authority for package and target enterprise')
    state = ImportLifecycleService().get(import_run_id)
    if state.state in {'promoted', 'superseded', 'archived', 'cancelled', 'deleted'} or state.canonical_writes:
        raise ValueError('Handoff requires an unaccepted active package; no legacy reassignment')
    if not rationale.strip():
        raise ValueError('An explicit enterprise mapping and handoff rationale is required')
    offer = next((o for o in handoff_offers(rows) if o['wrapper_id'] == wrapper_id and o['evidence_source_id'] == evidence_source_id), None)
    if not offer or offer['reason']:
        raise ValueError((offer or {}).get('reason') or 'Evidence is not explicitly linked from this dossier')
    if observation_type not in HANDOFF_TYPES or not attribute.startswith(CLAIM_VOCABULARY[observation_type]['attribute_prefix']) or attribute.endswith('.'):
        raise ValueError('Select an existing supported event/leadership Observation attribute')
    wrapper = next(c for c in rows if c['candidate_record_id'] == wrapper_id)
    source = next(c for c in rows if c['candidate_object_class'] == 'evidence' and c['original_source_id'] == evidence_source_id)
    raw = source['payload']['source_payload']
    declared=source['payload'].get('canonical_enterprise_id') or source['payload'].get('enterprise_id')
    if declared and canonical_enterprise_id(declared) not in {target,canonical_enterprise_id(package.identity.enterprise_id)}:
        raise ValueError('Source Evidence explicitly belongs to another enterprise')
    if raw.get('contradiction_state') not in (None,'','none') or raw.get('contradicts_evidence_id'):
        raise ValueError('Unresolved source contradiction requires review outside this handoff')
    if not evidence_is_current(source['payload']) or not evidence_is_current(raw):
        raise ValueError('Rejected, expired or retired Evidence cannot support a handoff')
    assigned = source['payload'].get('researcher_handoff_owner')
    if assigned and assigned != target:
        raise ValueError('Selected Evidence already has a different explicit enterprise owner')
    # Existing canonical ownership is immutable here; use the existing scoped
    # mapping path, which rejects foreign accepted targets rather than copying.
    for row in EvidenceRepository().list():
        if row.get('source_external_id') == evidence_source_id and row.get('governed_source_scope', {}).get('access_owner') == canonical_enterprise_id(package.identity.enterprise_id) and row.get('enterprise_id') != target:
            raise ValueError('Evidence was already accepted under a different owner')
    mapper = ImportMappingService()
    identity_mapping = mapper.record_mapping(wrapper, 'map_existing', actor, headers,
                                             'Enterprise', target, rationale)
    metadata = {'source_wrapper_id': wrapper_id, 'enterprise_mapping_id': identity_mapping.mapping_id,
                'source_evidence_id': evidence_source_id, 'source_content_fingerprint': content_fingerprint(source['payload']),
                'canonical_enterprise_id': target, 'rationale': rationale, 'actor': actor,
                'date_basis': 'source publication date; event-effective timing not inferred',
                'uncertainty': raw.get('uncertainty'), 'source_confidence': raw.get('confidence'),
                'wrapper_unknowns': wrapper['payload'].get('source_payload',{}).get('unknowns',[]),
                'wrapper_contradictions': wrapper['payload'].get('source_payload',{}).get('contradictions',[])}
    hp = {'researcher_handoff': metadata, 'source_date': raw['publication_date']}
    hp.update({key: raw[key] for key in ('effective_date', 'effective_period', 'scope') if raw.get(key)})
    obs = Observation(target, observation_type, raw['supported_claim'], raw['publication_date'],
                      raw['collection_date'], attribute, _as_confidence(raw.get('confidence')),
                      (evidence_source_id,), evidence_publication_date=raw['publication_date'],
                      human_provenance=hp, contradiction_state=raw.get('contradiction_state') or 'none',
                      supersedes_observation_id=raw.get('supersedes_observation_id'))
    payload = obs.to_dict() | {'researcher_handoff': metadata,
                              'source_payload': raw, 'summary': raw['supported_claim']}
    cid = candidate_id(package.package_ref, source['source_file'], obs.observation_id, 'observation')
    candidate = CandidateImportRecord('1.0', cid, package.package_ref, package.package_sha256,
        source['source_file'], source['source_sheet'], source['source_location'], obs.observation_id,
        'observation', 'observed', payload, 'accepted', (), content_fingerprint(payload), utc_now(), import_run_id)
    existing = next((c for c in rows if c['candidate_record_id'] == cid), None)
    if existing:
        if existing['payload'].get('researcher_handoff') != metadata:
            raise ValueError('An existing handoff requires a new reviewed decision; do not overwrite staged lineage')
        return existing
    evidence_payload = dict(source['payload'], canonical_enterprise_id=target,
                            researcher_handoff_owner=target, summary=raw['supported_claim'])
    # Do not replace original source_payload, location or source fingerprint.
    typed = CandidateImportRecord(**{**source, 'payload': evidence_payload,
        'validation_findings': tuple(ValidationFinding(**f) for f in source.get('validation_findings', []))})
    # All preflight checks precede staging writes. These are review artefacts,
    # not a canonical transaction. Failure cannot write memory/model state.
    staging.save_candidate(typed)
    staging.save_candidate(candidate)
    mapper.record_mapping(typed.to_dict(), 'propose_create', actor, headers, 'Evidence', rationale=rationale)
    mapper.record_mapping(candidate.to_dict(), 'propose_create', actor, headers, 'Observation', obs.observation_id, rationale)
    review = CandidateReviewService()
    review.record_decision(cid, 'defer', actor, 'Explicit Observation review required after handoff', headers)
    if selected_subset:
        for row in rows:
            if row['candidate_record_id'] != source['candidate_record_id'] and row['validation_status'] == 'accepted':
                review.record_decision(row['candidate_record_id'], 'defer', actor,
                                       'Owner selected subset handoff; remaining candidate preserved', headers)
    summary = staging.load_summary(import_run_id) or {}
    current = staging.list_candidates(import_run_id)
    summary.update(candidate_records_staged=len(current), records_accepted_into_staging=sum(c['validation_status'] == 'accepted' for c in current))
    staging.save_summary(import_run_id, summary)
    BlueprintImportLedger().append('researcher_observation_handoff_staged',
        {'import_run_id': import_run_id, 'candidate_id': cid, **metadata, 'selected_subset': selected_subset,
         'canonical_writes': 0})
    return candidate.to_dict()


def validate_handoff(candidate, candidates, mappings):
    """Recheck source and owner decisions at approval/execution, before writes."""
    from .mapping import content_fingerprint, evidence_is_current
    p = candidate.get('payload') or {}
    handoff = p.get('researcher_handoff')
    if not handoff:
        return
    source = next((c for c in candidates if c['candidate_object_class'] == 'evidence' and c['original_source_id'] == handoff['source_evidence_id']), None)
    identity = next((m for m in mappings if m['mapping_id'] == handoff['enterprise_mapping_id']), None)
    if not source or source['validation_status'] != 'accepted' or not evidence_is_current(source['payload']):
        raise ValueError('Handoff supporting source is missing or ineligible')
    raw = source['payload'].get('source_payload') or {}
    if not evidence_is_current(raw): raise ValueError('Original source Evidence is not current support')
    _handoff_dates(raw)
    if (p.get('atomic_statement') != raw.get('supported_claim') or
        content_fingerprint(source['payload']) != handoff['source_content_fingerprint'] or
        p.get('enterprise_id') != handoff['canonical_enterprise_id'] or
        source['payload'].get('canonical_enterprise_id') != p.get('enterprise_id') or
        not identity or identity.get('canonical_type') != 'Enterprise' or identity.get('canonical_id') != p.get('enterprise_id') or
        identity.get('candidate_id') != handoff['source_wrapper_id'] or
        p.get('observation_date') != raw.get('publication_date') or p.get('collection_date') != raw.get('collection_date') or
        p.get('supporting_evidence_ids') != [handoff['source_evidence_id']]):
        raise ValueError('Handoff source, dates or governed enterprise mapping changed; review again')
