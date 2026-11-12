"""Illustrated global/macro entry point; one inspector, canonical evidence on demand."""
from copy import deepcopy
from html import escape as e
from urllib.parse import urlencode
from . import macro_intelligence as m
from .model import load_assessment
from .unified_views import page, routes_for
from .visual_specs import build_visual_specs
from .visual_templates import pestle, operating, text
from .visual_intelligence import _icon, _art

STYLE='''
.shell:has(.mi){max-width:1360px}.mi{color:#174d3f}.mi[aria-busy=true]{opacity:.7;cursor:progress}.mi *{box-sizing:border-box}.mi h1{font:600 clamp(2rem,4vw,3.1rem)/1.08 Georgia,serif;margin:10px 0}.mi h2{font:600 1.55rem/1.15 Georgia,serif}.mi-kicker{font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;font-weight:800;color:#846538}.mi-intro{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:18px}.mi-intro p{font-size:.86rem;margin:8px 0;color:#617569}.mi-context{display:flex;gap:10px;flex-wrap:wrap;padding:12px 0 18px;align-items:end}.mi-context label{font-size:.73rem;display:grid;gap:5px;flex:1;min-width:130px}.mi-context select{font:inherit;color:#174d3f;min-height:44px;border-radius:12px;border:1px solid #bfcebe;padding:9px;background:#fffdf7;max-width:100%;width:100%}.mi-context button{min-height:44px}.mi-steps{display:flex;flex-wrap:wrap;gap:7px;margin:8px 0 18px}.mi-steps a,.mi-pill{border:1px solid #bcccbd;border-radius:18px;padding:8px 13px;font-size:.8rem;text-decoration:none;min-height:44px;display:inline-flex;align-items:center;background:#fffdf6}.mi-steps [aria-current],.mi-pill[aria-current]{background:#174d3f;color:white}.mi-grid{display:grid;grid-template-columns:minmax(0,1.9fr) minmax(275px,1fr);gap:18px;align-items:start}.mi-stage{border:1px solid #c1d1c1;border-radius:24px;overflow:hidden;background:radial-gradient(ellipse at center,#e1ebdc,#f7f4e8 70%);min-width:0;box-shadow:0 12px 30px #174d3f08}.mi-stage-title{font:600 1.2rem Georgia,serif;padding:10px 20px}.mi-stage svg{display:block;width:100%;height:auto}.mi-stage svg a:hover rect,.mi-stage svg a:focus rect{stroke:#906c34;stroke-width:3}.mi-stage svg a:focus{outline:none}.mi-stage svg a:focus-visible rect{stroke:#8b562a;stroke-width:4}.mi-stage svg a[aria-current] rect{stroke:#174d3f;stroke-width:3;fill:#e1ebda}.mi-stage svg a[data-related] .vt-box{stroke:#a37a39;stroke-width:3;fill:#dfebd8}.mi-stage svg a:not([data-related]) .vt-box{opacity:.7}.mi-legend{padding:12px 20px;font-size:.72rem;color:#657669;border-top:1px solid #d7dfcf}.mi-inspector{padding:23px;background:#fffef8;border:1px solid #c3d0bd;border-radius:22px;position:sticky;top:16px;min-width:0}.mi-inspector h2{margin:12px 0 20px}.mi-inspector h3{font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;color:#886639;margin:20px 0 7px}.mi-inspector p{font-size:.87rem;line-height:1.55;margin:8px 0;overflow-wrap:anywhere}.mi-inspector a{display:inline-flex;min-height:44px;align-items:center;font-size:.85rem}.mi-kind{display:inline-block;background:#e4edde;padding:5px 8px;border-radius:7px;font-size:.67rem}.mi-kind.proposed_legislation{background:#eee5f0;color:#674d77}.mi-kind.policy_priority{background:#f1e5cf;color:#806039}.mi-unknown{padding:10px 13px;border-left:3px dotted #a68145;background:#f6edda;font-size:.8rem!important}.mi-next{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px}.mi-next a{padding:10px 14px;border:1px solid #b5c9b4;border-radius:20px;text-decoration:none}.mi-next a:first-child{background:#174d3f;color:white}.mi-themes{display:flex;flex-wrap:wrap;gap:5px;margin:0 0 12px}.mi-themes a{font-size:.73rem;padding:7px 9px;min-height:44px}.mi-mobile-nav{display:none}.mi-footer{font-size:.77rem;margin:18px 0;color:#687b6b}.mi-report{background:#fffdf7;border:1px solid #c3d1bd;border-radius:20px;padding:24px;margin:20px 0}.mi-report article{border-top:1px solid #ced9c7;padding:20px 0;overflow-wrap:anywhere;scroll-margin-top:20px}.mi-report blockquote{border-left:3px solid #af925d;margin:12px 0;padding:8px 16px}.mi-report p,.mi-report li{font-size:.9rem;line-height:1.6}.mi-report pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.75rem}.mi-country{display:none}.mi-controls{display:flex;gap:9px;flex-wrap:wrap;margin:15px 0}.mi-controls button{min-height:44px}.mi a:focus-visible,.mi button:focus-visible,.mi select:focus-visible{outline:3px solid #9b6f35;outline-offset:3px}.mi-compact{font-size:.78rem;color:#637263}.mi-print-only{display:none}
@media(max-width:1100px){.mi-grid{grid-template-columns:1fr}.mi-inspector{position:static}.mi-intro{display:block}}
@media(max-width:580px){.shell:has(.mi) .topbar{flex-direction:row;align-items:center;gap:7px;margin-bottom:15px}.shell:has(.mi) .primary-nav{gap:3px}.shell:has(.mi) .primary-nav a{font-size:.78rem;padding:8px 6px}.shell:has(.mi) .profile-control{font-size:.77rem}.mi{display:flex;flex-direction:column}.mi>.mi-intro{order:0}.mi>.mi-steps{order:1}.mi>.mi-grid{order:2}.mi>.mi-context{order:3;border-top:1px solid #cbd7c6;margin-top:20px}.mi>.mi-footer{order:4}.mi>.mi-controls{order:5}.mi>.mi-report{order:6}.mi h1{font-size:2rem}.mi-intro{margin-bottom:4px}.mi-country{display:flex;flex-wrap:wrap;gap:5px;margin-top:10px}.mi-country a{font-size:.75rem;padding:7px 12px}.mi-context{display:grid;grid-template-columns:1fr 1fr}.mi-context label{min-width:0}.mi-context button{grid-column:1/-1}.mi-context label:last-of-type{grid-column:1/-1}.mi-atlas,.mi-portable{display:none!important}.mi-mobile-nav{display:grid;grid-template-columns:1fr 1fr;gap:9px;padding:16px}.mi-mobile-nav a{border:1px solid #bdcdbb;border-radius:16px;padding:16px 12px;min-height:112px;background:#fffdf7;text-decoration:none;font-size:.85rem;display:block}.mi-mobile-nav a[aria-current]{background:#e2ecdc;border:2px solid #174d3f}.mi-mobile-nav small{display:block;font-size:.68rem;color:#7c714e;margin-top:9px}.mi-mobile-nav svg{width:36px;height:36px;margin-bottom:10px}.mi-stage .mi-mobile-art{display:block!important;height:130px;width:100%}.mi-inspector{padding:20px}.mi-steps a{font-size:.73rem;padding:8px 10px}.mi-report{padding:18px}}
@media(prefers-reduced-motion:reduce){.mi *{scroll-behavior:auto!important;transition:none!important}}
@media print{.shell{max-width:none!important;padding:0!important}.mi-intro>a,.mi-themes,.shell>footer{display:none!important}.mi-intro{margin-bottom:8px}.mi h1{font-size:26pt}.mi-context,.mi-steps,.mi-controls,.mi-next,.mi-mobile-nav,.topbar,.context-tools{display:none!important}.mi-grid{display:block}.mi-inspector{position:static}.mi-stage{box-shadow:none;break-inside:avoid}.mi-atlas,.mi-portable{display:block!important}.mi-report article{break-inside:avoid}.mi-print-only{display:block}html[data-macro-print=executive] .mi-report{display:none}html[data-macro-print=executive] .mi-stage svg{max-height:95mm}html[data-macro-print=executive] .mi-inspector{padding:10px;border:0}html[data-macro-print=executive] .mi-inspector h3{margin:9px 0 3px}html[data-macro-print=executive] .mi-inspector p{font-size:9pt}html[data-macro-print=executive] .mi-grid{display:grid;grid-template-columns:1.3fr 1fr}@page{size:A4;margin:12mm}}
'''
SCRIPT='''
(function(){if(window.floraMacroReady)return;window.floraMacroReady=true;var generation=0;
 async function navigate(url,push){var ticket=++generation;var root=document.getElementById('macro-root');if(!root)return;root.setAttribute('aria-busy','true');try{var response=await fetch(url,{credentials:'same-origin'});if(!response.ok)throw Error('Unavailable');var doc=new DOMParser().parseFromString(await response.text(),'text/html'),next=doc.getElementById('macro-root');if(!next)throw Error('Unavailable');if(ticket!==generation)return;root.replaceWith(next);if(push)history.pushState({},'',url);document.title=doc.title;var heading=document.querySelector('#macro-inspector h2');if(heading){heading.focus({preventScroll:true});if(matchMedia('(max-width:1100px)').matches)heading.scrollIntoView({block:'start',behavior:'auto'});}}catch(error){if(ticket===generation)location.assign(url);}}
 document.addEventListener('click',function(event){var a=event.target.closest('a[data-macro-nav]');if(a&&!event.ctrlKey&&!event.metaKey&&!event.shiftKey&&!event.altKey&&event.button===0){var url=a.getAttribute('href');if(url==='/macro'||url.startsWith('/macro?')){event.preventDefault();navigate(url,true);}}var print=event.target.closest('[data-macro-print]');if(print){document.documentElement.dataset.macroPrint=print.dataset.macroPrint;window.print();}});
 addEventListener('popstate',function(){if(location.pathname==='/macro')navigate(location.pathname+location.search,false);});
 addEventListener('afterprint',function(){delete document.documentElement.dataset.macroPrint;});
})();
'''


