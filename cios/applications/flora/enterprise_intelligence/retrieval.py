from __future__ import annotations
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository, EvidenceRepository
from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasService
from cios.applications.flora.live.source_registry import canonical_enterprise_id
from .models import EvidencePackageItem, EvidencePackageV1, ReasoningRequestV1, stable_hash

THEME_WORDS=('affordability','productivity','readiness','availability','programme','operational effect','data','AI','industrial','supplier','workforce','skills','decision','commercial','contract','capability','system')

def _date_ok(value, cutoff): return not cutoff or not value or str(value) <= cutoff

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
        model=self.models.get(enterprise)
        observations=[o for o in self.observations.list() if (canonical_enterprise_id(o.enterprise_id) or o.enterprise_id)==enterprise and _date_ok(o.observation_date, request.evidence_cut_off)]
        observations.sort(key=lambda o: score_item(o.atomic_statement,o.confidence,o.freshness), reverse=True)
        budget=max(1000, request.maximum_evidence_volume); used=0; obs_items=[]; human=[]; contradictions=[]; lineage=[]
        for o in observations:
            text=o.atomic_statement[:900]; cost=len(text)
            if used+cost>budget: break
            used+=cost; lineage.extend([o.observation_id or '', *o.supporting_evidence_ids])
            item=EvidencePackageItem(o.observation_id or '', 'observation', text, o.lifecycle_state if o.provenance_type!='human-supplied' else 'human_supplied_knowledge', o.confidence, o.freshness, tuple(o.supporting_evidence_ids), tuple(o.contradicted_by_observation_ids), '', enterprise)
            if o.provenance_type=='human-supplied': human.append(item)
            elif o.contradiction_state!='none' or o.contradicted_by_observation_ids: contradictions.append(item)
            else: obs_items.append(item)
        ev_by_id={str(e.get('evidence_id')):e for e in self.evidence.list() if (canonical_enterprise_id(str(e.get('enterprise_id') or enterprise)) or str(e.get('enterprise_id') or enterprise))==enterprise}
        entities=[]; programmes=[]
        for a in model.attributes.values():
            item=EvidencePackageItem(a.attribute,'entity_relationship' if a.domain not in {'programme','initiative'} else 'programme', f"{a.attribute}: {a.current_value or 'Unknown'}", a.trust_state, a.confidence, a.freshness, tuple(a.evidence_ids), tuple(a.observation_ids), '', enterprise)
            (programmes if a.domain in {'programme','initiative'} or 'programme' in a.attribute else entities).append(item)
        unknowns=[EvidencePackageItem(u.unknown_id,'unknown',u.question,'unknown',u.priority,'current',tuple(u.related_observation_ids),(),'',enterprise) for u in model.unknowns.values() if u.status=='open']
        evidence_items=[]
        for eid in dict.fromkeys(lineage):
            ev=ev_by_id.get(eid)
            if ev: evidence_items.append(EvidencePackageItem(eid,'evidence',str(ev.get('summary') or ev.get('snippet') or ev.get('claim') or ev.get('source_title') or '')[:900], str(ev.get('truth_status') or ev.get('stance') or 'evidence'), ev.get('confidence',''), ev.get('freshness',''), (), (), str(ev.get('source_location') or ev.get('source_locator') or ''), enterprise))
        package_dict={'enterprise':enterprise,'obs':[i.to_dict() for i in obs_items[:30]],'unk':[i.to_dict() for i in unknowns], 'contr':[i.to_dict() for i in contradictions]}
        return EvidencePackageV1('ep-'+stable_hash(package_dict)[:16], enterprise, {'enterprise_id':enterprise}, request.twin_version, request.evidence_cut_off, 'Progressive Assurance accepted', tuple(obs_items[:30]+evidence_items[:20]), tuple(entities[:25]), tuple(programmes[:15]), tuple(unknowns[:20]), tuple(contradictions[:20]), tuple(human[:20]), tuple(), tuple(dict.fromkeys(lineage)), 'current', 'bounded', ('Scoped to requested enterprise and evidence cut-off.', 'Ranked by materiality, recency, evidence strength, change significance, decision and commercial relevance, uncertainty and contradiction; not by record count.', 'Trimmed to configured evidence volume.'))
