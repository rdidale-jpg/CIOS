"""Technology lenses in the shared FLORA shell; repository research only."""
from html import escape as e
import re
from urllib.parse import urlencode, urlsplit
from . import technology as t
from .unified_views import page

LABELS={'applications':'Applications','cloud':'Cloud & data','ai':'AI & decisions','cyber':'Cyber & resilience','services':'Technology services','channels':'Channels','infrastructure':'Infrastructure & connectivity','frontier':'Frontier technologies'}
DESCRIPTIONS={
'applications':'Software supports business workflows. Product ownership, customer adoption and implementation are different relationships.',
'cloud':'Compute, storage and data platforms support workloads. Consumption, hosting and managed operation have different economics.',
'ai':'Models, data and decision systems connect research to workflows. Announced adoption is distinct from operational value.',
'cyber':'Protection, detection, response and recovery span the system. A product purchase does not prove an effective control.',
'services':'People and delivery processes design, integrate, transform and run technology. Accountability is programme-specific.',
'channels':'Distribution, sourcing, resale and finance connect vendors to buyers. Gross invoicing, revenue and margin differ.',
'infrastructure':'Facilities, networks, equipment and power enable capacity. Network ownership is distinct from the retail customer contract.',
'frontier':'Semiconductor IP and quantum capabilities connect research to future systems. Collaboration is distinct from production advantage.'}
STYLE='''
.tech summary{overflow-wrap:anywhere;word-break:normal}.tech .tech-fold table{display:block;max-width:100%;overflow:auto}.tech .tech-fold{min-width:0;overflow-wrap:anywhere}
.tech-node strong,.tech-node small{display:block}
.tech{--ink:#243552;--muted:#526078;--violet:#5646a2;--line:#cdd2df;color:var(--ink);margin:auto;max-width:1400px}.tech *{box-sizing:border-box}.tech h1,.tech h2,.tech h3{color:var(--ink);letter-spacing:-.025em}.tech h1{font-size:clamp(2.3rem,4vw,3.7rem);line-height:1.06;margin:12px 0 18px}.tech h2{font-size:1.7rem}.tech h3{font-size:1.13rem}.tech p{line-height:1.6}.tech a{color:#3e3b87;text-underline-offset:4px}.tech a:focus-visible,.tech summary:focus-visible,.tech select:focus-visible,.tech button:focus-visible{outline:3px solid #865d0e;outline-offset:4px}.tech a,.tech button,.tech summary{min-height:44px}.tech a{align-content:center}.tech .crumb{font-size:.85rem;margin:15px 0 26px}.tech .eyebrow{font:700 .74rem/1.4 system-ui;letter-spacing:.14em;text-transform:uppercase;color:#5b5484}.tech-hero{display:grid;grid-template-columns:1fr 270px;gap:45px;align-items:center;padding:8px 0 24px}.tech-hero p{max-width:730px;color:var(--muted)}.tech-count{border-left:1px solid var(--line);padding:10px 0 10px 28px}.tech-count strong{font-size:3.6rem;font-weight:450;display:block;letter-spacing:-.07em}.tech-count span{font-size:.85rem;color:var(--muted)}.tech-nav{display:flex;gap:5px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:9px 0;margin:4px 0 28px;flex-wrap:wrap}.tech-nav a{padding:12px 17px;text-decoration:none;border-radius:7px;font-size:.94rem}.tech-nav a[aria-current]{background:var(--ink);color:white}.tech-support{display:flex;gap:16px;flex-wrap:wrap;margin:20px 0 30px;font-size:.9rem}.tech-badge{font-size:.72rem;font-weight:650;background:#eee9fa;color:#51427f;border-radius:4px;display:inline-block;padding:5px 8px}.tech-note{font-size:.84rem;color:var(--muted);padding:12px 0}.tech-stage{display:grid;grid-template-columns:minmax(0,1fr) 290px;gap:28px;align-items:start}.tech-landscape{position:relative;background:linear-gradient(135deg,#f0f1fb,#f8f7f1);border:1px solid #d5d7e6;padding:24px 22px 15px;border-radius:16px;isolation:isolate}.tech-landscape>p{margin:0 0 16px;font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:#66617f}.tech-nodes{position:relative;display:grid;grid-template-columns:1fr 1.6fr 1.6fr 1fr;grid-template-areas:'cyber applications ai services' 'cyber cloud infrastructure services' 'channels channels frontier frontier';gap:22px 14px}.tech-node{z-index:1;background:#fffdfb;border:1px solid #b6bdd4;border-radius:9px;text-decoration:none;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;min-width:0;min-height:150px;padding:14px 10px;color:var(--ink)!important;box-shadow:0 5px 0 #e2e3ee}.tech-node:hover{border-color:#53448e;background:#f3f0fc}.tech-node[aria-current]{outline:2px solid #6752a0;background:#f1edfa}.tech-node strong{font-size:.94rem;line-height:1.3;margin-top:7px}.tech-node small{font-size:.7rem;color:#59647a;margin-top:8px}.tech-node svg{width:70px;height:55px;stroke:#706298;fill:none;stroke-width:1.7}.tech-node.cyber,.tech-node.services{background:#e9e9f4;box-shadow:none}.tech-node.channels,.tech-node.frontier{min-height:114px;flex-direction:row;gap:16px}.tech-node.cyber svg{height:85px}.tech-connectors{position:absolute;inset:40px 0 0;width:100%;height:80%;z-index:0;stroke:#8e90ae;stroke-dasharray:5 5;fill:none;opacity:.65}.tech-inspector{border-top:3px solid #7564a3;padding:12px 2px}.tech-inspector h2{font-size:1.4rem;margin:15px 0}.tech-inspector p{font-size:.93rem}.tech-provider-links{display:flex;flex-wrap:wrap;gap:6px}.tech-provider-links a{border-bottom:1px solid #bfc3d5;display:inline-block;padding:5px 4px;font-size:.85rem}.tech-section{margin:35px 0;border-top:1px solid var(--line);padding-top:20px}.tech-measures{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;padding:22px 0}.tech-measure{border-left:2px solid #c1b58f;padding:0 16px}.tech-measure strong{font-size:1.55rem;font-weight:500;display:block}.tech-measure p{font-size:.82rem;margin:8px 0}.tech-fold{margin:14px 0!important;padding:15px 18px!important;background:#fffdfa!important;border:1px solid var(--line)!important;border-radius:7px!important}.tech summary{cursor:pointer;align-content:center;font-weight:650}.tech-source{font-size:.85rem;border-left:3px solid #aaa0c6;padding:8px 16px;margin:20px 0;overflow-wrap:anywhere}.tech-source p{margin:6px 0}.tech-source a{display:inline-block}.tech-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.tech-grid>*{min-width:0}.tech-theme{padding:24px 20px;border-top:3px solid #8976ac;background:#f4f2f9;border-radius:0 0 10px 10px}.tech-theme .number{font-size:2rem;font-weight:350;color:#75638e}.tech-theme p{font-size:.9rem}.tech-theme h2{font-size:1.35rem}.tech-theme details{background:transparent!important;padding:0!important;border:none!important}.tech-theme dl,.tech-programme dl{font-size:.9rem}.tech dt{font-weight:700;margin-top:14px}.tech dd{margin:6px 0 15px;line-height:1.55}.tech-explorer{display:grid;grid-template-columns:265px minmax(0,1fr);gap:30px}.tech-programme-list{max-height:570px;overflow:auto;border-right:1px solid var(--line);padding-right:16px}.tech-programme-list a{display:block;padding:12px;text-decoration:none;border-bottom:1px solid #dce0e7;font-size:.88rem}.tech-programme-list a[aria-current]{background:#ece8f6;border-left:3px solid #776196}.tech-programme-list small{display:block;font-size:.74rem;color:var(--muted);line-height:1.4;margin-top:4px}.tech-chain{display:grid;grid-template-columns:1fr 30px 1.4fr;gap:10px;align-items:center;background:#eef0f7;padding:28px 22px;border-radius:12px;margin:20px 0}.tech-chain article{background:#fffefa;padding:17px;border:1px solid #c7cbdc;border-radius:8px;min-width:0}.tech-chain .arrow{text-align:center;font-size:1.8rem;color:#796898}.tech-chain strong{font-size:1.1rem;display:block;line-height:1.45}.tech-chain small{display:block;font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:8px}.tech-programme h2{font-size:1.7rem}.tech table{border-collapse:collapse;width:100%;font-size:.87rem}.tech th,.tech td{padding:13px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}.tech select,.tech button{font:inherit;padding:11px;border:1px solid #afb6c9;background:#fffefa;border-radius:5px;color:var(--ink);max-width:100%}.tech-form{display:flex;gap:12px;align-items:end;flex-wrap:wrap;margin:20px 0}.tech-form label{display:grid;gap:7px;font-size:.85rem}.tech-directory-row{display:grid;grid-template-columns:1.1fr 1.3fr 1.6fr;gap:20px;padding:17px 0;border-bottom:1px solid var(--line);font-size:.88rem}.tech-directory-row a{font-weight:650}.tech-directory-row small{color:var(--muted)}.tech-timeline{border-left:2px solid #9b8fb6;padding-left:28px;margin:25px 0}.tech-event{position:relative;margin:20px 0;padding:0 0 20px}.tech-event:before{content:'';position:absolute;width:12px;height:12px;border-radius:50%;background:#776293;left:-35px;top:9px}.tech-event time{font-size:.84rem}.tech-event h3{margin:8px 0}.tech .unknown{background:#f5edda;color:#68512d}.tech-prose{overflow-wrap:anywhere}.tech-prose pre{white-space:pre-wrap}.tech-prose table{display:block;overflow:auto}.tech-prose p{max-width:1000px}.tech-footer{margin:40px 0 15px;padding-top:15px;border-top:1px solid var(--line);font-size:.8rem;color:var(--muted)}
@media(max-width:1100px){.tech-stage{grid-template-columns:minmax(0,1fr) 235px}.tech-nodes{gap:15px 9px;grid-template-columns:1fr 1.35fr 1.35fr 1fr}.tech-landscape{padding:18px 12px}.tech-node{padding:10px 6px}.tech-node strong{font-size:.82rem}.tech-grid{grid-template-columns:1fr 1fr}.tech-explorer{grid-template-columns:220px minmax(0,1fr)}}
@media(max-width:850px){.tech-stage{grid-template-columns:1fr}.tech-inspector{border-top:1px solid var(--line);padding:12px}.tech-hero{grid-template-columns:1fr 170px;gap:20px}.tech-count{padding-left:18px}.tech-explorer{grid-template-columns:1fr}.tech-programme-list{max-height:230px;border-right:0;border-bottom:1px solid var(--line)}.tech-chain{padding:16px}.tech-measures{gap:9px}.tech-directory-row{grid-template-columns:1fr 1fr}.tech-directory-row small{grid-column:1/-1}}
@media(max-width:540px){.tech-hero{grid-template-columns:1fr;gap:0}.tech-count{border-left:0;border-top:1px solid var(--line);padding:12px 0}.tech-count strong{font-size:2rem;display:inline;margin-right:12px}.tech-count p{display:none}.tech-nav a{padding:10px;font-size:.85rem}.tech-nodes{grid-template-columns:1fr 1fr;grid-template-areas:'applications ai' 'cloud infrastructure' 'cyber services' 'channels frontier';gap:13px}.tech-node{min-height:135px}.tech-node.channels,.tech-node.frontier{flex-direction:column;gap:0}.tech-node.cyber svg{height:55px}.tech-connectors{display:none}.tech-grid,.tech-measures{grid-template-columns:1fr}.tech-chain{grid-template-columns:1fr}.tech-chain .arrow{transform:rotate(90deg)}.tech-directory-row{grid-template-columns:1fr;gap:5px}.tech th,.tech td{padding:8px}.tech h1{font-size:2.45rem}}
@media(prefers-reduced-motion:reduce){.tech *{scroll-behavior:auto!important;transition:none!important}}
@media print{.tech-nav,.tech-support,.tech-form{display:none}.tech-stage,.tech-explorer{display:block}.tech-programme-list{display:none}.tech-grid{grid-template-columns:1fr 1fr}.tech-landscape{break-inside:avoid}.tech details{display:block}.tech-source a:after{content:' (' attr(href) ')';font-size:.7rem}.tech-node{box-shadow:none}.tech p,.tech li,.tech dd{color:#243552!important}}
'''
ICONS={
'applications':'<rect x="10" y="10" width="48" height="34" rx="3"/><path d="M10 20h48M17 15h2m4 0h2M18 27h14v11H18zM38 27h12m-12 6h12m-12 6h9"/>',
'cloud':'<path d="M18 36C3 36 5 20 17 21c-1-17 26-22 33-4 17-4 24 20 5 21H18z"/><ellipse cx="35" cy="38" rx="11" ry="4"/><path d="M24 38v11c0 5 22 5 22 0V38m-22 5c0 5 22 5 22 0"/>',
'ai':'<path d="M17 12l34 3-16 28L17 12m0 0l-6 30 24 1 25-10-9-18M11 42l49-9"/><circle cx="17" cy="12" r="4"/><circle cx="51" cy="15" r="5"/><circle cx="35" cy="43" r="6"/><circle cx="11" cy="42" r="3"/><circle cx="60" cy="33" r="3"/>',
'cyber':'<path d="M35 4l24 8v18c0 12-16 20-24 24C27 50 11 42 11 30V12zM24 28l8 8 15-18"/>',
'services':'<circle cx="35" cy="12" r="7"/><circle cx="13" cy="37" r="5"/><circle cx="57" cy="37" r="5"/><path d="M25 32v-6c0-9 20-9 20 0v6M6 51v-5c0-8 14-8 14 0v5m30 0v-5c0-8 14-8 14 0v5M19 35l10-6m12 0l10 6"/>',
'channels':'<rect x="3" y="21" width="16" height="16" rx="2"/><rect x="50" y="3" width="16" height="13" rx="2"/><rect x="50" y="23" width="16" height="13" rx="2"/><rect x="50" y="43" width="16" height="12" rx="2"/><path d="M19 29h16V9h15M35 29h15M35 29v20h15"/>',
'infrastructure':'<rect x="6" y="8" width="19" height="42" rx="2"/><rect x="30" y="8" width="19" height="42" rx="2"/><path d="M10 17h11m-11 8h11m-11 8h11m-11 8h11M34 17h11m-11 8h11m-11 8h11m-11 8h11M55 44h12m-6 0V18m-7 6l7-6 7 6"/>',
'frontier':'<ellipse cx="35" cy="29" rx="29" ry="11"/><ellipse cx="35" cy="29" rx="29" ry="11" transform="rotate(60 35 29)"/><ellipse cx="35" cy="29" rx="29" ry="11" transform="rotate(120 35 29)"/><circle cx="35" cy="29" r="5"/>'}