def url(chosen,path='/macro',**updates):
    values={**chosen.model_dump(),**updates}
    return path+'?'+urlencode({k:v for k,v in values.items() if v!=''})


def nav(chosen,label,**updates):
    return "<a data-macro-nav href='"+e(url(chosen,**updates),quote=True)+"'>"+e(label)+"</a>"


def globe():
    return "<g aria-hidden='true'><circle cx='460' cy='315' r='132' fill='#dce8d5' stroke='#a0b69f'/><ellipse cx='460' cy='315' rx='65' ry='132' fill='none' stroke='#b9cbb3'/><ellipse cx='460' cy='315' rx='132' ry='48' fill='none' stroke='#b9cbb3'/><path d='M328 315H592 M350 245H570 M350 385H570' fill='none' stroke='#b9cbb3'/><path d='M370 250L395 221 443 229 458 250 433 279 410 280 397 308 375 295Z M457 291L481 280 504 301 500 345 480 364 466 335Z M510 252L544 259 557 287 536 307 515 293Z' fill='#b9cfad' stroke='#96ad8c'/><path d='M335 440Q460 460 585 440' fill='none' stroke='#a88a55' stroke-dasharray='4 7'/></g>"+text(460,490,'One world. Different contexts.',size=14,anchor='middle',color='#58745f')


