"""Derived extension of the existing visual specification, never canonical knowledge.

Presentation profiles organise existing research; measurements, statuses, dates and
relationships are resolved from the validated overlay / SemanticTwin review boundary.
"""
from copy import deepcopy
from datetime import date,datetime
from decimal import Decimal,InvalidOperation
import json,re

from .model import validate,primary_claim_supported,claim_segment
from .registry import assessment_path,DOMAINS,enterprise_reference
from .understanding import assess as assess_understanding,load_review
from .cycle import digest
from .visual_specs import claim_state,build_visual_specs

FAMILIES=('industry-signature','enterprise-story','strategic-timeline')
LANES=('Regulation','Economics','Technology','Competition','AI disruption','Transformation','Suppliers & contracts')
KINDS=('historical fact','historical disclosure','current condition','announced commitment','forecast','scenario','unknown')


def load_profile(domain):
    return json.loads((assessment_path(domain).parent/'Visual-Profile.json').read_text())


def _derive(data,review,profile,as_of):
    validate(data)
    if profile.get('version')!=1 or profile.get('domain')!=data.get('research_domain','banking'):
        raise ValueError('Visual profile does not match the registered research boundary')
    if date.fromisoformat(as_of)>date.today():raise ValueError('Future visual snapshot')
    for group in ('actors','activities','events','ai_scenarios'):
        ids=[row['id'] for row in profile[group]]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate visual presentation identity')
    domain=profile['domain'];_,slug,root=DOMAINS[domain]
    industry='/industries/'+domain;enterprise='/enterprises/'+slug
    understanding=assess_understanding(data,review,as_of)
    base={c['id']:c for c in data['claims']}
    observations={o['candidate']['claim_id']:o for o in review['observations']}
    assessments={c['id']:c for c in understanding['claims']}
    resources={r['id']:r for key in ('frameworks','capabilities','programmes','suppliers','gaps') for r in data[key]}
    sources={s['id']:s for s in data['sources']+review['sources']}
    original_specs=build_visual_specs(data,{'industry':industry,'enterprise':enterprise,'nodes':root+'/nodes','evidence':root+'/evidence','candidates':root+'/candidates'})
    pin={'assessment_id':data['assessment_id'],'as_of':as_of,'assessment_digest':digest(data),'review_digest':digest(review),'profile_digest':digest(profile)}
    snapshot=digest(pin)

    def resolve(selectors):
        found=[]
        for selector in selectors:
            if isinstance(selector,str):
                if selector in base or selector in observations:found.append(selector)
            elif isinstance(selector,dict):
                found.extend(cid for cid,o in observations.items() if o['source_id']==selector.get('review_source') and selector.get('contains','') in o['candidate']['statement'])
            else:raise ValueError('Unknown research reference selector')
        return list(dict.fromkeys(found))

    def evidence(cid):
        if cid in base:
            c=base[cid];segment=claim_segment(data,c)
            supported=(primary_claim_supported(data,c) and 'index' not in claim_state(data,c).lower()
                and all((not sources[s].get('publication_date') or sources[s]['publication_date']<=as_of)
                    and (not sources[s].get('retrieved_at') or sources[s]['retrieved_at'][:10]<=as_of) for s in c['source_ids']))
            state=claim_state(data,c)
            return {'id':cid,'label':c['statement'],'subject_id':c['asset_id'],'scope':c.get('entity_scope',c['asset_id']),
                'period':c['reporting_period'],'state':state,'supported':supported,'source_ids':list(c['source_ids']),
                'source_dates':[{k:sources[s].get(k) for k in ('publication_date','reporting_period','retrieved_at')} for s in c['source_ids']],
                'passage':segment.content,'locator':segment.section_heading,'url':root+'/evidence/'+cid,
                'temporal_kind':'forecast' if 'forecast' in (c['statement']+' '+c['reporting_period']).lower() or c['kind']=='management_expectation' else 'unknown' if c['kind']=='unknown' else 'disclosure',
                'metric_value':c.get('metric_value'),'metric_unit':c.get('metric_unit')}
        o=observations[cid];c=o['candidate'];a=assessments[cid];s=sources[o['source_id']]
        return {'id':cid,'label':c['statement'],'subject_id':c['subject'],'scope':c['subject'],'period':c['time_scope'],
            'state':a['quality_state'],'supported':a['direct_support_reviewed'],'source_ids':[o['source_id']],
            'source_dates':[{k:s.get(k) for k in ('publication_date','reporting_period','retrieved_at')}],
            'passage':o['segment']['content'],'locator':o['segment']['section_heading'],
            'url':enterprise+'/understanding#claim-'+cid,'temporal_kind':'disclosure','metric_value':None,'metric_unit':None}

    def destination(resource):
        if resource in base:return root+'/evidence/'+resource
        if resource in observations:return enterprise+'/understanding#claim-'+resource
        if resource in resources:
            return root+'/gaps' if any(g['id']==resource for g in data['gaps']) else root+'/nodes/'+resource
        return root+'/gaps'

    def node(row,category,extra_refs=()):
        refs=resolve(list(row.get('claim_refs',[]))+list(extra_refs));proof=[evidence(r) for r in refs]
        rid=row.get('resource_id') or next(iter(row.get('resource_ids',[])),None)
        if rid in resources and not proof:
            related=[c for edge in data['relationships'] if rid in (edge['subject'],edge['object']) for c in edge['claim_ids']]
            proof=[evidence(c) for c in dict.fromkeys(related)];refs=[e['id'] for e in proof]
        state='Interpretation' if proof else 'Unknown'
        if row.get('presentation_state')=='unknown':state='Unknown'
        if row.get('temporal_kind')=='scenario' or category=='AI scenario':state='Scenario'
        conflicts=[c['id'] for c in understanding['contradictions'] if set(c['claim_ids'])&set(refs)]
        if conflicts:state='Challenged / scope unresolved'
        ent=enterprise_reference(row.get('enterprise_slug')) if row.get('enterprise_slug') else None
        url=('/enterprises/'+ent.slug if ent else destination(rid or (refs[0] if refs else None)))
        suppliers=[]
        for sid in row.get('supplier_ids',[]):
            if sid not in resources:continue
            edges=[e for e in understanding['relationships'] if e['object']==sid and e['subject']==data['enterprise_twin_id']]
            factual=[e for e in edges if e['state']=='Verified factual relationship']
            suppliers.append({'id':sid,'label':resources[sid]['title'],'url':destination(sid),
                'status':'Documented enterprise relationship; activity dependency and current contract unknown' if factual else 'Activity association / current supplier scope unverified',
                'periods':[e['period'] for e in factual],'claim_ids':list(dict.fromkeys(c for e in factual for c in e['claim_ids']))})
        return {'id':row['id'],'label':row['label'],'category':category,'icon':row.get('icon','network'),
            'purpose':row.get('purpose','Explore this role in the current research; position and size do not express market rank.'),
            'canonical_ids':[r for r in row.get('resource_ids',[]) if r in resources]+([ent.id] if ent else [rid] if rid in resources else []),
            'scope_id':data['enterprise_twin_id'] if category=='Activity' else data['industry_twin_id'],
            'state':state,'evidence_refs':refs,'evidence':proof,'url':url,'supplier_context':suppliers,
            'programme_links':[{'id':p,'label':resources[p]['title'],'url':destination(p)} for p in row.get('programme_ids',[]) if p in resources],
            'capability_links':[{'id':p,'label':resources[p]['title'],'url':destination(p)} for p in row.get('resource_ids',[]) if p in resources],
            'conflict_ids':conflicts,'limitations':row.get('structure','Research membership/context does not prove a relationship, market position or enterprise dependency.'),
            'opportunity_links':[{'label':c['title'],'url':root+'/candidates/'+c['id']} for c in data['candidates'] if set(row.get('resource_ids',[]))&set(c['capability_ids'])],
            'size_basis':'Equal-sized navigation categories; not measured importance or market share'}

    def metric(row,scope):
        refs=resolve(row.get('claim_refs',[]));proof=[evidence(r) for r in refs]
        proof=[p for p in proof if p['subject_id']==scope and p['supported']]
        value=None;unit=None
        if proof:
            first=proof[0]
            if row.get('measure')=='typed' and first['metric_value'] is not None:
                expected=str(first['metric_value'])
                if re.search(r'(?<![\d.])'+re.escape(expected)+r'(?![\d.])',first['passage'].replace(',','')):
                    value=first['metric_value'];unit=first['metric_unit']
            elif row.get('measure')=='quote':
                match=re.search(row['pattern'],first['passage'])
                if match:
                    try:value=str(Decimal(match.group('value').replace(',','')));unit=row['unit']
                    except (InvalidOperation,IndexError):value=None
        return {'id':row['id'],'label':row['label'],'value':value,'unit':unit,'scope_id':scope,
            'scope_note':row.get('scope',''),'state':('Forecast, not actual' if any(p['temporal_kind']=='forecast' for p in proof) else 'Source-supported report; not independent verification') if value is not None else 'Not established',
            'period':proof[0]['period'] if proof else None,'evidence':proof if value is not None else [],
            'limitation':row.get('missing','No verified comparable measure in the pinned research') if value is None else 'Measures retain their own entity, period and units; no cross-metric size/ranking is inferred.'}

    actors=[node(a,a['category']) for a in profile['actors']]
    # New public research suppliers become inspectable without editing graphics.
    existing={a.get('resource_id') for a in profile['actors']}
    for s in data['suppliers']:
        if s['id'] in existing:continue
        actors.append(node({'id':'VI-ACTOR-'+s['id'],'label':s['title'],'resource_id':s['id']},'Research supplier context'))
    if domain=='banking':
        from ..banking_portfolio import BANKS
        present={a.get('enterprise_slug') for a in profile['actors']}
        for slug0,bank in BANKS.items():
            if slug0 not in present:actors.append(node({'id':'VI-ACTOR-'+bank.id,'label':bank.name,'enterprise_slug':slug0},'Enterprise'))
    activities=[node(a,'Activity') for a in profile['activities']]
    activity_ids={n['id'] for n in activities}
    if any(f['source'] not in activity_ids or f['target'] not in activity_ids or f['state']!='Conceptual activity relationship; not verified enterprise topology' for f in profile.get('activity_flows',[])):
        raise ValueError('Unresolved or asserted conceptual flow')
    pressures=[{'id':f['id'],'label':f['title'],'purpose':f['assessment'],'state':'Interpretation',
                'evidence':[evidence(cid) for cid in f['claim_ids']],'url':destination(f['id'])} for f in data['frameworks'] if f['lens']=='pestle']
    scenarios=[node(a,'AI scenario')|{'defence':a['defence'],'affected_ids':a['affected_ids'],'affected_links':[{'label':resources[i]['title'],'url':destination(i)} for i in a['affected_ids'] if i in resources]} for a in profile['ai_scenarios']]
    value_chain=deepcopy(original_specs['value-chain']['nodes'])

    def timeline_event(row):
        if row['lane'] not in LANES or row['temporal_kind'] not in KINDS:raise ValueError('Unknown temporal/lane semantics')
        refs=resolve(row['claim_refs']);proof=[evidence(r) for r in refs];basis=row['date_basis'];start=end=None;precision='Unknown';label='Date unknown'
        kind=row['temporal_kind']
        if kind not in ('unknown','scenario') and any(p['supported'] for p in proof):
            if basis=='publication':
                source=sources.get(row['date_selector']);published=source.get('publication_date') if source else None
                # Only a source actually supporting the event can supply its publication date.
                if published and any(source['id'] in p['source_ids'] for p in proof):
                    start=end=date.fromisoformat(published).year;precision='Publication day (not go-live)';label=published
            else:
                selected=resolve([row['date_selector']]);q=evidence(selected[0]) if selected else None
                if q and q['supported'] and q['id'] in refs:
                    text=q['period']+' '+q['label'];needle=row['date_needle']
                    if needle and needle in text:
                        if basis=='claim-date':
                            try:parsed=datetime.strptime(needle,'%d %B %Y').date();start=end=parsed.year;precision='Explicit reporting/effective day';label=needle
                            except ValueError:pass
                        elif basis=='claim-years':
                            years=[int(y) for y in re.findall(r'\b20\d{2}\b',needle)]
                            if years:start=min(years);end=max(years);label=needle;precision='Declared year / quarter / half-year / range; no invented day'
        if start is None:
            if kind not in ('scenario','unknown'):kind='unknown'
        applicability='Industry context; enterprise applicability unverified' if any(p['subject_id']==data['industry_twin_id'] for p in proof) else 'Enterprise-specific disclosed context; readiness and causal impact unverified'
        return {'id':row['id'],'label':row['label'] if proof or row['temporal_kind'] in ('unknown','scenario') else 'Research unavailable',
            'lane':row['lane'],'temporal_kind':kind,'start_year':start,'end_year':end,'date_label':label,'precision':precision,
            'date_basis':basis,'evidence':proof,'evidence_refs':refs,'affected_links':[{'label':resources[i].get('title',i),'url':destination(i)} for i in row['affected_ids'] if i in resources],
            'readiness':row['readiness'],'consequence':row['consequence'],'applicability':applicability,
            'limitations':'An announcement/forecast is not a completed programme, actual contract expiry, current failure or qualified demand.'}
    events=[timeline_event(r) for r in profile['events']]
    skeleton={'schema_version':1,'extension':'flora-visual-intelligence-v1','authority':'candidate_intelligence',
              'research_assessment_id':data['assessment_id'],'as_of':as_of,'pin':pin,'snapshot_digest':snapshot,
              'industry':{'id':data['industry_twin_id'],'label':data['industry_name'],'url':industry},
              'enterprise':{'id':data['enterprise_twin_id'],'label':data['enterprise_name'],'url':enterprise},
              'domain':domain,'geography':profile['geography'],'illustration':profile['illustration'],
              'interpretation':'Visual navigation/structure is not a verified causal chain, market ranking or ownership map.'}
    return {
      'industry-signature':{**skeleton,'diagram_type':'industry-signature','title':profile['industry_title'],'summary':profile['industry_summary'],
         'nodes':actors,'pressures':pressures,'value_chain':value_chain,'scenarios':scenarios,'metrics':[metric(m,data['industry_twin_id']) for m in profile['metrics']['industry']],
         'relationships':[],'participant_limitation':'Reference portfolio / source comparators, not a comprehensive market census or rank. Named AI-native entrants, shares and employment may remain unknown.'},
      'enterprise-story':{**skeleton,'diagram_type':'enterprise-story','title':profile['enterprise_title'],'summary':profile['enterprise_summary'],
         'conceptual_flows':deepcopy(profile.get('activity_flows',[])),'nodes':activities,'metrics':[metric(m,data['enterprise_twin_id']) for m in profile['metrics']['enterprise']],
         'relationships':deepcopy(understanding['relationships']),'structure_notice':profile['structure_notice'],
         'conflicts':deepcopy(understanding['contradictions']),'understanding_url':enterprise+'/understanding'},
      'strategic-timeline':{**skeleton,'diagram_type':'strategic-timeline','title':'The pressure to change.','summary':'What is known, what is announced and what is still uncertain. Dates retain their actual precision.',
         'nodes':events,'lanes':list(LANES),'years':sorted({y for e in events if e['start_year'] for y in range(e['start_year'],e['end_year']+1)}),
         'relationships':[],'interpretation':'Burning-platform questions are not assertions of enterprise failure or buying intent.'}}


def build_intelligence_specs(data,review=None,profile=None,as_of=None):
    domain=data.get('research_domain','banking')
    return _derive(data,review if review is not None else load_review(domain),profile if profile is not None else load_profile(domain),as_of or date.today().isoformat())


def validate_intelligence_specs(specs,data,review,profile,as_of):
    if specs!=_derive(data,review,profile,as_of):raise ValueError('Visual intelligence drift: unsupported identity, measure, status, date, relationship or scope')
    return True
