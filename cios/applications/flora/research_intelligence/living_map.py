"""Illustrated Living Industry Map; facts and topology stay in derived specs."""
from html import escape as e
import re
from textwrap import wrap
from .visual_intelligence import _icon,_sources,_badge,STYLE as EVIDENCE_STYLE
from .visual_templates import text

STYLE='''
.lm-page-head h1{font-size:2.5rem;margin:8px 0 15px;color:#174d3f}.lm{--lm-ink:#173f37;--lm-line:#b5c7b8;color:var(--lm-ink);margin:22px 0}.lm *{box-sizing:border-box}.lm-frame{border:1px solid #bdcfc1;border-radius:26px;overflow:hidden;background:#fffdf6}.lm-intro{display:flex;justify-content:space-between;gap:24px;padding:28px 30px 18px}.lm-intro h2{font-size:clamp(2rem,3.5vw,3rem);line-height:1.05;margin:8px 0 14px}.lm-intro p{max-width:700px;line-height:1.55;color:#52685c}.lm-kicker{font-size:.72rem;letter-spacing:.13em;text-transform:uppercase;font-weight:800;color:#5a6e5e}.lm-scale{min-width:255px;max-width:360px;border-left:1px solid #c4d0c1;padding-left:24px}.lm-scale strong{display:block;font-size:2.3rem;margin:9px 0;line-height:1.1}.lm-scale small{display:block;font-size:.76rem;line-height:1.5;color:#526456}.lm-scale a{font-size:.8rem}.lm-toolbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:13px 26px;border-top:1px solid #d7e0d0;border-bottom:1px solid #d7e0d0}.lm-toolbar a,.lm-toolbar button{font:inherit;font-size:.84rem;padding:9px 13px;background:#fffdf7;color:#194f40;border:1px solid #b5c7b5;border-radius:22px;min-height:40px;text-decoration:none}.lm-toolbar [aria-current]{background:#174d3f;color:#fff}.lm-toolbar .lm-zoom{margin-left:auto}.lm-pan{overflow:auto;max-width:100%;background:#f6f3e7}.lm-pan svg{display:block;width:100%;min-width:1100px;height:auto}.lm-pan[data-zoom=detail] svg{width:145%;min-width:1440px}.lm-map-node{color:#224f41;text-decoration:none}.lm-map-node .lm-ground{fill:#d9e6d3;stroke:#b7cbb4;stroke-width:1}.lm-map-node:hover .lm-ground,.lm-map-node[aria-current] .lm-ground{stroke:#2b6553;stroke-width:4;fill:#c7ddc4}.lm-map-node[data-ai=true] .lm-lens{stroke:#796087;stroke-width:3;stroke-dasharray:6 5;fill:#eee6ef;fill-opacity:.6}.lm-map-node[data-regulation=true] .lm-lens{stroke:#aa7840;stroke-width:3;stroke-dasharray:8 5;fill:#f4e5c9;fill-opacity:.5}.lm-lens{fill:none;stroke:none}.lm-map-node[data-conflict=true] .lm-ground{stroke:#ac583b;stroke-width:3}.lm-participant text{font-weight:650;paint-order:stroke;stroke:#f6f3e7;stroke-width:3px;stroke-linejoin:round}.lm-map-node text{paint-order:stroke;stroke:#f6f3e7;stroke-width:4px;stroke-linejoin:round}.lm-participant:hover text,.lm-participant[aria-current] text{text-decoration:underline;fill:#6e4a80}.lm-flow{stroke:#729d9f;stroke-width:3;stroke-dasharray:8 6;fill:none}.lm-flow-link:hover .lm-flow,.lm-flow-link[aria-current] .lm-flow{stroke:#315f68;stroke-width:5}.lm-flow-risk{stroke:#b89152}.lm-flow-information{stroke:#a390b0}.lm a:focus-visible,.lm button:focus-visible,.lm-pan:focus-visible,.lm summary:focus-visible{outline:3px solid #855622;outline-offset:3px}.lm-map-node:focus-visible .lm-ground{stroke:#855622;stroke-width:5}.lm-note{padding:13px 26px;color:#586b5e;font-size:.81rem;line-height:1.55;margin:0}.lm-legend{display:flex;gap:10px 20px;flex-wrap:wrap;padding:15px 26px;border-top:1px solid #d0ddce;font-size:.78rem}.lm-legend b{font-weight:650}.lm-live{font-size:.85rem;padding:14px 25px;border-top:1px solid #d1decf;color:#3c5b48}.lm-inspector{margin:20px 0}.lm-panel{scroll-margin-top:24px}.lm-panel summary{font-size:1.2rem}.lm-panel[open]{border:2px solid #80a48c;background:#fffdf7}.lm-panel p,.lm-panel li{line-height:1.6}.lm-context{display:grid;grid-template-columns:1fr 1fr;gap:24px}.lm-pill{display:inline-block;border:1px solid #c1cfbd;border-radius:17px;padding:7px 11px;text-decoration:none;font-size:.84rem;margin:4px}.lm-warning{border-left:3px solid #b58c51;padding:10px 15px;background:#f7f0e1;font-size:.87rem}.lm[data-ready=true] .lm-panel:not([open]){display:none}.lm-text-list{display:flex;gap:7px;flex-wrap:wrap}.lm-pressures{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:15px 0}.lm-pressure{padding:16px;border:1px solid #d2dacb;border-radius:13px}.lm-pressure h3{font-size:1rem}.lm-support{margin:20px 0}.lm-snapshot{font-size:.8rem;overflow-wrap:anywhere}.lm [hidden]{display:none!important}.lm-compare{font-size:.83rem;color:#5a6d5e}.lm-flow-caption{font-size:.8rem}.lm-print-note{display:none}@media(max-width:850px){.lm-intro{padding:22px;gap:18px}.lm-scale{min-width:230px;max-width:260px;padding-left:18px}.lm-scale strong{font-size:2rem}.lm-pressures{grid-template-columns:1fr 1fr}}@media(max-width:600px){.lm-intro{display:block}.lm-scale{max-width:none;border-left:0;border-top:1px solid #ccd8c5;padding:16px 0 0}.lm-context,.lm-pressures{grid-template-columns:1fr}.lm-pan{display:none}.lm-toolbar .lm-zoom{display:none}.lm .lm-keyboard>.lm-text-list{display:flex!important}.lm .lm-keyboard summary{font-weight:800}.lm-intro h2{font-size:2.15rem}}@media(prefers-reduced-motion:reduce){.lm *{scroll-behavior:auto!important;transition:none!important}}@media print{@page{size:A3 portrait;margin:12mm}.topbar,.lm-page-head,.ux-breadcrumb,.ux-tabs,.profile-control,.lm-toolbar,.lm-keyboard,.lm-live{display:none!important}.lm{margin:0}.lm-frame{break-inside:avoid;box-shadow:none}.lm-pan{display:block!important;overflow:visible!important}.lm-pan svg,.lm-pan[data-zoom=detail] svg{width:100%!important;min-width:0!important}.lm-intro{padding:12px 20px}.lm-intro h2{font-size:25pt}.lm-note,.lm-legend{font-size:9pt;padding:8px 20px}.lm[data-ready=true] .lm-panel{display:block!important;break-inside:avoid}.lm-panel{border:1px solid #aaa!important}.lm-inspector{break-before:page}.lm-print-note{display:block;font-size:10pt}.lm-context{grid-template-columns:1fr 1fr}details{break-inside:avoid}.lm-support{break-before:page}.shell{max-width:none!important;padding:0!important;margin:0!important}body{background:white!important}}
'''