def atlas(chosen,data):
    positions=[(25,35),(645,35),(25,245),(645,245),(25,455),(645,455)]
    icons=['network','home','data','bank','people','document'];shapes=[];mobile=[]
    for i,category in enumerate(data['categories']):
        x,y=positions[i];active=category['id']==chosen.category
        themes=[f for f in data['forces'] if category['id'] in f['category_ids']]
        count=sum(chosen.market=='global' or chosen.market in f['country_ids'] for f in themes)
        label=('Outside country scope' if themes else 'Not researched') if not count else str(count)+(' reviewed theme' if count==1 else ' reviewed themes')
        destination=url(chosen,category=category['id'],force='',view='atlas',factor='',capability='')
        lines=category['label'].replace(' & ',' &|').split('|')
        card=f"<rect x='{x}' y='{y}' width='250' height='140' rx='22' fill='#fffdf5' stroke='#b9cbb7'/>"+_icon(icons[i],x+18,y+17,1.1)
        card+=''.join(text(x+18,y+79+n*21,v,size=17,width=28) for n,v in enumerate(lines))
        card+=text(x+18,y+122,label,size=11,color='#8c7045',bold=False)
        shapes.append(f"<a data-macro-nav href='{e(destination,quote=True)}'"+(" aria-current='true'" if active else '')+f" aria-label='{e(category['label']+' — '+label,quote=True)}'><title>{e(category['label'])}</title>{card}</a>")
        mobile.append(f"<a data-macro-nav href='{e(destination,quote=True)}'"+(" aria-current='true'" if active else '')+"><svg viewBox='0 0 42 42' aria-hidden='true'>"+_icon(icons[i],5,5,1)+"</svg>"+e(category['label'])+'<small>'+e(label)+'</small></a>')
    orbit="<g aria-hidden='true' fill='none' stroke='#bda77d' stroke-dasharray='4 8'><ellipse cx='460' cy='315' rx='175' ry='218'/><path d='M275 105Q315 150 350 215 M645 105Q605 150 570 215 M275 315H328 M592 315H645 M275 525Q320 485 355 415 M645 525Q600 485 565 415'/></g>"
    artwork="<svg class='mi-atlas' viewBox='0 0 920 635' role='group' aria-labelledby='mi-atlas-title mi-atlas-desc'><title id='mi-atlas-title'>Systemic force atlas</title><desc id='mi-atlas-desc'>Six navigation categories around a schematic globe. This is not a geographic impact heatmap; only UK and France reference contexts are researched.</desc>"+orbit+globe()+''.join(shapes)+"</svg><svg class='mi-mobile-art' style='display:none' viewBox='310 175 300 330' aria-hidden='true'>"+globe()+"</svg>"
    return artwork+"<nav class='mi-mobile-nav' aria-label='Systemic force categories'>"+''.join(mobile)+"</nav>"


