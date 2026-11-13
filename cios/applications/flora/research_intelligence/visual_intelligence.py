"""Lightweight editorial SVG layers over the shared visual specification extension.

Artwork is conceptual. Every company label, metric, date and evidence destination
comes from the generated spec, never from a bitmap or facts embedded in drawing code.
"""
from .. import design_system as ds
from html import escape as e
import re
from textwrap import wrap
from .visual_templates import text

STYLE="""
.vi{--vi-ink:#173f37;--vi-line:#b9cabe;--vi-paper:#fffdf7;--vi-plum:#695178;color:var(--vi-ink);margin:20px 0 32px}.vi *{box-sizing:border-box}.vi-head{display:flex;justify-content:space-between;align-items:start;gap:20px;padding:26px 30px 12px}.vi-kicker{font-size:.72rem;letter-spacing:.13em;text-transform:uppercase;font-weight:800;color:#526c60}.vi h2{font-size:clamp(1.7rem,2.7vw,2.5rem);line-height:1.13;margin:8px 0 14px;max-width:850px}.vi-head p{max-width:740px;line-height:1.6;color:#53675d}.vi-frame{border:1px solid #c6d3c8;border-radius:24px;overflow:hidden;background:var(--vi-paper);box-shadow:0 12px 40px #173f3708}.vi-scene{overflow:auto;max-width:100%;background:#f7f5ec}.vi-scene svg{display:block;width:100%;min-width:960px;height:auto}.vi-scene a{cursor:pointer;outline-offset:-3px}.vi-node .vi-card{transition:stroke-width .12s,fill .12s}.vi-node:hover .vi-card,.vi-node[aria-current] .vi-card{fill:#e0ebdf;stroke:#164d3f;stroke-width:3}.vi a:focus-visible,.vi select:focus-visible,.vi-scene:focus-visible{outline:3px solid #885520;outline-offset:3px}.vi-node:focus-visible .vi-card{stroke:#885520;stroke-width:4}.vi-node[data-state='Scenario'] .vi-card{stroke:#695178;stroke-dasharray:5 4}.vi-node[data-state='Unknown'] .vi-card{stroke-dasharray:2 4}.vi-node[data-state^='Challenged'] .vi-card{stroke:#a44e31;stroke-width:3}.vi-note{font-size:.84rem;color:#56685d;padding:12px 28px;line-height:1.6}.vi-legend{display:flex;flex-wrap:wrap;gap:10px 20px;padding:14px 28px;font-size:.8rem;border-top:1px solid #d8e1d5}.vi-legend span{display:flex;align-items:center;gap:7px}.vi-mark{width:11px;height:11px;background:#25574a;border-radius:2px;display:inline-block}.vi-mark.interpret{background:#dfc294}.vi-mark.unknown{background:transparent;border:2px dotted #806126;transform:rotate(45deg)}.vi-mark.scenario{background:#d9cee0;border:1px dashed #695178}.vi-mark.conflict{background:linear-gradient(45deg,#a44e31 45%,#fff 45%,#fff 55%,#a44e31 55%)}.vi-text-nav{display:flex;gap:8px;flex-wrap:wrap;padding:12px 28px 24px}.vi-text-nav a,.vi-link-pill{border:1px solid #c6d3c8;border-radius:20px;padding:8px 12px;font-size:.84rem;text-decoration:none;min-height:40px;display:inline-flex;align-items:center;background:#fffdf7}.vi-text-nav a[aria-current]{background:#194f40;color:white}.vi-metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:18px 0}.vi-metric{padding:22px 25px;border:1px solid #c9d5c9;border-radius:18px;background:#fffdf7}.vi-metric strong{display:block;font-size:2.15rem;line-height:1.2;margin:10px 0;color:#194f40}.vi-metric p{font-size:.83rem;line-height:1.5;margin:5px 0;color:#52645a}.vi-badge{display:inline-block;border:1px solid #bccbbf;padding:4px 8px;border-radius:5px;font-size:.73rem;font-weight:750}.vi-badge.unknown{background:#f4ebd9;border-style:dotted}.vi-badge.scenario{background:#eee7f1;border-style:dashed;color:#513c61}.vi-badge.conflict{background:#f9e9df;color:#7f3e2b}.vi-level{display:flex;gap:14px;flex-wrap:wrap;margin:20px 0;font-size:.84rem}.vi-level strong{font-weight:800}.vi-detail{scroll-margin-top:24px}.vi-details details[open]{border-color:#6c9380;background:#fffdf7}.vi-detail h3{margin:8px 0}.vi-detail .vi-columns{display:grid;grid-template-columns:1fr 1fr;gap:25px}.vi-detail p,.vi-detail li{line-height:1.6}.vi-detail li{margin:8px 0}.vi-source{border-left:3px solid #c5b48b;padding-left:16px;margin:18px 0}.vi-source small{color:#596c60}.vi-empty{padding:24px;border:1px dashed #c0cdbf;border-radius:16px;color:#586858}.vi-pressure-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:16px 0}.vi-pressure{border:1px solid #d0dbcd;border-radius:14px;background:#f8f5eb;padding:16px}.vi-pressure h3{font-size:1rem;margin:0 0 8px}.vi-pressure p{font-size:.85rem;line-height:1.5}.vi-scenario-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:16px 0}.vi-scenario{border:1px dashed #8e7898;border-radius:18px;padding:24px;background:#f4eff5}.vi-scenario h3{font-size:1.2rem}.vi-scenario p{line-height:1.55;font-size:.92rem}.vi-timeline-controls{display:flex;flex-wrap:wrap;gap:16px;align-items:end;padding:15px 28px;border-top:1px solid #d5dfd1}.vi-timeline-controls label{font-size:.83rem;font-weight:750;display:grid;gap:7px}.vi-timeline-controls select{min-height:42px;border:1px solid #aebfae;border-radius:9px;background:#fffdf7;padding:8px 32px 8px 10px;color:#173f37;font:inherit;max-width:260px}.vi-timeline-scroll{overflow:auto;padding:12px 20px;max-width:100%}.vi-time-axis,.vi-lane-grid{display:grid;grid-template-columns:145px repeat(var(--vi-years),minmax(140px,1fr));min-width:calc(145px + var(--vi-years)*140px);gap:6px}.vi-time-axis{color:#5a6d60;font-size:.8rem;font-weight:800;padding-bottom:12px}.vi-lane{border-top:1px solid #d4dfd0;padding:12px 0}.vi-lane-name{font-size:.84rem;font-weight:800;align-self:center}.vi-time-event{border:1px solid #bdcdbf;background:#e7eee2;border-radius:10px;padding:10px;text-decoration:none;min-height:82px;display:block;font-size:.8rem;line-height:1.4;align-self:start;min-width:0;overflow-wrap:anywhere}.vi-time-event strong{display:block}.vi-time-event small{display:block;margin-top:6px;color:#526557}.vi-time-event[data-kind='announced commitment']{border-style:dashed;background:#f1e9d8}.vi-time-event[data-kind='scenario']{border-color:#857090;background:#eee7f2;border-style:dashed}.vi-undated{padding:16px 28px;background:#f7f0e3;border-top:1px solid #d4c8ae}.vi-undated-links{display:flex;flex-wrap:wrap;gap:10px}.vi-undated a{border:1px dotted #8c713e;border-radius:9px;padding:12px;display:block;text-decoration:none;max-width:340px;font-size:.86rem}.vi-page-head{margin:20px 0}.vi-page-head h1{font-size:clamp(2.3rem,4.2vw,3.5rem);line-height:1.08;margin:12px 0;color:#174d3f}.vi-page-head p{max-width:850px;color:#52695b;line-height:1.6}.vi-snapshot{overflow-wrap:anywhere;font-size:.82rem}.vi-live{font-size:.8rem;margin:0;padding:0 28px 16px;color:#5b6b60}.vi-related .vi-card{stroke:#9e7e4b;stroke-dasharray:4 3}.vi[hidden],.vi [hidden]{display:none!important}@media(max-width:800px){.vi-head{padding:22px}.vi-pressure-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.vi-detail .vi-columns{grid-template-columns:1fr}.vi-scene svg{min-width:1060px}.vi-note,.vi-legend,.vi-text-nav{padding-left:20px;padding-right:20px}}@media(max-width:560px){.vi-metrics,.vi-scenario-grid,.vi-pressure-grid{grid-template-columns:1fr}.vi-scene{display:none}.vi-head{padding:20px 18px 10px}.vi h2{font-size:1.8rem}.vi-text-nav{display:grid;grid-template-columns:1fr 1fr;padding:14px}.vi-text-nav a{border-radius:10px;font-size:.8rem}.vi-timeline-controls{padding:14px}.vi-metric strong{font-size:1.85rem}}@media(prefers-reduced-motion:reduce){.vi *{transition:none!important;scroll-behavior:auto!important}}
"""

