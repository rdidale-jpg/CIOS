"""Commercial inspection UI; no private-store reads or mutations on public pages."""
from html import escape as e
import json
from .visual_intelligence import STYLE as EVIDENCE_STYLE,_sources,_badge

STYLE='''
.cv-summary{margin:18px 0}.cv-summary dl{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 22px;margin:0}.cv-summary dl>div{padding:14px 0;border-top:1px solid #d0dbc8;min-width:0}.cv-summary dt{font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;font-weight:800}.cv-summary dd{margin:7px 0;line-height:1.55;font-size:.94rem}.cv-investigation{margin:18px 0}.cv-investigation>summary{min-height:44px;padding:14px;background:#eef0e2;border-radius:12px;cursor:pointer;font-weight:750}.cv{color:#173f37;margin:22px 0}.cv *{box-sizing:border-box}.cv-header{padding:28px 30px;background:#eef0e2;border:1px solid #c3d2bf;border-radius:23px}.cv-header h1,.cv-header h2{font-size:clamp(1.8rem,3.1vw,2.9rem);line-height:1.13;max-width:900px;margin:10px 0 16px}.cv-kicker{font-size:.73rem;letter-spacing:.09em;text-transform:uppercase;font-weight:800;color:#586d5d}.cv p{line-height:1.6}.cv-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin:20px 0}.cv-card{border:1px solid #c5d3bf;border-radius:18px;padding:22px;background:#fffdf7;min-width:0}.cv-card h3{font-size:1.15rem;margin:9px 0}.cv-card h2{font-size:1.3rem}.cv-card p{font-size:.94rem}.cv-links{display:flex;gap:9px;flex-wrap:wrap;margin:15px 0}.cv-link{display:inline-flex;align-items:center;min-height:44px;border:1px solid #b9cdbb;border-radius:22px;padding:9px 14px;text-decoration:none;font-size:.86rem;background:#fffdf7;color:#194f40}.cv-link.primary{background:#174d3f;color:white}.cv-warning{padding:15px 20px;border-left:3px solid #b58c51;background:#f7f0e2;margin:18px 0;line-height:1.6;font-size:.9rem}.cv-ratings{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:18px 0}.cv-rating{border:1px solid #d0dbc8;padding:17px;border-radius:14px;background:#f6f4eb}.cv-rating strong{font-size:1.4rem;display:block;margin:8px 0}.cv-rating small{font-size:.83rem;line-height:1.5;display:block}.cv-activity{scroll-margin-top:20px}.cv-activity[open]{border:2px solid #7d9f85}.cv-list{display:flex;gap:8px;flex-wrap:wrap}.cv details>summary,.cv a:focus-visible,.cv button:focus-visible{outline-offset:3px}.cv a:focus-visible,.cv button:focus-visible{outline:3px solid #875622}.cv .vi-source{overflow-wrap:anywhere}.cv-empty{padding:20px;border:1px dashed #b2c3ad;border-radius:15px;color:#5b6e5e}.cv-capture form{margin:15px 0}.cv-capture button{min-height:44px}.cv-provenance{overflow-wrap:anywhere;font-size:.82rem}.cv-step{font-weight:800;color:#6b5a36}.cv-snapshot{font-size:.82rem;overflow-wrap:anywhere}.cv blockquote{border-left:3px solid #afc5ad;margin:15px 0;padding:10px 17px;background:#f3f4e9}.cv .cv-unknown{font-weight:750;color:#805b32}.cv-sticky{scroll-margin-top:20px}@media(max-width:850px){.cv-ratings{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:600px){.cv-grid,.cv-ratings,.cv-summary dl{grid-template-columns:1fr}.cv-header,.cv-card{padding:20px}.cv-header h1{font-size:2rem}.cv-link{max-width:100%;overflow-wrap:anywhere}}@media(pointer:coarse){.cv summary{min-height:44px;align-content:center}.cv a{display:inline-block;min-height:44px;align-content:center}}@media(prefers-reduced-motion:reduce){.cv *{scroll-behavior:auto!important;transition:none!important}}@media print{.cv-header,.cv-card,.cv-rating{break-inside:avoid}.cv-ratings{grid-template-columns:repeat(3,1fr)}.cv-grid{grid-template-columns:1fr 1fr}.cv-capture form{display:none}.cv a{color:#173f37}.cv details{break-inside:avoid}}
'''
SCRIPT='''
(function(){document.querySelectorAll('.cv[data-cv-ready=false]').forEach(function(root){
 root.dataset.cvReady='true';
 function restore(){var h='';try{h=decodeURIComponent(location.hash.slice(1))}catch(error){return}
  var data=root.querySelector('[data-cv-returns]');if(h.indexOf('from-')===0&&data){var choices=JSON.parse(data.textContent),key=h.slice(5);if(Object.prototype.hasOwnProperty.call(choices,key)){var item=choices[key],a=root.querySelector('.cv-return'),b=root.querySelector('.cv-enterprise-return');if(a){a.href=item.url;a.textContent='← Back to '+item.label+' · commercial map'}if(b)b.href=item.enterprise_url}}
  var node=document.getElementById(h);if(node&&root.contains(node)){var parent=node.parentElement;while(parent&&parent!==root){if(parent.tagName==='DETAILS')parent.open=true;parent=parent.parentElement}}if(node&&root.contains(node)&&node.classList.contains('cv-activity')){node.open=true;requestAnimationFrame(function(){node.querySelector('summary').focus({preventScroll:true});node.scrollIntoView({block:'start'})})}
 }
 root.addEventListener('click',function(event){var a=event.target.closest('a[href^="#"]');if(a)setTimeout(restore,0)});
 restore();if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',restore,{once:true});window.addEventListener('hashchange',restore);
 var states=[];window.addEventListener('beforeprint',function(){states=Array.from(document.querySelectorAll('details')).map(function(d){var s=[d,d.open];d.open=true;return s})});window.addEventListener('afterprint',function(){states.forEach(function(s){s[0].open=s[1]});states=[]});
});})();
'''