def industry_visual(chosen,spec):
    data=load_assessment(chosen.industry);shared=build_visual_specs(data,routes_for(data))
    key='pestle' if chosen.view=='industry' else 'operating-model'
    nodes=deepcopy(shared[key]['nodes']);mobile=[];destinations={}
    for node in nodes:
        changes={'factor':node['label'],'capability':''} if key=='pestle' else {'capability':node['id'],'factor':''}
        destinations[node['id']]=url(chosen,**changes)
        related=bool(spec['force'] and any(edge['object']==node['id'] and edge['status']=='interpreted' for edge in spec['edges']))
        mobile.append(f"<a data-macro-nav href='{e(destinations[node['id']],quote=True)}'>"+e(node['label'])+'<small>'+('Interpreted pressure' if related else 'Not assessed for this force')+'</small></a>')
    w,h,shapes=pestle(nodes) if key=='pestle' else operating(nodes)
    for node in nodes:
        related=any(edge['object']==node['id'] and edge['status']=='interpreted' for edge in spec['edges'])
        attr=" data-related='interpreted'" if related else ''
        selected=node['label']==chosen.factor if key=='pestle' else node['id']==chosen.capability
        shapes=shapes.replace("<a href='"+e(node['url'],quote=True)+"'", "<a data-macro-nav"+attr+(" aria-current='true'" if selected else '')+" href='"+e(destinations[node['id']],quote=True)+"'",1)
    banner=("<p class='mi-stage-title'>"+e(spec['enterprise']['name'] if chosen.view=='enterprise' else ('Banking' if chosen.industry=='banking' else 'Commercial aviation'))+" · "+(('Lloyds Bank plc identity verified; duty Unknown' if spec.get('enterprise_trace') and spec['enterprise_trace']['entity']['status']=='verified' else 'Group reference; local entity Unknown') if chosen.view=='enterprise' else 'Interpreted PESTLE pressure')+"</p>")
    if key!='pestle':banner+="<svg viewBox='360 120 560 220' style='height:130px' aria-hidden='true'>"+_art('banking' if chosen.industry=='banking' else 'aviation','mi-enterprise',True)+"</svg>"
    if key=='pestle':shapes+="<circle cx='450' cy='240' r='75' fill='#e4ecdc'/>"+_icon('bank' if chosen.industry=='banking' else 'plane',422,205,1.8)+text(450,280,'CONTEXT',size=10,anchor='middle',color='#63785e')
    return banner+f"<svg class='mi-portable' data-shared-template='{key}' viewBox='0 0 {w} {h}' role='group' aria-label='{e(key+' · interpreted macro pressure',quote=True)}'>{shapes}</svg><nav class='mi-mobile-nav' aria-label='Equivalent {key} destinations'>"+''.join(mobile)+"</nav>"


