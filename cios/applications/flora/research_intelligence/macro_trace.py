"""Candidate entity/instrument projections over existing evidence, never legal authority.

No private-store access or persistence. MacroContextReference is an adapter design
for deliberate future capture; it cannot be submitted to today's capture service.
"""
from copy import deepcopy
from datetime import date
import json
from typing import Literal
from pydantic import Field, model_validator
from . import macro_intelligence as macro
from .cycle import digest
from .model import load_assessment, commercial_capture
from .understanding import load_review

PATH = macro.PATH.parent / 'Entity-Traces-v2.json'


class Alternative(macro.Specification):
    interpretation: str
    status: Literal['unverified', 'supported_possibility']
    test: str
    source_ids: list[str] = Field(min_length=1)


class EntityTrace(macro.Specification):
    id: str
    country_id: Literal['GB', 'FR']
    industry_id: Literal['banking', 'aviation']
    force_id: str
    instrument_id: str
    instrument_status: str
    instrument_effective_from: date
    implementation_milestone: date | None
    enterprise_id: str
    entity: macro.LegalEntityScope
    applicability: Literal['unknown']  # This reviewed cut proves no binding entity duty.
    scope_reason: str
    pestle: str
    capability_ids: list[str] = Field(min_length=1)
    consequence: str
    hypothesis_id: str | None
    question: str
    source_ids: list[str] = Field(min_length=1)
    alternatives: list[Alternative] = Field(min_length=2)
    limitations: list[str] = Field(min_length=1)
    contradictions: list[str] = Field(min_length=1)
    supersedes: str | None

    @model_validator(mode='after')
    def preserve_entity_boundary(self):
        if self.entity.enterprise_id != self.enterprise_id:
            raise ValueError('Group/entity scope mismatch')
        if self.country_id == 'FR' and self.entity.status != 'unknown':
            raise ValueError('French registry identity is unresolved in this reviewed cut')
        if self.country_id == 'FR' and self.hypothesis_id:
            raise ValueError('No reviewed French hypothesis association')
        return self


def load_traces():
    data = json.loads(PATH.read_text())
    previous = macro.load_context()
    if (data['schema_version'] != 2 or data['authority'] != 'candidate_intelligence'
            or data['previous_context_digest'] != digest(previous)
            or date.fromisoformat(data['as_of']) > date.today()):
        raise ValueError('Trace version, lineage or cut-off drift')
    # Reuse the full SourceSegment/CandidateClaim validation and SemanticTwin owner.
    combined = deepcopy(previous)
    combined.update(as_of=data['as_of'], sources=previous['sources'] + data['sources'],
                    observations=previous['observations'] + data['observations'])
    macro.validate_context(combined)
    sources = {s['id'] for s in combined['sources']}
    source_rows = {s['id']:s for s in combined['sources']}
    seen = set(); contexts = set()
    for row in data['traces']:
        trace = EntityTrace(**row)
        if trace.id in seen:
            raise ValueError('Duplicate trace identity')
        seen.add(trace.id)
        key=(trace.country_id,trace.industry_id,trace.force_id)
        if key in contexts:raise ValueError('Ambiguous market trace')
        contexts.add(key)
        if trace.entity.status=='verified':
            identity_text=' '.join(macro.primary_text(source_rows[sid]) for sid in trace.entity.evidence_ids if sid in source_rows)
            if (trace.entity.registry_id not in identity_text or trace.entity.legal_name not in identity_text
                    or trace.entity.legal_entity_id!='GB-COH-'+trace.entity.registry_id):
                raise ValueError('Verified identity exceeds located registry passage')
        assessment = load_assessment(trace.industry_id)
        if trace.enterprise_id != assessment['enterprise_twin_id']:
            raise ValueError('Canonical enterprise identity drift')
        force = next((f for f in previous['forces'] if f['id'] == trace.force_id), None)
        if not force or trace.country_id not in force['country_ids']:
            raise ValueError('Unsupported force/country trace')
        if set(trace.capability_ids) - {c['id'] for c in assessment['capabilities']}:
            raise ValueError('Unknown canonical capability')
        if trace.pestle not in {f['title'] for f in assessment['frameworks'] if f['lens']=='pestle'}:
            raise ValueError('Unknown PESTLE factor')
        if trace.hypothesis_id:
            candidate = next((c for c in assessment['candidates'] if c['id']==trace.hypothesis_id), None)
            if not candidate or not set(trace.capability_ids).intersection(candidate['capability_ids']):
                raise ValueError('Unsupported hypothesis/capability association')
        references = set(trace.source_ids) | set(trace.entity.evidence_ids)
        references.update(sid for alt in trace.alternatives for sid in alt.source_ids)
        if references - sources:
            raise ValueError('Unresolved trace provenance')
        if trace.instrument_effective_from > date.fromisoformat(data['as_of']):
            raise ValueError('Future effectivity is not reviewed current scope')
    return data, combined