def link(url,label,primary=False,extra='',class_name=''):
    return f"<a class='cv-link{' primary' if primary else ''}{' '+e(class_name,quote=True) if class_name else ''}' href='{e(url,quote=True)}' {extra}>{e(label)}</a>"


def cards(rows,activity_id=''):
    if not rows:return "<p class='cv-empty'>No mapped commercial hypotheses for this activity. Zero signals is valid; obtain relevant enterprise evidence before proposing an opportunity.</p>"
    out=[]
    for row in rows:
        c=row['commercial'];url=row['url']+('#from-'+activity_id if activity_id else '')
        grade='Source-supported context · demand unverified' if row['context_supported'] else 'Current source support missing / unverified'
        out.append(f"<article class='cv-card' data-hypothesis='{row['id']}'>{_badge('Commercial hypothesis')}<p class='cv-kicker'>{e(grade)}</p><h3>{e(row['title'])}</h3><p>{e(row['problem'])}</p><p><strong>Access:</strong> {e(c['buyer_status'])}. Budget, procurement timing and buying intent are not established.</p><p><strong>Next:</strong> {e(c['next_commercial_action'])}</p>{link(url,'Inspect hypothesis, evidence & qualification →')}</article>")
    return "<div class='cv-grid'>"+''.join(out)+'</div>'


def activity_commercial(spec,node):
    rows=node.get('commercial_candidates',[]);supported=sum(r['context_supported'] for r in rows)
    return f"<section class='cv'><p class='cv-step'>Activity → Enterprise → Hypothesis → Qualification</p><h3>Commercial Opportunities · {len(rows)} hypotheses / {supported} with source-supported context</h3><p class='cv-warning'>Research coverage association, not a confirmed implementation dependency, unmet need, supplier mandate or market-attractiveness ranking.</p><div class='cv-links'>"+link(spec['enterprise']['url']+'?lens=commercial#activity-'+node['id'],'Explore '+spec['enterprise']['label']+' commercial intelligence →',True)+"</div>"+cards(rows,node['id'])+'</section>'