def controls(chosen):
    values=chosen.model_dump();fields=[]
    choices={'market':[('global','Global · 2 reference markets'),('GB','United Kingdom'),('FR','France')],
             'industry':[('banking','Banking'),('aviation','Commercial aviation')],
             'offering':list(m.OFFERINGS.items()),'mode':[('explore','Explore at your pace'),('new','New to this industry'),('expert','Direct evidence access')]}
    labels={'market':'Market context','industry':'Industry','offering':'Declared seller offering · relevance only','mode':'Exploration depth'}
    for key,options in choices.items():
        fields.append("<label>"+labels[key]+f"<select name='{key}'>"+''.join("<option value='"+value+"'"+(' selected' if values[key]==value else '')+'>'+e(label)+'</option>' for value,label in options)+"</select></label>")
    hidden=''.join(f"<input type='hidden' name='{key}' value='{e(value,quote=True)}'>" for key,value in values.items() if key not in choices and key not in ('factor','capability') and value)
    return "<form class='mi-context' id='macro-controls' action='/macro' method='get'>"+hidden+''.join(fields)+"<button type='submit'>Apply context →</button></form>"


def trace_inspector(chosen, spec, trace):
    entity = trace['entity']
    identified = entity['status'] == 'verified'
    title = 'Lloyds Bank plc · resilience assurance' if identified else 'France · reporting perimeter'
    body = "<aside class='mi-inspector' id='macro-inspector' aria-label='Contextual intelligence panel'>"
    body += "<span class='mi-kind'>Entity trace · candidate research</span><h2 tabindex='-1'>"+e(title)+"</h2>"
    body += "<p class='mi-compact'>"+e(trace['instrument_id'])+" · reviewed "+e(trace['as_of'])+"</p>"
    body += "<h3>What matters</h3><p>"+e(trace['consequence'])+"</p>"
    body += "<h3>What we know</h3><p class='mi-unknown'>"+e(
        'Identity verified: '+entity['legal_name']+' / '+entity['registry_id']+'. Formal applicability: Unknown. Bank category supported; binding rule and regulator-register cross-check outstanding.'
        if identified else 'Exact French legal entity and formal applicability: Unknown. National code exists; amended EU thresholds, phase-in and consolidation exemption require separate review.')+"</p>"
    body += "<h3>Why a sale may not follow</h3><p>"+e(
        'Existing teams or suppliers may already meet the need. The 2025 milestone is past; ongoing maintenance need does not prove an external contract.'
        if identified else 'Group reporting can remove a separate obligation. No Lloyds French mandate or UK hypothesis is transferred here.')+"</p>"
    body += "<h3>What next</h3><p>"+e(trace['question'])+"</p>"
    if chosen.capability and chosen.capability not in trace['capability_ids']:
        body += "<p class='mi-unknown'>Selected capability has no reviewed mechanism in this trace.</p>"
    body += "<p class='mi-compact'>Customer demand and territorial eligibility: Unverified. Buyer, budget and supplier opportunity remain unverified.</p>"
    sources={source['id']:source for source in trace['sources']}
    direct=['MT-UK-REGISTER','MT-UK-SS121'] if identified else ['MT-FR-CODE']
    body += "<div class='mi-next'>"+''.join("<a href='"+e(sources[sid]['url'],quote=True)+"'>"+('Entity register' if sid=='MT-UK-REGISTER' else 'Official instrument')+" →</a>" for sid in direct)
    body += "<a href='"+e(url(chosen,'/macro/evidence')+'#entity-trace',quote=True)+"'>Decision & evidence dossier →</a></div>"
    if trace['hypothesis_id']:
        row=next(c for c in spec['candidates'] if c['id']==trace['hypothesis_id'])
        body += "<p><a href='"+e(row['url'],quote=True)+"'>Existing research hypothesis →</a></p>"
    body += nav(chosen,'← Industry consequence',view='industry',factor=trace['pestle'],capability='')
    body += "<p><a href='#macro-visual'>← Back to visual</a></p></aside>"
    return body


