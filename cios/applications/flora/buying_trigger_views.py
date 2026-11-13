"""Simple private discovery and reviewed-shortlist views over the single matcher."""
from html import escape as e
from . import offers, design_system as ds
from .research_intelligence import buying_evidence as research

CSS='''
.trigger-list{list-style:none;padding:0;margin:26px 0}.trigger-row{display:grid;grid-template-columns:minmax(150px,1fr) minmax(220px,2fr) auto;gap:24px;align-items:start;border-bottom:1px solid #d4d9c9;padding:24px 0}.trigger-row h2{font-size:1.4rem;margin:0 0 10px}.trigger-tier{font-size:.85rem;font-weight:600}.trigger-action{display:inline-flex;align-items:center;min-height:44px;padding:10px 16px;border:1px solid #adc0af;border-radius:24px;text-decoration:none}.trigger-brief{max-width:850px}.trigger-brief h2{margin-bottom:8px}.trigger-timeline{padding-left:22px}.trigger-timeline li{padding:10px 0;line-height:1.55}.trigger-checks{margin:20px 0}.trigger-checks label{display:flex;gap:10px;align-items:start;min-height:44px}.trigger-checks input{width:20px;height:20px;flex:0 0 auto}.trigger-row p{margin:4px 0 10px}@media(max-width:700px){.trigger-row{grid-template-columns:1fr;gap:8px}.trigger-action{justify-self:start}}
'''


def permitted_targets(headers):
    from .access import can_access_enterprise
    return {slug:a for slug,a in research.accounts(offers.accounts()).items()
            if a['id'].startswith('presentation:') or can_access_enterprise(headers,a['id'])}


def _offers(state):
    return sorted([r for r in state['offers'] if r['current'] and r['eligible'] and r.get('template_source',{}).get('id') in research.OFFER_DIMENSIONS],
                  key=lambda r:(list(research.OFFER_DIMENSIONS).index(r['template_source']['id']),r['content']['name']))


def sources(results):
    refs={};limits=[]
    for r in results:
        for f in r['buying_trigger']['timeline']:refs[(f['source_id'],f['id'])]=f
        limits.extend(r['buying_trigger']['identity_scope']['canonical_identity_gap'] for _ in [0])
    body='<h2>Buying trigger sources & method</h2><p>Source-supported candidate research, not accepted Evidence/APPA or buyer intent. Tiers prioritise validation. A 90-day catalyst review window is an operational pilot rule, not a buying half-life or customer deadline. Source publication, effective period and last source verification are separate. The review date never resets an old event.</p>'
    body+='<p>No verified procurement invitation, seller access, funding or contract value is established. Research is bounded and incomplete. Private notes never become research facts. Canonical source/identity rights are not granted by this view.</p>'
    for f in refs.values():
        body+='<section><h3>'+e(f['id'])+'</h3><p>'+e(f['statement'])+'</p><p>Retained excerpt: '+e(f['quote'])+'</p><p><a rel="noreferrer" href="'+e(f['source_url'],quote=True)+'">'+e(f['source_title'])+'</a> · '+e(f['locator'])+'</p><p>Published '+e(f['publication_date'] or 'Unknown')+' · source checked '+e(f['last_verified'] or 'Unknown')+' · effective '+e(f['effective_date'] or f['effective_period'] or 'Unknown')+'</p><p>Scope: '+e(f['source_scope'])+'</p><p>'+e(f['source_rights'])+'</p><p>'+e(f['interpretation_limit'])+'</p></section>'
    body+='<p>Identity boundaries: '+e('; '.join(dict.fromkeys(limits)))+'</p>'
    ds.source_note(body)


