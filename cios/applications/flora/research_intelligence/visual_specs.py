"""Sector-neutral visual output from the existing research overlay.

No new facts, permission engine, ranking engine, network call or image API.
Consumers may supply their existing commercial ranking through ``priorities``.
"""
from copy import deepcopy
from datetime import date
import re
from urllib.parse import urlsplit

TYPES=('pestle','five-forces','value-chain','operating-model','ecosystem','opportunities')


def local_link(value):
    p=urlsplit(value)
    if not value.startswith('/') or value.startswith('//') or p.scheme or p.netloc or p.fragment or p.query or not re.fullmatch(r'/[A-Za-z0-9/_-]*',p.path):
        raise ValueError('Visual links must be registered local presentation paths')
    return value


def claim_state(data, claim):
    if any('search-index' in s.get('retrieval_extent','') for s in data['sources'] if s['id'] in claim['source_ids']):return 'official search-index excerpt; original unverified'
    if any(c.get('supersedes')==claim['id'] for c in data['claims']):return 'superseded'
    if any(c.get('updates')==claim['id'] for c in data['claims']):return 'historical'
    if claim['kind'] in {'interpretation','management_expectation','unknown'}:return claim['kind'].replace('_',' ')
    return 'source-supported disclosure' if claim['verification']=='source_supported' else 'unverified historical research'


def build_visual_specs(data, routes, priorities=None):
    """Generate explicit visual specifications without modifying research or stores.

    routes: industry, enterprise, evidence, nodes, candidates (server-owned paths).
    Diagram importance is absent unless an existing commercial rank supports it.
    """
    opportunity_url=local_link(routes.get('opportunities','/opportunities'))
    routes={k:local_link(routes[k]) for k in ('industry','enterprise','evidence','nodes','candidates')}
    from .model import commercial_candidates
    priorities=priorities if priorities is not None else commercial_candidates(data)
    claims={c['id']:c for c in data['claims']}
    def node(row, category, verification, evidence=None, target='nodes', priority=None):
        refs=list(dict.fromkeys(evidence if evidence is not None else row.get('claim_ids',[])))
        related=[c['id'] for c in data['candidates'] if row['id'] in c.get('capability_ids',[])+c.get('driver_ids',[])+c.get('programme_ids',[]) or row['id']==c['id']]
        return {'id':row['id'],'label':row.get('title',row['id']),'category':category,
                'summary':row.get('assessment',row.get('scope','')),'verification':verification,
                'evidence_refs':refs,'evidence':[{'id':r,'url':routes['evidence']+'/'+r,'status':claim_state(data,claims[r]),'period':claims[r]['reporting_period']} for r in refs],
                'last_research_update':data['assessed_at'],'priority':priority,
                'url':routes[target]+'/'+row['id'],'enterprise_url':routes['enterprise'],
                'opportunity_links':[{'id':r,'url':routes['candidates']+'/'+r} for r in related]}
    def spec(kind,title,summary,nodes):
        ids={r['id'] for r in nodes}|{data['enterprise_twin_id']}
        edges=[deepcopy(r) for r in data['relationships'] if r['subject'] in ids and r['object'] in ids]
        return {'schema_version':1,'diagram_type':kind,'title':title,'summary':summary,
                'research_assessment_id':data['assessment_id'],'last_research_update':data['assessed_at'],
                'authority':'candidate_intelligence','verification':'Analytical presentation; inspect node and relationship status',
                'enterprise':{'id':data['enterprise_twin_id'],'label':data['enterprise_name'],'url':routes['enterprise']},
                'nodes':nodes,'relationships':edges,'opportunities_url':opportunity_url,
                'generation':'Deterministic rendering of research. No generated illustration or new factual claim.'}
    result={}
    for kind,lens,title in [('pestle','pestle','PESTLE / six external forces'),('five-forces','porter','Porter’s Five Forces'),('value-chain','value-chain','Industry value chain')]:
        rows=[r for r in data['frameworks'] if r['lens']==lens]
        result[kind]=spec(kind,title,'Interpretive assessment linked to evidence, capabilities and commercial questions.',[node(r,lens,'analyst interpretation') for r in rows])
    caps=[]
    for r in data['capabilities']:
        refs=list(dict.fromkeys(c for edge in data['relationships'] if r['id'] in {edge['subject'],edge['object']} for c in edge['claim_ids']))
        caps.append(node(r,r.get('category','Business capability'),'conceptual capability; ownership unverified',refs))
    result['operating-model']=spec('operating-model','Enterprise operating landscape','Conceptual capabilities, not a verified organisation chart or application inventory.',caps)
    suppliers=[]
    for r in data['suppliers']:
        edges=[e for e in data['relationships'] if e['subject']==data['enterprise_twin_id'] and e['object']==r['id']]
        refs=list(dict.fromkeys(c for edge in edges for c in edge['claim_ids']))
        status='source-supported relationship; contract scope unverified' if any(e['verified'] for e in edges) else 'reported relationship; primary verification pending' if any(e['predicate'] in {'reported_uses','reported_licences'} for e in edges) else 'enterprise relationship unverified'
        suppliers.append(node(r,'Supplier / technology',status,refs))
    result['ecosystem']=spec('ecosystem','Supplier & technology ecosystem','Solid links are explicit source-supported relationships. Dashed links remain reported or unknown; no current incumbency is implied.',suppliers)
    nodes=[]
    for r in priorities:
        n=node(r,r['family'],'unqualified opportunity hypothesis',r['commercial']['evidence_claim_ids'],target='candidates',priority=r['commercial_rank'])
        n['ratings']={k:deepcopy(r['commercial'][k]) for k in ('strategic_relevance','commercial_accessibility','evidence_maturity','seller_fit') if k in r['commercial']}
        nodes.append(n)
    result['opportunities']=spec('opportunities','Commercial opportunity landscape','Existing account-development rank. Independent ordinal ratings, not deal value, probability or verified demand.',nodes)
    for s in result.values():validate_visual_spec(s,data,routes,priorities)
    return result