SCRIPT="""
(function(){document.querySelectorAll('.vi[data-vi-ready="false"]').forEach(function(root){
 root.dataset.viReady='true';
 root.addEventListener('click',function(event){var link=event.target.closest('a[data-vi-pick]');if(!link||!root.contains(link))return;
  var detail=document.getElementById(link.dataset.viPick);if(!detail)return;detail.open=true;var summary=detail.querySelector('summary');if(summary)requestAnimationFrame(function(){summary.focus({preventScroll:true});});
  var selected=link.dataset.nodeId;root.querySelectorAll('[data-node-id]').forEach(function(n){if(n.dataset.nodeId===selected)n.setAttribute('aria-current','location');else n.removeAttribute('aria-current');});
  var live=root.querySelector('.vi-live');if(live)live.textContent='Selected '+link.dataset.label+'. Inspect scope, evidence and Unknowns below; selection does not establish a new relationship.';
 });
 var controls=root.querySelectorAll('[data-vi-filter]');controls.forEach(function(c){c.disabled=false;c.addEventListener('change',filter);});
 function filter(){var period=root.querySelector('[data-vi-filter="period"]').value,kind=root.querySelector('[data-vi-filter="kind"]').value,count=0;
  root.querySelectorAll('.vi-time-event').forEach(function(item){var show=(period==='all'||(+period>=+item.dataset.start&&+period<=+item.dataset.end))&&(kind==='all'||kind===item.dataset.kind);item.hidden=!show;if(show)count++;});
  var live=root.querySelector('.vi-live');if(live)live.textContent=count+' dated events shown. Undated scenarios and research gaps remain visible on their separate shelf.';
 }
});})();
"""


