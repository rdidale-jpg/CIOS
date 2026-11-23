"""Design-only arrangement of the existing FLORA frame and eligible public views.

Serial loopback server, no application route registration or persistence. Temporary
render seams are scoped to this process/request and restored before returning.
"""
from dataclasses import dataclass, replace
from html import escape as e
from http.server import HTTPServer
from pathlib import Path
import argparse
import os
import re
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import parse_qs, urlencode, urlsplit

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from cios.applications.flora import design_system as ds, visual_streams as v, visual_panels as panels
from cios.applications.flora import intelligence_presentation as p, leadership_agenda as agenda
from cios.applications.flora import lloyds_flagship as flagship, lloyds_recovery as recovery
from cios.applications.flora import lloyds_twin_visual as twin
from cios.applications.flora.supabase_identity import public_read
from cios.applications.flora.web.app import FloraWebHandler

HERE = Path(__file__).parent
BASE = '97d316c640c96d99c2301819f8aac00b3b9c1398'
ART = twin.ART
PATH = '/design/lloyds'
# View geometry, not an organisation, dependency graph or new intelligence owner.
REGIONS = {
 'landscape': (
  ('retail','Retail Banking','30,675 330,660 350,1070 25,1105',174,890),
  ('commercial','Commercial Banking','55,245 355,252 370,417 55,420',211,330),
  ('retirement','Insurance, Pensions & Investments','487,238 746,215 755,420 505,435',621,318),
  ('funding','Funding & earnings','360,680 720,670 742,1050 365,1065',548,944)),
 'inside': (
  ('operations','Customer operations','30,675 330,660 350,1070 25,1105',174,890),
  ('credit','Credit & risk','55,245 355,252 370,417 55,420',211,330),
  ('platforms','Platforms & applications','26,445 320,420 330,630 25,640',170,528),
  ('data','Data & AI','515,423 750,400 758,625 515,642',638,523)),
 'forces': (
  ('funding','Rates & funding','30,675 330,660 350,1070 25,1105',174,890),
  ('resilience','Regulation & resilience','330,425 505,420 575,750 340,830',438,663),
  ('competition','Competition','487,238 746,215 755,420 505,435',621,318),
  ('renewal','Renewal & change','515,423 750,400 758,625 515,642',638,523)),
}
SUBJECTS = {key:label for rows in REGIONS.values() for key,label,*_ in rows}
# A view correspondence only. It deliberately makes no enterprise relationship claim.
CORRESPONDENCE = {
 'landscape': {'operations':'retail','credit':'retail','platforms':'funding','data':'commercial','resilience':'funding','competition':'commercial','renewal':'funding'},
 'inside': {'retail':'operations','commercial':'credit','retirement':'operations','funding':'credit','resilience':'platforms','competition':'data','renewal':'platforms'},
 'forces': {'retail':'competition','commercial':'competition','retirement':'resilience','operations':'resilience','credit':'funding','platforms':'renewal','data':'competition'},
}

@dataclass(frozen=True)
class State:
    stream: str = 'landscape'
    focus: str = 'retail'
    subject: str = 'retail'


def resolve(query):
    if set(query)-{'stream','focus','subject'} or any(len(values)!=1 for values in query.values()):
        raise ValueError('Unsupported design state')
    stream=query.get('stream',['landscape'])[0]
    if stream not in REGIONS: raise ValueError('Unsupported perspective')
    focus=query.get('focus',[REGIONS[stream][0][0]])[0]
    subject=query.get('subject',[focus])[0]
    if focus not in {row[0] for row in REGIONS[stream]} or subject not in SUBJECTS:
        raise ValueError('Unsupported subject')
    return State(stream,focus,subject)


def href(state, *, stream=None, focus=None, fragment=''):
    target=stream or state.stream
    if focus is None:
        choices={row[0] for row in REGIONS[target]}
        focus=state.focus if state.focus in choices else CORRESPONDENCE[target].get(state.focus,REGIONS[target][0][0])
    return PATH+'?'+urlencode({'stream':target,'focus':focus,'subject':state.subject})+fragment


def choose(state, key):
    return href(replace(state,subject=key),focus=key,fragment='#visual-content')