def enterprise_body(projection):
    enterprise=projection['enterprise'];domain=projection['domain'];industry=projection['industry']
    body=f"<style>{EVIDENCE_STYLE}{STYLE}</style><section class='cv' data-cv-ready='false'><header class='cv-header' id='content'><p class='cv-kicker'>Enterprise intelligence / Commercial Opportunities</p><h1>{e(enterprise['label'])}. From signal to a testable proposition.</h1><p>Existing hypotheses, their source context, counterevidence and customer-validation gaps. No confirmed buying intent or automatic Pipeline record.</p></header><nav class='cv-links'>"+link(industry['url']+'?lens=commercial','← Industry commercial map')+link(enterprise['url'],'How the enterprise works')+link(enterprise['url']+'/understanding','Evidence quality & relationships')+'</nav>'
    body+="<p class='cv-warning'>Source-supported context is not verified customer demand. Buying roles are inferred unless explicitly evidenced. All current hypotheses remain unqualified; value, budget and procurement dates are Unknown.</p>"
    for activity in projection['activities']:
        rows=[r for r in projection['candidates'] if activity['id'] in {a['id'] for a in r['activities']}]
        body+=f"<details class='cv-activity' id='activity-{activity['id']}'><summary>{e(activity['label'])} · {len(rows)} research hypotheses</summary><p>Validated capability/programme references connect this research; they do not establish a confirmed enterprise dependency.</p>"+cards(rows,activity['id'])+'</details>'
    return body+f"<p class='cv-snapshot'>Candidate research snapshot {e(projection['snapshot_digest'])}; as of {e(projection['as_of'])}. Separate authored assessment dates appear within each hypothesis.</p><script>{SCRIPT}</script></section>"


def executive_summary(row):
    """Concise source-scoped decision aid; full original investigation follows."""
    from textwrap import shorten
    c=row['commercial']
    cells=[('Problem',c['business_problem']),('Why now',row['programme_signal']+' '+c['timing_context']),
           ('Potential service',c['proposed_service']),
           ('Evidence state','Source-supported context; customer demand unverified.' if row['context_supported'] else 'Current source support missing / unverified. Historical hypothesis retained.'),
           ('Buyer access',c['buyer_status']+'. Buying authority and access require customer validation.'),
           ('Next action',c['next_commercial_action'])]
    body="<section class='cv-summary cv-card' aria-label='Executive hypothesis summary'><p class='cv-kicker'>Decision brief · research hypothesis</p><h2>What merits a conversation?</h2><dl>"
    body+=''.join('<div><dt>'+e(label)+'</dt><dd>'+e(shorten(value,width=245,placeholder='…'))+'</dd></div>' for label,value in cells)
    body+="</dl><p class='cv-unknown'>Customer budget: Unknown · Procurement date: Unknown · Confirmed decision-maker: Unknown</p>"
    if row['conflicts']:
        body+="<p class='cv-warning'><strong>Conflicting findings — inspect before acting.</strong> "+e('; '.join(c['status'] for c in row['conflicts']))+'</p>'
    body+=link('#commercial-counterevidence',f"Inspect counterevidence & disconfirmation · {len(row['counterevidence'])} mapped statements")
    return body+"<p class='cv-provenance'>Enterprise-specific source scope and periods apply. Summary is abbreviated; full dimensions and exact passages follow. No confirmed external supplier demand.</p></section>"