SCRIPT='''
(function(){document.querySelectorAll('.lm[data-ready=false]').forEach(function(root){
 root.dataset.ready='true';var panels=root.querySelectorAll('.lm-panel');
 root.addEventListener('click',function(event){var a=event.target.closest('[data-lm-target]');if(!a||!root.contains(a))return;var panel=document.getElementById(a.dataset.lmTarget);if(!panel)return;
 panels.forEach(function(p){p.open=p===panel});root.querySelectorAll('[data-lm-target]').forEach(function(n){if(n.dataset.lmTarget===a.dataset.lmTarget)n.setAttribute('aria-current','location');else n.removeAttribute('aria-current')});
 root.querySelector('.lm-live').textContent='Selected '+a.dataset.label+'. Inspect the role, scoped evidence and what remains unknown below.';
 requestAnimationFrame(function(){panel.querySelector('summary').focus({preventScroll:true})});
 });
 var zoom=root.querySelector('.lm-zoom');zoom.hidden=false;zoom.addEventListener('click',function(){var scene=root.querySelector('.lm-pan'),detail=scene.dataset.zoom!=='detail';scene.dataset.zoom=detail?'detail':'fit';zoom.textContent=detail?'Fit whole system':'Inspect at larger scale';zoom.setAttribute('aria-pressed',String(detail))});
 var states=[];window.addEventListener('beforeprint',function(){states=Array.from(document.querySelectorAll('details')).map(function(d){var s=[d,d.open];d.open=true;return s})});window.addEventListener('afterprint',function(){states.forEach(function(s){s[0].open=s[1]});states=[]});
});})();
'''


