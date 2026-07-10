from __future__ import annotations
from typing import Any

CLAIM_CLASSES={'canonical_fact_summary','evidence_backed_interpretation','projection','human_supplied_knowledge','unknown','contradiction','recommendation'}

class ClaimValidator:
    def validate(self, brief: dict[str,Any], package) -> dict[str,Any]:
        ids={i.stable_id:i for i in package.all_items() if i.stable_id}
        rejected=[]; weakened=[]
        def check_refs(refs, path, require=True):
            good=[]
            for r in refs or []:
                if r not in ids:
                    rejected.append({'path':path,'reason':f'invalid cited ID {r}'})
                elif ids[r].enterprise_id != package.enterprise_id:
                    rejected.append({'path':path,'reason':f'cross-enterprise cited ID {r}'})
                else: good.append(r)
            if require and not good: rejected.append({'path':path,'reason':'material claim lacks lineage'})
            return good
        for idx,item in enumerate(brief.get('material_pressures') or []):
            obs=check_refs(item.get('supporting_observation_ids'), f'material_pressures[{idx}].supporting_observation_ids')
            ev=check_refs(item.get('supporting_evidence_ids'), f'material_pressures[{idx}].supporting_evidence_ids', require=False)
            item['supporting_observation_ids']=obs; item['supporting_evidence_ids']=ev
            if item.get('confidence') in {'high', 'very_high'} and len(obs)+len(ev)<2:
                item['confidence']='medium'; weakened.append({'path':f'material_pressures[{idx}]','reason':'confidence weakened because support is limited'})
            for uid in item.get('linked_unknown_ids') or []:
                if uid in ids and ids[uid].truth_status=='unknown': continue
                rejected.append({'path':f'material_pressures[{idx}].linked_unknown_ids','reason':'unknown citation does not resolve to Unknown'})
        for idx,item in enumerate(brief.get('recommended_next_moves') or []):
            refs=item.get('lineage') or item.get('supporting_evidence') or []
            check_refs(refs, f'recommended_next_moves[{idx}].lineage')
        for key, klass in [('unknowns','unknown'),('contradictions','contradiction')]:
            for idx,item in enumerate(brief.get(key) or []):
                item['claim_classification']=klass
        brief['validation_status']={'status':'valid_with_weakening' if weakened and not rejected else ('invalid' if rejected else 'valid'), 'rejected_claims':rejected, 'weakened_claims':weakened, 'claim_classes':sorted(CLAIM_CLASSES)}
        return brief