def url(path='', **query):
    return t.BASE+path+('?' + urlencode(query) if query else '')


def link(target, label, **attrs):
    extra=''.join(' '+k.replace('_','-')+"='"+e(str(v),quote=True)+"'" for k,v in attrs.items())
    return f"<a href='{e(target,quote=True)}'{extra}>{label}</a>"


def inline(text):
    """Escape Page prose first; only allow explicit HTTPS Markdown links."""
    chunks=[];pos=0
    for m in re.finditer(r'\[([^\]]+)\]\((https://[^\s)]+)\)',text):
        chunks.append(e(text[pos:m.start()]));u=urlsplit(m[2])
        chunks.append(link(m[2],e(m[1])) if u.hostname and not u.username and not u.password else e(m[0]));pos=m.end()
    chunks.append(e(text[pos:]))
    return ''.join(chunks)


def prose(text):
    rows=text.splitlines()
    if len(rows)>2 and rows[0].startswith('|') and rows[1].startswith('| ---'):
        cells=lambda s:[c.strip() for c in s.strip().strip('|').split('|')]
        head=''.join('<th scope="col">'+inline(s)+'</th>' for s in cells(rows[0]))
        body=''.join('<tr>'+''.join('<td>'+inline(s)+'</td>' for s in cells(row))+'</tr>' for row in rows[2:] if row.startswith('|'))
        return '<table><thead><tr>'+head+'</tr></thead><tbody>'+body+'</tbody></table>'
    return ''.join('<p>'+inline(s.lstrip('# '))+'</p>' for s in rows if s.strip() and not s.startswith('```'))


