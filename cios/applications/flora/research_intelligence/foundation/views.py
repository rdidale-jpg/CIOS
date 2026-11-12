"""One public, read-only programme projection through FLORA's existing visual shell."""
from html import escape as e
from urllib.parse import parse_qsl
from .snapshot import assets
from ..unified_views import page
from ..visual_templates import text

ROUTE='/research/programmes/uk-technology'
STYLE='''
.rf-map{background:#f7f5ec;border:1px solid #cbd8c8;border-radius:24px;overflow:hidden;margin-top:24px}.rf-map svg{width:100%;display:block;height:auto}.rf-node:hover rect,.rf-node:focus rect{stroke:#9c733c;stroke-width:3}.rf-node:focus-visible{outline:3px solid #7c4dba}.rf-layout{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(320px,1fr);gap:24px;align-items:start}.rf-panel{padding:25px;background:#fffdf7;border:1px solid #cbd8c8;border-radius:20px;margin-top:24px;min-width:0}.rf-panel h2{margin-top:8px}.rf-panel p{line-height:1.6}.rf-metrics{display:flex;gap:24px;flex-wrap:wrap;margin:24px 0;color:#49634e}.rf-metrics b{display:block;font-size:2rem;color:#174d3f}.rf-links{display:none;flex-wrap:wrap;gap:8px;padding:16px}.rf-links a{padding:10px;border:1px solid #d2dbc8;border-radius:14px;background:#fffdf7;min-height:44px}.rf-claim{padding:18px 0;border-top:1px solid #d2dbc8;overflow-wrap:anywhere}.rf-claim blockquote{margin:12px 0;padding-left:12px;border-left:3px solid #ad8653;white-space:pre-line}.rf-small{font-size:.85rem;color:#53685a}.rf-provider{background:#e9eee0;padding:16px;border-radius:14px}.rf-panel li{margin-bottom:12px}.rf-panel a{overflow-wrap:anywhere}.rf-panel:focus{outline:2px solid #9c733c}.rf-map a{color:#174d3f}@media(max-width:1050px){.rf-layout{grid-template-columns:1fr}}@media(max-width:600px){.rf-map svg{display:none}.rf-links{display:grid;grid-template-columns:1fr 1fr}.rf-panel{padding:20px}.rf-metrics{gap:16px}.rf-metrics b{font-size:1.5rem}}@media print{.rf-map{break-inside:avoid}.rf-layout{display:block}.rf-links,.ux-tabs,.primary-nav{display:none}.rf-panel{border:0;padding:0}.ux-hero{color:#174d3f!important;background:none!important}.ux-hero p{color:#174d3f!important}}
'''


def selection(query,taxonomy):
    pairs=parse_qsl(query,keep_blank_values=True,strict_parsing=True,max_num_fields=2)
    params=dict(pairs)
    if len(params)!=len(pairs) or set(params)-{'view','segment'}:raise ValueError('Unknown programme selector')
    if params.get('view','overview') not in ('overview','provider','evidence','gaps'):raise ValueError('Unknown programme view')
    if 'segment' in params and params['segment'] not in {r['id'] for r in taxonomy}:raise ValueError('Unknown taxonomy segment')
    return params.get('view','overview'),params.get('segment')


def evidence(claims,receipts):
    items=[]
    for row in claims:
        c=row['candidate'];s=row['segment']
        refs=[r for r in receipts if r['source_id']==row['source_id']]
        items.append(f"<article class='rf-claim'><span class='ux-status'>Publisher-reported fact / research release</span><h3>{e(c['statement'])}</h3><p>{e(row['assertion'])}</p><blockquote>{e(s['content'])}</blockquote><p class='rf-small'>{e(s['section_heading'])} · retrieved {e(row['retrieved_at'][:10])} · publication date unknown</p><p><a href='{e(row['url'],quote=True)}' rel='noreferrer'>Official source ↗</a></p><p class='rf-small'>Exact excerpt SHA-256: {e(s['content_hash'])}</p><p class='rf-small'>Separate acquisition references: {e(' · '.join(r['role']+': '+r['tool_reference'] for r in refs))}</p></article>")
    return ''.join(items)


