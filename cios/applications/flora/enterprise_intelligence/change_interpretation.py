"""Read-only external-to-enterprise interpretation in the existing EI boundary.

Canonical Evidence/Observation owners supply governed semantic annotations. This
module resolves and validates those annotations; it does not invent sector rules,
accept source facts, dispatch research or write Enterprise Models.
"""
from __future__ import annotations

from datetime import datetime, timezone

from cios.applications.flora.blueprint_import.material_pressure import (
    _active, _canonical, _refs, _supported, candidate_from_source, qualify_candidates,
)
from cios.applications.flora.blueprint_import.promotion import CanonicalJsonlRepository
from cios.applications.flora.blueprint_import.semantic_twin import SemanticObject, SemanticTwin, resolve_relationships
from cios.applications.flora.memory.repository import (
    ContradictionRepository, EnterpriseModelRepository, EvidenceRepository, ObservationRepository,
)
from .models import stable_hash


def _annotation(row, key):
    provenance=row.get('human_provenance') if isinstance(row,dict) else row.human_provenance
    if not isinstance(provenance,dict): return {}
    value=provenance.get(key,{})
    return value if isinstance(value,dict) else {}


def _evidence_refs(row):
    return _refs(row.get('supporting_evidence_ids') or row.get('evidence_refs') or row.get('evidence_ids'))


def _object(row, kind):
    """Project canonical owner rows into the existing relationship resolver."""
    identity=str(row['canonical_id'])
    return SemanticObject(identity,kind,str(row.get('name') or ''),'',_evidence_refs(row),'current','',
        'governed','','',True,original_id=identity,attributes=row)