def block_link(block, label='Inspect research passage & source limits'):
    return link(url('/evidence')+'#block-'+block,e(label))


def source_detail(r):
    sources=' · '.join(link(s['url'],e(s['label'])) for s in r['source_links']) or 'Source URL unresolved'
    return f"<aside class='tech-source'><span class='tech-badge'>{e(r['evidence_status'])}</span><p>{e(r['attribution'])} · Published {e(r['publication_date'] or 'Unknown')} · Event {e(r['event_date'] or 'Unknown')}</p><p>Retrieved {r['retrieval_date']} (date only). {e(r['geography'])}</p><p>{sources}</p><p>{block_link(r['source_block'])}</p><p>Original-source hash: unavailable. Reuse rights: unestablished. Current contract: unconfirmed.</p></aside>"


def header(lens):
    nav=''.join(link(url(lens=k),f'{n:02} &nbsp; {label}',**({'aria_current':'page'} if lens==k else {})) for n,(k,label) in enumerate((('how','How it works'),('uses','Who uses what'),('work','Where work may emerge')),1))
    return f"<nav class='crumb' aria-label='Breadcrumb'><a href='/industries'>Industries</a> / UK Technology</nav><header class='tech-hero' id='content'><div><p class='eyebrow'>UK Technology / Industry intelligence</p><h1>The systems behind<br>the next change.</h1><p>Understand how technology is built, delivered and used. Follow the evidence into the businesses it supports.</p></div><aside class='tech-count'><strong>80</strong><span>selected provider views · 8 population groups</span><p><span class='tech-badge'>Research foundation · 12 Nov 2026</span></p></aside></header><nav class='tech-nav' aria-label='Technology lenses'>{nav}</nav>"


