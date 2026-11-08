"""ADR-026 Material Pressure qualification over canonical Enterprise facts.

The qualifier is deliberately read-only.  It neither persists a second model nor
creates Opportunities, Procurements, or Watchpoints.  Candidate discovery consumes
the structured financial-condition fact already held by the canonical Enterprise
object; prose, presentation labels and rendered output are never searched.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import re
from hashlib import sha256

from .semantic_twin import SemanticEnterprise


@dataclass(frozen=True)
class PressureCandidate:
    canonical_input_id: str
    canonical_input_type: str
    enterprise_id: str
    condition: str
    affected_domain: str
    consequence: str
    consequence_domain: str
    evidence_refs: tuple[str, ...]
    applicable: bool = True
    pressure_semantics: bool = True
    materiality_established: bool = True
    consequence_established: bool = True
    lineage_established: bool = True
    unknown_refs: tuple[str, ...] = ()
    contradiction_refs: tuple[str, ...] = ()
    core_contradiction: bool = False
    time_context: str = ""
    condition_concept: str = ""
    scope: str = ""
    mechanism: str = ""
    identity_rationale: str = ""
    observation_refs: tuple[str, ...] = ()
    confidence: int | str | None = None
    observed_at: str = ""
    effective_at: str = ""
    resolved_at: str = ""
    resolution_evidence_refs: tuple[str, ...] = ()
    supersedes_pressure_id: str = ""


@dataclass(frozen=True)
class PressureAssessment:
    candidate: PressureCandidate
    identity: str
    applicability: str
    pressure_semantics: str
    materiality: str
    enterprise_consequence: str
    lineage: str
    qualification: str
    reason: str
    gate_results: tuple[tuple[str, str], ...] = ()
    counter_evidence_refs: tuple[str, ...] = ()

    @property
    def qualified(self) -> bool:
        return self.qualification == "QUALIFIED"


@dataclass(frozen=True)
class MaterialPressureQualification:
    assessments: tuple[PressureAssessment, ...]
    eligible_input_count: int = 0
    pipeline_error: str = ""

    @property
    def qualified(self) -> tuple[PressureAssessment, ...]:
        return tuple(a for a in self.assessments if a.qualified)

    @property
    def rejected(self) -> tuple[PressureAssessment, ...]:
        return tuple(a for a in self.assessments if a.qualification == "REJECTED")

    @property
    def unresolved(self) -> tuple[PressureAssessment, ...]:
        return tuple(a for a in self.assessments if a.qualification == "UNRESOLVED")

    @property
    def projection_state(self) -> str:
        if self.pipeline_error:
            return "FAILURE"
        if self.qualified:
            return "STRONG" if all(len(a.candidate.evidence_refs) > 1 for a in self.qualified) else "ACCEPTABLE"
        return "EMPTY" if not self.unresolved else "ACCEPTABLE"

    @property
    def candidates_assessed(self) -> int:
        return len(self.assessments)

    @property
    def discovery_state(self) -> str:
        if self.pipeline_error or (self.eligible_input_count and not self.assessments):
            return "PIPELINE_FAILURE"
        if not self.assessments and not self.eligible_input_count:
            return "NO_ELIGIBLE_INPUT"
        if not self.qualified:
            return "ASSESSED_NONE_QUALIFIED"
        return "ASSESSED_WITH_RESULTS"


def _canonical(value):
    from cios.applications.flora.live.source_registry import canonical_enterprise_id
    return canonical_enterprise_id(str(value or '')) or ''


def _get(source,key,default=None):
    return source.get(key,default) if isinstance(source,dict) else getattr(source,key,default)


def _descriptor(source):
    if isinstance(source,dict):
        return source.get('material_pressure') or (source.get('human_provenance') or {}).get('material_pressure') or {}
    return (source.human_provenance or {}).get('material_pressure') or {}


def _refs(value):
    return tuple(dict.fromkeys(str(v) for v in value)) if isinstance(value,(list,tuple)) else ((value,) if isinstance(value,str) and value else ())


def _date_ok(value,cutoff):
    if not value or str(value).casefold() in {'undated','unknown'}: return True
    try: return datetime.fromisoformat(str(value).replace('Z','+00:00')).date()<=datetime.fromisoformat(cutoff.replace('Z','+00:00')).date()
    except ValueError: return False


def _active(source,cutoff):
    if source is None: return False
    if str(_get(source,'status','')).casefold() in {'rejected','quarantined','retired','expired','superseded','pending','draft','invalid'}: return False
    for key in ('lifecycle_state','acceptance_state','validation_status','truth_status','truth_class'):
        state=str(_get(source,key,'') or '').casefold()
        if state in {'rejected','quarantined','retired','expired','superseded','candidate','staged','unresolved',
                     'unknown','hypothesis','projection','analytical_projection','inferred','human_supplied_knowledge'}: return False
        if state and state not in {'accepted','validated','valid','trusted','evidence','supports','evidence_backed','evidence-backed','observed','fact','factual'}: return False
    if _get(source,'retired_at'): return False
    if any(word in str(_get(source,'freshness','') or _get(source,'evidence_freshness','')).casefold() for word in ('expired','retired','superseded')): return False
    provenance=_get(source,'human_provenance',{}) or {}
    return (all(_date_ok(_get(source,key),cutoff) for key in ('observation_date','observed_at','effective_date','evidence_publication_date','publication_date','collection_date','last_confirmed_date'))
            and all(_date_ok(provenance.get(key),cutoff) for key in ('effective_date','source_date')))


def _supported(assertion,evidence):
    # Direct clause support is deliberately conservative: the governed semantic
    # interpretation supplies meaning; this check does not invent entailment.
    norm=lambda text:' '.join(re.findall(r'[\w£$€%]+',str(text).casefold()))
    if not assertion: return False
    for row in evidence:
        text=row.get('summary') or row.get('snippet') or row.get('claim') or row.get('cleaned_observation') or row.get('quote') or ''
        if any(norm(assertion)==norm(clause) for clause in re.split(r'(?<=[.!?;])\s+',str(text))): return True
    return False


def candidate_from_source(source,source_type='observation'):
    data=_descriptor(source)
    if not isinstance(data,dict): data={}
    return PressureCandidate(str(_get(source,'observation_id') if source_type=='observation' else _get(source,'canonical_id')),
        source_type,_canonical(_get(source,'enterprise_id')),str(data.get('condition') or ''),
        str(data.get('affected_domain') or ''),str(data.get('consequence') or ''),str(data.get('consequence_domain') or ''),
        _refs(_get(source,'supporting_evidence_ids') or _get(source,'evidence_refs') or _get(source,'evidence_ids')),
        unknown_refs=_refs(data.get('unknown_refs')),contradiction_refs=_refs(data.get('contradiction_refs')),
        time_context=str(data.get('time_context') or ''))


def semantic_identity(candidate: PressureCandidate) -> str:
    """Identity uses a governed semantic basis, never descriptive label wording."""
    if not candidate.condition_concept or not candidate.scope or not candidate.time_context:
        return ''
    basis='\x1f'.join((_canonical(candidate.enterprise_id),candidate.condition_concept,candidate.affected_domain,candidate.scope,candidate.time_context))
    return 'MP-'+sha256(basis.encode()).hexdigest()[:16].upper()


def qualify_candidates(candidates: tuple[PressureCandidate,...], *, observations=None,evidence=None,facts=None,contradictions=None,unknowns=None,model=None,cutoff=None) -> MaterialPressureQualification:
    from cios.applications.flora.memory.repository import ObservationRepository,EvidenceRepository,ContradictionRepository,EnterpriseModelRepository
    from .promotion import CanonicalJsonlRepository
    observations=observations or ObservationRepository(); evidence=evidence or EvidenceRepository()
    facts=facts or CanonicalJsonlRepository('fact'); contradictions=contradictions or ContradictionRepository()
    unknowns=unknowns or CanonicalJsonlRepository('unknown')
    cutoff=cutoff or datetime.now(timezone.utc).date().isoformat()
    domains={'strategic','financial/economic','operational','regulatory/obligation','investment','programme/change'}
    noncore={'severity','financial_magnitude','magnitude','timing','precise_timing','duration','owner','response','resolution','resolution_path'}
    assessments=[]; seen=set(); eligible_count=0
    for requested in candidates:
        source=(observations.get(requested.canonical_input_id) if requested.canonical_input_type=='observation' else
                facts.get(requested.canonical_input_id) if requested.canonical_input_type=='canonical_factual_object' else None)
        data=_descriptor(source) if source is not None else {}
        if not isinstance(data,dict): data={}
        enterprise=_canonical(requested.enterprise_id)
        owned_model=model if model is not None and _canonical(model.enterprise_id)==enterprise else EnterpriseModelRepository().get(enterprise)
        owned_refs=_refs(_get(source,'supporting_evidence_ids') or _get(source,'evidence_refs') or _get(source,'evidence_ids'))
        observation_refs=tuple(dict.fromkeys((*( (requested.canonical_input_id,) if requested.canonical_input_type=='observation' else ()),*_refs(data.get('observation_refs')))))
        source_observations=[observations.get(ref) for ref in observation_refs]
        ev_refs=tuple(dict.fromkeys((*owned_refs,*(ref for obs in source_observations if obs for ref in obs.supporting_evidence_ids))))
        evidence_rows=[evidence.get(ref) for ref in ev_refs]
        candidate=replace(requested,enterprise_id=enterprise,evidence_refs=ev_refs,observation_refs=observation_refs,
            unknown_refs=tuple(dict.fromkeys((*requested.unknown_refs,*_refs(data.get('unknown_refs'))))),
            contradiction_refs=tuple(dict.fromkeys((*requested.contradiction_refs,*_refs(data.get('contradiction_refs'))))),
            condition_concept=str(data.get('condition_concept') or ''),scope=str(data.get('scope') or ''),
            mechanism=str(data.get('mechanism') or ''),identity_rationale=str(data.get('identity_rationale') or ''),
            observed_at=str(_get(source,'observation_date') or _get(source,'observed_at') or ''),
            effective_at=str(data.get('effective_at') or _get(source,'observation_date') or ''),
            resolved_at=str(data.get('resolved_at') or ''),resolution_evidence_refs=_refs(data.get('resolution_evidence_refs')),
            supersedes_pressure_id=str(data.get('supersedes_pressure_id') or ''))
        identity=semantic_identity(candidate)
        previous_pressure=owned_model.material_pressures.get(identity)
        if previous_pressure:
            candidate=replace(candidate,unknown_refs=tuple(dict.fromkeys((*previous_pressure.unknown_refs,*candidate.unknown_refs))))
        binding=all(str(getattr(requested,key))==str(data.get(key) or '') for key in ('condition','affected_domain','consequence','consequence_domain','time_context'))
        eligible=(source is not None and _active(source,cutoff) and binding and bool(ev_refs)
                  and set(requested.evidence_refs)<=set(owned_refs)
                  and all(_active(row,cutoff) for row in evidence_rows)
                  and all(obs is not None and _active(obs,cutoff) for obs in source_observations))
        # The existing Observation owner keeps supersession as a relation; the
        # predecessor need not have had its lifecycle label rewritten.
        if any(peer.supersedes_observation_id in observation_refs and _active(peer,cutoff)
               and _canonical(peer.enterprise_id)==enterprise for peer in observations.list()):
            eligible=False
        if str(_get(source,'observation_type') or _get(source,'object_type') or '').casefold() in {'keyword','programme','program','opportunity','procurement','strategic_priority','renderer_text','generic_assumption'}:
            eligible=False
        applicable=(requested.applicable and data.get('applicable',True) and bool(enterprise) and _canonical(_get(source,'enterprise_id'))==enterprise
                    and all(_canonical(row.get('enterprise_id') or row.get('canonical_enterprise_id') or row.get('organisation'))==enterprise
                            and str(row.get('scope','')).casefold()!='industry' for row in evidence_rows if row)
                    and all(_canonical(obs.enterprise_id)==enterprise for obs in source_observations if obs))
        actual=[row for row in evidence_rows if row]
        causal=bool(re.search(r'\b(constrain|limit|reduc|increas|requir|forc|prevent|restrict|redirect|delay|accelerat|oblig|compress|affect)\w*',candidate.mechanism,re.I))
        semantics=(requested.pressure_semantics and data.get('pressure_semantics',True) and bool(candidate.condition) and causal
                   and candidate.mechanism!=data.get('condition_basis')
                   and _supported(data.get('condition_basis'),actual) and _supported(candidate.mechanism,actual))
        period=(_get(source,'human_provenance',{}) or {}).get('effective_period')
        identity_ok=bool(identity and _supported(candidate.identity_rationale,actual) and _date_ok(candidate.effective_at,cutoff)
                         and (not period or period==candidate.time_context))
        consequence_action=r'\b(constrain|limit|reduc|increas|requir|forc|prevent|restrict|redirect|delay|accelerat|oblig|compress|affect)\w*'
        materiality=(requested.materiality_established and data.get('materiality_established',True) and candidate.consequence_domain in domains
                     and bool(re.search(consequence_action,str(data.get('materiality_rationale') or ''),re.I))
                     and _supported(data.get('materiality_rationale'),actual))
        consequence=(requested.consequence_established and data.get('consequence_established',True) and bool(candidate.consequence)
                     and bool(re.search(consequence_action,candidate.consequence,re.I)) and candidate.consequence!=data.get('condition_basis')
                     and _supported(candidate.consequence,actual))
        lineage=bool(requested.lineage_established and ev_refs and all(evidence_rows))
        core=requested.core_contradiction or bool(data.get('core_contradiction')) or bool(data.get('core_unknowns'))
        contradiction_refs=list(candidate.contradiction_refs); counter_refs=[]; uncertainty_error='core Unknown remains unresolved' if data.get('core_unknowns') else ''
        for obs in source_observations:
            if obs and (obs.contradiction_state!='none' or obs.contradicted_by_observation_ids):
                if obs.contradiction_state.casefold() not in {'resolved','closed'}: core=True
                contradiction_refs.extend(obs.contradicted_by_observation_ids or (obs.observation_id,))
                for peer_id in obs.contradicted_by_observation_ids:
                    peer=observations.get(peer_id)
                    if peer and _canonical(peer.enterprise_id)==enterprise:
                        counter_refs.extend(peer.supporting_evidence_ids)
                    else: lineage=False
            if obs:
                for peer in observations.list():
                    if (obs.observation_id in peer.contradicted_by_observation_ids and _active(peer,cutoff)
                            and peer.contradiction_state.casefold() not in {'none','resolved','closed'}):
                        core=True;contradiction_refs.append(peer.observation_id);counter_refs.extend(peer.supporting_evidence_ids)
        for ref in candidate.unknown_refs:
            unknown=unknowns.get(ref) or owned_model.unknowns.get(ref)
            field=_get(unknown,'affected_field') or (_get(unknown,'review_metadata',{}) or {}).get('affected_field')
            if unknown is None or _canonical(_get(unknown,'enterprise_id'))!=enterprise: lineage=False
            elif str(_get(unknown,'status','open')).casefold() not in {'resolved','closed'} and str(field or '').casefold().replace(' ','_') not in noncore:
                core=True; uncertainty_error='core Unknown remains unresolved'
        for ref in candidate.contradiction_refs:
            conflict=contradictions.get(ref)
            if conflict is None or not _active(conflict,cutoff) or _canonical(conflict.get('enterprise_id'))!=enterprise:
                lineage=False; continue
            counter_refs.extend(_refs(conflict.get('counter_evidence_ids')))
            if conflict.get('status','open').casefold() not in {'resolved','closed'} and not _refs(conflict.get('counter_evidence_ids')): lineage=False
            if conflict.get('status','open').casefold() not in {'resolved','closed'} and str(conflict.get('affected_field') or '').casefold().replace(' ','_') not in noncore:
                core=True
        for ref in counter_refs:
            row=evidence.get(ref)
            if not _active(row,cutoff) or _canonical((row or {}).get('enterprise_id'))!=enterprise: lineage=False
        supplied_confidence=[_get(source,'confidence'),*(row.get('confidence') for row in actual)]
        confidence=[v for v in supplied_confidence if isinstance(v,(int,float))]
        labels=[str(v).casefold() for v in supplied_confidence if isinstance(v,str) and v]
        if confidence and min(confidence)<=0: eligible=False
        eligible_count+=int(bool(eligible))
        confidence_value=min(confidence) if confidence else None
        if labels:
            confidence_value=min(labels,key=lambda label: {'unknown':0,'low':1,'medium':2,'high':3}.get(label,0))
        candidate=replace(candidate,confidence=confidence_value,contradiction_refs=tuple(dict.fromkeys(contradiction_refs)))
        gates=(eligible,applicable,semantics,identity_ok,materiality,consequence and lineage)
        names=('eligible_input','enterprise_applicability','pressure_semantics','identity','materiality','consequence_and_lineage')
        reasons=('ineligible input','wrong Enterprise','insufficient Pressure semantics','identity reconciliation required',
                 'materiality not established','insufficient lineage' if not lineage else 'Enterprise consequence not established')
        qualification='QUALIFIED';reason='all ADR-026 mandatory gates passed'
        if not all(gates):
            index=gates.index(False);reason=reasons[index]
            qualification='UNRESOLVED' if index==3 and all(gates[:3]) else 'REJECTED'
        elif core:
            qualification='UNRESOLVED';reason=uncertainty_error or 'core contradiction'
        if any(p.source_input_id==requested.canonical_input_id and p.source_input_type==requested.canonical_input_type
               and p.pressure_id!=identity for p in owned_model.material_pressures.values()):
            qualification='UNRESOLVED';reason='source identity changed; explicit reconciliation required'
        if previous_pressure and previous_pressure.superseded_by:
            qualification='UNRESOLVED';reason='superseded Pressure requires governed reconciliation'
        if previous_pressure and previous_pressure.resolved_at and not candidate.resolved_at:
            reopened=(data.get('reopens_pressure_id')==identity and _supported(data.get('requalification_basis'),actual)
                      and bool(candidate.effective_at) and _date_ok(previous_pressure.resolved_at,candidate.effective_at))
            if not reopened:
                qualification='UNRESOLVED';reason='resolved Pressure requires governed reconciliation'
        if qualification=='QUALIFIED':
            for existing in owned_model.material_pressures.values():
                if (existing.pressure_id!=identity and existing.affected_domain==candidate.affected_domain
                        and existing.scope==candidate.scope and existing.time_context==candidate.time_context
                        and existing.pressure_id not in _refs(data.get('distinct_from'))
                        and existing.pressure_id!=candidate.supersedes_pressure_id):
                    qualification='UNRESOLVED';reason='semantic identity reconciliation required against '+existing.pressure_id
                    break
        if candidate.resolved_at:
            target=owned_model.material_pressures.get(str(data.get('resolves_pressure_id') or ''))
            resolution=[evidence.get(ref) for ref in candidate.resolution_evidence_refs]
            resolution_ok=(eligible and applicable and identity_ok and not data.get('core_unknowns') and target is not None and target.pressure_id==identity
                and bool(resolution) and all(_active(row,cutoff) and _canonical(row.get('enterprise_id'))==enterprise for row in resolution)
                and _supported(data.get('resolution_basis'),[row for row in resolution if row]) and _date_ok(candidate.resolved_at,cutoff)
                and _date_ok(target.effective_at,candidate.resolved_at))
            qualification='REJECTED' if resolution_ok else 'UNRESOLVED'
            reason='resolved through governed Evidence' if resolution_ok else 'resolution lineage or target is unresolved'
            if not resolution_ok: candidate=replace(candidate,resolved_at='')
        if candidate.supersedes_pressure_id and qualification=='QUALIFIED':
            target=owned_model.material_pressures.get(candidate.supersedes_pressure_id)
            if (target is None or target.pressure_id==identity or target.supersedes_pressure_id==identity
                    or (target.superseded_by and target.superseded_by!=identity) or not _supported(data.get('supersession_basis'),actual)):
                qualification='UNRESOLVED';reason='supersession lineage or target is unresolved'
        if qualification=='QUALIFIED' and identity in seen:
            qualification='REJECTED';reason='duplicate/same Pressure'
        if qualification=='QUALIFIED': seen.add(identity)
        assessments.append(PressureAssessment(candidate,identity,'PASS' if applicable else 'FAIL','PASS' if semantics else 'FAIL',
            'PASS' if materiality else 'FAIL','PASS' if consequence else 'FAIL','PASS' if lineage else 'FAIL',qualification,reason,
            tuple((name,'PASS' if value else 'FAIL') for name,value in zip(names,gates)),tuple(dict.fromkeys(counter_refs))))
    return MaterialPressureQualification(tuple(assessments),eligible_count)


def material_pressure_qualification(ent: SemanticEnterprise) -> MaterialPressureQualification:
    """Read-only diagnostics; staged/renderer labels cannot self-authorise truth."""
    try:
        identity=next((o for o in ent.records if o.kind in {'enterprise_twin','enterprise','entity'}),None)
        if identity is None: return MaterialPressureQualification(())
        attrs=identity.attributes or {};financial=attrs.get('financial_intelligence') or attrs.get('financial_context') or {}
        if not isinstance(financial,dict): return MaterialPressureQualification(())
        conditions=financial.get('major_financial_pressures') or attrs.get('executive_risks') or ()
        conditions=(conditions,) if isinstance(conditions,str) else tuple(conditions)
        evidence=financial.get('evidence') or (attrs.get('executive_overview') or {}).get('evidence') or ()
        consequence=str(financial.get('financial_outlook') or '')
        candidates=tuple(PressureCandidate(identity.original_id or identity.record_id,'canonical_factual_object',ent.identity_key,
            str(condition),'financial/economic',consequence,'financial/economic',_refs(evidence),
            applicable=identity.eligible_conclusion and identity.validation_status=='accepted') for condition in conditions)
        return qualify_candidates(candidates)
    except (AttributeError,TypeError,ValueError) as exc:
        return MaterialPressureQualification((),0,'candidate discovery failed: '+type(exc).__name__)


def model_pressure_assessments(model, *, observations=None,evidence=None,cutoff=None):
    """Read-only current assurance; never promote a stored/staged label by itself."""
    from cios.applications.flora.memory.repository import ObservationRepository
    from .promotion import CanonicalJsonlRepository
    observations=observations or ObservationRepository()
    rows=[]
    for pressure in sorted(model.material_pressures.values(),key=lambda p:p.pressure_id):
        source=observations.get(pressure.source_input_id) if pressure.source_input_type=='observation' else CanonicalJsonlRepository('fact').get(pressure.source_input_id)
        assessment=None
        if source:
            assessed=qualify_candidates((candidate_from_source(source,pressure.source_input_type),),observations=observations,evidence=evidence,model=model,cutoff=cutoff)
            assessment=assessed.assessments[0] if assessed.assessments else None
        qualification=assessment.qualification if assessment else 'REJECTED'
        if pressure.resolved_at or pressure.superseded_by: qualification='REJECTED'
        rows.append({'pressure_id':pressure.pressure_id,'qualification':qualification,
            'reason':assessment.reason if assessment else 'canonical source is unavailable',
            'condition':pressure.condition,'consequence':pressure.consequence,
            'observation_refs':assessment.candidate.observation_refs if assessment else pressure.observation_refs,
            'evidence_refs':assessment.candidate.evidence_refs if assessment else pressure.current_evidence_refs,
            'counter_evidence_refs':assessment.counter_evidence_refs if assessment else pressure.counter_evidence_refs,
            'unknown_refs':pressure.unknown_refs,'contradiction_refs':pressure.contradiction_refs,
            'observed_at':pressure.observed_at,'effective_at':pressure.effective_at,
            'last_change':pressure.last_change,'gates':dict(assessment.gate_results) if assessment else {}})
    known={row['pressure_id'] for row in rows}
    for assessment in model.pressure_assessments.values():
        if assessment.get('identity') not in known and assessment.get('qualification')!='QUALIFIED':
            rows.append({'pressure_id':assessment.get('identity',''),'qualification':assessment['qualification'],
                'reason':assessment['reason'],'gates':dict(assessment.get('gate_results',[])),
                'condition':assessment['candidate']['condition'],'consequence':assessment['candidate']['consequence'],
                'evidence_refs':assessment['candidate']['evidence_refs'],'observation_refs':assessment['candidate']['observation_refs'],
                'unknown_refs':assessment['candidate']['unknown_refs'],'contradiction_refs':assessment['candidate']['contradiction_refs'],
                'observed_at':assessment['candidate']['observed_at'],'effective_at':assessment['candidate']['effective_at'],
                'counter_evidence_refs':assessment.get('counter_evidence_refs',()),'last_change':'diagnostic only'})
    return rows
