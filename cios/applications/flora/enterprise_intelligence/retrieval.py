from __future__ import annotations
from datetime import datetime, timezone

from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository, EvidenceRepository
from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasService
from cios.applications.flora.live.source_registry import canonical_enterprise_id
from .models import EvidencePackageItem, EvidencePackageV1, ReasoningRequestV1, stable_hash

THEME_WORDS=('affordability','productivity','readiness','availability','programme','operational effect','data','AI','industrial','supplier','workforce','skills','decision','commercial','contract','capability','system')


def _date_ok(value, cutoff):
    if not value or str(value).casefold() in {'undated', 'unknown'}:
        return True
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00')).date() <= datetime.fromisoformat(cutoff.replace('Z', '+00:00')).date()
    except ValueError:
        return False


def _active(freshness, status='accepted'):
    return str(status).casefold() in {'accepted', 'validated', 'trusted', 'evidence', 'supports', 'evidence_backed'} and not any(
        word in str(freshness).casefold() for word in ('expired', 'retired', 'superseded'))


def score_item(statement, confidence=0, freshness=''):
    s=str(statement).casefold(); score=int(confidence or 0)
    score += sum(18 for w in THEME_WORDS if w.casefold() in s)
    if any(w in s for w in ('unknown','unclear','contradict','conflict')): score += 35
    if freshness == 'current': score += 15
    if any(w in s for w in ('material','strategic','executive','owner','pressure','change')): score += 20
    return score