def _id(spec,node):return 'vi-'+spec['diagram_type']+'-'+spec['domain']+'-'+re.sub(r'[^A-Za-z0-9_-]','-',node['id'])
def _badge(state):
    kind='conflict' if 'Challenged' in state else 'scenario' if 'Scenario' in state else 'unknown' if 'Unknown' in state or 'Not established' in state else ''
    return f"<span class='vi-badge {kind}'>{e(state)}</span>"


def _icon(kind,x,y,scale=1):
    paths={
      'bank':"<path d='M2 12 16 3 30 12Z M4 29H28 M7 13V27 M13 13V27 M19 13V27 M25 13V27'/>",
      'plane':"<path d='m2 18 12-4V4l3-2 3 12 11 4v3l-11-2v7l4 3v2l-8-2-8 2v-2l5-3v-7l-11 2Z'/>",
      'terminal':"<path d='M2 29V12H30V29 M7 12V5H25V12 M7 19H11 M15 19H19 M23 19H27 M11 29V24H21V29'/>",
      'people':"<circle cx='11' cy='9' r='5'/><circle cx='24' cy='11' r='4'/><path d='M2 29V22c0-10 18-10 18 0v7 M20 19c8-3 12 3 12 10'/>",
      'vault':"<rect x='3' y='4' width='27' height='26' rx='3'/><circle cx='17' cy='17' r='7'/><path d='M17 10v14 M10 17h14 M5 9h2 M5 25h2'/>",
      'home':"<path d='m2 15 14-12 14 12 M6 12V29H26V12 M13 29V20H20V29'/>",
      'transfer':"<path d='M2 10H28l-5-5 M30 23H4l5 5 M28 10l-5 5 M4 23l5-5'/>",
      'shield':"<path d='m16 2 13 5v9c0 9-13 15-13 15S3 25 3 16V7Z m-7 14 5 5 10-11'/>",
      'server':"<rect x='3' y='3' width='26' height='8' rx='2'/><rect x='3' y='13' width='26' height='8' rx='2'/><rect x='3' y='23' width='26' height='8' rx='2'/><path d='M8 7h2 M8 17h2 M8 27h2'/>",
      'cloud':"<path d='M8 26a8 8 0 0 1-1-16 10 10 0 0 1 19 2 7 7 0 0 1-1 14Z M12 16v6 M18 13v9 M24 17v5'/>",
      'tower':"<path d='M12 29V16H21V29 M8 6H25L22 16H11Z M6 2H27 M16 6V2 M4 29H29'/>",
      'leaf':"<path d='M5 27C-2 6 15 5 29 3c-1 19-7 31-24 24Z M5 27 24 9'/>",
      'wrench':"<path d='m4 28 13-13a9 9 0 0 1 10-12l-6 6 4 4 6-6a9 9 0 0 1-12 10L7 30Z'/>",
      'ticket':"<path d='M2 7H30V14c-7 0-7 7 0 7v6H2V21c7 0 7-7 0-7Z M21 7v4 m0 4v3 m0 4v5'/>",
      'network':"<circle cx='16' cy='16' r='4'/><circle cx='4' cy='5' r='3'/><circle cx='29' cy='5' r='3'/><circle cx='5' cy='29' r='3'/><circle cx='29' cy='28' r='3'/><path d='m7 8 6 5 m6 0 7-5 M13 19l-6 7 m12-7 7 6'/>",
      'chart':"<path d='M3 3V30H31 M8 24V17 M16 24V10 M25 24V4'/>",
      'spark':"<path d='m16 1 3 11 12 4-12 4-3 11-4-11-11-4 11-4Z'/>",
    }
    return f"<g transform='translate({x} {y}) scale({scale})' fill='none' stroke='currentColor' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'>{paths.get(kind,paths['network'])}</g>"