def target(spec,n):return 'lm-'+spec['domain']+'-'+re.sub(r'[^A-Za-z0-9_-]','-',n['id'])
def pick(spec,n,body,cls='lm-map-node',extra=''):
    name=e(n['label'],quote=True);tid=target(spec,n)
    return f"<a class='{cls}' href='#{tid}' data-lm-target='{tid}' data-label='{name}' aria-label='{name} — inspect role, evidence and Unknowns' {extra}><title>{e(n['label'])} · {e(n.get('state','Conceptual industry flow'))}</title>{body}</a>"


def _person(x,y):
    return f"<g transform='translate({x} {y})' stroke='#47735d' stroke-width='2'><circle cy='-15' r='7' fill='#dbc5a0'/><path d='M-9-3H9L12 27H-12Z' fill='#668874'/><path d='M-6 28V43 M6 28V43' fill='none'/></g>"


def _building(x,y,w=120,h=80,color='#e5dfc4',roof='#f4edda'):
    out=f"<g transform='translate({x} {y})' stroke='#799c86' stroke-width='1.5'><path d='M{-w/2} 0 0 24 {w/2} 0 0-24Z' fill='{roof}'/><path d='M{-w/2} 0 0 24V{24+h}L{-w/2} {h}Z' fill='{color}'/><path d='M0 24 {w/2} 0V{h}L0 {24+h}Z' fill='#bbd0b7'/>"
    for row in range(2):
        for col in range(3):
            xx=-w/2+12+col*14;yy=22+row*24+col*6
            out+=f"<path d='M{xx} {yy}v12m4-10v10' stroke='#628a73'/>"
    return out+'</g>'


def _asset(domain,n):
    x,y=n['position'];icon=n['illustration'];a=f"<ellipse class='lm-lens' cx='{x}' cy='{y+17}' rx='145' ry='112'/><ellipse class='lm-ground' cx='{x}' cy='{y+50}' rx='105' ry='44'/>"
    if icon=='people':
        if domain=='banking':a+=_building(x-25,y-45,92,55)+'<g stroke="#73947c" fill="#e7d8b8">'+f"<path d='M{x-91} {y-15}l34-35 34 35v44h-68Z'/></g>"
        else:a+=f"<path d='M{x-70} {y+25}H{x+68}' stroke='#8eaa8e' stroke-width='5'/>"
        a+=_person(x-57,y+4)+_person(x+26,y-8)+_person(x+62,y+13)
    elif icon=='plane':
        a+=_building(x-20,y-28,130,42)
        a+=f"<g transform='translate({x+5} {y-64}) rotate(62 38 38)' color='#426c5b'>"+_icon('plane',0,0,2.4)+'</g>'+_person(x-72,y+4)
    elif icon=='terminal':
        a+=_building(x-4,y-53,185,62)
        a+=f"<path d='M{x-115} {y+72}H{x+119}' stroke='#769285' stroke-width='15'/><path d='M{x-110} {y+72}H{x+110}' stroke='#fff9e8' stroke-dasharray='16 10' stroke-width='2'/>"+_icon('tower',x+61,y-67,1.3)
    elif icon=='wrench':
        a+=f"<path d='M{x-85} {y+30}V{y-42}Q{x} {y-113} {x+85} {y-42}V{y+30}Z' fill='#d5dfcc' stroke='#7b9b82' stroke-width='2'/><path d='M{x-63} {y+28}V{y-30}Q{x} {y-78} {x+63} {y-30}V{y+28}' fill='#b7cbb3'/>"+_icon('plane',x-35,y-19,1.8)+_icon('wrench',x+55,y+12,1.15)
    elif icon=='leaf':
        a+=f"<g stroke='#779580' fill='#ddd8b8'><path d='M{x-65} {y-40}a24 9 0 0 1 48 0v77a24 9 0 0 1-48 0Z'/><ellipse cx='{x-41}' cy='{y-40}' rx='24' ry='9'/><path d='M{x+5} {y+35}V{y-70}l35 16v50l-35-16M{x+5} {y-70}l-35 16v50l35-16'/></g>"+_icon('leaf',x+37,y,1.4)
    elif icon in ('vault','home','bank'):
        a+=_building(x,y-54,150,80)
        a+=f"<path d='M{x-84} {y-52}l84-43 84 43-84 19Z' fill='#f0e5ca' stroke='#74937b' stroke-width='2'/>"+_icon('bank' if icon=='vault' else icon,x-20,y-25,1.4)
        if icon=='home':a+=_building(x+67,y+4,50,30)
    elif icon=='server':
        a+=_building(x-28,y-44,115,67)+_building(x+50,y+2,70,48)+_icon('server',x-57,y-17,1.5)
    elif icon=='transfer':
        a+=_building(x,y-34,145,56)+_icon('transfer',x-29,y-14,1.8)
        a+=f"<path d='M{x-105} {y+57}h49m110-30h57' stroke='#75a7a8' stroke-width='5'/>"
    else:
        a+=_building(x-5,y-41,117,62)+_icon(icon,x-28,y-28,1.8)
    a+=text(x,y+123,n['label'],width=31,size=18,anchor='middle')
    if n['conflict_ids']:a+=text(x,y+151,'Scope disputed · inspect evidence',width=45,size=12,anchor='middle',color='#975136')
    return a