def trace_dossier(chosen, trace):
    import json
    body="<article id='entity-trace'><h2>Entity / instrument decision</h2><p>"+e(trace['scope_reason'])+"</p>"
    body+="<p>Instrument: "+e(trace['instrument_status'])+" · version effective "+e(trace['instrument_effective_from'])+" · implementation milestone "+e(trace['implementation_milestone'] or 'Not established')+". These dates do not establish this enterprise’s legal duty.</p>"
    body+="<h3>Separate decisions</h3><ul>"+''.join("<li>"+e(edge['predicate'].replace('_',' ').title())+": <strong>"+e(edge['status'])+"</strong> · "+e(edge['object'])+"</li>" for edge in trace['edges'])+"</ul>"
    body+="<h3>Counter-tests</h3><ul>"+''.join("<li>"+e(alt['interpretation'])+" — "+e(alt['status'])+". "+e(alt['test'])+"</li>" for alt in trace['alternatives'])+"</ul>"
    for source in trace['sources']:
        if not source['id'].startswith('MT-'):continue
        body+="<article id='"+e(source['id'])+"'><h3>"+e(source['title'])+"</h3><blockquote>"+e(source['excerpts'][0]['quote'])+"</blockquote><p>Locator: "+e(source['excerpts'][0]['locator'])+"</p><p>Published/version: "+e(source['publication_date'] or 'Unknown')+" · Retrieved: "+e(source['retrieved_at'])+"</p><p>"+e(source['limitation'])+"</p><a href='"+e(source['url'],quote=True)+"'>Official source →</a><p class='mi-compact'>Excerpt SHA-256 "+e(source['text_sha256'])+" · original bytes not archived; candidate observation, not accepted Evidence.</p></article>"
    body+="<h3>Versioned edge manifest</h3><pre>"+e(json.dumps(trace['edges'],ensure_ascii=False,indent=2))+"</pre>"
    if trace['hypothesis_id']:
        from .macro_trace import capture_reference
        body+="<h3>MacroContextReference · design only</h3><p>Not saved to Pipeline. Existing immutable provenance, original opportunity identity and qualification gates remain unchanged.</p><pre>"+e(json.dumps(capture_reference(chosen,trace['hypothesis_id']),indent=2))+"</pre>"
    return body+"</article>"