def _art(sector,ns,story=False):
    # Pure visual context; these outlines encode no actual topology or quantities.
    if story:
        if sector=='banking':
            return ("<g opacity='.92' fill='none' stroke='#91ad99' stroke-width='2'><path d='M390 220Q640 120 890 220 M390 295Q640 365 890 295' stroke-dasharray='5 8'/><path d='M540 245V185L640 145 740 185V245 M520 250H760 M550 190H730 M570 195V240 M610 195V240 M650 195V240 M690 195V240' fill='#e6eddf'/></g>"+_icon('bank',609,191,1.8)+text(640,285,'A banking value loop',size=15,anchor='middle',bold=False,color='#577360'))
        return ("<g fill='none' stroke='#8da59b' stroke-width='2'><path d='M395 295H884 M425 310H851' stroke-dasharray='16 12'/><path d='M440 280V248H560V280 M458 248V225H542V248' fill='#f3e3cd'/><path d='M798 280V218H824V280 M790 203H832L826 218H796Z' fill='#e6eadd'/></g><g transform='translate(580 172) rotate(68 50 50)' color='#456d60'>"+_icon('plane',0,0,3.5)+"</g>"+text(640,330,'An airline operating system',size=15,anchor='middle',bold=False,color='#577360'))
    if sector=='banking':
        art="<path d='M0 269Q230 236 460 263T900 254T1280 266V315H0Z' fill='#dce7d8'/><path d='M0 288Q370 264 660 286T1280 279' fill='none' stroke='#a5bdac' stroke-width='2'/>"
        for i,(x,w,h) in enumerate([(55,95,90),(175,110,130),(320,115,98),(470,130,168),(641,105,115),(785,140,142),(975,110,92),(1120,105,125)]):
            art+=f"<g stroke='#98b09e' fill='{['#e8eddd','#f0e5d0','#dbe7d8'][i%3]}'><path d='M{x} 265V{265-h}H{x+w}V265Z'/>"
            for j in range(3):art+=f"<path d='M{x+18+j*27} {285-h}V245' opacity='.6'/>"
            art+='</g>'
        art+=_icon('bank',509,143,2)+_icon('home',205,177,1.8)+_icon('transfer',664,186,1.5)
    else:
        art="<path d='M0 274Q260 226 480 253T880 253T1280 268V315H0Z' fill='#dfe8d8'/><path d='M65 261H1220' stroke='#96ada0' stroke-width='3'/><path d='M85 280H1210' stroke='#fffaf0' stroke-width='3' stroke-dasharray='25 20'/><path d='M80 253V188H340V253 M115 188V166H310V188' stroke='#9cb39d' fill='#ede4ce'/><path d='M1015 253V174H1040V253 M1001 151H1053L1045 174H1010Z' stroke='#a2b6a5' fill='#e4e9d7'/><path d='M280 128Q650 25 980 126' fill='none' stroke='#b79d7b' stroke-dasharray='4 9' stroke-width='2'/>"
        art+="<g transform='translate(590 94) rotate(65 40 40)' color='#326250'>"+_icon('plane',0,0,3.8)+"</g>"+_icon('terminal',190,190,1.6)+_icon('wrench',838,198,1.5)
    return "<g aria-hidden='true'>"+art+'</g>'