def supporting():
    return "<nav class='tech-support' aria-label='Technology supporting views'>"+' · '.join(link(url(p),e(label)) for p,label in (('/providers','Provider directory'),('/models','Reference operating models'),('/timeline','Strategic timeline'),('/evidence','Evidence & Unknowns'),('/handoff','Candidate handoff JSON')))+'</nav>'


def landscape(data, selected):
    nodes=''
    for key in t.SEGMENTS:
        count=sum(key in r['memberships'] for r in data['providers'])
        attrs={'class':f'tech-node {key}','style':f'grid-area:{key}'}
        if key==selected:attrs['aria_current']='true'
        icon=f"<svg viewBox='0 0 70 60' aria-hidden='true'>{ICONS[key]}</svg>"
        nodes+=link(url(lens='how',segment=key)+'#landscape',icon+f"<div><strong>{LABELS[key]}</strong><small>{count} selected role memberships</small></div>",**attrs)
    providers=[r for r in data['providers'] if selected in r['memberships']]
    links=''.join(link(url('/providers',provider=r['key']),e(r['label'])) for r in providers[:7])
    role=next((r for r in data['segments'] if r['key']==selected),None)
    inspector=f"<aside class='tech-inspector' aria-live='polite'><p class='eyebrow'>Selected role / conceptual model</p><h2>{LABELS[selected]}</h2><p>{DESCRIPTIONS[selected]}</p><p class='tech-note'>{e(role['economics']) if role else 'Capacity, IP and research economics differ. No common market-size denominator.'}</p><div class='tech-provider-links'>{links}</div><p>{link(url('/providers',segment=selected),f'Explore all {len(providers)} views →')}</p><p class='tech-note'>Memberships overlap. Placement and equal-sized symbols explain roles; they do not encode importance, market share or customer deployments.</p></aside>"
    return f"<section class='tech-stage' id='landscape' aria-label='Industry operating landscape'><div class='tech-landscape'><p>Build → enable → deliver → operate</p><svg class='tech-connectors' viewBox='0 0 700 500' preserveAspectRatio='none' aria-hidden='true'><path d='M80 100H620M80 280H620M240 70V390M460 70V390M80 100V410H620V100'/></svg><div class='tech-nodes'>{nodes}</div><p class='tech-note' style='margin-top:20px'>Conceptual dependencies · select a role to inspect its economics and providers</p></div>{inspector}</section>"


