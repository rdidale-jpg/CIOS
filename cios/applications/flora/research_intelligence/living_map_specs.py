"""Presentation-only industry systems over the v1 validated visual projection."""
from copy import deepcopy
from datetime import date
import json
from .registry import assessment_path
from .visual_intelligence_specs import build_intelligence_specs,load_profile
from .understanding import load_review
from .cycle import digest


def load_mapping(domain):
    return json.loads((assessment_path(domain).parent/'Living-Map.json').read_text())


def build_living_map(data,review=None,mapping=None,as_of=None):
    domain=data.get('research_domain','banking');mapping=deepcopy(mapping if mapping is not None else load_mapping(domain))
    if mapping.get('version')!=2 or mapping.get('domain')!=domain:raise ValueError('Wrong living-map presentation boundary')
    if not mapping.get('activities'):raise ValueError('No mapped industry activities')
    profile=load_profile(domain);profile['metrics']['industry']=mapping['metrics']
    profile['living_map']=mapping # Snapshot digest covers the complete presentation mapping.
    extras=([('CLIENTS','Passengers','people',0),('LESSORS','Aircraft lessors','plane',2),('GROUND','Ground handlers','terminal',3),('ATM','Air traffic management','tower',3),('FUEL','Fuel providers','leaf',7),('CREW','Pilots & cabin crew','people',2),('TRAVEL','Travel partners','ticket',8)] if domain=='aviation' else [('INFRA','Market infrastructure','network',3),('FINTECH','Fintech challengers','spark',0)])
    for key,label,icon,activity in extras:
        pid='LM-ROLE-'+key
        profile['actors'].append({'id':pid,'label':label,'category':'Industry role — specific operators unverified','icon':icon,'presentation_state':'unknown','purpose':'A conceptual role in this industry model. Specific providers, current contracts and enterprise applicability require research.'})
        mapping['participant_roles'][pid]=mapping['activities'][min(activity,len(mapping['activities'])-1)]['id']
    base=build_intelligence_specs(data,review if review is not None else load_review(domain),profile,as_of or date.today().isoformat())
    signature=base['industry-signature'];activities={n['id']:n for n in base['enterprise-story']['nodes']}
    rows=[]
    for row in mapping['activities']:
        if row['id'] not in activities:raise ValueError('Unresolved source activity')
        if len(row['position'])!=2 or any(not isinstance(x,(int,float)) or not 60<=x<=limit for x,limit in zip(row['position'],(1380,900))):raise ValueError('Invalid map placement')
        n=deepcopy(activities[row['id']]);n.update(row)
        n.update(scope_id=data['industry_twin_id'],category='Conceptual industry activity',state='Challenged / scope unresolved' if n['conflict_ids'] else 'Conceptual industry structure',limitations='Industry-standard explanatory model, not a verified organisation, system or contractual map. Reference-company disclosures illustrate their own entity and period only; they do not prove sector-wide adoption.')
        rows.append(n)
    if not rows:raise ValueError('No mapped industry activities')
    ids={n['id'] for n in rows}
    if len(ids)!=len(rows):raise ValueError('Duplicate map activity')
    for f in mapping['flows']:
        if f['kind'] not in ('Money','Services','Risk','Information','Control','Demand','Resources','Passengers','Availability','Service') or f['source'] not in ids or f['target'] not in ids or f['state']!='Conceptual industry flow; not verified enterprise topology':raise ValueError('Unresolved or falsely verified industry flow')
    flowids=[f['id'] for f in mapping['flows']]
    if len(flowids)!=len(set(flowids)):raise ValueError('Duplicate flow')
    actors=signature['nodes']
    for i,n in enumerate(actors):
        target=mapping['participant_roles'].get(n['id'])
        if target is None:target=rows[min(6,len(rows)-1)]['id'] # New research suppliers are context, not automatic activity incumbency.
        if target not in ids:raise ValueError('Foreign participant role')
        n['activity_id']=target
        n['position_override']=mapping.get('participant_locations',{}).get(n['id'])
        n['documented_relationships']=[deepcopy(edge) for edge in base['enterprise-story']['relationships'] if edge['state']=='Verified factual relationship' and edge['object'] in n['canonical_ids'] and edge['subject']==data['enterprise_twin_id']]
        n['association_state']='Role/context placement only; not evidence of a contract, ownership or quantified influence'
    scenarios=signature['scenarios']
    for n in rows:
        canonical=set(n['canonical_ids'])
        n['ai_scenarios']=[s for s in scenarios if canonical & set(s['affected_ids'])]
        n['timeline_events']=[event for event in base['strategic-timeline']['nodes'] if any(link['url'] in {a['url'] for a in n['capability_links']} for link in event['affected_links'])]
        n['participants']=[a for a in actors if a['activity_id']==n['id']]
        n['flows']=[f for f in mapping['flows'] if n['id'] in (f['source'],f['target'])]
    return {**signature,'extension':'flora-living-map-v2','title':mapping['title'],'summary':mapping['subtitle'],
        'map_nodes':rows,'flows':mapping['flows'],'participants':actors,'conflicts':base['enterprise-story']['conflicts'],
        'timeline_url':signature['enterprise']['url']+'?lens=timeline','timeline_events':base['strategic-timeline']['nodes'],
        'scale_gaps':mapping['scale_gaps'],'weighting':mapping['weighting'],'mapping_digest':digest(mapping),
        'snapshot_digest':digest({'v1_snapshot':signature['snapshot_digest'],'living_mapping':mapping}),
        'conceptual_flows':[]}


def validate_living_map(spec,data,review,mapping,as_of):
    if spec!=build_living_map(data,review,mapping,as_of):raise ValueError('Living-map drift: measure, evidence, identity, scope, flow or state changed')
    return True
