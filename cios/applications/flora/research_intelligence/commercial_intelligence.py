"""Read-only commercial presentation over existing hypothesis and evidence owners."""
from copy import deepcopy
from datetime import date
from .model import commercial_candidates,commercial_dimensions
from .living_map_specs import build_living_map
from .visual_intelligence_specs import load_profile,build_intelligence_specs
from .understanding import load_review,source_quality
from .cycle import digest


def commercial_projection(data,review=None,as_of=None):
    domain=data.get('research_domain','banking');review=review if review is not None else load_review(domain)
    as_of=as_of or date.today().isoformat();scene=build_living_map(data,review,as_of=as_of)
    candidates=commercial_candidates(data);profile=load_profile(domain)
    refs=list(dict.fromkeys(c for row in candidates for c in row['claim_ids']+row['commercial']['evidence_claim_ids']))
    # Explicit source-owned hypothesis links are bound to the assessed snapshot.
    linked={c['id']:[] for c in candidates}
    sources={s['id']:s for s in data['sources']+review.get('sources',[])}
    for observation in review.get('observations',[]):
        source=sources[observation['source_id']]
        if source.get('assessment_digest')==digest(data) and observation['candidate']['subject']==data['enterprise_twin_id']:
            for cid in source.get('hypothesis_ids',[]):
                if cid in linked:linked[cid].append(observation['candidate']['claim_id'])
    refs+=list(dict.fromkeys(cid for values in linked.values() for cid in values))
    refs+=list(dict.fromkeys(c for conflict in scene['conflicts'] for c in conflict['claim_ids']))
    # A transient presentation selection reuses the existing exact source resolver.
    # It is never a canonical actor or persisted research record.
    profile['actors'].append({'id':'VIEW-COMMERCIAL-EVIDENCE','label':'Commercial source selection','category':'Presentation selection','claim_refs':list(dict.fromkeys(refs))})
    source_spec=build_intelligence_specs(data,review,profile,as_of)['industry-signature']
    catalog=next(n['evidence'] for n in source_spec['nodes'] if n['id']=='VIEW-COMMERCIAL-EVIDENCE')
    quality={s['id']:source_quality(s,as_of) for s in data['sources']+review['sources']}
    for proof in catalog:
        if any(not quality[s]['eligible_at_cutoff'] or quality[s]['kind'] in ('Search-index-only excerpt','Unverified source reference') for s in proof['source_ids']):
            proof['supported']=False;proof['state']='Unverified/index-only context at this research cut-off'
    evidence={p['id']:p for p in catalog};gaps={g['id']:g for g in data['gaps']}
    root=data.get('route_root','/flora/banking/research');rows=[]
    for row in candidates:
        n=deepcopy(row);commercial=n['commercial']
        activities=[a for a in scene['map_nodes'] if set(a['canonical_ids']) & set(n['capability_ids']) or {p['id'] for p in a['programme_links']} & set(n.get('programme_ids',[]))]
        conflict_ids={c for a in activities for c in a['conflict_ids']}
        conflicts=[deepcopy(c) for c in scene['conflicts'] if c['id'] in conflict_ids or set(c['claim_ids']) & set(n['claim_ids'])]
        n['support']=[deepcopy(evidence[c]) for c in dict.fromkeys(n['claim_ids']+commercial['evidence_claim_ids']+linked[n['id']]) if c in evidence]
        n['conflicts']=conflicts
        n['counterevidence']=[deepcopy(evidence[c]) for c in dict.fromkeys(c for conflict in conflicts for c in conflict['claim_ids']) if c in evidence]
        n['context_supported']=any(p['supported'] for p in n['support'])
        n['activities']=[{'id':a['id'],'label':a['label'],'url':scene['industry']['url']+'?lens=commercial#lm-'+domain+'-'+a['id']} for a in activities]
        n['url']=root+'/candidates/'+n['id']
        n['enterprise_url']=scene['enterprise']['url']+'?lens=commercial'
        n['gaps']=[deepcopy(gaps[g]) for g in n['gap_ids'] if g in gaps]
        n['assessment_date']=data['assessed_at'];n['status']='Unqualified research hypothesis'
        n['dimensions']=[{'id':key,'label':key.replace('_',' ').title(),**deepcopy(commercial[key]),
            'anchor':data.get('commercial_assessment',{}).get('rating_anchors',{}).get(key,{}).get(str(commercial[key]['score']),'Ordinal authored assessment; inspect the stated rationale. Not a probability.')} for key in commercial_dimensions(data)]
        n['assessment_limitation']='Authored research assessment retained at its original date; current support/counterevidence is shown separately. Not a recomputed win probability, verified need or Pipeline qualification.'
        n['review_digest']=digest(review)
        n['inspection_digest']=digest({'assessment':digest(data),'review':digest(review),'candidate_id':n['id'],'as_of':as_of})
        rows.append(n)
    return {'authority':'candidate_intelligence','automatic_capture':False,'automatic_qualification':False,
        'domain':domain,'industry':scene['industry'],'enterprise':scene['enterprise'],'as_of':as_of,
        'assessment_digest':digest(data),'review_digest':digest(review),'snapshot_digest':digest({'scene':scene['snapshot_digest'],'sources':source_spec['snapshot_digest']}),
        'activities':[{'id':a['id'],'label':a['label'],'url':scene['industry']['url']+'?lens=commercial#lm-'+domain+'-'+a['id']} for a in scene['map_nodes']],
        'candidates':rows}


def commercial_map(scene,projection):
    if scene['domain']!=projection['domain'] or scene['enterprise']['id']!=projection['enterprise']['id']:raise ValueError('Commercial map scope mismatch')
    result=deepcopy(scene)
    for node in result['map_nodes']:
        rows=[r for r in projection['candidates'] if node['id'] in {a['id'] for a in r['activities']}]
        node['commercial_candidates']=deepcopy(rows)
        node['commercial_supported_count']=sum(r['context_supported'] for r in rows)
    result['commercial_snapshot']=projection['snapshot_digest']
    return result


def frozen_review(row):
    return {'authority':'candidate_intelligence','assessment_date':row['assessment_date'],'review_digest':row['review_digest'],
        'inspection_digest':row['inspection_digest'],'support_claim_ids':[p['id'] for p in row['support']],
        'counterevidence_claim_ids':[p['id'] for p in row['counterevidence']],
        'activity_ids':[a['id'] for a in row['activities']],
        'limitations':'Snapshot of public candidate research, not accepted Evidence or customer-confirmed demand. Historical supplier context is not a current contract.'}