class ExternalChangeInterpretationService:
    def __init__(self, observations=None, evidence=None, models=None, entities=None, relationships=None, contradictions=None, unknowns=None):
        self.observations=observations or ObservationRepository()
        self.evidence=evidence or EvidenceRepository()
        self.models=models or EnterpriseModelRepository()
        self.entities=entities or CanonicalJsonlRepository('entity')
        self.relationships=relationships or CanonicalJsonlRepository('relationship')
        self.contradictions=contradictions or ContradictionRepository()
        self.unknowns=unknowns or CanonicalJsonlRepository('unknown')

    def _support(self, refs, cutoff, enterprise=None):
        rows=[self.evidence.get(ref) for ref in refs]
        if not refs or not all(row and _active(row,cutoff) and row.get('confidence',1)!=0 for row in rows): return []
        if enterprise and not all(_canonical(row.get('enterprise_id') or row.get('canonical_enterprise_id') or row.get('organisation'))==enterprise
                                 and str(row.get('scope','')).casefold() not in {'industry','external'} for row in rows): return []
        return rows

    def _candidates(self, scope_id, allowed, cutoff):
        entities=[row for row in self.entities.list() if _active(row,cutoff)]
        relationships=[row for row in self.relationships.list() if _active(row,cutoff) and self._support(_evidence_refs(row),cutoff)]
        twin=SemanticTwin(tuple([*(_object(row,'entity') for row in entities),*(_object(row,'relationship') for row in relationships)]),())
        candidates={}
        def consider(obj, relationship=None):
            attrs=obj.attributes or {}
            kind=str(attrs.get('entity_type') or attrs.get('object_type') or '').casefold()
            ent=_canonical(attrs.get('enterprise_id') or attrs.get('canonical_enterprise_id') or obj.original_id)
            if kind not in {'enterprise','enterprise_twin','market_participant','market_participant_twin'} or ent not in allowed: return
            row=candidates.setdefault(ent,{'entity_refs':[],'relationship_refs':[],'relationship_evidence_refs':[]})
            row['entity_refs'].append(obj.original_id)
            if relationship:
                row['relationship_refs'].append(relationship.relationship.original_id)
                row['relationship_evidence_refs'].extend(relationship.relationship.evidence_refs)
        scope=next((obj for obj in twin.objects if obj.kind=='entity' and obj.original_id==scope_id),None)
        if not scope: return {}
        consider(scope)
        for rel in resolve_relationships(twin):
            if rel.status!='promoted relationship resolved': continue
            if rel.source_id==scope_id: consider(rel.target,rel)
            elif rel.target_id==scope_id: consider(rel.source,rel)
        return {ent:{key:sorted(set(value)) for key,value in row.items()} for ent,row in sorted(candidates.items())}

    def assess(self, evidence_id, *, allowed_enterprise_ids, cutoff=None):
        """Caller supplies its authorized target scope; this method never writes."""
        cutoff=cutoff or datetime.now(timezone.utc).date().isoformat()
        external=self.evidence.get(evidence_id)
        data=_annotation(external,'external_change') if external else {}
        result={'external_evidence_id':evidence_id,'event_state':'REJECTED','reason':'External Evidence or governed change descriptor is ineligible.',
                'assessments':[],'evidence_demands':[],'authority':'derived_runtime_assessment','canonical_mutation_allowed':False}
        if (not external or not _active(external,cutoff) or external.get('confidence',1)==0
                or str(external.get('scope','')).casefold() not in {'industry','external'}
                or not data.get('scope_id') or not data.get('time_context') or not _supported(data.get('statement'),[external])):
            return result
        scope=self.entities.get(str(data['scope_id']))
        if not scope or not _active(scope,cutoff): return result
        allowed={_canonical(ent) for ent in allowed_enterprise_ids}
        candidates=self._candidates(str(data['scope_id']),allowed,cutoff)
        result.update(event_state='ELIGIBLE',reason='Governed external context; Enterprise consequence requires separate support.')
        if allowed and not candidates:
            result['reason']='No eligible governed relationship resolves to an authorized Enterprise; this does not establish non-applicability.'
            result['evidence_demands'].append('Governed Enterprise identity and Evidence-backed canonical relationship to the external scope.')
        all_observations=self.observations.list()
        conflicts=[conflict for conflict in self.contradictions.list() if _active(conflict,cutoff)
                   and (not conflict.get('time_context') or conflict['time_context']==data['time_context'])]
        external_conflicts=[conflict for conflict in conflicts if evidence_id in
                           (*_evidence_refs(conflict),*_refs(conflict.get('counter_evidence_ids')))]
        for ent,links in list(candidates.items())[:50]:
            model=self.models.get(ent)
            annotated=[obs for obs in all_observations if _canonical(obs.enterprise_id)==ent
                       and _annotation(obs,'external_change_interpretation').get('evidence_id')==evidence_id
                       and _annotation(obs,'external_change_interpretation').get('time_context')==data['time_context']]
            current=[obs for obs in annotated if _active(obs,cutoff) and obs.confidence>0
                     and (not obs.human_provenance.get('effective_period') or obs.human_provenance['effective_period']==data['time_context'])
                     and not any(peer.supersedes_observation_id==obs.observation_id and _canonical(peer.enterprise_id)==ent
                                 and _active(peer,cutoff) for peer in all_observations)]
            row={'enterprise_id':ent,'external_evidence_id':evidence_id,'external_statement':data['statement'],
                 'time_context':data['time_context'],'state':'POTENTIALLY_APPLICABLE',
                 'explanation':'Governed relationship identifies a candidate; Enterprise applicability or consequence remains incomplete.',
                 **links,'observation_refs':[],'applicability_explanations':[],'mechanisms':[],'mitigations':[],'consequences':[],'unknown_refs':[],
                 'contradiction_refs':[],'contradictions':[],'evidence_demands':[],
                 'evidence_roles':{'external_context':[evidence_id],'relationship_context':links['relationship_evidence_refs'],
                                   'enterprise_support':[],'counter_evidence':[],'external_counter_evidence':[]},
                 'reassessment_targets':{'model_attributes':[],'material_pressures':[]},'pressure_qualification_previews':[],
                 'authority':'derived_runtime_assessment','canonical_mutation_allowed':False}
            states=set();sources=[];blocked=False
            core=str(external.get('contradiction_state') or 'none').casefold() not in {'none','resolved','closed'}
            def demand(text): row['evidence_demands'].append(text)
            if core:
                row['contradictions'].append('The external development has an unresolved governed conflict; its preferred assertion cannot establish Enterprise consequence.')
                row['contradiction_refs'].extend(_refs(external.get('contradiction_refs')))
            for conflict in external_conflicts:
                row['contradiction_refs'].append(conflict['contradiction_id'])
                row['evidence_roles']['external_counter_evidence'].extend(_refs(conflict.get('counter_evidence_ids')))
                if conflict.get('status','open') not in {'resolved','closed'}:
                    core=True;row['contradictions'].append('Canonical external conflict '+conflict['contradiction_id']+' remains unresolved.')
            for obs in current:
                annotation=_annotation(obs,'external_change_interpretation')
                backing=self._support(obs.supporting_evidence_ids,cutoff,ent)
                row['observation_refs'].append(obs.observation_id)
                if not backing or not _supported(annotation.get('applicability_basis'),backing):
                    demand('Accepted Enterprise-specific Evidence establishing applicability to '+evidence_id+'.')
                    continue
                row['evidence_roles']['enterprise_support'].extend(obs.supporting_evidence_ids)
                row['applicability_explanations'].append(annotation['applicability_basis'])
                sources.append(obs)
                state=annotation.get('applicability')
                if not isinstance(state,str): state=''
                if state in {'applicable','not_applicable','potential'}: states.add(state)
                else: demand('Explicit governed applicability assessment for '+evidence_id+'.')
                assertions_supported=True
                for field,output in (('mechanism','mechanisms'),('mitigation','mitigations'),('consequence','consequences')):
                    text=annotation.get(field)
                    if text and _supported(text,backing): row[output].append(text)
                    elif text:
                        assertions_supported=False;demand('Enterprise Evidence supporting the '+field+' assertion for '+evidence_id+'.')
                if not assertions_supported or state!='applicable':
                    # A partial or negative claim cannot smuggle a consequence
                    # into the available factual result.
                    if annotation.get('consequence') in row['consequences']: row['consequences'].remove(annotation['consequence'])
                for ref in _refs(annotation.get('unknown_refs')):
                    row['unknown_refs'].append(ref)
                    unknown=self.unknowns.get(ref) or model.unknowns.get(ref)
                    owner=unknown.get('enterprise_id') if isinstance(unknown,dict) else getattr(unknown,'enterprise_id',None)
                    if not unknown or _canonical(owner)!=ent:
                        blocked=True;demand('Resolve missing or out-of-scope Unknown '+ref+'.');continue
                    status=unknown.get('status','open') if isinstance(unknown,dict) else unknown.status
                    field=unknown.get('affected_field','') if isinstance(unknown,dict) else unknown.review_metadata.get('affected_field','')
                    noncore={'severity','magnitude','financial_magnitude','timing','precise_timing','duration','owner','response','resolution','resolution_path'}
                    if status not in {'resolved','closed'} and str(field).casefold().replace(' ','_') not in noncore:
                        blocked=True;demand('Resolve applicability/consequence Unknown '+ref+'.')
                historical_peers=set(obs.contradicted_by_observation_ids)
                row['contradiction_refs'].extend(sorted(historical_peers))
                peers=historical_peers if obs.contradiction_state not in {'resolved','closed'} else set()
                peers.update(peer.observation_id for peer in all_observations if obs.observation_id in peer.contradicted_by_observation_ids
                             and peer.contradiction_state not in {'none','resolved','closed'} and _active(peer,cutoff))
                if obs.contradiction_state not in {'none','resolved','closed'} or peers:
                    core=True;row['contradiction_refs'].extend(sorted(peers) or [obs.observation_id])
                    row['contradictions'].append('Governed Observation conflict leaves applicability or consequence unresolved.')
                    for ref in peers:
                        peer=self.observations.get(ref)
                        if peer and _canonical(peer.enterprise_id)==ent:
                            row['evidence_roles']['counter_evidence'].extend(peer.supporting_evidence_ids)
                        else: demand('Resolve conflicting Observation '+ref+'.')
                conflict_refs=set(_refs(annotation.get('contradiction_refs')))
                conflict_refs.update(conflict['contradiction_id'] for conflict in conflicts
                    if _canonical(conflict.get('enterprise_id'))==ent
                    and (set(_evidence_refs(conflict)).intersection(obs.supporting_evidence_ids)
                         or obs.observation_id in _refs(conflict.get('affected_observation_ids'))))
                for ref in sorted(conflict_refs):
                    conflict=self.contradictions.get(ref);row['contradiction_refs'].append(ref)
                    if not conflict or _canonical(conflict.get('enterprise_id'))!=ent:
                        core=True;demand('Resolve missing or out-of-scope Contradiction '+ref+'.');continue
                    row['evidence_roles']['counter_evidence'].extend(_refs(conflict.get('counter_evidence_ids')))
                    if conflict.get('status','open') not in {'resolved','closed'}:
                        core=True;row['contradictions'].append('Canonical conflict '+ref+' requires resolution.')
            for ref in row['evidence_roles']['counter_evidence']:
                if not self._support((ref,),cutoff,ent):
                    core=True;demand('Resolve missing, inactive or out-of-scope counter Evidence '+ref+'.')
            for ref in row['evidence_roles']['external_counter_evidence']:
                if not self._support((ref,),cutoff):
                    core=True;demand('Resolve external counter Evidence '+ref+'.')
            if 'applicable' in states and 'not_applicable' in states:
                core=True;row['contradictions'].append('Opposing Enterprise applicability assertions in the same event and effective period.')
            if core:
                row['state']='UNRESOLVED';row['explanation']='Governed applicability/consequence uncertainty or contradiction remains unresolved.'
                demand('Resolve competing applicability/consequence claims while retaining both Evidence paths.')
            elif not blocked and states=={'not_applicable'} and not row['consequences']:
                row['state']='NOT_APPLICABLE';row['explanation']='Enterprise-specific Evidence explicitly establishes non-applicability for this period.'
            elif not blocked and 'applicable' in states and row['mechanisms'] and row['consequences']:
                row['state']='APPLICABLE_WITH_EVIDENCED_CONSEQUENCE';row['explanation']='Separate Enterprise Evidence establishes applicability, mechanism and consequence.'
            else:
                demand('Enterprise-specific exposure/mitigation and an evidenced consequence for '+evidence_id+' in '+data['time_context']+'.')
            for obs in sources:
                attribute=model.attributes.get(obs.affected_attribute)
                if attribute and obs.observation_id in attribute.observation_ids:
                    row['reassessment_targets']['model_attributes'].append(obs.affected_attribute)
                for pressure in model.material_pressures.values():
                    if obs.observation_id in pressure.observation_refs or any(
                        (self.observations.get(ref) and self.observations.get(ref).affected_attribute==obs.affected_attribute)
                        for ref in pressure.observation_refs):
                        row['reassessment_targets']['material_pressures'].append(pressure.pressure_id)
                pressure_data=_annotation(obs,'material_pressure')
                if (row['state']=='APPLICABLE_WITH_EVIDENCED_CONSEQUENCE' and pressure_data
                        and pressure_data.get('consequence') in row['consequences'] and pressure_data.get('time_context')==data['time_context']):
                    qualification=qualify_candidates((candidate_from_source(obs),),observations=self.observations,evidence=self.evidence,
                        contradictions=self.contradictions,unknowns=self.unknowns,model=model,cutoff=cutoff)
                    row['pressure_qualification_previews'].extend({'pressure_id':a.identity,'qualification':a.qualification,'reason':a.reason,
                        'gates':dict(a.gate_results),'source_observation_id':obs.observation_id,'canonical_update_performed':False} for a in qualification.assessments)
            for key in ('observation_refs','applicability_explanations','mechanisms','mitigations','consequences','unknown_refs','contradiction_refs','contradictions','evidence_demands'):
                row[key]=sorted(set(row[key]))
            for group in ('evidence_roles','reassessment_targets'):
                row[group]={key:sorted(set(values)) for key,values in row[group].items()}
            row['assessment_id']='ECI-'+stable_hash([evidence_id,ent,data['time_context']])[:20]
            result['assessments'].append(row)
        if len(candidates)>50: result['limitation']='Candidate budget reached; assess remaining authorized enterprises in a separate bounded request.'
        return result

    def for_enterprise(self, enterprise_id, *, cutoff=None, limit=20):
        """Existing EI read-model adapter; no cross-enterprise output is returned."""
        results=[]
        for row in sorted(self.evidence.list(),key=lambda item:str(item.get('evidence_id',''))):
            if not _annotation(row,'external_change'): continue
            result=self.assess(row['evidence_id'],allowed_enterprise_ids=(enterprise_id,),cutoff=cutoff)
            results.extend(result['assessments'])
            if len(results)>=limit: break
        return results[:limit]