def _scene(spec,lens):
    domain=spec['domain'];positions={n['id']:n['position'] for n in spec['map_nodes']}
    ns='lm-'+domain
    out=f"<svg viewBox='0 0 1440 1080' role='group' aria-labelledby='{ns}-title {ns}-desc'><title id='{ns}-title'>{e(spec['title'])}</title><desc id='{ns}-desc'>Illustrated conceptual industry system. Select activities, participants or dashed flows; text navigation follows. Spatial roles and artwork size are not market shares or verified contracts.</desc><defs><marker id='{ns}-arrow' markerWidth='7' markerHeight='7' refX='6' refY='3.5' orient='auto'><path d='M0 0 6 3.5 0 7' fill='none' stroke='#668e93' stroke-width='1.5'/></marker></defs><rect width='1440' height='1080' fill='#f6f3e6'/>"
    if domain=='banking':
        out+="<g aria-hidden='true'><path d='M0 385Q240 340 480 410T960 380T1440 420V515Q1160 460 920 485T450 475T0 460Z' fill='#dce9e3'/><path d='M0 423Q240 378 480 448T960 418T1440 458' fill='none' stroke='#adc8bc' stroke-width='2'/><path d='M90 980 1420 605M30 315 1310 40' stroke='#e7e3cf' stroke-width='33'/><path d='M120 1000 1440 630' stroke='#b8c9af' stroke-dasharray='5 10' fill='none'/></g>"
    else:
        out+="<g aria-hidden='true'><path d='M30 440Q490 255 1410 340L1380 590Q720 430 60 620Z' fill='#e1e8d6'/><path d='M480 380 1360 370' stroke='#b4c0ad' stroke-width='36'/><path d='M500 380 1350 370' stroke='#fff9e8' stroke-dasharray='28 18' stroke-width='3'/><path d='M630 350Q900 20 1370 90' stroke='#c5b28d' stroke-width='2' stroke-dasharray='4 12' fill='none'/></g>"
        out+=f"<g aria-hidden='true' transform='translate(1120 68) rotate(68 40 40)' color='#72937b'>"+_icon('plane',0,0,2.2)+'</g>'
    out+=text(55,55,'CUSTOMERS / DEMAND',size=13,color='#71846c')+text(570,55,'OPERATING ACTIVITIES',size=13,color='#71846c')+text(1070,55,'RESOURCES / CONTROLS',size=13,color='#71846c')
    for f in spec['flows']:
        x,y=positions[f['source']];xx,yy=positions[f['target']]
        path=f'M{x} {y+36}Q{(x+xx)/2} {(y+yy)/2-65} {xx} {yy+36}'
        kind=f['kind'].lower();body=f"<path d='{path}' stroke='transparent' stroke-width='20' fill='none'/><path class='lm-flow lm-flow-{kind}' d='{path}' marker-end='url(#{ns}-arrow)'/>"
        body+=text((x+xx)/2,(y+yy)/2-39,f['kind'],width=30,size=13,anchor='middle',color='#56777a',bold=False)
        out+=pick(spec,f,body,'lm-flow-link')
    for n in spec['map_nodes']:
        attrs=f"data-ai='{str(lens=='ai-disruption' and bool(n['ai_scenarios'])).lower()}' data-regulation='{str(lens=='regulation' and n['regulatory']).lower()}' data-conflict='{str(bool(n['conflict_ids'])).lower()}'"
        out+=pick(spec,n,_asset(domain,n),extra=attrs)
    for n in spec['map_nodes']:
        actors=n['participants']
        for i,a in enumerate(actors):
            x,y=n['position'];x=max(25,x-155+(i%2)*168);y=y+178+(i//2)*28
            if a['position_override']:x,y=a['position_override']
            short=a['label'];lines=wrap(short,width=21,break_long_words=True)
            label=lines[0]+('…' if len(lines)>1 else '')
            mark=f"<circle cx='{x}' cy='{y-5}' r='3' fill='#456f59'/>" if a['state']!='Unknown' else f"<path d='M{x-4} {y-5}l4-4 4 4-4 4Z' fill='none' stroke='#967342'/>"
            if a['documented_relationships']:mark=f"<rect x='{x-4}' y='{y-9}' width='7' height='7' fill='#385f55'><title>Dated reference-company relationship; current contract unknown</title></rect>"
            out+=pick(spec,a,mark+text(x+9,y,label,width=100,size=13,bold=False),'lm-participant')
    out+=text(55,1038,'Dashed arrows = conceptual flows. Locations = roles. Labels = equal-weight navigation, not market rank.',width=150,size=13,bold=False,color='#526b5b')
    return out+'</svg>'


def _links(items):return ''.join(f"<a class='lm-pill' href='{e(a['url'],quote=True)}'>{e(a['label'])}</a>" for a in items) or '<p>Not mapped in current research.</p>'


def _panel(spec,n,kind='activity'):
    tid=target(spec,n);warning=n.get('limitations',n.get('association_state','Conceptual explanatory flow; no enterprise-specific topology or contract is asserted.'))
    body=f"<details class='lm-panel' id='{tid}'><summary>{e(n['label'])}</summary>{_badge(n.get('state','Conceptual industry flow'))}<p>{e(n.get('purpose',n['label']))}</p><p class='lm-warning'>{e(warning)}</p>"
    if kind=='activity':
        body+=f"<div class='lm-context'><div><h3>Role, dependencies & participants</h3>"
        for a in n['participants']:body+=pick(spec,a,f"{e(a['label'])} →",'lm-pill')
        body+='<h4>Conceptual flows</h4>'+''.join(pick(spec,f,e(f['label']),'lm-pill') for f in n['flows'])
        body+='<h4>Capabilities & programmes</h4>'+_links(n['capability_links']+n['programme_links'])+'</div><div><h3>Cost, risk & transformation</h3><p>'+e(n['pressure'])+'</p>'
        for s in n['ai_scenarios']:body+=f"<p>{_badge('Analytical scenario — not a proven threat')} {e(s['purpose'])}</p><p>Structural defences: {e(s['defence'])}</p>"
        for t in n['timeline_events']:
            url=spec['timeline_url']+'#vi-strategic-timeline-'+spec['domain']+'-'+t['id']
            body+=f"<p><a href='{e(url,quote=True)}'>{e(t['label'])} · {e(t['date_label'])} → timeline</a><br><small>{e(t['applicability'])}</small></p>"
        body+='</div></div>'
        for c in spec['conflicts']:
            if c['id'] in n['conflict_ids']:body+=f"<p class='lm-warning'>Challenged / scope unresolved: {e(c['status'])}. {e(c['treatment'])}</p>"
        body+='<h3>Scoped evidence — examples are not sector-wide proof</h3>'+_sources(n['evidence'])
    elif kind=='actor':
        for edge in n['documented_relationships']:
            body+=f"<h3>Documented reference-company relationship</h3><p>{e(edge['state'])} · {e(edge['period'])} · {e(spec['enterprise']['label'])}</p><p>{e(edge['reason'])}</p><p>Still unknown: {e(', '.join(edge['missing_evidence']))}</p>"
            for claim in edge['claim_ids']:body+=f"<a class='lm-pill' href='{spec['enterprise']['url']}/understanding#claim-{e(claim,quote=True)}'>Inspect relationship evidence →</a>"
        body+=f"<p><a href='{e(n['url'],quote=True)}'>Open enterprise / underlying research →</a></p>"+_sources(n['evidence'])
    else:
        for endpoint in (n['source'],n['target']):
            a=next(a for a in spec['map_nodes'] if a['id']==endpoint);body+=pick(spec,a,e(a['label']),'lm-pill')
        body+="<p>No verified causal or contractual claim follows from this arrow. Inspect endpoint research for source-specific facts and remaining gaps.</p>"
    return body+'</details>'


def render_living_map(spec,lens='overview'):
    if spec.get('extension')!='flora-living-map-v2' or lens not in ('overview','ai-disruption','regulation'):raise ValueError('Unknown Living Industry Map')
    m=spec['metrics'][0] if spec['metrics'] else None
    scale="<strong>Not established</strong><small>No supported industry measurement at this snapshot.</small>"
    if m:
        scale=f"<span class='lm-kicker'>{e(m['label'])}</span><strong>{e(str(m['value'])) if m['value'] is not None else 'Not established'}</strong><small>{e(m['unit'] or m['limitation'])}<br>{e(m['scope_note'])}<br>{e(m['period'] or 'Period not established')}</small>"+(''.join(f"<a href='{e(p['url'],quote=True)}'>Inspect measurement & source →</a>" for p in m['evidence'][:1]))
    root=spec['industry']['url']
    toolbar=''.join(f"<a href='{root}?lens={k}' {'aria-current=page' if k==lens else ''}>{label}</a>" for k,label in [('overview','Operating system'),('ai-disruption','AI disruption'),('regulation','Regulation & resilience')])
    body=f"<style>{EVIDENCE_STYLE}{STYLE}</style><section class='lm' data-ready='false' data-visual-family='industry-signature' data-living-map='2' data-snapshot='{e(spec['snapshot_digest'],quote=True)}'><div class='lm-frame'><header class='lm-intro'><div><span class='lm-kicker'>01 / Understand · {e(spec['industry']['label'])}</span><h2>{e(spec['title'])}</h2><p>{e(spec['summary'])}</p></div><aside class='lm-scale'>{scale}</aside></header><nav class='lm-toolbar' aria-label='Living industry layers'>{toolbar}<button class='lm-zoom' type='button' aria-pressed='false' hidden>Inspect at larger scale</button></nav>"
    body+=f"<div class='lm-pan' tabindex='0' data-zoom='fit' aria-label='Pan the industry system; equivalent text navigation follows'>{_scene(spec,lens)}</div>"
    body+="<div class='lm-legend'><b>Dashed → conceptual money / passenger / service flow</b><span>◇ Unknown provider / scope</span><span>■ Dated reference-company relationship — inspect period</span><span>Rust outline: challenged finding</span><span>Plum: AI scenario</span><span>Amber: regulatory exposure to investigate</span></div>"
    body+=f"<p class='lm-note'>{e(spec['weighting'])} {e(spec['scale_gaps'])}</p>"
    if lens!='overview':body+="<p class='lm-note'>Highlighted activities are presentation mappings of potential exposure, not proven harm, adoption, measured impact or enterprise failure. Company disclosures retain their own entity and date.</p>"
    body+="<p class='lm-live' aria-live='polite'>02 / Explore — select an illustrated activity, participant or dashed flow to inspect its intelligence.</p></div>"
    body+="<details class='lm-keyboard'><summary>Equivalent text navigation · activities, participants & flows</summary><div class='lm-text-list'>"+''.join(pick(spec,n,e(n['label']),'lm-pill') for n in spec['map_nodes']+spec['participants']+spec['flows'])+'</div></details>'
    body+="<div class='lm-inspector' aria-label='Contextual intelligence inspection'><p class='lm-print-note'>Print includes all contextual panels; source dates and conceptual/unknown status are retained.</p>"+''.join(_panel(spec,n) for n in spec['map_nodes'])+''.join(_panel(spec,n,'actor') for n in spec['participants'])+''.join(_panel(spec,n,'flow') for n in spec['flows'])+'</div>'
    body+=f"<p><a href='{e(spec['enterprise']['url'],quote=True)}'>Explore {e(spec['enterprise']['label'])} Enterprise Twin →</a> · <a href='{e(spec['timeline_url'],quote=True)}'>Strategic timeline →</a></p>"
    body+=f"<details class='lm-snapshot'><summary>Research scope, source limitations & reproducible snapshot</summary><p>{e(spec['scale_gaps'])}</p><p>As of {e(spec['as_of'])}; input source periods differ. Snapshot {e(spec['snapshot_digest'])}. Candidate research remains unaccepted; no Pipeline qualification.</p></details><script>{SCRIPT}</script></section>"
    return body