def candidate_overview(data,row,projection,headers=None):
    from ..sales_views import capture_controls
    c=row['commercial'];enterprise=projection['enterprise'];root=projection['industry']['url']+'?lens=commercial'
    choices={a['id']:{**a,'enterprise_url':row['enterprise_url']+'#activity-'+a['id']} for a in row['activities']}
    default=next(iter(choices.values()),{'url':root,'label':'industry','enterprise_url':row['enterprise_url']})
    payload=json.dumps(choices,ensure_ascii=True).replace('<','\\u003c')
    body=f"<style>{EVIDENCE_STYLE}{STYLE}</style><section class='cv' data-cv-ready='false'><script type='application/json' data-cv-returns>{payload}</script><nav class='cv-links'>"+link(default['url'],'← Back to '+default['label']+' · commercial map',class_name='cv-return')+link(default['enterprise_url'],enterprise['label']+' commercial intelligence',class_name='cv-enterprise-return')+'</nav>'
    current_status=c['confidence'] if row['context_supported'] else 'Current source support missing — retained historical hypothesis; verify evidence before advancement.'
    body+=f"<header class='cv-header' id='explorer-content'>{_badge('Unqualified commercial hypothesis')}<p class='cv-kicker'>{e(enterprise['label'])} / {row['id']}</p><h1>{e(row['title'])}</h1><p>{e(c['offer'])}</p><p>{e(current_status)}</p></header>"
    body+=executive_summary(row)
    body+="<nav class='cv-links' aria-label='Hypothesis inspection'>"+link('#commercial-support','Inspect supporting context')+link('#commercial-counterevidence','Inspect counterevidence')+link('#commercial-capture','Review create/link & qualification →',True)+'</nav>'
    body+="<p class='cv-warning'>Research exploration is read-only. No confirmed customer requirement, allocated budget, named buyer authority, tender or current supplier contract is established by this hypothesis. Missing information is not evidence of a problem.</p>"
    sections=[('01','Potential business problem / outcome',c['business_problem']+' Potential outcome: '+row.get('review',{}).get('measurable_outcome','Define a customer-owned measurable outcome before advancing.')),
      ('02','Why might the enterprise act?',row['programme_signal']+' '+c['timing_context']),
      ('05','Potential technology, consulting or managed service',c['proposed_service']+' '+row['intervention']),
      ('06','Possible stakeholders and decision-makers',c['buyer_status']+'. '+', '.join(c['buyer_functions'])+'. Verified buying authority: '+(', '.join(c['verified_buyer_names']) or 'Not established')),
      ('07','Supplier and competitive position — inspect scope/date',c['supplier_position']+' '+c['delivery_and_competition']),
      ('10','Next commercial action',c['next_commercial_action']+' Route to market: '+c['route_to_market'])]
    body+="<details class='cv-investigation'><summary>Investigate the problem, service, buyer and supporting evidence · dimensions 01–03, 05–07, 10</summary><div class='cv-grid'>"+''.join(f"<article class='cv-card'><span class='cv-kicker'>{number} / Investigate</span><h2>{e(title)}</h2><p>{e(text)}</p></article>" for number,title,text in sections)+'</div>'
    body+="<section class='cv-card' id='commercial-support'><h2>03 / Evidence supporting the context</h2><p>These statements support their own scope and period, not the commercial premise or customer demand. Last retrieval is a provenance review date, not a guarantee of current deployment.</p>"+_sources([next(p for p in row['support'] if p['supported'])] if any(p['supported'] for p in row['support']) else [])+"<details><summary>Inspect all scoped supporting statements, source dates and limitations</summary>"+_sources(row['support'])+'</details></section>'
    body+="</details><section class='cv-card' id='commercial-counterevidence'><h2>04 / Counterevidence, contradictions & disconfirmation</h2>"
    for conflict in row['conflicts']:body+=f"<p class='cv-warning'>{e(conflict['status'])}. {e(conflict['treatment'])}</p>"
    body+=_sources(row['counterevidence']) if row['counterevidence'] else "<p>No explicit contradictory claim is mapped in this snapshot. This is not corroboration or proof of an unmet need. Test existing internal delivery, alternative providers and whether the customer wants external help.</p>"
    body+="<p>Competing periods or denominators must not be merged. Do not sell an assumed failure or control gap.</p></section>"
    body+="<details class='cv-investigation'><summary>Commercial gaps and separate assessments · dimensions 08–09</summary><section class='cv-card'><h2>08 / Missing commercial information</h2><p class='cv-unknown'>Deal value: Unknown · Customer budget: Unknown · Procurement date: Unknown · Confirmed decision-maker: Unknown</p><ul>"+''.join(f"<li><strong>{e(g['title'])}</strong>: {e(g['question'])}<br>Needed: {e(g['required_evidence'])}</li>" for g in row['gaps'])+'</ul></section>'
    body+=f"<section class='cv-card'><h2>09 / Attractiveness and actionability — separate assessments</h2><p>Authored assessment {e(row['assessment_date'])}. {e(row['assessment_limitation'])}</p><div class='cv-ratings'>"+''.join(f"<article class='cv-rating'><span>{e(d['label'])}</span><strong>{d['score']} / 3</strong><small>{e(d['anchor'])}</small><p>{e(d['reason'])}</p></article>" for d in row['dimensions'])+'</div><p>No combined score, win probability or automatic qualification. '+('Current source context supports investigation.' if row['context_supported'] else 'Current source support is missing; historic authored scores are not recalculated into commercial certainty.')+'</p></section>'
    body+='</details>'
    capture=capture_controls(row['enterprise_slug'],row['id'],headers).replace('Add to pipeline & qualify →','Create or link record → qualification')
    body+=f"<section class='cv-card cv-capture' id='commercial-capture'><p class='cv-step'>Review → deliberate capture/link → private qualification</p><h2>Develop the hypothesis in your workspace</h2><p>By choosing Create or link, you request a private <strong>Discovered</strong> research-stage record. Duplicate capture returns the existing workspace record without rewriting its provenance. All ten qualification inputs, evidence review and explicit stage confirmation remain required to advance.</p>{capture}<p>The existing Pipeline remains demonstration-marked. Public research is never promoted to an established fact or qualified deal by this action.</p>{link('/flora/sales/pipeline','Open authorised Pipeline')}</section>"
    body+="<div class='cv-links'>"+''.join(link(a['url'],'Back to '+a['label']) for a in row['activities'])+'</div>'
    body+=f"<details class='cv-snapshot'><summary>Inspection snapshot and authority boundary</summary><p>Review {row['review_digest']}; inspection {row['inspection_digest']}; authored assessment {row['assessment_date']}. Public candidate intelligence only; no automatic acceptance or qualification.</p></details><script>{SCRIPT}</script></section>"
    return body