def body(path,state,q,headers):
    from .offers_views import url,link,form,hidden,field
    extra='<style>'+CSS+'</style>'
    if path=='/shortlists':
        records=offers.shortlist_snapshot(headers=headers)
        if q.get('shortlist'):
            records=[r for r in records if r['id']==q['shortlist']]
            if not records:raise PermissionError('Reviewed shortlist unavailable')
        content='<p>Your private research reviews. These are snapshots, with no lead, contact or Pipeline creation.</p>'
        if not records:content+='<p>No reviewed shortlists yet.</p>'
        for r in records:
            content+='<article class="pair"><h2>Reviewed shortlist · v'+str(r['version'])+'</h2><p>As of '+e(r['source_cutoff'])+' · '+('Inputs changed — refresh before use' if r['stale'] else 'Retained reviewed research snapshot')+'</p><p>'+e(r['note'])+'</p><ul>'
            for entry in r['entries']:content+='<li>'+e(entry['enterprise_name']+' · '+entry['tier']+' · '+entry['why'])+'</li>'
            content+='</ul>'+link('/triggers','Refresh assessment',mode='offer',selected=r['offer_id'],cutoff=r['source_cutoff'])+'</article>'
        return 'Reviewed shortlists',extra+content
    choices=_offers(state)
    if not choices:return 'Discover customers',extra+'<p>Choose one of the five strategic Offers to start.</p>'+link('/start','Set up my offers')
    cutoff=q.get('cutoff','2026-11-13');mode=q.get('mode','offer')
    if mode not in {'offer','account'}:raise ValueError('Choose offer-led or account-led discovery')
    targets=permitted_targets(headers)
    if path=='/trigger-detail':
        if not q.get('offer') or not q.get('enterprise'):raise ValueError('Select an Offer and an enterprise')
        results=offers.discover('offer',q.get('offer',''),cutoff,intelligence=True,headers=headers)
        chosen=next((r for r in results if r['enterprise_slug']==q.get('enterprise')),None)
        if not chosen:raise PermissionError('Offer/account assessment unavailable')
        row=next(r for r in choices if r['id']==chosen['offer_id']);b=chosen['buying_trigger'];sources([chosen])
        content='<article class="trigger-brief"><p class="eyebrow">'+e(row['content']['name'])+'</p><h2>'+e(chosen['enterprise_name'])+'</h2><p class="trigger-tier">'+e(b['tier']+' · '+b['stage'])+'</p><p>'+e(chosen['why_account'])+'</p>'
        content+='<h3>A useful first conversation</h3><p>'+e(chosen['entry_play'])+'</p><h3>The deciding question</h3><p>'+e(chosen['next_validation_action'])+'</p>'
        if b.get('entry_play_detail'):content+='<p><strong>Stop condition:</strong> '+e(b['entry_play_detail']['stop'])+'</p>'
        content+='<h3>Value to validate</h3><p>'+e('; '.join(chosen['economic_value_hypothesis']['mechanisms']))+'</p><p>'+e(chosen['economic_value_hypothesis']['method'])+'</p>'
        content+='<h3>Reported timeline</h3><ol class="trigger-timeline">'
        for f in b['timeline']:
            content+='<li><strong>'+e(f['publication_date'] or 'Publication date unknown')+'</strong> · '+e(f['statement'])+'<br><small>'+e(f['effective_period'] or 'Effective date unknown')+' · '+e(f['freshness'])+'</small></li>'
        if not b['timeline']:content+='<li>No current Offer-specific signal found in the reviewed sources.</li>'
        content+='</ol><details><summary>Alternatives and remaining questions</summary><p>'+e('; '.join(chosen['contradictions']) or 'No specific counter-evidence retained; this does not establish absence of an incumbent solution.')+'</p><p>'+e('; '.join(b['reasons']))+'</p><p>Next evidence task: '+e(b['next_evidence_task'])+'</p><p>Unknown: '+e('; '.join(b['unknowns']))+'</p><p>'+e(b['research_completeness'])+'</p></details></article>'
        return 'Offer fit',extra+content
    selected=q.get('selected') or (choices[0]['id'] if mode=='offer' else ('lloyds' if 'lloyds' in targets else next(iter(targets),'')))
    results=offers.discover(mode,selected,cutoff,intelligence=True,headers=headers);sources(results)
    options=''.join('<option value="'+e(r['id'],quote=True)+'" '+('selected' if selected==r['id'] else '')+'>'+e(r['content']['name'])+'</option>' for r in choices) if mode=='offer' else ''.join('<option value="'+e(slug)+'" '+('selected' if selected==slug else '')+'>'+e(a['name'])+'</option>' for slug,a in targets.items())
    content='<p>Choose an Offer or an account. Prioritise the next validation conversation; these tiers do not establish buying intent.</p>'
    ds.context_link(url('/triggers',mode='offer'),'Offer-led customer discovery');ds.context_link(url('/triggers',mode='account'),'Account-led customer discovery')
    content+='<form method="get" action="'+url('/triggers')+'" class="inline">'+hidden('mode',mode)+'<label>'+('Offer' if mode=='offer' else 'Account')+'<select name="selected">'+options+'</select></label><label>Evidence cutoff<input type="date" name="cutoff" value="'+e(cutoff,quote=True)+'" required></label><button>Discover customers</button></form>'
    content+='<ol class="trigger-list">'
    for r in results:
        b=r['buying_trigger'];offer=next(c for c in choices if c['id']==r['offer_id'])
        content+='<li class="trigger-row" data-assessment-id="'+e(r['assessment_id'])+'" data-tier="'+e(b['tier'])+'"><div><h2>'+e(r['enterprise_name'] if mode=='offer' else offer['content']['name'])+'</h2><span class="trigger-tier">'+e(b['tier'])+'</span></div><div><p>'+e(r['why_account'])+'</p><small>'+e(b['stage'])+'</small></div><a class="trigger-action" href="'+e(url('/trigger-detail',offer=r['offer_id'],enterprise=r['enterprise_slug'],cutoff=cutoff),quote=True)+'">Explore fit</a></li>'
    content+='</ol>'
    if not results:content+='<p>No permitted accounts or eligible Offers are available.</p>'
    if mode=='offer' and results:
        row=next(c for c in choices if c['id']==selected);prior=next((r for r in offers.shortlist_snapshot(headers=headers) if r['offer_id']==selected and r['source_cutoff']==cutoff),None)
        checks=''.join('<label><input type="checkbox" name="assessment_ids" value="'+e(r['assessment_id'])+'"><span>'+e(r['enterprise_name']+' · '+r['buying_trigger']['tier'])+'</span></label>' for r in results if r['buying_trigger']['shortlist_eligible'])
        values=hidden('offer_id',selected)+hidden('offer_version',row['version'])+hidden('employer_version',state['selected']['version'])+hidden('cutoff',cutoff)+hidden('registry_digest',research.DATA_SHA256)+hidden('expected_version',prior['version'] if prior else 0)
        values+='<div class="trigger-checks">'+checks+'</div>'+field('note','','Private review note',area=True)+'<label><input type="checkbox" name="confirmed" value="reviewed" required> I reviewed these as research candidates, not qualified opportunities.</label>'
        content+='<details><summary>Save a private reviewed shortlist</summary>'+form('/shortlist-save',values,'Save reviewed shortlist')+'</details>'
    return 'Discover customers',extra+content


def submit(values,headers):
    from .offers_views import url
    allowed={'csrf','offer_id','offer_version','employer_version','cutoff','registry_digest','expected_version','note','assessment_ids','confirmed'}
    if set(values)-allowed or any(not isinstance(v,list) or not 1<=len(v)<=(12 if k=='assessment_ids' else 1) for k,v in values.items()):
        raise ValueError('Unsupported or duplicate shortlist fields')
    def one(k,default=''):
        v=values.get(k,[default])[0]
        if not isinstance(v,str) or len(v)>1000:raise ValueError('Bounded shortlist fields required')
        return v
    saved=offers.save_shortlist(one('offer_id'),int(one('offer_version')),int(one('employer_version')),one('cutoff'),one('registry_digest'),values.get('assessment_ids',[]),one('note'),int(one('expected_version','0')),one('confirmed')=='reviewed',headers=headers)
    return url('/shortlists',shortlist=saved['id'])