def economics(data, blocks):
    values=[('£158bn','D&T GVA · UK · 2024','Novel Digital and Technologies definition; £408bn turnover, 1.33m employees. Do not add to the separate Digital Sector series.',data['economic_blocks'][0]),('£177.2bn','Digital Sector GVA · UK · 2024','Provisional, 6.8% of UK GVA. Different statistical boundary from D&T.',data['economic_blocks'][1]),('£14.7bn','Cyber sector revenue · 2026 study','2,603 firms; 69,600 FTEs. Study estimates; overlapping populations are not additive.',data['economic_blocks'][2])]
    return "<section class='tech-section'><p class='eyebrow'>Scale / separate definitions</p><div class='tech-measures'>"+''.join(f"<article class='tech-measure'><strong>{v}</strong><p><b>{title}</b></p><p>{note}</p>{block_link(b,'Definition, period & source →')}</article>" for v,title,note,b in values)+"</div><details class='tech-fold'><summary>Value chain, capabilities, PESTLE & competition</summary><p>Analytical reference models, not a named enterprise’s confidential architecture.</p>"+''.join(prose(blocks[x]['markdown']) for x in data['value_chain_blocks'])+''.join(prose(blocks[data[k]]['markdown']) for k in ('pestle_block','competition_block'))+'</details></section>'