def inspector(chosen,spec,data):
    if chosen.view=='enterprise' and spec.get('enterprise_trace'):
        return trace_inspector(chosen,spec,spec['enterprise_trace'])
    force=spec['force'];body="<aside class='mi-inspector' id='macro-inspector' aria-label='Contextual intelligence panel'>"
    if not force:
        return body+"<span class='mi-kind'>Research coverage gap</span><h2 tabindex='-1'>Not researched yet.</h2><p>This category is available for navigation, but this bounded pilot has no reviewed theme here. Blank does not mean no risk or opportunity.</p><h3>Next research action</h3><p>Select a high-value question and an official source family before adding an observation. Do not manufacture coverage.</p>"+nav(chosen,'Return to cyber reference journey',category='cyber',force='cyber',view='atlas')+'</aside>'
    body+=f"<span class='mi-kind {force['kind']}'>{e(m.KINDS[force['kind']])}</span><h2 tabindex='-1'>{e(force['label'])}</h2>"
    themes=[f for f in data['forces'] if chosen.category in f['category_ids']]
    if len(themes)>1:
        short={'cyber':'Threat research','cyber-bill':'Proposed bill','social-value':'UK social value','uk-srs':'UK reporting','eu-csrd':'France / EU reporting'}
        body+="<nav class='mi-themes' aria-label='Reviewed themes'>"+''.join(nav(chosen,short[f['id']],force=f['id'],factor='',capability='').replace('<a data-macro-nav',"<a class='mi-pill'"+(" aria-current='true'" if f['id']==force['id'] else '')+' data-macro-nav',1) for f in themes)+'</nav>'
    eligible=any(country['country_id'] in force['country_ids'] for country in spec['markets'])
    if not eligible:
        reference=', '.join('United Kingdom' if country=='GB' else 'France' for country in force['country_ids'])
        target='United Kingdom' if chosen.market=='GB' else 'France'
        what='Outside reviewed country coverage: evidence for '+reference+' does not establish applicability in the selected '+target+' view.'
        why='Country coverage is not a legal applicability decision. Cross-border reach, listing status, entity and activity scope need separate evidence.'
        if force['id']=='social-value':
            why+=' Cross-border suppliers may encounter UK tender conditions when bidding into a covered UK procurement. Supplier nationality and buyer jurisdiction are different questions.'
    else:what=force['what'];why=force['why']
    selected=chosen.factor if chosen.view=='industry' else chosen.capability if chosen.view=='enterprise' else ''
    if selected:
        assessment=load_assessment(chosen.industry)
        if chosen.view=='enterprise':selected=next(c['title'] for c in assessment['capabilities'] if c['id']==chosen.capability)
        body+="<p class='mi-compact'>Inspecting: "+e(selected)+'</p>'
    if force['effective_from']:body+="<p class='mi-compact'>Instrument reference date: "+e(force['effective_from'])+" · entity applicability not established.</p>"
    body+="<h3>What matters</h3><p>"+e(what)+"</p><h3>Why it matters</h3><p>"+e(why)+'</p>'
    if chosen.view!='atlas':
        affected=[edge for edge in spec['edges'] if edge['predicate']==('INTERPRETED_PESTLE_IMPACT' if chosen.view=='industry' else 'INTERPRETED_CAPABILITY_PRESSURE')]
        body+="<p class='mi-compact'>"+('Scoped analyst interpretation; highlighted nodes are research pressures, not proven enterprise effects.' if affected else 'No reviewed impact mechanism in this market context. Do not carry another market’s obligations across.')+'</p>'
        if chosen.factor and chosen.factor not in force['pestle']:body+="<p class='mi-unknown'>No reviewed mechanism is mapped to this PESTLE factor.</p>"
        if chosen.view=='enterprise':body+="<p class='mi-unknown'>Exact legal entity, ownership, actual exposure and business owner: Unknown. A parent’s identity or duty does not establish a subsidiary’s duty.</p>"
    body+="<h3>Evidence & uncertainty</h3><p>"+e(force['counter'])+'</p>'
    body+="<p class='mi-compact'>Reviewed "+data['as_of']+' · '+str(len(force['source_ids']))+' primary-source excerpts · original document bytes not archived.</p>'
    if chosen.offering!='none':body+="<p class='mi-unknown'>Seller relevance: "+e(spec['seller_relevance']['match'])+'. Customer demand and territorial eligibility: Unverified.</p>'
    if chosen.mode=='new':body+="<p class='mi-compact'><strong>In plain language:</strong> PESTLE means political, economic, social, technological, legal and environmental pressures. A hypothesis is a question to validate, not a customer order.</p>"
    body+="<h3>Next action</h3><p>"+e(force['next'])+'</p>'
    body+="<div class='mi-next'>"+nav(chosen,'Trace industry impact →',view='industry',factor='',capability='')+nav(chosen,'Inspect enterprise →',view='enterprise',factor='',capability='')+"<a href='"+e(url(chosen,'/macro/evidence')+'#macro-evidence',quote=True)+"'>Primary evidence & full dossier →</a></div>"
    if chosen.view=='enterprise':
        if spec['candidates']:
            body+="<h3>Existing research hypotheses</h3><p class='mi-compact'>UK reference group research, not a French mandate. Analytical capability association only; no statutory project or qualified deal.</p>"
            for row in spec['candidates']:
                body+="<a href='"+e(row['url'],quote=True)+"'>"+e(row['title'])+' →</a>'
        else:body+="<p class='mi-unknown'>No supported market-scoped hypothesis mapping. Verify the entity and need before proposing an opportunity.</p>"
        body+="<p><a href='/enterprises/"+spec['enterprise']['slug']+"'>Existing Enterprise Twin →</a></p>"
    body+="<p><a href='#macro-visual'>← Back to visual</a></p>"
    return body+'</aside>'