def scene(state, facts):
    regions=[]
    for key,label,points,x,y in REGIONS[state.stream]:
        active=key==state.focus
        words=label.split(' & ') if len(label)>23 else [label]
        if key=='retirement': words=['Insurance, Pensions','& Investments']
        text=''.join(f'<tspan x="{x}" dy="{0 if i==0 else 27}">{e(word)}</tspan>' for i,word in enumerate(words))
        regions.append(f'<a href="{e(choose(state,key),quote=True)}" aria-label="{e(label,quote=True)}"'
                       +(' aria-current="true"' if active else '')+f' data-region-key="{key}">'
                       f'<polygon class="area" points="{points}"/><g class="region-label">'
                       f'<rect x="{x-123}" y="{y-28}" width="246" height="{54 if len(words)==1 else 80}" rx="9"/>'
                       f'<text x="{x}" y="{y+5}">{text}</text></g></a>')
    marker=''
    if 'LBG-Q326-CURVE' in facts:
        marker=(f'<a class="change-marker" href="{e(href(state,stream="forces",focus="renewal",fragment="#curve"),quote=True)}" '
                'aria-label="Curve: acquisition reported complete; explore strategic change">'
                '<circle class="marker-hit" cx="698" cy="715" r="56"/><circle cx="698" cy="715" r="33"/><text x="698" y="723">+</text></a>')
    return ('<aside id="left" data-region="left" aria-label="Living enterprise visual navigation">'
            '<div class="le-sticky"><button class="le-compact" type="button" aria-expanded="true" aria-controls="enterprise-scene">'
            'Explore Lloyds <span aria-hidden="true">−</span></button><figure id="enterprise-scene" class="le-scene">'
            f'<img src="{v.ASSET_BASE+ART}" width="768" height="1152" alt="Illustrative living banking enterprise: customer spaces, meeting rooms and technology floors; not Lloyds premises">'
            '<svg viewBox="0 0 768 1152" aria-label="Select an enterprise region">'+''.join(regions)+marker+'</svg>'
            '<figcaption>Illustrative enterprise · not actual premises</figcaption></figure></div></aside>')


def flow(items, *, caption='Illustrative value path · not to scale'):
    return '<figure class="le-flow"><figcaption>'+e(caption)+'</figcaption><ol>'+''.join(
        '<li><span class="le-node" aria-hidden="true">'+str(i+1).zfill(2)+'</span><strong>'+e(title)+'</strong><span>'+e(text)+'</span></li>'
        for i,(title,text) in enumerate(items))+'</ol></figure>'


def reported(facts, keys):
    return ''.join(p.render(facts[key],compact=True) for key in keys if key in facts and p.eligible(facts[key]))


def measures(facts):
    return ''.join(recovery._amount(facts[key],label,period) for key,label,period in (
        ('LBG-Q326-DEPOSITS','Group customer deposits · reported stock','30 September 2026'),
        ('LBG-Q326-PROFIT','Group statutory pretax profit · reported flow','Nine months to 30 September 2026')) if key in facts)


def insight(facts, dependencies, text):
    if not all(key in facts and p.eligible(facts[key]) for key in dependencies): return ''
    for key in dependencies:p.note_editorial_sources(facts[key].sources)
    return '<p class="le-meaning" data-semantic-type="insight"><span class="intelligence-label">FLORA Insight</span> '+e(text)+'</p>'


def swot(facts):
    rows=tuple(row for key,_,rows in flagship.VIEWS if key in {'swot','swot-more'} for row in rows)
    quadrants=[]
    for quadrant in ('Strength','Weakness','Opportunity','Threat'):
        cards=[]
        for index,(label,dependencies,analysis) in enumerate(rows):
            if not label.startswith(quadrant+' · ') or not all(key in facts for key in dependencies): continue
            cards.append((f'swot-{index}',label.split(' · ',1)[1],reported(facts,dependencies)+insight(facts,dependencies,analysis)))
        if cards:quadrants.append(('quadrant-'+quadrant.lower(),quadrant,twin.choices(quadrant+' themes',cards,'themes')))
    return ('<section id="investigate" class="llf le-investigate"><h2>Investigate · SWOT</h2>'
            '<p class="le-limit">Strategic choices for Lloyds; not qualified sales opportunities.</p>'
            +twin.choices('SWOT quadrants',quadrants,'swot')+twin.INTERACTIONS+'</section>')


def timeline(facts):
    rows=next(rows for key,_,rows in flagship.VIEWS if key=='timeline')
    out=[]
    for label,keys,_ in rows:
        eligible=[key for key in keys if key in facts]
        if eligible:out.append('<li><strong>'+e(label)+'</strong>'+reported(facts,eligible[:1])+'</li>')
    return '<section id="timeline"><h2>Strategic change over time</h2><ol class="le-timeline">'+''.join(out)+'</ol></section>'


