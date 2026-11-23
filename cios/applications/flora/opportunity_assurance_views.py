"""Restricted owner inspection UI. No seller navigation or mutation controls."""
from html import escape as e
from urllib.parse import urlencode
from . import opportunity_assurance as service,offers,design_system as ds
from .research_intelligence.unified_views import page

CSS='''
.assurance{max-width:1160px;margin:auto;padding:30px 24px 70px;color:#173e32}.assurance h1{font:clamp(2.5rem,5vw,4rem)/1.1 Georgia,serif}.assurance h2{font:1.7rem Georgia,serif}.assurance p{max-width:78ch;line-height:1.65}.assurance *{box-sizing:border-box}.assurance-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.assurance-card{border:1px solid #d4ddd1;border-radius:18px;padding:20px;min-width:0;background:#fffdf8}.assurance-card strong{font:2rem Georgia,serif;display:block}.assurance details{border:1px solid #d4ddd1;border-radius:15px;padding:16px;margin:18px 0}.assurance summary{cursor:pointer;font-weight:650;min-height:32px}.assurance label{display:block;margin:12px 0}.assurance input,.assurance select,.assurance button{font:inherit;min-height:44px;max-width:100%;padding:9px;border-radius:9px;border:1px solid #aabeb1}.assurance select{width:100%}.assurance button{background:#174d3f;color:white;padding:12px 20px}.assurance fieldset{min-width:0;border:0;padding:0}.assurance pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.85rem}.assurance-row{border-top:1px solid #d4ddd1;padding:18px 0;display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:14px;align-items:start}.assurance a{color:#174d3f;display:inline-block;min-height:30px;overflow-wrap:anywhere}.assurance dd{margin:0 0 14px;overflow-wrap:anywhere}.assurance dt{font-weight:bold}.assurance progress{max-width:100%;width:100%;accent-color:#174d3f}.assurance .status{font-weight:650}.assurance :focus-visible{outline:3px solid #6f49c5;outline-offset:3px}@media(max-width:720px){.assurance-grid,.assurance-row{grid-template-columns:1fr}.assurance{padding:24px 16px}.assurance h1{font-size:2.4rem}}
'''


def link(label,**q):return '<a href="'+e(service.BASE+'?'+urlencode(q|{'view':'advanced'}),quote=True)+'">'+e(label)+'</a>'


def select(name,value,choices,label):
    return '<label>'+e(label)+'<select name="'+e(name)+'">'+''.join('<option value="'+e(v,quote=True)+'" '+('selected' if v==value else '')+'>'+e(t)+'</option>' for v,t in choices)+'</select></label>'


def details(label,value):
    import json
    return '<details><summary>'+e(label)+'</summary><pre>'+e(json.dumps(value,indent=2,ensure_ascii=False))+'</pre></details>'


def criteria(data):
    content='<h2>Qualification input completeness</h2><p><strong>'+str(data['complete'])+'/'+str(data['total'])+' inputs · '+str(data['percent'])+'% input completeness</strong></p><progress aria-label="Qualification input completeness" value="'+str(data['complete'])+'" max="'+str(data['total'])+'"></progress><p>Independently verified buyer need: '+e(data['independently_verified_buyer_need'])+'. Opportunity accuracy: '+e(data['opportunity_accuracy'])+'.</p>'
    for r in data['criteria']:
        content+='<details><summary>'+e(r['label']+' · inputs '+r['input_state']+' · development check '+r['development_state'])+'</summary><dl>'
        for k in ('note','reference','evidence_kind','date'):content+='<dt>'+e(k.replace('_',' ').title())+'</dt><dd>'+e(r[k] or 'Unknown')+'</dd>'
        content+='</dl>'+details('Actual typed check',r['actual_development_check'])+'</details>'
    return content