def evidence_report(chosen,spec,data):
    force=spec['force'];sources=[s for s in data['sources'] if not force or s['id'] in force['source_ids']]
    body="<section class='mi-report' id='macro-evidence'><h2>Full research & evidence</h2><p>Read-only candidate intelligence. Reviewed primary excerpts support their own scope, not enterprise applicability, buyer demand or legal advice.</p>"
    if not force:body+="<p>Selected category is unresearched. This is the cross-category source register, not evidence of coverage for that category.</p>"
    for source in sources:
        observation=next(o for o in data['observations'] if o['source_id']==source['id'])
        from .understanding import source_quality
        quality=source_quality(source,data['as_of'])
        body+=f"<article id='{e(source['id'])}'><p class='mi-kicker'>{e(source['publisher'])} · {e(source['id'])}</p><h3>{e(source['title'])}</h3><blockquote>{e(observation['segment']['content'])}</blockquote><p>Locator: {e(observation['segment']['section_heading'])}</p><p>Published: {e(source['publication_date'] or 'Unknown')} · Retrieved: {e(source['retrieved_at'])}</p><p>Scope / period: {e(source['reporting_period'])}</p><p>{e(source['review_notes'])}</p><p>Existing freshness review: {e(quality['currentness'])}. Review date is not the effective or publication date.</p><a href='{e(source['url'],quote=True)}'>Open official primary source →</a><p class='mi-compact'>Claim {e(observation['candidate']['claim_id'])} · excerpt SHA-256 {e(source['text_sha256'])} · original checksum unavailable. No accepted observation.</p></article>"
    if spec.get('enterprise_trace'):body+=trace_dossier(chosen,spec['enterprise_trace'])
    body+="<h3>Traceable relationship projection</h3><p>Every edge below retains its market, period, status and evidence references. Enterprise applicability remains Unknown.</p><pre>"+e(__import__('json').dumps(spec['edges'],ensure_ascii=False,indent=2))+"</pre><h3>Open research actions</h3><ul><li>Resolve exact legal entity and register identity without inheriting parent duties.</li><li>Check live instrument and French transposition text; retain contrary evidence and supersession lineage.</li><li>Obtain customer-verified need, owner, buying route and delivery gap through the existing qualification process.</li></ul></section>"
    return body


def render(query='',headers=None,evidence=False):
    chosen=m.selection(query);data=m.load_context();spec=m.context_spec(chosen,data)
    stage=atlas(chosen,data) if chosen.view=='atlas' else industry_visual(chosen,spec)
    label={'global':'Global · UK/France reference coverage','GB':'United Kingdom','FR':'France'}[chosen.market]
    stepnav="<nav class='mi-steps' aria-label='Intelligence journey'>"+''.join("<a data-macro-nav href='"+e(url(chosen,view=key,factor='',capability=''),quote=True)+"'"+(" aria-current='step'" if chosen.view==key else '')+'>'+title+'</a>' for key,title in [('atlas','01 / Systemic force'),('industry','02 / Industry PESTLE'),('enterprise','03 / Enterprise & hypotheses')])+"</nav>"
    intro="<header class='mi-intro' id='content'><div><span class='mi-kicker'>FLORA / Global & Macro Intelligence</span><h1>See the forces.<br>Follow the evidence.</h1><p>"+e(label)+' · research cut-off '+data['as_of']+"</p></div><a class='mi-pill' href='"+e(url(chosen,'/macro/evidence')+'#macro-evidence',quote=True)+"'>Evidence first →</a></header>"
    quick="<nav class='mi-country' aria-label='Quick market context'>"+''.join(nav(chosen,label,market=value) for value,label in [('global','Global'),('GB','UK'),('FR','France')])+"<a class='mi-pill' href='#macro-controls'>Refine context ↓</a></nav>"
    intro=intro.replace('</header>',quick+'</header>')
    body="<style>"+STYLE+"</style><div class='mi' id='macro-root'>"+intro+controls(chosen)+stepnav+"<div class='mi-grid'><section class='mi-stage' id='macro-visual' aria-label='Interactive intelligence visual'>"+stage+"<div class='mi-legend'>Green / selected context · gold / interpreted pressure · dotted / unresolved. Schematic layout, not impact severity or verified enterprise dependency.</div></section>"+inspector(chosen,spec,data)+"</div><p class='mi-footer'>"+('France reuses the same industry structure; French market facts and enterprise footprint remain incomplete. ' if chosen.market=='FR' else '')+"Seller match is not demand. Location is not legal applicability. No Pipeline record is created.</p><div class='mi-controls'><button type='button' data-macro-print='executive'>Print executive view</button><a class='mi-pill' href='"+e(url(chosen,'/macro/evidence')+'#macro-evidence',quote=True)+"'>Open full evidence / print appendix →</a></div>"
    if evidence:body+=evidence_report(chosen,spec,data)+"<p>"+nav(chosen,'← Return to selected visual context')+"</p><div class='mi-controls'><button type='button' data-macro-print='appendix'>Print full evidence</button></div>"
    body+="<p class='mi-print-only'>Primary sources and exact passages: "+''.join("<br>"+e(s['url']) for s in data['sources'] if not spec['force'] or s['id'] in spec['force']['source_ids'])+"</p></div><script>"+SCRIPT+'</script>'
    return page('FLORA Global & Macro Intelligence',body,headers,'industries','/macro')