def main(state, data, facts):
    name=next(row[1] for row in REGIONS[state.stream] if row[0]==state.focus)
    stage={'landscape':'Overview','inside':'Explore','forces':'Investigate'}[state.stream]
    inherited=state.subject!=state.focus
    context=(f' · From {e(SUBJECTS[state.subject])}' if inherited else '')
    body=f'<section id="overview"><p class="eyebrow">{stage} · Lloyds Group{context}</p><h1>{e(name)}</h1>'
    if state.stream=='landscape':
        if state.focus!='funding':
            division=next(row for row in twin.DIVISIONS if row[-1]==state.focus)
            _,customer,activity,driver,_=division
            body+=f'<p class="le-deck">{e(customer)}. {e(activity)}.</p>'
            body+=flow(((customer,'Customers'),(activity,'Products & services'),('Economic value',driver)))
            body+='<p class="le-limit">Business-model orientation, not measured divisional flows or financial allocation.</p>'
            body+='<section id="explore"><h2>Group scale, in context</h2><div class="le-measures">'+measures(facts)+'</div></section>'
        else:
            body+='<p class="le-deck">Funding supports lending. Income meets costs and credit losses.</p>'
            body+=flow((('Funding','Deposits and other funding'),('Lending & services','Interest and service income'),('Earnings','After operating costs and credit losses')))
            body+='<p class="le-limit">Conceptual economic mechanism; balances are stocks and profit is a nine-month flow.</p>'
            body+='<div class="le-measures">'+measures(facts)+'</div>'
        body+=f'<p class="le-next"><a href="{e(href(state,stream="inside"),quote=True)}">Explore how the business operates <span aria-hidden="true">→</span></a></p>'
    elif state.stream=='inside':
        if state.focus in {'operations','credit'}:
            key='customer-operations' if state.focus=='operations' else'risk-assessment'
            _,_,tasks,basis,mechanism=next(row for row in recovery.CAPABILITIES if row[0]==key)
            body+='<p class="le-deck">'+e(mechanism)+'</p>'
            body+=flow((('Credit journey',tasks[0]),('Shared capability',name),('Service journey',tasks[1])),caption='Conceptual activities and durable capability · not an organisation chart')
            body+='<p class="le-limit">'+e(basis)+'</p>'
            if state.focus=='operations':body+=reported(facts,('LBG-BRAND26-TIMING',))
        elif state.focus=='platforms':
            body+='<p class="le-deck">Renew the bank while it runs.</p>'
            body+=flow((('Applications','Current service delivery'),('Continuity','Keep services operating'),('Renewal','Application retirement and core change')),caption='Conceptual operating dependency · actual system topology is not established')
            body+=reported(facts,('LBG-AR25-MIGRATION','LBG-A2030-PLATFORMS'))
            body+='<p class="le-limit">Group disclosures do not identify a divisional system estate or supplier workshare.</p>'
        else:
            body+='<p class="le-deck">Platform controls can make monitoring part of the operating process as AI use scales.</p>'
            body+=flow((('Develop','Build platform tools'),('Operate','Use platform controls'),('Monitor','Review activity')),caption='Conceptual capability sequence; not verified workflow implementation')
            body+=reported(facts,('LBG-ENVOY-CONTROLS','LBG-ENVOY-GOOGLE'))
            body+='<p class="le-limit">An Envoy collaboration does not establish contract scope, estate-wide dependencies or control effectiveness.</p>'
        if inherited:body+='<p class="le-limit">The selected context is retained for orientation. Content is Group-wide; no divisional allocation is asserted.</p>'
        body+=f'<p class="le-next"><a href="{e(href(state,stream="forces"),quote=True)}">Investigate the relevant forces <span aria-hidden="true">→</span></a></p>'
    else:
        if state.focus=='funding':
            body+='<p class="le-deck">Repricing timing can change the spread between lending income and funding costs.</p>'
            body+=flow((('Funding reprices first','Spread can narrow'),('Different timing','Exposure depends on the book'),('Lending reprices first','Spread can widen')),caption='Conditional repricing paths · no Lloyds-specific sensitivity is established')
            body+=reported(facts,('UK-RATE-NOV26',))
            body+='<p class="le-limit">A UK rate decision does not establish a Lloyds response, margin loss or buying demand.</p>'
        elif state.focus=='resilience':
            body+='<p class="le-deck">Reporting requirements have a date; readiness requires enterprise-specific evidence.</p>'
            body+=flow((('Policy','Incident and third-party reporting'),('Implementation','Published March 2027 timetable'),('Continuity','Keep live services resilient')),caption='Regulatory context and conditional mechanism · not a confirmed Lloyds implementation plan')
            body+=reported(facts,('UK-PRA-REPORT27','UK-FCA-REPORT27'))
            body+='<p class="le-limit">Lloyds-specific readiness, exposure and remediation cost are not established by the policy.</p>'
        elif state.focus=='competition':
            body+='<p class="le-deck">Payments and AI change the possible route to the customer.</p>'
            body+=flow((('Payments','Customer interaction'),('Technology','Alternative discovery and service'),('Adoption','Consent, trust and protection')),caption='Conditional competitive mechanism · no entrant launch or customer adoption is established')
            body+=reported(facts,('LBG-A2030-WALLET','LBG-A2030-DATA'))
            body+='<p class="le-limit">Management direction and a policy pilot are not delivered outcomes or evidence of customer demand.</p>'
        else:
            body+='<p class="le-deck">Core renewal links the efficiency ambition with the work of keeping the bank running.</p>'
            body+=flow((('Direction','Efficiency ambition'),('Execution','Retirement and core renewal'),('Constraint','Service continuity and control testing')),caption='Analytical connection of Group disclosures · no project-level savings or causal outcome is established')
            body+=reported(facts,('LBG-A2030-CIR','LBG-AR25-MIGRATION'))
            if 'LBG-Q326-CURVE' in facts:
                body+='<section id="curve" class="le-change"><h2>Curve · reported complete</h2>'+reported(facts,('LBG-Q326-CURVE',))+'<p class="le-limit">Integration progress, external procurement and customer adoption are not established.</p></section>'
            body+=timeline(facts)
        if inherited:body+='<p class="le-limit">Retained selection is context, not proof that this pressure applies to that division or capability.</p>'
        body+=swot(facts)
    return body+'</section>'