def _pick(spec,n,x,y,w,h,icon=True):
    target=_id(spec,n);short='Scope unresolved' if n['conflict_ids'] else 'Conceptual activity' if n['category']=='Activity' else n['category']
    body=f"<rect class='vi-card' x='{x}' y='{y}' width='{w}' height='{h}' rx='15' fill='#fffdf8' stroke='#b5c7b8'/>"
    if icon:body+=_icon(n['icon'],x+14,y+18,.8)
    lines=wrap(n['label'],width=int((w-(64 if icon else 30))/8),break_long_words=True,break_on_hyphens=False) or ['']
    labels=lines[:2]
    if len(lines)>2:labels[-1]=labels[-1].rstrip()+'…'
    body+=''.join(text(x+(50 if icon else 16),y+28+i*20,label,width=1000,size=15) for i,label in enumerate(labels))
    body+=text(x+(50 if icon else 16),y+h-14,short,width=int((w-40)/6),size=11,color='#5a6f61',bold=False)
    return f"<a class='vi-node' data-node-id='{e(n['id'],quote=True)}' data-state='{e(n['state'],quote=True)}' data-vi-pick='{target}' data-label='{e(n['label'],quote=True)}' href='#{target}' aria-controls='{target}' aria-label='{e(n['label']+' — inspect purpose and evidence',quote=True)}'><title>{e(n['label'])} · {e(n['state'])}</title>{body}</a>"