def render(query='',headers=None):
    if dict(parse_qsl(query,keep_blank_values=True)).get('view') in ('research','briefings','journeys','assurance'):
        from .sprint2.views import render as render_research
        return render_research(query,headers)
    data=assets();p=data['Programme.json'];release=data['Release-v1.json'];content=release['content'];pop=data['Population-v1.json'];receipts=data['Acquisition-Receipts-v1.json']['receipts']
    view,segment=selection(query,p['taxonomy']);claims=content['claims'];count=len(pop['records'])
    short_labels={'infrastructure':'Cloud & infrastructure','services':'Consulting & managed services','channels':'Channels & partnerships'}
    positions=[(35,55),(295,55),(555,55),(35,205),(295,205),(555,205),(295,355)]
    nodes=[];links=[]
    for row,(x,y) in zip(p['taxonomy'],positions):
        status='Acquired catalogue cohort' if row['id'] in ('software','infrastructure','cyber','services') else 'Research coverage gap'
        href=ROUTE+'?segment='+row['id']+'#research-panel'
        nodes.append(f"<a class='rf-node' href='{href}' aria-label='{e(row['label'])}'><title>{e(row['label'])}: {status}</title><rect x='{x}' y='{y}' width='230' height='115' rx='18' fill='{'#e4eddf' if status.startswith('Acquired') else '#f4ead7'}' stroke='#b3c2ad'/>{text(x+18,y+33,short_labels.get(row['id'],row['label']),width=22,size=18)}{text(x+18,y+95,status,width=34,size=10,bold=False)}</a>")
        links.append(f"<a href='{href}'>{e(row['label'])}</a>")
    svg="<svg viewBox='0 0 820 505' role='img' aria-label='UK technology research coverage map'><rect width='820' height='505' fill='#f7f5ec'/><path d='M150 170V190H670V170M410 170V355M150 320V340H670V320' stroke='#bccab6' stroke-width='2' fill='none'/>"+''.join(nodes)+text(35,485,'Coverage categories; connecting lines indicate taxonomy, not enterprise relationships.',width=110,size=11,bold=False)+"</svg>"
    title='How the programme works';panel=f"<p>Establish a comparable UK technology baseline, then deepen the highest-value gaps. This first bounded release checks the machinery against real official sources.</p><p><strong>{count} research candidates</strong> were discovered by a first-four-headings rule across four procurement cohorts. These are potential population members, not a verified ranking of key UK enterprises.</p><p>One provider tests the route from catalogue evidence to an inspectable research release.</p><a href='{ROUTE}?view=provider#research-panel'>Inspect ADVANIA UK (CCS) LIMITED →</a><p class='rf-small'>Separate retrievals verify literal source support. One source family; no independent semantic or real-world truth guarantee.</p>"
    if segment:
        row=next(r for r in p['taxonomy'] if r['id']==segment);title=row['label']
        members=[r for r in pop['records'] if segment in r['primary_cohorts']]
        panel=f"<span class='ux-status uncertain'>Taxonomy / research scope</span><p>{e(row['boundary'])}</p>"+("<h3>Discovered catalogue labels</h3><ul>"+''.join(f"<li>{e(r['name'])}</li>" for r in members)+"</ul><p class='rf-small'>Legal identity, significant UK operations, scale and ecosystem role still require evidence. Catalogue membership alone proves none of these.</p>" if members else "<p>No independently verified population evidence retained for this category yet. This is a gap, not an empty market.</p>")
        panel+=f"<a href='{ROUTE}?view=evidence#research-panel'>Inspect source passages →</a>"
    elif view=='provider':
        title='ADVANIA UK (CCS) LIMITED'
        selected=[c for c in claims if c['source_id']=='TECH-PROVIDER']
        panel="<span class='ux-status'>Literal-source provider baseline / partial</span><p>The published government supplier page provides a named catalogue entry. It does not establish product ownership, customer implementation, revenue, strategy or buying intent.</p><div class='rf-provider'><strong>Identity guard</strong><p>ADVANIA UK (CCS) LIMITED and ADVANIA UK LIMITED remain separate catalogue labels. No automatic brand, parent or registry merge.</p></div><h3>Still unknown</h3><p>Legal-register linkage, UK operating significance, business model, divisions, strategy, financial scale and transformation priorities.</p>"+evidence(selected,receipts)
    elif view=='evidence':
        title='Inspect the evidence'
        # One located excerpt per source rather than repeating it for each extracted name.
        unique={r['source_id']:r for r in claims};panel="<p>Five official pages, ten separate acquisition receipts. Only short permitted name/label excerpts are retained; original page bytes are not archived.</p>"+evidence(list(unique.values()),receipts)+"<p class='rf-small'>Contains public sector information licensed under the Open Government Licence v3.0. Source: Government Commercial Agency. No endorsement.</p><a href='https://www.gca.gov.uk/terms-and-conditions'>Source content terms ↗</a>"
    elif view=='gaps':
        title='What should research do next?'
        panel="<p>Baseline breadth is specified, not falsely marked complete. Fresh retrieval does not make an undated publication current.</p><ol>"+''.join(f"<li>{e(step)}</li>" for step in pop['next_population_increment'])+"</ol><h3>Comparable baseline still required</h3><ul>"+''.join(f"<li>{e(g['requirement'])}</li>" for g in content['gaps'])+"</ul><p>No opportunity has been created, captured or qualified by this programme.</p>"
    tabs=''.join(f"<a href='{ROUTE}?view={v}#research-panel' {'aria-current=page' if view==v and not segment else ''}>{label}</a>" for v,label in [('research','Industry research'),('overview','Programme'),('provider','Provider baseline'),('evidence','Evidence & assurance'),('gaps','Gaps & next actions')])
    body=f"<style>{STYLE}</style><nav class='ux-breadcrumb' aria-label='Breadcrumb'><a href='/'>Home</a> / <a href='/industries'>Industries</a> / UK technology research</nav><section class='ux-hero' id='content'><p class='eyebrow'>FLORA / Research foundation</p><h1>Understand the UK<br>technology ecosystem.</h1><p>Build evidence before conclusions. Explore coverage, inspect a provider and see exactly what remains unknown.</p></section><div class='rf-metrics'><span><b>7</b>coverage categories</span><span><b>{count}</b>population candidates</span><span><b>1</b>publisher family</span><span><b>0</b>automatic promotions</span></div><nav class='ux-tabs' aria-label='Research views'>{tabs}</nav><div class='rf-layout'><figure class='rf-map'>{svg}<nav class='rf-links' aria-label='Research coverage categories'>{''.join(links)}</nav></figure><section class='rf-panel' id='research-panel' tabindex='-1' aria-labelledby='panel-title'><p class='ux-kicker'>As of {e(content['as_of'])} / release {release['version']}</p><h2 id='panel-title'>{e(title)}</h2>{panel}</section></div><p class='ux-disclosure'>Accepted for bounded research publication. Candidate intelligence; canonical facts and Pipeline authority remain with their existing owners. No private workspace data is read here.</p>"
    return page('UK technology research programme',body,headers,'industries',ROUTE)