@ds.view_scope
def _advanced_render(path,query,headers):
    service.authority(headers)
    allowed={'offer','enterprise','candidate','pipeline','cutoff','challenge','source','fact','tier','industry','freshness','sort','review','stale','version','gate','page'}
    if set(query)-allowed or any(len(v)!=1 or len(v[0])>300 for v in query.values()):raise ValueError('Unsupported or duplicate assurance selector')
    q={k:v[0] for k,v in query.items()};ds.context_link('/flora/command-centre','Command Centre');ds.context_link(service.BASE,'Opportunity Assurance')
    title='Advanced Inspection'
    back={k:v for k,v in q.items() if k in {'offer','enterprise','candidate','pipeline','cutoff'}}
    body='<p>'+commercial_link('Back to commercial review',**back)+'</p>'
    body+='<p>Read-only inspection in your authorised workspace. Validation priority, seller review and independently verified buying need are different things.</p>'
    if path=='/flora/command-centre':
        title='Owner Command Centre';body='<p>Inspect the decisions you are authorised to review.</p>'+link('Opportunity Assurance')
    elif q.get('pipeline'):
        if set(q)!={'pipeline'}:raise ValueError('Pipeline inspection accepts only its authorised identifier')
        data=service.inspect_pipeline(q['pipeline'],headers=headers);record=data['record']
        body+='<h2>'+e(record['enterprise'])+'</h2><p>'+e(record['stage'])+' · record v'+str(record['version'])+'</p>'+criteria(data['qualification'])+details('Pipeline evidence maturity',data['evidence_maturity'])+'<p>'+e(data['limitation'])+'</p>'
    elif q.get('offer') or q.get('enterprise') or q.get('candidate'):
        if not q.get('offer') or not q.get('enterprise'):raise ValueError('Select an Offer and enterprise together')
        data=service.inspect_pair(q['offer'],q['enterprise'],q.get('cutoff',''),q.get('candidate',''),q.get('challenge','Original'),q.get('source',''),q.get('fact',''),headers=headers)
        a=data['original'];b=a['buying_trigger'];changed=data['challenged'];record=data['development']
        from .opportunity_assurance_commercial import summary,TSB_NOTE
        business=summary(a)
        body+='<p>Historical Sprint B tiers describe research-validation priority, not an early strategic sales opportunity.</p>'
        if a['enterprise_slug']=='santander-uk' and any(f['id']=='BTI-TSB-MIGRATION' for f in b['timeline']):body+='<p>'+e(TSB_NOTE['warning'])+'</p>'+details('Presentation clarification, separately reviewed; original facts preserved',TSB_NOTE)
        body+='<p class="eyebrow">UK · '+e(a['enterprise_name']+' · '+data['offer']['name'])+'</p><h2>'+e(b['tier'])+' validation</h2><p>'+e(a['why_account'])+'</p><p>'+e(b['stage'])+'</p><p>'+e(data['outcome'])+'</p>'
        body+='<div class="assurance-grid"><section class="assurance-card"><h3>Observed context</h3><p>'+e(b['signal_strength'])+'</p></section><section class="assurance-card"><h3>Buying need</h3><p>Unknown; public evidence is not customer confirmation.</p></section><section class="assurance-card"><h3>Seller decision</h3><p>'+e(data['handoff'])+'</p></section></div>'
        retained=len(b['timeline']);fresh=sum(f['dated_current'] for f in b['timeline'])
        body+='<p>Current dated source facts: '+str(fresh)+'/'+str(retained)+' retained relevant facts. Admitted support: '+str(len(b['evaluation_trace']['positive_fact_ids']))+'/'+str(retained)+' evaluated facts. These counts do not measure evidence sufficiency or opportunity accuracy.</p>'
        body+='<h2>First conversation</h2><p>'+e(a['entry_play'])+'</p><p><strong>Deciding question:</strong> '+e(a['next_validation_action'])+'</p>'
        if b['entry_play_detail']:body+='<p>'+e(b['entry_play_detail']['stop'])+'</p>'
        body+=details('Entity, identity and UK/group scope',b['identity_scope'])+details('Offer approval, version and delivery limits',data['offer'])
        body+=details('Actual matcher conditions and admitted/rejected facts',b['evaluation_trace'])+details('Ranking, counter-evidence and unknowns',{'rank_key':b['rank_key'],'ordering':'tier, programme/catalyst/structural state, enterprise name, Offer ID; no probability score','counter_evidence':a['contradictions'],'reasons':b['reasons'],'unknowns':b['unknowns'],'next_evidence_task':b['next_evidence_task']})
        body+='<details><summary>Originating sources, dates and rights</summary>'
        for f in b['timeline']:
            body+='<article><h3>'+e(f['id'])+'</h3><p>'+e(f['statement'])+'</p><p>'+e(f['quote'])+'</p><p><a rel="noreferrer" href="'+e(f['source_url'],quote=True)+'">'+e(f['source_title'])+'</a> · '+e(f['source_id'])+' · '+e(f['locator'])+'</p><p>Published '+e(f['publication_date'] or 'Unknown')+' · effective '+e(f['effective_date'] or f['effective_period'] or 'Unknown')+' · verified '+e(f['last_verified'] or 'Unknown')+'</p><p>'+e(f['source_rights'])+' · Candidate, not accepted Evidence.</p><p>'+e(f['interpretation_limit'])+'</p></article>'
        body+='</details>'+criteria(data['qualification'])
        body+=details('Actual development gates and missing checks',data['original_readiness'])+details('Explicit qualification decision and hand-off prerequisites',data['original_handoff_checks'])
        if record:
            body+='<p>Private development '+e(record['state'])+' · v'+str(record['version'])+' · '+('Stale — Reassess' if record['stale'] else 'Snapshot dependencies current')+'</p>'+details('Authorised seller attestations, roles and source dependencies',{'customer_attested':record['customer_attested'],'reviewed':record['reviewed'],'buying_group':record['buying_group'],'changed_dependencies':record['changed_dependencies'],'source_cutoff':record['assessment_snapshot']['source_cut_off']})
        if data['pipeline']:body+='<p>'+link('Inspect authorised Pipeline record',pipeline=data['pipeline']['id'])+'</p>'
        body+='<h2>Read-only challenge</h2><p>Hypothetical copied inputs only. Actual sources, private notes, reviews and Pipeline remain unchanged.</p><form method="get" action="'+service.BASE+'"><input type="hidden" name="view" value="advanced">'
        for k in ('offer','enterprise','candidate','cutoff'):
            if q.get(k):body+='<input type="hidden" name="'+e(k)+'" value="'+e(q[k],quote=True)+'">'
        body+=select('challenge',data['challenge'],[(c,c) for c in service.CHALLENGES],'Challenge')
        source_choices=[('','No source selection')]+list(dict.fromkeys((f['source_id'],f['source_id']) for f in b['timeline']))
        fact_choices=[('','No programme selection')]+[(f['id'],f['id']) for f in b['timeline'] if f.get('programme_id')]
        body+=select('source',q.get('source',''),source_choices,'Source for withdrawal')+select('fact',q.get('fact',''),fact_choices,'Programme fact for closure/contradiction')+'<button>Compare without saving</button></form>'
        body+='<section aria-live="polite"><h3>Original → challenge</h3><p>'+e(b['tier']+' → '+changed['buying_trigger']['tier'])+'</p><p>'+e(data['challenge_note'])+'</p><p>Hand-off checks: '+('ready' if data['original_handoff_checks'] and data['original_handoff_checks']['ready'] else 'blocked')+' → '+('ready' if data['challenged_handoff_checks'] and data['challenged_handoff_checks']['ready'] else 'blocked')+'. Existing Pipeline unchanged.</p></section>'
        body+=details('Challenge conditions, blockers and affected dependencies',{'actual_trace':changed['buying_trigger']['evaluation_trace'],'hypothetical_fact_ids':data['hypothetical_fact_ids'],'qualification':data['challenged_readiness'],'handoff_prerequisites':data['challenged_handoff_checks'],'changed_dependencies':data['changed_dependencies'],'would_require_reassessment':data['would_require_reassessment']})
        body+=details('Policy, data snapshot and deterministic replay',data['policy']|{'reproduced':data['reproduced']})
    else:
        if set(q)-{'cutoff','tier','industry','freshness','sort','review','stale','version','gate','page'}:raise ValueError('Queue selectors required')
        data=service.overview(q.get('cutoff',''),headers=headers);counts=data['counts']
        body+='<p>'+e(data['scope'])+' · cutoff '+e(data['cutoff'])+'</p><div class="assurance-grid">'
        for label,key,denominator in [('Research only','Research only','assessments'),('Investigate','Investigate','assessments'),('Prioritise validation','Prioritise','assessments'),('Your reviewed shortlists','private_shortlists',None),('Your development','private_development',None),('Qualified Pipeline','qualified_pipeline','pipeline')]:
            body+='<section class="assurance-card"><h2>'+e(label)+'</h2><strong>'+str(counts[key])+(' / '+str(counts[denominator]) if denominator else '')+'</strong><p>'+('Authorised assessment pairs' if denominator=='assessments' else 'Authorised Pipeline records' if denominator=='pipeline' else 'Your private records only')+'</p></section>'
        body+='</div><p>'+e(data['accuracy'])+'</p><h2>Review queue</h2>'
        rows=data['assessments'];private={ (r['offer_id'],r['enterprise_slug']):r for r in data['development'] }
        states=offers.snapshot(headers=headers);names={r['id']:r['content']['name'] for r in states['offers'] if r['current']}
        def has_gate(a):return not all(a['buying_trigger']['evaluation_trace'][k] for k in ('employer_approved','identity_allows_priority','mission_not_excluded','sector_fit'))
        def fresh(a):return any(f['dated_current'] for f in a['buying_trigger']['timeline'])
        for key,valid in [('tier',{'','Research only','Investigate','Prioritise'}),('industry',{'','banking','aviation','technology'}),('freshness',{'','current','historical'}),('sort',{'','rank','enterprise','offer','version','review'}),('review',{'','reviewed','unreviewed'}),('stale',{'','yes','no'}),('gate',{'','blocked','clear'})]:
            if q.get(key,'') not in valid:raise ValueError('Unsupported queue filter')
        if q.get('version') and not q['version'].isdigit():raise ValueError('Offer version must be numeric')
        if q.get('tier'):rows=[a for a in rows if a['buying_trigger']['tier']==q['tier']]
        if q.get('industry'):rows=[a for a in rows if a['buying_trigger']['identity_scope']['industry']==q['industry']]
        if q.get('freshness'):rows=[a for a in rows if fresh(a)==(q['freshness']=='current')]
        if q.get('gate'):rows=[a for a in rows if has_gate(a)==(q['gate']=='blocked')]
        if q.get('version'):rows=[a for a in rows if a['offer_version']==int(q['version'])]
        if q.get('review'):rows=[a for a in rows if bool(private.get((a['offer_id'],a['enterprise_slug']),{}).get('reviewed'))==(q['review']=='reviewed')]
        if q.get('stale'):rows=[a for a in rows if (a['offer_id'],a['enterprise_slug']) in private and private[a['offer_id'],a['enterprise_slug']]['stale']==(q['stale']=='yes')]
        sort=q.get('sort','rank')
        if sort!='rank':rows=sorted(rows,key=lambda a:a['enterprise_name'] if sort=='enterprise' else names[a['offer_id']] if sort=='offer' else a['offer_version'] if sort=='version' else bool(private.get((a['offer_id'],a['enterprise_slug']),{}).get('reviewed')))
        body+='<form method="get"><input type="hidden" name="view" value="advanced"><label>Source cutoff<input type="date" name="cutoff" value="'+e(data['cutoff'])+'"></label>'+select('tier',q.get('tier',''),[('','All tiers')]+[(t,t) for t in ('Research only','Investigate','Prioritise')],'Recommendation tier')+select('industry',q.get('industry',''),[('','All industries')]+[(t,t.title()) for t in ('banking','aviation','technology')],'Industry')+select('sort',sort,[(t,t.title()) for t in ('rank','enterprise','offer','version','review')],'Sort by')+ '<details><summary>Other queue filters</summary>'+select('freshness',q.get('freshness',''),[('','All freshness'),('current','Current dated facts'),('historical','Historical or undated only')],'Source freshness')+select('gate',q.get('gate',''),[('','All applicability checks'),('blocked','Failed applicability checks'),('clear','Applicability checks clear')],'Applicability checks')+select('review',q.get('review',''),[('','All seller reviews'),('reviewed','Seller-reviewed'),('unreviewed','Not seller-reviewed')],'Seller review')+select('stale',q.get('stale',''),[('','All records'),('yes','Stale development'),('no','Current development')],'Development freshness')+'<label>Offer version<input type="number" min="1" name="version" value="'+e(q.get('version',''),quote=True)+'"></label></details><button>Filter queue</button></form>'
        total=len(rows)
        requested=q.get('page','1')
        if not requested.isdigit() or not 1<=int(requested)<=100:raise ValueError('Choose a bounded review page')
        current_page=int(requested);rows=rows[(current_page-1)*10:current_page*10]
        body+='<p>'+str(total)+' matching authorised pairs · page '+str(current_page)+'. Showing up to ten. Denominators above describe the full authorised cohort.</p>'
        for a in rows:
            b=a['buying_trigger'];r=private.get((a['offer_id'],a['enterprise_slug']))
            body+='<article class="assurance-row"><div><strong>'+e(a['enterprise_name'])+'</strong><p>'+e(names[a['offer_id']])+' · v'+str(a['offer_version'])+'</p></div><div>'+e(b['tier'])+'<p>'+e(b['stage'])+'</p></div><div>'+('Stale — Reassess' if r and r['stale'] else 'Owner review not recorded; private seller review '+('yes' if r and r['reviewed'] else 'unknown'))+'<p>Last private record change: '+e(r['updated_at'] if r else 'Unknown — no authorised development record')+'</p></div>'+link('Inspect logic',offer=a['offer_id'],enterprise=a['enterprise_slug'],cutoff=data['cutoff'],**({'candidate':r['id']} if r else {}))+'</article>'
        body+='<p>'
        if current_page>1:body+=link('Previous ten',**(q|{'page':str(current_page-1)}))+' · '
        if current_page*10<total:body+=link('Next ten',**(q|{'page':str(current_page+1)}))
        body+='</p>'
        body+='<h2>Authorised Pipeline</h2>'
        for p in data['pipeline']:body+='<p>'+e(p['enterprise']+' · '+p['stage'])+' · '+link('Inspect inputs',pipeline=p['id'])+'</p>'
        body+=details('Evaluator and source revisions',data['policy'])
    return page(title,'<style>'+CSS+'</style><section class="assurance"><p class="eyebrow">Owner Command Centre</p><h1>'+e(title)+'</h1>'+body+'</section>',headers,'offers',path)