def uses(data, key):
    rows=data['relationships']; r=next((r for r in rows if r['key']==key),rows[4])
    choices=''.join(link(url(lens='uses',relationship=x['key'])+'#programme',e(x['customer'])+f"<small>{e(x['participants'])}</small>",**({'aria_current':'true'} if x==r else {})) for x in rows)
    reference=t.existing_navigation(r)
    jump=link('/enterprises/'+reference.slug,'Open existing '+e(reference.name)+' enterprise →') if reference else 'Enterprise identity remains unbound; no duplicate enterprise created.'
    return f"<section class='tech-explorer' id='programme'><nav class='tech-programme-list' aria-label='Evidenced programmes'>{choices}</nav><article class='tech-programme'><p class='eyebrow'>One programme / exact roles retained</p><h2>{e(r['customer'])}</h2><span class='tech-badge'>{e(r['attribution'])}</span><div class='tech-chain'><article><small>Customer / participant</small><strong>{e(r['customer'])}</strong></article><div class='arrow' aria-hidden='true'>→</div><article><small>Product / capability / stated programme</small><strong>{e(r['offering'])}</strong></article></div><p class='eyebrow'>Provider, hosting & delivery roles</p><p>{e(r['participants'])}</p><dl><dt>Temporal status</dt><dd>{e(r['temporal_status'])}</dd><dt>Scope and alternative inference</dt><dd>{inline(r['boundary'])}</dd><dd>{e(r.get('role_boundary','Roles apply only to this cited programme; no exclusive supplier or all-enterprise scope is inferred.'))}</dd></dl><p>{jump}</p>{source_detail(r)}</article></section>"