def validate_visual_spec(spec, data, routes, priorities=None):
    """Reject visual drift: unknown nodes, invented edges or evidence upgrades."""
    if spec['schema_version']!=1 or spec['diagram_type'] not in TYPES or spec['authority']!='candidate_intelligence':raise ValueError('Unknown visual contract')
    if spec['last_research_update']!=data['assessed_at']:raise ValueError('Visual research date drift')
    date.fromisoformat(spec['last_research_update'])
    available={r['id']:r for key in ('frameworks','capabilities','suppliers','candidates') for r in data[key]}
    claims={r['id']:r for r in data['claims']};seen=set()
    from .model import commercial_candidates
    ranked={r['id']:r for r in (priorities if priorities is not None else commercial_candidates(data))}
    expected_edges={r['id']:r for r in data['relationships']}
    if spec['enterprise']!={'id':data['enterprise_twin_id'],'label':data['enterprise_name'],'url':routes['enterprise']}:raise ValueError('Visual enterprise identity drift')
    for n in spec['nodes']:
        if n['id'] in seen or n['id'] not in available:raise ValueError('Unknown/duplicate visual node')
        seen.add(n['id'])
        if n['label']!=available[n['id']]['title'] or set(n['evidence_refs'])-set(claims):raise ValueError('Unsupported visual fact or evidence')
        expected_summary=available[n['id']].get('assessment',available[n['id']].get('scope',''))
        if n['summary']!=expected_summary or n['last_research_update']!=data['assessed_at']:raise ValueError('Visual cannot introduce an unsupported summary or date')
        related=[c['id'] for c in data['candidates'] if n['id'] in c.get('capability_ids',[])+c.get('driver_ids',[])+c.get('programme_ids',[]) or n['id']==c['id']]
        if n['opportunity_links']!=[{'id':r,'url':routes['candidates']+'/'+r} for r in related]:raise ValueError('Visual opportunity-link drift')
        kind=spec['diagram_type'];key='candidates' if kind=='opportunities' else 'nodes'
        if n['url']!=routes[key]+'/'+n['id'] or n['enterprise_url']!=routes['enterprise']:raise ValueError('Visual destination drift')
        local_link(n['url'])
        if kind in ('pestle','five-forces','value-chain'):
            expected=available[n['id']].get('claim_ids',[])
        elif kind=='opportunities':
            expected=ranked[n['id']]['commercial']['evidence_claim_ids']
            ratings={k:ranked[n['id']]['commercial'][k] for k in ('strategic_relevance','commercial_accessibility','evidence_maturity','seller_fit') if k in ranked[n['id']]['commercial']}
            if n['priority']!=ranked[n['id']]['commercial_rank'] or n['ratings']!=ratings:raise ValueError('Unsupported visual priority or rating')
        else:
            edges=[r for r in data['relationships'] if (n['id'] in {r['subject'],r['object']} if kind=='operating-model' else r['subject']==data['enterprise_twin_id'] and r['object']==n['id'])]
            expected=[c for r in edges for c in r['claim_ids']]
            status=('conceptual capability; ownership unverified' if kind=='operating-model' else 'source-supported relationship; contract scope unverified' if any(r['verified'] for r in edges) else 'reported relationship; primary verification pending' if any(r['predicate'] in {'reported_uses','reported_licences'} for r in edges) else 'enterprise relationship unverified')
            if n['verification']!=status:raise ValueError('Visual cannot upgrade verification')
        if set(n['evidence_refs'])!=set(expected):raise ValueError('Visual evidence lineage drift')
        if kind!='opportunities' and n['priority'] is not None:raise ValueError('Visual cannot invent importance')
        if kind=='opportunities' and (type(n['priority']) is not int or n['priority']<1 or n['verification']!='unqualified opportunity hypothesis'):raise ValueError('Visual cannot qualify an opportunity')
        if kind in ('pestle','five-forces','value-chain') and n['verification']!='analyst interpretation':raise ValueError('Framework cannot become a verified fact')
        for edge in n['evidence']:
            if edge['status']!=claim_state(data,claims[edge['id']]) or edge['period']!=claims[edge['id']]['reporting_period']:raise ValueError('Visual cannot change evidence status or period')
            if edge['id'] not in n['evidence_refs'] or edge['url']!=routes['evidence']+'/'+edge['id']:raise ValueError('Evidence destination drift')
    lens={'pestle':'pestle','five-forces':'porter','value-chain':'value-chain'}.get(spec['diagram_type'])
    expected_nodes=([r['id'] for r in data['frameworks'] if r['lens']==lens] if lens else list(ranked) if spec['diagram_type']=='opportunities' else [r['id'] for r in data['capabilities' if spec['diagram_type']=='operating-model' else 'suppliers']])
    if [n['id'] for n in spec['nodes']]!=expected_nodes:raise ValueError('Visual cannot omit or reorder research nodes')
    connected=set(expected_nodes)|{data['enterprise_twin_id']}
    if spec['relationships']!=[r for r in data['relationships'] if r['subject'] in connected and r['object'] in connected]:raise ValueError('Visual relationship coverage drift')
    for r in spec['relationships']:
        if r!=expected_edges.get(r['id']):raise ValueError('Invented or upgraded visual relationship')
    return True