class BoundedTwinRetrievalService:
    def __init__(self, models=None, observations=None, evidence=None, canvas=None):
        self.models=models or EnterpriseModelRepository(); self.observations=observations or ObservationRepository(); self.evidence=evidence or EvidenceRepository(); self.canvas=canvas or EnterpriseCanvasService()

    def retrieve(self, request: ReasoningRequestV1) -> EvidencePackageV1:
        enterprise=canonical_enterprise_id(request.enterprise_id) or request.enterprise_id
        cutoff=request.evidence_cut_off or datetime.now(timezone.utc).date().isoformat()
        model=self.models.get(enterprise)
        all_observations=[o for o in self.observations.list() if (canonical_enterprise_id(o.enterprise_id) or o.enterprise_id)==enterprise]
        observations=[o for o in all_observations if _active(o.freshness, o.lifecycle_state)
                      and not o.retired_at
                      and all(_date_ok(d, cutoff) for d in (o.observation_date, o.evidence_publication_date,
                              o.collection_date, o.last_confirmed_date, o.human_provenance.get('effective_date')))]
        superseded={o.supersedes_observation_id for o in observations if o.supersedes_observation_id}
        observations=[o for o in observations if o.observation_id not in superseded]
        eligible_ids={o.observation_id for o in observations}
        known_ids={o.observation_id for o in all_observations}
        eligible_evidence={eid for o in observations for eid in o.supporting_evidence_ids}
        inactive_evidence={eid for o in all_observations if o.observation_id not in eligible_ids
                           for eid in o.supporting_evidence_ids} - eligible_evidence
        observations.sort(key=lambda o: score_item(o.atomic_statement,o.confidence,o.freshness), reverse=True)
        budget=max(1000, request.maximum_evidence_volume); used=0; obs_items=[]; human=[]; contradictions=[]; dates={}
        for o in observations:
            text=o.atomic_statement[:900]; cost=len(text)
            if used+cost>budget: break
            used+=cost
            contested=o.contradiction_state!='none' or bool(o.contradicted_by_observation_ids)
            status='human_supplied_knowledge' if o.provenance_type=='human-supplied' else ('contradiction' if contested else o.lifecycle_state)
            item=EvidencePackageItem(o.observation_id or '', 'observation', text, status, o.confidence, o.freshness, tuple(o.supporting_evidence_ids), tuple(o.contradicted_by_observation_ids), '', enterprise)
            if contested: contradictions.append(item)
            elif o.provenance_type=='human-supplied': human.append(item)
            else: obs_items.append(item)
            dates[item.stable_id]={'observed_date':o.observation_date, 'source_publication_date':o.evidence_publication_date,
                                  'collection_date':o.collection_date, 'last_confirmed_date':o.last_confirmed_date,
                                  'effective_date':o.human_provenance.get('effective_date'),
                                  'source_date':o.human_provenance.get('source_date'),
                                  'effective_period':o.human_provenance.get('effective_period'),
                                  'supersedes_observation_id':o.supersedes_observation_id, 'retired_at':o.retired_at}
        entities=[]; programmes=[]; attribute_dates={}
        for a in model.attributes.values():
            if not _active(a.freshness, a.trust_state) or not _date_ok(a.last_observed_date, cutoff):
                continue
            # A current snapshot cannot resurrect a retired/future/superseded
            # Observation. Missing legacy references remain visible as missing
            # support; the claim validator must resolve Evidence before use.
            refs=set(a.observation_ids)
            if refs and refs & known_ids and not refs & eligible_ids:
                continue
            backing=[o for o in all_observations if o.observation_id in refs
                     and a.last_observed_date in {o.observation_date, o.last_confirmed_date}]
            if backing and not any(o.observation_id in eligible_ids for o in backing):
                continue
            contested=a.contradiction_state!='none' or bool(a.conflicting_observation_ids)
            item=EvidencePackageItem(a.attribute,'entity_relationship' if a.domain not in {'programme','initiative'} else 'programme', f"{a.attribute}: {a.current_value or 'Unknown'}", 'contradiction' if contested else a.trust_state, a.confidence, a.freshness, tuple(a.evidence_ids), tuple(a.observation_ids), '', enterprise)
            (programmes if a.domain in {'programme','initiative'} or 'programme' in a.attribute else entities).append(item)
            attribute_dates[a.attribute]=a.last_observed_date
        unknowns=[EvidencePackageItem(u.unknown_id,'unknown',u.question,'unknown',u.priority,'current',tuple(u.related_observation_ids),(),'',enterprise) for u in model.unknowns.values() if u.status=='open']
        obs_items=obs_items[:30]; entities=entities[:25]; programmes=programmes[:15]
        unknowns=unknowns[:20]; contradictions=contradictions[:20]; human=human[:20]
        selected=[*obs_items,*entities,*programmes,*unknowns,*contradictions,*human]
        contested_evidence={ref for i in selected if i.truth_status=='contradiction' for ref in i.lineage}
        lineage=list(dict.fromkeys(ref for i in selected for ref in (i.stable_id,*i.lineage)))
        ev_by_id={str(e.get('evidence_id')):e for e in self.evidence.list()
                  if (canonical_enterprise_id(str(e.get('enterprise_id') or e.get('canonical_enterprise_id') or e.get('organisation') or enterprise)) or enterprise)==enterprise
                  and _active(e.get('freshness') or e.get('evidence_freshness'), e.get('lifecycle_state') or e.get('truth_status') or 'accepted')
                  and all(_date_ok(e.get(d), cutoff) for d in ('publication_date','effective_date','observation_date','collection_date'))}
        evidence_items=[]
        for eid in lineage:
            ev=ev_by_id.get(eid)
            if ev and eid not in inactive_evidence:
                evidence_items.append(EvidencePackageItem(eid,'evidence',str(ev.get('summary') or ev.get('snippet') or ev.get('claim') or ev.get('cleaned_observation') or ev.get('source_title') or '')[:900], 'contradiction' if eid in contested_evidence else str(ev.get('truth_status') or ev.get('stance') or 'evidence'),ev.get('confidence',''),ev.get('freshness',''),(),(),str(ev.get('source_location') or ev.get('source_locator') or ''),enterprise))
        context={'enterprise_id':enterprise, 'observation_dates':{i.stable_id:dates[i.stable_id] for i in selected if i.stable_id in dates},
                 'model_attribute_dates':{i.stable_id:attribute_dates[i.stable_id] for i in selected if i.stable_id in attribute_dates}}
        package_dict={'enterprise':enterprise,'cutoff':cutoff,'context':context,'items':[i.to_dict() for i in (*selected,*evidence_items)]}
        return EvidencePackageV1('ep-'+stable_hash(package_dict)[:16],enterprise,context,request.twin_version,request.evidence_cut_off,
            'Progressive Assurance accepted',tuple(obs_items+evidence_items),tuple(entities),tuple(programmes),tuple(unknowns),tuple(contradictions),tuple(human),tuple(),tuple(lineage),
            'current','bounded',('Scoped to requested enterprise and evidence cut-off.',
                'Retired, expired, superseded and future support excluded; original records retained.',
                'Ranked and trimmed to configured observation budget and per-family limits; supporting Evidence retained.'))