def work(data, blocks):
    cards=''
    for n,r in enumerate(data['themes'],1):
        support=''.join('<li>'+link(url(lens='uses',relationship=k),e(next(x['customer']+' — '+x['offering'] for x in data['relationships'] if x['key']==k)))+'</li>' for k in r['relationship_keys'])
        support+=''.join('<li>'+block_link(k,'Supporting research passage')+'</li>' for k in r['support_blocks'][1:])
        cards+=f"<article class='tech-theme' id='{r['key']}'><span class='number'>{n:02}</span><p class='eyebrow'>Unqualified research hypothesis</p><h2>{e(r['title'])}</h2><p>{e(r['consequence'])}</p><details><summary>Evidence, alternatives & questions</summary><dl><dt>Possible intervention</dt><dd>{e(r['intervention'])}</dd><dt>Alternative explanation</dt><dd>{e(r['alternative'])}</dd><dt>Qualification question</dt><dd>{e(r['qualification'])}</dd></dl><ul>{support}</ul><p>Budget, buyer mandate and procurement: Unknown. No Pipeline record created.</p></details></article>"
    return "<p class='tech-note'>Six themes to investigate. Research priority is separate from buying intent, market attractiveness and sales qualification.</p><section class='tech-grid' aria-label='Unqualified commercial themes'>"+cards+'</section>'


def directory(data, provider, segment):
    rows=[r for r in data['providers'] if not segment or segment in r['memberships']]
    chosen=next((r for r in data['providers'] if r['key']==provider),None)
    options="<option value=''>All roles</option>"+''.join(f"<option value='{k}'"+(' selected' if k==segment else '')+f'>{v}</option>' for k,v in LABELS.items())
    body=f"<h2>Provider directory</h2><p>80 selected views, not 80 independent corporate groups. A profile is a research draft; canonical enterprise identities remain unbound.</p><form class='tech-form' action='{t.BASE}/providers'><label>Filter role<select name='segment'>{options}</select></label><button>Show providers</button></form>"
    if chosen:
        r=chosen
        body+=f"<section class='tech-section' id='provider'><p class='eyebrow'>{e(r['profile_status'])} / identity unbound</p><h2>{e(r['label'])}</h2><p>{e(r['identity_note'])}</p><p>Roles: {e(', '.join(LABELS[k] for k in r['memberships']))}</p>"
        body+=''.join("<div class='tech-prose'>"+prose(x['text'])+block_link(x['block'])+'</div>' for x in r['profile']) or '<p>No comparable profile recovered beyond population selection.</p>'
        body+="<aside class='tech-source unknown'><b>Open research</b><ul>"+''.join('<li>'+e(x)+'</li>' for x in r['gaps'])+'</ul></aside></section>'
    body+=f"<p class='tech-note'>{len(rows)} views in this filter. Multiple roles do not increase the 80-view denominator.</p>"
    for r in rows:
        body+=f"<div class='tech-directory-row'>{link(url('/providers',provider=r['key'])+'#provider',e(r['label']))}<span>{e(', '.join(LABELS[k] for k in r['memberships']))}</span><small>{e(r['profile_status'])} · {e(r['identity_note'])}</small></div>"
    return body


def models(data, key):
    body="<h2>Reference operating models</h2><p>Hypothetical archetypes explain industry roles. Enterprise-specific Page profiles supply attributed overlays; neither reconstructs confidential architecture.</p>"
    for n,r in enumerate(data['reference_models'],1):
        body+=f"<details class='tech-fold' id='model-{n}'"+(' open' if key==str(n) else '')+f"><summary>{e(r['title'])}</summary><dl>"+''.join(f'<dt>{label}</dt><dd>{e(r[k])}</dd>' for k,label in (('value','Value creation'),('commercial','Commercial mechanism'),('dependencies','Dependencies'),('question','Questions to investigate')))+f"</dl>{block_link(r['source_block'])}</details>"
    body+="<h3>Published provider overlays</h3><p>Select a researched provider to inspect its attributed operating roles and the remaining identity gaps.</p><div class='tech-provider-links'>"+''.join(link(url('/providers',provider=key),label) for key,label in [('computacenter','Computacenter: sourcing + delivery + operations'),('arm','Arm: IP + royalties + planned silicon'),('sap','SAP: applications + partner ecosystem'),('equinix','Equinix: colocation + interconnection'),('oqc','OQC: quantum hardware + access')])+'</div>'
    return body