@ds.view_scope
def render(state):
    ctx=v.Context('lloyds',state.stream)
    with p.editorial_view(), public_read():
        data=v.current_data(ctx);facts=flagship._facts(data);issues=agenda.agenda(ctx.scope,data)
        for key,(unit,period) in recovery.MEASURES.items():
            item=recovery._claims(data,(key,)).get(key)
            item=recovery._measure(item,unit,period)
            if item:facts[key]=item
        body=main(state,data,facts)
        original_top=panels._top
        def top(context,headers):
            markup=original_top(context,headers)
            for stream in REGIONS:
                old=e(v.stream_url(context,stream)+'#stream-'+stream,quote=True)
                markup=markup.replace('href="'+old+'"','href="'+e(href(state,stream=stream),quote=True)+'"')
            return markup.replace('<!--flora-system-notice-->','<span class="le-design-note">Design preview</span>')
        with patch.object(panels,'_left',lambda *args:scene(state,facts)),patch.object(panels,'_top',top):
            markup=panels._frame(ctx,{},data,issues,(),body)
        # The approved shell constructs these unrelated layer controls. Omit them
        # from this design arrangement; no runtime component/file is modified.
        markup=re.sub(r'<nav class="context-nav" aria-label="Context layers">.*?</nav>','',markup)
        markup=markup.replace('</head>',twin.STYLE+'<link rel="stylesheet" href="/design/living.css"><script defer src="/design/living.js"></script></head>')
        return markup.replace('class="ds-page vp-page"',f'class="ds-page vp-page le-page" data-prototype="design-only" data-focus="{state.focus}" data-subject="{state.subject}"')


class Handler(FloraWebHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        url=urlsplit(self.path)
        if url.path==PATH:
            try:self._html(render(resolve(parse_qs(url.query,keep_blank_values=True))))
            except ValueError:self.send_error(404,'Unsupported design state')
        elif url.path in {'/design/living.css','/design/living.js','/design/preview.html'} and (not url.query or url.path=='/design/preview.html'):
            if url.path=='/design/preview.html':
                try:resolve(parse_qs(url.query,keep_blank_values=True))
                except ValueError:
                    self.send_error(404,'Unsupported design state');return
            path=HERE/Path(url.path).name
            body=path.read_bytes();self.send_response(200);self.send_header('Content-Type','text/css' if path.suffix=='.css' else 'text/html; charset=utf-8' if path.suffix=='.html' else 'text/javascript');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        elif self._public_read_request():super().do_GET()
        else:self.send_error(403,'Design preview exposes public reading only')
    def do_POST(self):self.send_error(405,'Design preview is read-only')
    do_PUT=do_POST
    do_DELETE=do_POST


def serve(port,host):
    with TemporaryDirectory(prefix='flora-living-design-') as directory:
        os.environ.update(FLORA_DATA_DIR=directory,FLORA_ENVIRONMENT='development',FLORA_AUTH_PROVIDER='local',FLORA_TRUST_PROXY_HEADERS='0')
        os.environ.pop('OPENAI_API_KEY',None)
        server=HTTPServer((host,port),Handler)
        print(f'Design-only preview: http://{host}:{port}{PATH}',flush=True)
        try:server.serve_forever()
        finally:server.server_close()

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('--port',type=int,default=8787);cli.add_argument('--host',default='127.0.0.1');args=cli.parse_args();serve(args.port,args.host)