def pipeline_context(record):
    """Called only after existing private record authorisation; no public store lookup."""
    if not record.get('origin_id','').startswith('RCO-'):return ''
    from .registry import enterprise_domain
    from .model import load_assessment,candidate
    from .living_map_specs import load_mapping
    try:domain=enterprise_domain(record['enterprise_slug'])
    except ValueError:return ''
    data=load_assessment(domain);row=candidate(record['origin_id'],data)
    mapping=load_mapping(domain);frozen=record.get('provenance',{}).get('commercial_review',{})
    ids=frozen.get('activity_ids',[])
    if not ids and row:
        from .visual_intelligence_specs import load_profile
        ids=[a['id'] for a in load_profile(domain)['activities'] if set(a.get('resource_ids',[])) & set(row['capability_ids'])]
    body=f"<style>{EVIDENCE_STYLE}{STYLE}</style><section class='cv' data-cv-ready='false'><details><summary>Industry origin & immutable research snapshot</summary><div class='cv-links'>"
    body+=''.join(link('/industries/'+domain+'?lens=commercial#lm-'+domain+'-'+a['id'],'← '+a['label']) for a in mapping['activities'] if a['id'] in ids)+'</div>'
    if frozen:body+=f"<p class='cv-provenance'>Captured review {e(frozen['review_digest'])}; source/counterevidence references frozen in provenance. Counterevidence IDs: {e(', '.join(frozen['counterevidence_claim_ids']) or 'None mapped at capture')}. Current research may differ; no historical record is rewritten.</p>"
    else:body+="<p>Existing capture retains its original provenance. Current map navigation does not backfill or replace that historical record.</p>"
    return body+f"</details><script>{SCRIPT}</script></section>"