def timeline(data):
    return "<h2>Strategic change timeline</h2><p>Announcement, plan, completion, reported go-live and legislative proposal remain distinct. Unknown event dates are not replaced with publication dates.</p><div class='tech-timeline'>"+''.join(f"<article class='tech-event'><time>{e(r['date'] or 'Date Unknown')}</time> <span class='tech-badge'>{e(r['status'])}</span><h3>{e(r['title'])}</h3><p class='tech-note'>{e(r['date_basis'])}</p>{block_link(r['block'])}</article>" for r in data['timeline'])+'</div>'


def evidence(data, blocks):
    body=f"<h2>Evidence, Unknowns & contradictions</h2><p>Page sequence {data['page_sequence']} · {len(data['atomic_references'])} bounded passage references · 0 accepted imports. A citation is not an accepted Evidence record.</p><p>{link(url('/handoff'),'Inspect deterministic handoff and withholding reasons →')}</p>"
    body+="<details class='tech-fold' open><summary>What remains unresolved</summary>"+''.join(prose(blocks[k]['markdown']) for k in data['gaps_blocks'])+'</details>'
    body+="<details class='tech-fold'><summary>Corrections, contradictions & withheld relationships</summary><ul><li>NCC / Escode: historical ownership superseded by completed disposal.</li><li>Microsoft / McLaren: withheld after 404; anonymous customers remain anonymous.</li><li>Oracle / NHS SBS: incidental supplier acquisition-year assertion excluded; customer corroboration has narrower scope.</li><li>Databricks engine monitoring and Deloitte AiRR remain separate Rolls-Royce use cases.</li></ul></details>"
    # Exact Page blocks remain addressable, with no interpretation as original publisher bytes.
    for key,block in blocks.items():
        if block['markdown'].startswith('!['):continue
        body+=f"<details class='tech-fold' id='block-{key}'><summary>{e(block['markdown'].splitlines()[0].lstrip('# ')[:115])}</summary><div class='tech-prose'>{prose(block['markdown'])}</div><p class='tech-note'>Recovered ChatGPT research Page passage, not original-source acquisition. Source-operation rights and canonical mapping remain unaccepted.</p></details>"
    return body


def render(path, query, headers=None):
    data, blocks=t.load(); lens=query.get('lens','how'); segment=query.get('segment','applications')
    if lens not in ('how','uses','work') or segment not in ('',*t.SEGMENTS):raise ValueError('Unknown Technology lens or role')
    provider=query.get('provider',''); relationship=query.get('relationship',''); model=query.get('model','')
    if provider and provider not in {r['key'] for r in data['providers']}:raise ValueError('Unknown provider')
    if relationship and relationship not in {r['key'] for r in data['relationships']}:raise ValueError('Unknown programme')
    if model and model not in ('1','2','3','4','5'):raise ValueError('Unknown reference model')
    suffix=path.removeprefix(t.BASE)
    if suffix=='':body=landscape(data,segment or 'applications')+economics(data,blocks) if lens=='how' else uses(data,relationship) if lens=='uses' else work(data,blocks)
    elif suffix=='/providers':body=directory(data,provider,query.get('segment',''))
    elif suffix=='/models':body=models(data,model)
    elif suffix=='/timeline':body=timeline(data)
    elif suffix=='/evidence':body=evidence(data,blocks)
    else:raise ValueError('Unknown Technology view')
    footer="<footer class='tech-footer'>Recovered research · 12 November 2026 · profiles and source permissions remain partial. No accepted enterprise facts, automatic Pipeline records or current-contract assurance. "+link(t.PAGE_URL,'Research Page')+"</footer>"
    script="<script>document.querySelectorAll('.tech details[id]').forEach(function(d){if('#'+d.id===location.hash)d.open=true});addEventListener('hashchange',function(){var d=document.getElementById(location.hash.slice(1));if(d&&d.tagName==='DETAILS')d.open=true});</script>"
    return page('UK Technology — FLORA',f"<style>{STYLE}</style><div class='tech'>{header(lens)}{supporting()}{body}{footer}</div>{script}",headers,'industries',t.BASE)