def trace_projection(chosen):
    if not isinstance(chosen, macro.Selection):
        raise ValueError('Validated selection required')
    data, combined = load_traces()
    rows = [deepcopy(t) for t in data['traces'] if t['country_id']==chosen.market
            and t['industry_id']==chosen.industry and t['force_id']==chosen.force]
    if not rows:
        return None  # Global never silently selects a UK legal entity.
    trace = rows[0]
    claims = {o['source_id']:o['candidate']['claim_id'] for o in combined['observations']}
    scope = trace['entity']
    steps = [
        ('ENTITY_IDENTIFICATION', scope['legal_entity_id'] or scope['id'], scope['status'], scope['evidence_ids']),
        ('INSTRUMENT_STATUS', trace['instrument_id'], 'source_supported', trace['source_ids']),
        ('FORMAL_APPLICABILITY', scope['id'], 'unknown', trace['source_ids']),
        ('BUSINESS_CONSEQUENCE', trace['capability_ids'][0], 'interpreted', trace['source_ids']),
        ('CUSTOMER_RESPONSE', trace['enterprise_id'], 'unknown', trace['source_ids']),
        ('SUPPLIER_OPPORTUNITY', trace['hypothesis_id'] or 'not-established', 'unknown', trace['source_ids'])]
    edges = [dict(id=trace['id']+'::'+predicate, subject=trace['force_id'], predicate=predicate,
                  object=target, status=status, country_id=trace['country_id'],
                  instrument_id=trace['instrument_id'], entity_scope_id=scope['id'],
                  source_ids=refs, claim_ids=[claims[s] for s in refs],
                  assessed_at=data['as_of'], effective_from=trace['instrument_effective_from'],
                  limitations=trace['limitations'], supersedes=trace['supersedes'])
             for predicate,target,status,refs in steps]
    return {**trace, 'as_of':data['as_of'], 'edges':edges,
            'sources':[s for s in combined['sources'] if s['id'] in trace['source_ids']],
            'observations':[o for o in combined['observations'] if o['source_id'] in trace['source_ids']],
            'assessment_digest':digest(data), 'review_digest':digest(trace),
            'source_context_digest':data['previous_context_digest'],
            'automatic_capture':False, 'automatic_qualification':False}


class MacroContextReference(macro.Specification):
    """Version 1 immutable adapter proposal; not a writable Pipeline payload."""
    trace_id: str
    force_id: str
    instrument_id: str
    country_id: Literal['GB','FR']
    jurisdiction_ids: list[str]
    entity_scope: macro.LegalEntityScope
    applicability: Literal['unknown']
    context_edge_ids: list[str]
    claim_ids: list[str]
    assessment_digest: str
    review_digest: str
    research_assessment_digest: str
    research_review_digest: str
    source_context_digest: str
    assessed_at: date
    instrument_effective_from: date
    limitations: list[str]
    contradictions: list[str]
    original_hypothesis_id: str


def capture_reference(chosen, hypothesis_id):
    """Server-derived design-only proposal. Deliberately never alters capture identity."""
    trace = trace_projection(chosen)
    if not trace or not trace['hypothesis_id'] or trace['hypothesis_id'] != hypothesis_id:
        raise ValueError('No reviewed trace association for this original hypothesis')
    capture = commercial_capture('lloyds', hypothesis_id)
    reference = MacroContextReference(
        trace_id=trace['id'], force_id=trace['force_id'], instrument_id=trace['instrument_id'],
        country_id=trace['country_id'], jurisdiction_ids=['UK-PRA'], entity_scope=trace['entity'],
        applicability='unknown', context_edge_ids=[e['id'] for e in trace['edges']],
        claim_ids=sorted({cid for e in trace['edges'] for cid in e['claim_ids']}),
        assessment_digest=trace['assessment_digest'], review_digest=trace['review_digest'],
        research_assessment_digest=capture['provenance']['assessment_digest'],
        research_review_digest=digest(load_review(chosen.industry)),
        source_context_digest=trace['source_context_digest'], assessed_at=trace['as_of'],
        instrument_effective_from=trace['instrument_effective_from'],
        limitations=trace['limitations'], contradictions=trace['contradictions'],
        original_hypothesis_id=hypothesis_id).model_dump(mode='json')
    return {'reference':reference, 'reference_digest':digest(reference),
            'persistence_supported':False, 'qualification_changed':False,
            'reason':'Existing authorised capture accepts commercial fields only. Integrate via its owner after #557/#561 reconciliation; no persistence change in this sprint.'}


def validate_reference(reference, chosen, hypothesis_id):
    """Reject stale, tampered or caller-constructed projection before future handoff."""
    expected = capture_reference(chosen, hypothesis_id)
    if reference != expected:
        raise ValueError('Macro reference differs from server-owned reviewed projection')
    return deepcopy(expected)