BUSINESS_CSS="""
.commercial{max-width:1080px;margin:auto;padding:44px 28px 80px;color:#173e32}.commercial h1{font:clamp(2.6rem,5vw,4rem)/1.08 Georgia,serif;letter-spacing:-.035em;max-width:850px}.commercial h2{font:1.8rem Georgia,serif;margin:0 0 12px}.commercial p{line-height:1.65;max-width:76ch}.commercial .eyebrow{font-size:.74rem;text-transform:uppercase;letter-spacing:.12em}.commercial .lead{font-size:1.15rem;max-width:70ch}.commercial .account-row{display:grid;grid-template-columns:1fr 2fr auto;gap:24px;padding:28px 0;border-top:1px solid #d9dfd4}.commercial .account-row p{margin:7px 0}.commercial .review-block{padding:24px 0;border-top:1px solid #d9dfd4}.commercial .review-block h2{font-size:1.3rem}.commercial a{color:#174d3f;display:inline-block;min-height:44px;padding:10px 0;text-underline-offset:4px;overflow-wrap:anywhere}.commercial .primary{padding:12px 18px;border:1px solid #acbfb0;border-radius:28px;text-decoration:none;align-self:start}.commercial details{padding:16px 0;border-top:1px solid #d9dfd4;margin-top:22px}.commercial summary{cursor:pointer;font-weight:600;min-height:36px}.commercial select,.commercial input,.commercial button{font:inherit;min-height:44px;max-width:100%;padding:9px;border:1px solid #b2c1b4;border-radius:10px}.commercial label{display:block;margin:12px 0}.commercial button{background:#174d3f;color:white;padding:10px 20px}.commercial .source-item{margin:20px 0}.commercial :focus-visible{outline:3px solid #7653b5;outline-offset:3px}@media(max-width:720px){.commercial{padding:28px 18px 60px}.commercial .account-row{grid-template-columns:1fr;gap:8px}.commercial h1{font-size:2.5rem}}
"""