def _scene(spec):
    kind=spec['diagram_type'];story=kind=='enterprise-story';ns='vi-art-'+spec['domain']+'-'+kind
    if story:
        positions=[(25,25),(475,25),(925,25),(25,235),(925,235),(475,480),(25,480),(925,480),(475,355)]
        shapes=_art(spec['illustration'],ns,True)
        positions_by_id={n['id']:positions[i] for i,n in enumerate(spec['nodes'][:9])}
        shapes+=f"<defs><marker id='{ns}-concept-arrow' markerWidth='7' markerHeight='7' refX='6' refY='3.5' orient='auto'><path d='M0 0 6 3.5 0 7' fill='none' stroke='#aa8a57'/></marker></defs>"
        for flow in spec.get('conceptual_flows',[]):
            if not flow['illustrated'] or flow['source'] not in positions_by_id or flow['target'] not in positions_by_id:continue
            x,y=positions_by_id[flow['source']];tx,ty=positions_by_id[flow['target']]
            if y==ty:coordinates=f'M{x+330} {y+50}H{tx}'
            elif x==tx:coordinates=f'M{x+165} {y+100}V{ty}'
            else:continue
            shapes+=f"<path d='{coordinates}' fill='none' stroke='#aa8a57' stroke-width='2' stroke-dasharray='5 7' marker-end='url(#{ns}-concept-arrow)'><title>{e(flow['state']+': '+flow['label'])}</title></path>"
        for i,n in enumerate(spec['nodes']):
            if i<9:x,y=positions[i]
            else:x,y=25+(i%3)*450,610+(i//3-3)*120
            shapes+=_pick(spec,n,x,y,330,100)
        height=max(610,610+max(0,(len(spec['nodes'])-9+2)//3)*120)
    else:
        shapes=_art(spec['illustration'],ns)
        for i,n in enumerate(spec['nodes']):
            x=25+(i%5)*250;y=325+(i//5)*104
            shapes+=_pick(spec,n,x,y,230,88,False)
        height=345+((len(spec['nodes'])+4)//5)*104
    return (f"<div class='vi-scene' tabindex='0' aria-label='Pan {e(spec['title'],quote=True)}; equivalent text links follow'><svg viewBox='0 0 1280 {height}' role='group' aria-labelledby='{ns}-title {ns}-desc' style='color:#234f41'><title id='{ns}-title'>{e(spec['title'])}</title><desc id='{ns}-desc'>Conceptual sector illustration with selectable research-backed roles. Marker sizes are equal, not a market ranking. No implied ownership or causal connections.</desc><rect width='1280' height='{height}' fill='#f6f3e8'/>{shapes}</svg></div>")


def _metrics(spec):
    cards=[]
    for m in spec.get('metrics',[]):
        val=str(m['value']) if m['value'] is not None else 'Not established'
        refs=''.join(f"<a href='{e(p['url'],quote=True)}'>Inspect source →</a>" for p in m['evidence'][:1])
        cards.append(f"<article class='vi-metric'><span class='vi-kicker'>{e(m['label'])}</span><strong>{e(val)}</strong><p>{e(m['unit'] or m['limitation'])}</p><p>{e(m['scope_note'])}</p><p>{e(m['period'] or 'No comparable period established')}</p>{_badge(m['state'])}<p>{refs}</p></article>")
    return "<div class='vi-metrics'>"+''.join(cards)+'</div>' if cards else ''


def _sources(proof):
    if not proof:return ds.source_note("<p class='vi-empty'>Supporting source evidence is not established in this snapshot. This is a research gap, not a verified fact.</p>")
    rows=[]
    for p in proof:
        dates='; '.join('publication '+str(s.get('publication_date') or 'Unknown')+' / retrieved '+str(s.get('retrieved_at') or 'not verified') for s in p['source_dates'])
        rows.append(f"<article class='vi-source'>{_badge(p['state'])}<p>{e(p['label'])}</p><small>{e(p['scope'])} · {e(p['period'])}<br>{e(dates)}</small><p><a href='{e(p['url'],quote=True)}'>Read the evidence and exact passage →</a></p></article>")
    return ds.source_note(''.join(rows))


def _detail(spec,n):
    target=_id(spec,n)
    def links(rows):return '<ul>'+''.join(f"<li><a href='{e(r['url'],quote=True)}'>{e(r['label'])}</a></li>" for r in rows)+'</ul>' if rows else '<p>Not mapped in current research.</p>'
    flows=[f for f in spec.get('conceptual_flows',[]) if n['id'] in (f['source'],f['target'])]
    conceptual='<h4>Conceptual interactions — not verified implementation</h4><ul>'+''.join(f"<li>{e(f['label'])} · <a href='#{_id(spec,other)}' data-vi-pick='{_id(spec,other)}' data-node-id='{e(other['id'],quote=True)}' data-label='{e(other['label'],quote=True)}'>{e(other['label'])}</a></li>" for f in flows for other in spec['nodes'] if other['id']==(f['target'] if f['source']==n['id'] else f['source']))+'</ul>' if flows else ''
    supplier=''.join(f"<li><a href='{e(s['url'],quote=True)}'>{e(s['label'])}</a> — {e(s['status'])}. {e('; '.join(s['periods']))}</li>" for s in n['supplier_context'])
    conflicts=''
    for c in spec.get('conflicts',[]):
        if c['id'] in n['conflict_ids']:conflicts+=f"<aside class='vi-source'>{_badge('Challenged / scope unresolved')}<p>{e(c['status'])}</p><p>{e(c['treatment'])}</p></aside>"
    return (f"<details class='vi-detail' id='{target}'><summary>{e(n['label'])} · {e(n['state'])}</summary><h3>{e(n['purpose'])}</h3><p>{e(n['limitations'])}</p>{conceptual}{conflicts}"
        +f"<div class='vi-columns'><div><h4>Capabilities & supporting activities</h4>{links(n['capability_links'])}<h4>Programmes & relevant change</h4>{links(n['programme_links'])}</div><div><h4>Supplier & dependency context</h4><ul>{supplier}</ul>"
        +("<p>Current supplier roles, activity-level dependencies and contract terms remain unknown where not explicitly evidenced.</p>" if not supplier else "<p>A documented enterprise supplier relationship does not establish this activity’s implementation, exclusivity or current contract.</p>")
        +f"<p><a href='{e(n['url'],quote=True)}'>Explore the underlying research / enterprise →</a></p></div></div><h4>Evidence, scope and reporting periods</h4>{_sources(n['evidence'])}"
        +f"<details><summary>Related commercial hypotheses — separate and unqualified</summary>{links(n['opportunity_links'])}<p>Research relevance does not establish customer demand, a budget or Pipeline qualification.</p></details></details>")


def _legend():return "<div class='vi-legend' aria-label='Visual evidence legend'><span><i class='vi-mark'></i>Disclosed context — inspect source</span><span><i class='vi-mark interpret'></i>Conceptual / interpretation · dashed arrows are modelled flows</span><span><i class='vi-mark scenario'></i>Scenario / hypothesis</span><span><i class='vi-mark unknown'></i>Unknown / missing</span><span><i class='vi-mark conflict'></i>Challenged / conflicting scope</span></div>"


def _pick_links(spec,nodes):
    return "<nav class='vi-text-nav' aria-label='Equivalent text navigation'>"+''.join(f"<a href='#{_id(spec,n)}' data-node-id='{e(n['id'],quote=True)}' data-vi-pick='{_id(spec,n)}' data-label='{e(n['label'],quote=True)}'>{e(n['label'])}</a>" for n in nodes)+'</nav>'


def _timeline(spec):
    known=[n for n in spec['nodes'] if n['start_year'] is not None];undated=[n for n in spec['nodes'] if n['start_year'] is None]
    years=list(range(min(spec['years']),max(spec['years'])+1)) if spec['years'] else []
    options="<option value='all'>All periods</option>"+''.join(f"<option value='{y}'>{y}</option>" for y in years)
    kinds=list(dict.fromkeys(n['temporal_kind'] for n in known))
    controls=f"<div class='vi-timeline-controls'><label>Focus a year<select data-vi-filter='period' disabled>{options}</select></label><label>Event meaning<select data-vi-filter='kind' disabled><option value='all'>All dated event types</option>"+''.join(f"<option value='{e(k,quote=True)}'>{e(k)}</option>" for k in kinds)+"</select></label><noscript>All events and text alternatives remain available below without filters.</noscript></div>"
    if years:
        plot=f"<div class='vi-timeline-scroll' tabindex='0' aria-label='Pan strategic timeline; text alternative follows' style='--vi-years:{len(years)}'><div class='vi-time-axis'><span>Pressure / change</span>"+''.join(f'<span>{y}</span>' for y in years)+'</div>'
        for lane in spec['lanes']:
            plot+=f"<div class='vi-lane vi-lane-grid'><div class='vi-lane-name'>{e(lane)}</div>"
            records=[n for n in known if n['lane']==lane]
            if not records:plot+="<p class='vi-note' style='grid-column:2/-1'>No dated event established in this snapshot.</p>"
            for n in records:
                a=years.index(n['start_year'])+2;b=years.index(n['end_year'])+3
                plot+=f"<a class='vi-time-event' data-kind='{e(n['temporal_kind'],quote=True)}' data-start='{n['start_year']}' data-end='{n['end_year']}' data-vi-pick='{_id(spec,n)}' data-node-id='{e(n['id'],quote=True)}' data-label='{e(n['label'],quote=True)}' href='#{_id(spec,n)}' style='grid-column:{a}/{b}'><strong>{e(n['label'])}</strong><small>{'Published ' if n['date_basis']=='publication' else ''}{e(n['date_label'])}<br>{e(n['temporal_kind'])}</small></a>"
            plot+='</div>'
        plot+='</div>'
    else:plot="<p class='vi-empty'>No dated events are established. Undated questions remain below; no date axis has been fabricated.</p>"
    shelf="<section class='vi-undated' aria-label='Undated scenarios and Unknowns'><h3>Unscheduled / still Unknown</h3><p>These items have no verified date. Their position is not a forecast.</p><div class='vi-undated-links'>"+''.join(f"<a href='#{_id(spec,n)}' data-vi-pick='{_id(spec,n)}' data-node-id='{e(n['id'],quote=True)}' data-label='{e(n['label'],quote=True)}'><strong>{e(n['label'])}</strong><br>{e(n['temporal_kind'])} · date Unknown</a>" for n in undated)+'</div></section>'
    return controls+plot+shelf


def _event_detail(spec,n):
    links=''.join(f"<li><a href='{e(a['url'],quote=True)}'>{e(a['label'])}</a></li>" for a in n['affected_links'])
    return (f"<details class='vi-detail' id='{_id(spec,n)}'><summary>{e(n['label'])} · {e(n['temporal_kind'])} · {e(n['date_label'])}</summary><p>{_badge(n['temporal_kind'])} {e(n['precision'])}.</p><p>{e(n['applicability'])}</p><div class='vi-columns'><div><h4>Affected process / capability</h4><ul>{links}</ul><h4>Current readiness</h4><p>{e(n['readiness'])}</p></div><div><h4>Why it may matter</h4><p>{e(n['consequence'])}</p><p>{e(n['limitations'])}</p></div></div>{_sources(n['evidence'])}</details>")


def render_intelligence(spec,lens=None):
    if spec.get('extension')!='flora-visual-intelligence-v1' or spec['authority']!='candidate_intelligence':raise ValueError('Unknown visual intelligence specification')
    timeline=spec['diagram_type']=='strategic-timeline';ai=lens=='ai-disruption'
    title='AI disruption: evidence before threat.' if ai else spec['title']
    body=f"<style>{STYLE}</style><section class='vi' data-vi-ready='false' data-visual-family='{spec['diagram_type']}' data-snapshot='{e(spec['snapshot_digest'],quote=True)}'><div class='vi-frame'><header class='vi-head'><div><span class='vi-kicker'>01 / Understand · {e(spec['geography'])}</span><h2>{e(title)}</h2><p>{e(spec['summary'])}</p></div></header>"
    body+=_timeline(spec) if timeline else _scene(spec) if spec['nodes'] else "<p class='vi-empty'>No research-linked activities or participants are available in this snapshot. No operating structure has been inferred.</p>"
    body+=_legend()+f"<p class='vi-note'>{e(spec.get('structure_notice',spec.get('participant_limitation',spec['interpretation'])))}</p>"
    if not timeline:body+=_pick_links(spec,spec['nodes'])
    body+="<p class='vi-live' aria-live='polite'>Select an element to explore purpose, supporting research and what remains Unknown.</p></div>"
    body+=_metrics(spec)
    if spec['diagram_type']=='industry-signature':
        body+="<h3>Value creation, in reading order</h3><nav class='vi-text-nav' aria-label='Industry operating structure'>"+''.join(f"<a href='{e(n['url'],quote=True)}'>{i+1:02} · {e(n['label'])}</a>" for i,n in enumerate(spec['value_chain']))+"</nav><p class='vi-note'>A conceptual industry value chain, not a verified connection between the illustrated participants.</p>"
        if ai:
            body+="<div class='vi-scenario-grid'>"
            for n in spec['scenarios']:
                affected=''.join(f"<a class='vi-link-pill' href='{e(a['url'],quote=True)}'>{e(a['label'])}</a> " for a in n['affected_links'])
                body+=f"<article class='vi-scenario'>{_badge('Scenario — no displacement prediction')}<h3>{e(n['label'])}</h3><p>{e(n['purpose'])}</p><p><strong>Structural defences:</strong> {e(n['defence'])}</p><p>Affected capabilities / potential responses:</p>{affected}{_sources(n['evidence'])}</article>"
            body+='</div>'
        body+="<details><summary>Explore structural forces · interpretation, not enterprise failure</summary><div class='vi-pressure-grid'>"+''.join(f"<article class='vi-pressure'><h3>{e(p['label'])}</h3><p>{e(p['purpose'])}</p><a href='{e(p['url'],quote=True)}'>Inspect force & evidence →</a></article>" for p in spec['pressures'])+'</div></details>'
    body+="<div class='vi-level'><strong>02 / Explore → 03 / Investigate</strong><span>Every disclosure keeps its own scope, reporting period and source limitations.</span></div><div class='vi-details'>"
    body+=''.join(_event_detail(spec,n) if timeline else _detail(spec,n) for n in spec['nodes'])+'</div>'
    body+=f"<details class='vi-snapshot'><summary>Pinned research snapshot</summary><p>As of {e(spec['as_of'])}; underlying source periods vary. Snapshot {e(spec['snapshot_digest'])}. Equal marker sizes do not imply market share, spend or importance. No canonical acceptance, automatic qualification or production-data change.</p></details><script>{SCRIPT}</script></section>"
    return body