def commercial_link(label,**q):
    return '<a class="primary" href="'+e(service.BASE+('?' +urlencode(q) if q else ''),quote=True)+'">'+e(label)+'</a>'


def business_sources(a):
    body='<details><summary>Sources and cautions</summary><p>Public reports inform this conversation. Customer need, access, funding and available work still need confirmation.</p>'
    seen=set()
    for f in a['buying_trigger']['timeline']:
        if f['source_id'] in seen:continue
        seen.add(f['source_id'])
        body+='<div class="source-item"><a rel="noreferrer" href="'+e(f['source_url'],quote=True)+'">'+e(f['source_title'])+'</a><p>Published '+e(f['publication_date'] or 'date unknown')+'. '+e(f['interpretation_limit'])+'</p></div>'
    if a['contradictions']:body+='<p>'+e('; '.join(a['contradictions']))+'</p>'
    return body+'</details>'


@ds.view_scope
def render(path,query,headers):
    service.authority(headers)
    view=query.get('view',['commercial'])
    if len(view)!=1 or view[0] not in {'commercial','advanced'}:raise ValueError('Choose a supported view')
    if view[0]=='advanced':return _advanced_render(path,{k:v for k,v in query.items() if k!='view'},headers)
    from .opportunity_assurance_commercial import summary
    allowed={'offer','enterprise','candidate','pipeline','cutoff','tier','industry','freshness','sort','review','stale','version','gate','page','view'}
    if set(query)-allowed or any(len(v)!=1 or len(v[0])>300 for v in query.values()):raise ValueError('Unsupported or duplicate review selector')
    q={k:v[0] for k,v in query.items() if k!='view'}
    ds.context_link('/flora/command-centre','Command Centre')
    title='Commercial review';body='<p class="lead">Understand the customer’s situation. Find out whether there is still a useful conversation to have.</p>'
    advanced=dict(q,view='advanced')
    if q.get('pipeline'):
        if set(q)!={'pipeline'}:raise ValueError('Select one sales record')
        data=service.inspect_pipeline(q['pipeline'],headers=headers);r=data['record']
        title=r['enterprise'];body='<p class="eyebrow">'+e(r['title'])+'</p><h2>Recorded sales work</h2><p>'+e(r['problem'])+'</p><h2>Best next action</h2><p>'+e(r['next_action'])+'</p><p>This is the seller’s recorded sales work. The record does not independently establish current customer demand or an open opportunity to influence.</p>'
    elif q.get('offer') or q.get('enterprise') or q.get('candidate'):
        if not q.get('offer') or not q.get('enterprise'):raise ValueError('Select a customer and Offer')
        data=service.inspect_pair(q['offer'],q['enterprise'],q.get('cutoff',''),q.get('candidate',''),headers=headers);a=data['original'];s=summary(a)
        title=s['customer'];body='<p class="eyebrow">'+e(data['offer']['name'])+'</p><p class="lead">'+e(s['outcome'])+'</p>'
        for label,key in [('Potential business challenge','challenge'),('Opportunity to influence','influence'),('Best next action','next_action'),('Biggest uncertainty','uncertainty')]:
            body+='<section class="review-block"><h2>'+label+'</h2><p>'+e(s[key])+'</p></section>'
        body+='<p>'+e(s['value'])+'</p>'+business_sources(a)
        if a['enterprise_slug']=='santander-uk' and any(f['id']=='BTI-TSB-MIGRATION' for f in a['buying_trigger']['timeline']):
            from .opportunity_assurance_commercial import TSB_NOTE
            body+='<details><summary>What the November update says</summary><p>'+e(TSB_NOTE['context'])+'</p><a rel="noreferrer" href="'+e(TSB_NOTE['url'],quote=True)+'">Read the 10 November TSB update</a></details>'
    else:
        data=service.overview(q.get('cutoff',''),headers=headers);state=offers.snapshot(headers=headers);names={r['id']:r['content']['name'] for r in state['offers'] if r['current']}
        private={(r['offer_id'],r['enterprise_slug']):r for r in data['development']}
        if q.get('sort','customer') not in {'customer','offer'}:raise ValueError('Choose customer or Offer order')
        rows=sorted(data['assessments'],key=lambda a:((a['offer_id'],a['enterprise_slug']) not in private,a['enterprise_name'],names[a['offer_id']]) if q.get('sort','customer')=='customer' else ((a['offer_id'],a['enterprise_slug']) not in private,names[a['offer_id']],a['enterprise_name']))
        # Saved work first, then alphabetical presentation deliberately does not repurpose the historical tier as a strategic-sales rank.
        page_number=q.get('page','1')
        if not page_number.isdigit() or not 1<=int(page_number)<=100:raise ValueError('Choose a review page')
        n=int(page_number);shown=rows[(n-1)*5:n*5]
        body+='<p>'+str(len(rows))+' customer and Offer conversations available in your workspace. No open buying opportunity is assumed.</p>'
        if not rows:body+='<p>Choose an authorised company and Offer to review customer conversations.</p>'
        for a in shown:
            s=summary(a);r=private.get((a['offer_id'],a['enterprise_slug']))
            body+='<article class="account-row"><div><h2>'+e(s['customer'])+'</h2><p>'+e(names[a['offer_id']])+'</p></div><div><p>'+e(s['challenge'])+'</p><p>'+e(s['outcome'])+'</p></div>'+commercial_link('Review conversation',offer=a['offer_id'],enterprise=a['enterprise_slug'],cutoff=data['cutoff'],**({'candidate':r['id']} if r else {}))+'</article>'
        if n>1:body+=commercial_link('Previous conversations',page=n-1,cutoff=data['cutoff'])+' '
        if n*5<len(rows):body+=commercial_link('Next conversations',page=n+1,cutoff=data['cutoff'])
    body+='<details class="advanced-entry"><summary>Advanced Inspection</summary><p>Optional source detail, original research priorities, sales checks and read-only challenges.</p><a href="'+e(service.BASE+'?'+urlencode(advanced),quote=True)+'">Open Advanced Inspection</a></details>'
    return page(title,'<style>'+BUSINESS_CSS+'</style><section class="commercial"><p class="eyebrow">Command Centre</p><h1>'+e(title)+'</h1>'+body+'</section>',headers,'offers',path)
