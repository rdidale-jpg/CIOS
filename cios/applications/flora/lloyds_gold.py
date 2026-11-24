"""Optional Lloyds Gold composition, not a new intelligence or financial owner.

Finite navigation over the existing live public research projection. No imports,
run lookup, persistence, canonical promotion or cache. Source withdrawal applies
before diagrams, prose, tables, inspection and accessible text are composed.
"""
from dataclasses import dataclass, replace
from html import escape as e
from pathlib import Path
from urllib.parse import urlencode

from . import design_system as ds, intelligence_presentation as p
from . import visual_streams as v, visual_panels as panels, leadership_agenda as agenda
from . import lloyds_flagship as flagship, lloyds_recovery as recovery
from . import living_enterprise_preview as preview, lloyds_twin_visual as twin
from .supabase_identity import public_read
from .research_intelligence import source_import

PATH = '/enterprises/lloyds/preview/gold'
# Presentation geometry only. Areas do not imply divisional size or premises.
REGIONS = {
 'landscape': (('group','Group overview'),('retail','Retail Banking'),('commercial','Commercial Banking'),
               ('retirement','Insurance, Pensions & Investments'),('economics','Group economics')),
 'inside': (('operations','Operating model'),('capabilities','Capabilities'),('applications','Applications & AI'),
            ('partners','Suppliers & partners'),('programmes','Transformation')),
 'forces': (('markets','Markets & earnings'),('resilience','Regulation & resilience'),('competition','Competition & technology'),
            ('strategy','Strategy & change'),('analysis','Analysis')),
}
GEOMETRY = (('278,125 512,125 510,250 278,250',395,185),
 ('30,675 330,660 350,1070 25,1105',174,890),('55,260 360,260 370,417 55,420',210,330),
 ('480,255 750,245 755,420 490,435',620,330),('350,685 735,675 742,1050 365,1065',548,940))
SUBJECTS = dict(row for rows in REGIONS.values() for row in rows)
# These are finite existing public claim identities, never query-supplied sources.
LLOYDS_IDS = (
 'LBG-Q326-PROFIT','LBG-Q326-DEPOSITS','LBG-Q326-CURVE','LBG-Q326-INVESTMENT',
 'LBG-AR25-DEPOSITS','LBG-AR25-COPILOT','LBG-AR25-MIGRATION','LBG-A2030-PLATFORMS',
 'LBG-A2030-DATA','LBG-A2030-SAVINGS','LBG-A2030-CIR','LBG-A2030-WALLET','LBG-A2030-INVESTMENT',
 'LBG-ENVOY-GOOGLE','LBG-ENVOY-CONTROLS','LBG-BRAND26-TIMING','LBG-BRAND26-NO-ROLES',
 'LBG-AI26-REPORTED','LBG-AI26-EXPECTED')
EXTERNAL_IDS = ('UK-RATE-NOV26','UK-PRA-REPORT27','UK-FCA-REPORT27','treasury-payments')
SWOT = tuple(row for key,_,rows in flagship.VIEWS if key in {'swot','swot-more'} for row in rows)
APPS = {
 'envoy': ('Envoy','Disclosed Lloyds AI platform',('LBG-ENVOY-CONTROLS','LBG-ENVOY-GOOGLE'),
           'AI development and monitoring · conceptual capability association',
           'Google Cloud is a disclosed collaborator. This is not proof of a contract, installed Google product, or Group-wide cloud dependency.'),
 'copilot': ('Microsoft Copilot','Disclosed colleague licences',('LBG-AR25-COPILOT',),
             'Colleague productivity · conceptual capability association',
             'Licence deployment is not active use, an application inventory, a contract schedule or realised net productivity.'),
}
DETAILS = {
 'group': ('economics','sources'), 'retail': ('model','sources'), 'commercial': ('model','sources'),
 'retirement': ('model','sources'), 'economics': ('comparison','central','sources'),
 'operations': ('credit','service','people','sources'), 'capabilities': ('risk','technology','data','sources'),
 'applications': ('envoy','copilot','sources'), 'partners': ('google','microsoft','sources'),
 'programmes': ('legacy','ai','brand','colleague','curve','sources'),
 'markets': ('mechanism','sources'), 'resilience': ('applicability','sources'),
 'competition': ('payments','ai','sources'), 'strategy': ('timeline','options','goals','sources'),
 'analysis': tuple('theme-'+str(i) for i in range(8))+('sources',),
}
FOCUS_FACTS = {
 'group':('LBG-Q326-PROFIT','LBG-Q326-DEPOSITS','LBG-AR25-MIGRATION','LBG-A2030-CIR'), 'economics':tuple(recovery.MEASURES)+('LBG-A2030-CIR','LBG-A2030-SAVINGS','LBG-Q326-INVESTMENT','LBG-A2030-INVESTMENT'),
 'retail':('LBG-BRAND26-TIMING','LBG-BRAND26-NO-ROLES'), 'commercial':(), 'retirement':(),
 'operations':('LBG-BRAND26-TIMING','LBG-BRAND26-NO-ROLES','LBG-AR25-COPILOT'),
 'capabilities':('LBG-AR25-MIGRATION','LBG-A2030-DATA','LBG-ENVOY-CONTROLS'),
 'applications':tuple(dict.fromkeys(k for row in APPS.values() for k in row[2]))+('LBG-AI26-REPORTED','LBG-AI26-EXPECTED'),
 'partners':('LBG-ENVOY-GOOGLE','LBG-AR25-COPILOT'),
 'programmes':('LBG-AR25-MIGRATION','LBG-A2030-PLATFORMS','LBG-ENVOY-CONTROLS','LBG-ENVOY-GOOGLE',
                'LBG-BRAND26-TIMING','LBG-BRAND26-NO-ROLES','LBG-AR25-COPILOT','LBG-Q326-CURVE','LBG-A2030-WALLET'),
 'markets':('UK-RATE-NOV26','LBG-Q326-DEPOSITS','LBG-A2030-CIR'),
 'resilience':('UK-PRA-REPORT27','UK-FCA-REPORT27','LBG-A2030-PLATFORMS'),
 'competition':('LBG-A2030-WALLET','treasury-payments','LBG-A2030-DATA','LBG-ENVOY-CONTROLS'),
 'strategy':('LBG-AR25-MIGRATION','LBG-Q326-CURVE','LBG-Q326-INVESTMENT','UK-PRA-REPORT27',
             'LBG-A2030-PLATFORMS','LBG-A2030-INVESTMENT','LBG-A2030-CIR','LBG-A2030-SAVINGS','LBG-A2030-WALLET'),
 'analysis':tuple(dict.fromkeys(k for _,keys,_ in SWOT for k in keys)),
}

@dataclass(frozen=True)
class State:
    stream: str = 'landscape'
    focus: str = 'group'
    subject: str = 'group'
    detail: str = ''


def resolve(query):
    if (set(query)-{'stream','focus','subject','detail'}
            or any(not isinstance(a,list) or len(a)!=1 or not isinstance(a[0],str) for a in query.values())):
        raise ValueError('Unsupported enterprise view')
    stream=query.get('stream',['landscape'])[0]
    if stream not in REGIONS:raise ValueError('Unsupported perspective')
    focus=query.get('focus',[REGIONS[stream][0][0]])[0]
    subject=query.get('subject',[focus])[0]; detail=query.get('detail',[''])[0]
    if (focus not in dict(REGIONS[stream]) or subject not in SUBJECTS
            or (detail and detail not in DETAILS[focus])):raise ValueError('Unsupported selection')
    return State(stream,focus,subject,detail)


def href(state, *, stream=None, focus=None, detail=None, subject=None):
    target=stream or state.stream
    if focus is None:
        # Preserve the originating subject, so switching back restores division.
        focus=state.subject if state.subject in dict(REGIONS[target]) else state.focus if state.focus in dict(REGIONS[target]) else REGIONS[target][0][0]
    if detail is None:detail=state.detail if target==state.stream and focus==state.focus else ''
    return PATH+'?'+urlencode({'stream':target,'focus':focus,'subject':subject or state.subject,'detail':detail})+'#visual-content'


def link(state,label,**kw):
    kw.setdefault('detail','')
    return '<a href="'+e(href(state,**kw),quote=True)+'">'+e(label)+'</a>'


def facts_for(data):
    if data.get('enterprise_twin_id')!='BK-ENT-001' or p.restricted_metadata(data):return {}
    facts={k:s for k,s in flagship._facts(data,extra_ids=LLOYDS_IDS+EXTERNAL_IDS).items() if p.eligible(s)}
    for key,(unit,period) in recovery.MEASURES.items():
        item=recovery._measure(facts.pop(key,None),unit,period)
        # Preserve the reviewed value-to-disclosure binding, not just its unit.
        if (item and item.value.is_finite() and item.value>=0
                and str(item.value) in item.text.replace(',', '')
                and any(str(item.value) in source.quote.replace(',', '') for source in item.sources)):
            facts[key]=item
    # Identity remains bound to the existing public assessment, never a private
    # model lookup or a same-name bank. Statement scope alone is insufficient.
    claims={c['id']:c for c in data['claims']}
    return {k:s for k,s in facts.items() if not k.startswith('LBG-') or (s.scope==recovery.GROUP
            and claims[k].get('asset_id')=='BK-ENT-001'
            and all(source.publisher=='Lloyds Banking Group' for source in s.sources))}


def reported(facts,keys):
    return ''.join('<div data-claim-id="'+k+'">'+p.render(facts[k],compact=True)+'</div>' for k in keys if k in facts)


def interpretation(facts,keys,text):
    return preview.insight(facts,keys,text)


def table(headings,rows,caption):
    return ('<div class="gold-table" role="region" tabindex="0" aria-label="'+e(caption,quote=True)+'"><table><caption>'+e(caption)
            +'</caption><thead><tr>'+''.join('<th scope="col">'+e(x)+'</th>' for x in headings)+'</tr></thead><tbody>'
            +''.join('<tr>'+''.join(('<th scope="row">' if i==0 else '<td>')+text+('</th>' if i==0 else '</td>') for i,text in enumerate(row))+'</tr>' for row in rows)+'</tbody></table></div>')


def scene(state,facts):
    areas=[]
    for (key,label),(points,x,y) in zip(REGIONS[state.stream],GEOMETRY):
        words=label.split(' & ') if len(label)>22 else [label]
        if key=='retirement':words=['Insurance, Pensions','& Investments']
        if key=='competition':words=['Competition','& technology']
        text=''.join(f'<tspan x="{x}" dy="{0 if i==0 else 27}">{e(word)}</tspan>' for i,word in enumerate(words))
        areas.append(f'<a data-region-key="{key}" aria-label="{e(label,quote=True)}" href="{e(href(state,focus=key,subject=key,detail=''),quote=True)}"'
                     +(' aria-current="true"' if key==state.focus else '')+f'><polygon class="area" points="{points}"/>'
                     f'<g class="region-label"><rect x="{x-124}" y="{y-27}" width="248" height="{78 if len(words)>1 else 54}" rx="9"/>'
                     f'<text x="{x}" y="{y+6}">{text}</text></g></a>')
    return ('<aside id="left" data-region="left" aria-label="Lloyds illustrated enterprise"><div class="le-sticky">'
            '<button type="button" class="le-compact" aria-expanded="true" aria-controls="enterprise-scene">Explore Lloyds <span aria-hidden="true">−</span></button>'
            '<figure id="enterprise-scene" class="le-scene"><img src="'+v.ASSET_BASE+twin.ART+'" width="768" height="1152" '
            'alt="Illustrative banking enterprise with customer spaces, operating floors and technology rooms; not actual Lloyds premises">'
            '<svg viewBox="0 0 768 1152" aria-label="Select an enterprise subject">'+''.join(areas)+'</svg>'
            '<figcaption>Illustrative enterprise · areas do not encode financial scale</figcaption></figure></div></aside>')


def economics(state,facts,issues=()):
    body='<p class="le-deck">Deposits fund lending. Service income adds to interest income. Costs, credit losses and capital shape the return.</p>'
    body+='<div class="gold-economic-map" aria-label="Conceptual Group economic mechanism"><span>Funding<small>Deposits & other sources</small></span><span>Lending & services<small>Interest & fees</small></span><span>Earnings<small>After costs & credit losses</small></span><span>Capital<small>Absorbs risk; constrains growth</small></span></div>'
    body+='<p class="le-limit">Conceptual model · not a measured allocation or accounting reconciliation.</p>'
    body+='<div class="le-measures">'+preview.measures(facts)+'</div>'
    stocks=[(key,label) for key,label in [('LBG-AR25-DEPOSITS','31 December 2025'),('LBG-Q326-DEPOSITS','30 September 2026')] if key in facts]
    if stocks:
        # Presentation only over existing typed, validated statements; no recipe,
        # new values, canonical facts or Financial runs are created.
        maximum=max(facts[key].value for key,_ in stocks)
        body+='<figure class="gold-stocks"><figcaption>Group customer deposits · GBP billion</figcaption>'
        for key,label in stocks:
            item=facts[key];p.note_editorial_sources(item.sources)
            body+='<div data-claim-id="'+key+'"><span>'+label+'</span><meter min="0" max="'+str(maximum)+'" value="'+str(item.value)+'" aria-label="Deposits at '+label+'">'+str(item.value)+'</meter><strong>£'+str(item.value)+'bn</strong></div>'
        body+='<p class="le-limit">Reported stocks at two dates. Zero-based bars; a stock difference is not an adjusted deposit flow. Profit above covers nine months and uses a different unit of time.</p></figure>'
    funding=next((row for row in issues if row.key=='funding-base'),None)
    if funding and all(key in facts for key in ('LBG-AR25-DEPOSITS','LBG-Q326-DEPOSITS')):
        body+=''.join('<div data-owner-item="funding-stock-change">'+p.render(item,compact=True)+'</div>'
                      for item in funding.facts if item.semantic_type=='calculated' and p.eligible(item))
        body+='<p class="le-limit">Arithmetic comparison of published stocks; not adjusted for consolidation, transfers or other balance-sheet effects. Not an organic inflow or earnings measure.</p>'
    if state.detail=='central':
        body+='<h2>Central / Equity and the Group tie-out</h2><p>Segment underlying profit and Group statutory profit have different accounting bases. Central items and the statutory bridge must remain separate; no residual is allocated to a business.</p><p>New segment and reconciliation figures are not published in this view.</p>'
    else:
        body+=table(('Business','Economic mechanism','Financial boundary'),[
            (link(state,'Retail Banking',focus='retail',subject='retail'),'Interest on loans and savings; service income','No Group balance or profit allocated to Retail'),
            (link(state,'Commercial Banking',focus='commercial',subject='commercial'),'Business lending, deposits and payment services','Transfer pricing and risk costs matter'),
            (link(state,'Insurance, Pensions & Investments',focus='retirement',subject='retirement'),'Long-term savings and policyholder obligations','Insurance accounting is not banking net interest margin'),
            (link(state,'Central / Equity',focus='economics',detail='central'),'Central items and consolidation','Underlying segments must reconcile to the statutory Group'),
        ],'Different businesses, different economics')
    if state.detail=='comparison':
        body+=economic_decisions()
        body+=reported(facts,('LBG-A2030-CIR','LBG-A2030-SAVINGS','LBG-Q326-INVESTMENT','LBG-A2030-INVESTMENT'))
        body+=interpretation(facts,('LBG-A2030-CIR','LBG-A2030-SAVINGS'),'Gross savings and a future cost ratio are management ambitions, not current net profit or money available to suppliers. Revenue, implementation costs and parallel running can change the result.')
    elif not state.detail:body+='<p class="gold-related">'+link(state,'Earnings, efficiency & capital decisions',focus='economics',detail='comparison')+'</p>'
    return body


def economic_decisions():
    return table(
        ('Decision', 'What changes the answer', 'Evidence needed'),
        [
            ('Protect funding economics', 'Deposit mix and pricing can offset growth in total balances.',
             'Deposit mix, effective rates and loan repricing on comparable dates.'),
            ('Separate efficiency from a favourable comparison',
             'Remediation and credit charges can move independently of ordinary operating costs.',
             'Comparable income, operating expense, remediation and impairment on the same basis.'),
            ('Balance growth and capital',
             'New lending and distributions compete for capacity once regulatory and management buffers are considered.',
             'Risk-weighted assets, capital generation, distributions and the capital bridge.'),
        ],
        'How to read Group earnings and capital · analytical framework',
    )


def division(state,facts):
    _,customers,activities,driver,_=next(row for row in twin.DIVISIONS if row[-1]==state.focus)
    body='<p class="le-deck">'+e(customers)+'. '+e(activities)+'.</p>'
    body+='<div class="gold-business"><h2>How value is created</h2><p>'+e(driver)+'.</p><p class="le-limit">Business-model orientation. Group disclosures below do not establish divisional outcomes or allocations.</p></div>'
    rows={'retail':(('Originate & service credit','Assess affordability; book and service credit','Risk assessment, servicing and controls'),('Support the customer','Resolve requests; correct accounts','Customer operations and access controls')),
          'commercial':(('Finance businesses','Evaluate and service business credit','Lending, risk and finance · conceptual'),('Move money','Provide payment and cash-management services','Payments, technology and operations · conceptual')),
          'retirement':(('Build long-term savings','Pensions and investment products','Product, servicing and risk · conceptual'),('Meet obligations','Administer policies and customer outcomes','Operations, finance and data · conceptual'))}
    body+=table(('Value stream','Activities','Durable capabilities'),[(e(a),e(b),e(c)) for a,b,c in rows[state.focus]],'Operating interpretation · not a verified workflow or organisation chart')
    body+=reported(facts,FOCUS_FACTS[state.focus])
    body+='<p class="gold-related">'+link(state,'Group economic context',focus='economics')+' · '+link(state,'Related operating capabilities',stream='inside',focus='capabilities')+'</p>'
    if state.focus in {'retail', 'commercial'}:
        body += '<p class="gold-related">' + link(
            state, 'Explore the credit journey', stream='inside', focus='operations', detail='credit'
        ) + '</p>'
    if not state.detail:body+='<p class="gold-related">'+link(state,'Division & legal entity',detail='model')+'</p>'
    if state.detail=='model':body+='<h2>Division versus legal entity</h2><p>A reporting business is not a single regulated legal entity. No capability-level profit, legal-bank allocation or application ownership is inferred from these navigation labels.</p>'
    return body


def people(state, facts):
    body = '<p class="le-deck">Who serves customers, who runs shared capabilities and what the workforce disclosures establish.</p>'
    body += table(
        ('Organisation lens', 'Executive question'),
        [
            ('Group leadership', 'Who sets the Group objective and which role owns the measured outcome?'),
            ('Reporting businesses', 'Which customer business owns the service or economic result?'),
            ('Shared functions', 'Which function operates the capability and which function tests its controls?'),
            ('External collaborators', 'What delivery obligation, if any, does each legal counterparty hold?'),
        ],
        'How to trace accountability · conceptual, with no inferred reporting lines',
    )
    body += reported(facts, ('LBG-AR25-COPILOT', 'LBG-BRAND26-NO-ROLES'))
    body += '<p class="le-limit">Licences do not establish headcount, adoption, productivity or the split between internal and external delivery. An announcement about roles does not provide a current workforce total or cost trend.</p>'
    body += '<p class="gold-related">' + link(state, 'Disclosed technology and collaborators', focus='partners') + '</p>'
    return body


def operating(state,data,facts,issues=()):
    if state.detail == 'people':
        return people(state, facts)
    body='<p class="le-deck">Customer journeys cross durable capabilities. Shared capabilities are not reporting divisions.</p>'
    body+=table(('Value stream','Activities','Supporting capabilities'),[
        ('Credit origination & servicing','Assess affordability → record a decision → service an account','Lending; risk assessment; finance; technology controls'),
        ('Customer support & service','Receive a request → resolve or escalate → correct the record','Customer operations; servicing; data; access controls'),
    ],'Conceptual operating map · workflow ownership and system topology unverified')
    body+='<p class="gold-related">'+link(state,'Organisation, accountability & workforce',detail='people')+'</p>'
    if state.detail in {'credit','service'}:
        row=recovery.CAPABILITIES[0 if state.detail=='credit' else 2]
        body+='<h2>'+e(row[1])+'</h2><p>'+e(row[4])+'</p><p>'+e(row[3])+'</p>'
        body+=table(('People & accountability','Process','Information & technology'),[('Decision role hypothesis; named mandate Unknown',e(' / '.join(row[2])),'Account and case information; actual application mapping Unknown')],'Operating detail · conceptual, not a verified role or system assignment')
        targets = (
            ('Risk capability', 'capabilities', 'risk'),
            ('Core platform renewal', 'programmes', 'legacy'),
        ) if state.detail == 'credit' else (
            ('Data capability', 'capabilities', 'data'),
            ('Colleague technology', 'applications', 'copilot'),
        )
        body += '<p class="le-limit">Explore related topics. The links do not establish actual system dependencies.</p>'
        body += '<p class="gold-related">' + ' · '.join(
            link(state, label, focus=focus, detail=detail) for label, focus, detail in targets
        ) + '</p>'
        body+='<h3>Commercial investigation</h3><p>Which hand-off causes avoidable repeat work, and what measured customer outcome would demonstrate an improvement? This is an investigation question, not established customer pain or demand.</p>'
    else:body+='<p class="gold-related">'+link(state,'Credit journey detail',detail='credit')+' · '+link(state,'Customer service detail',detail='service')+'</p>'
    body+=reported(facts,FOCUS_FACTS['operations'])
    if state.detail=='service':
        service=next((row for row in issues if row.key=='service-recovery'),None)
        if service:
            outcome='<section class="gold-dossier"><h2>Service outcomes · Lloyds Bank PLC</h2><p>January–June 2026 · this legal bank only, not consolidated Group or Retail reporting segment.</p>'
            outcome+=''.join('<div data-owner-item="'+key+'">'+p.render(item,compact=True)+'</div>'
                          for key,item in zip(('LBG-FCA-H126-RECEIVED','EAI-LBG-CLOSED','EAI-LBG-UPHELD'),service.facts) if p.eligible(item))
            outcome+='<p class="le-limit">Received and closed complaints are different cohorts. Firm-upheld is not independent adjudication. These figures establish no backlog clearance, harm rate, service-quality ranking, avoidable cost or external supplier need.</p></section>'
            body=outcome+body
    return body


def capabilities(state,data,facts):
    rows=[]
    for row in data.get('capabilities',()):
        if source_import.working_restricted(row):continue
        # The owner labels this library conceptual. Never promote relationship
        # edges or use its presence to assert an installed app or team owner.
        if row['id'] not in {'CAP-STRATEGY','CAP-CHANNEL','CAP-SERVICE','CAP-DEPOSITS','CAP-FINANCE','CAP-LENDING','CAP-PAYMENTS','CAP-RISK','CAP-TECH','CAP-DATA'}:continue
        rows.append((e(row['title']),'Conceptual capability; ownership and application mapping unverified'))
    body='<p class="le-deck">Capabilities describe what the bank must be able to do; value streams describe how work delivers an outcome.</p>'
    body+=table(('Capability','Model status'),rows,'Existing Lloyds capability library')
    body+='<p class="gold-related">'+link(state,'Risk & control',detail='risk')+' · '+link(state,'Technology renewal',detail='technology')+' · '+link(state,'Data & AI',detail='data')+'</p>'
    if state.detail:
        keys={'risk':('LBG-ENVOY-CONTROLS',),'technology':('LBG-AR25-MIGRATION',),'data':('LBG-A2030-DATA',)}.get(state.detail,())
        body+=reported(facts,keys)
        body+='<h2>Capability accountability</h2><p>Accountable team, process ownership, application installation and service-level measures: Unknown. The conceptual association does not establish an enterprise dependency.</p>'
    return body


def applications(state,facts):
    body='<p class="le-deck">Technology disclosures, with different kinds of evidence.</p>'
    rows=[]
    for key,(name,status,keys,capability,note) in APPS.items():
        available=tuple(k for k in keys if k in facts)
        if len(available)!=len(keys):continue
        rows.append((link(state,name,focus='applications',detail=key),e(status),e(capability)))
    body+=table(('Application / product','Disclosed status','Capability association'),rows,'Source-supported examples · not an installed estate inventory') if rows else ''
    body+=reported(facts,('LBG-AI26-REPORTED','LBG-AI26-EXPECTED'))
    body+=interpretation(facts,('LBG-AI26-REPORTED','LBG-AI26-EXPECTED'),'The earlier reported AI contribution and the later expectation use different temporal states. Neither establishes net return after all costs, divisional attribution or external supplier budget.')
    key={'google':'envoy','microsoft':'copilot'}.get(state.detail,state.detail)
    if key in APPS:
        name,status,keys,capability,note=APPS[key]
        available=tuple(k for k in keys if k in facts)
        if len(available)==len(keys):
            body+='<section class="gold-dossier"><h2>'+e(name)+'</h2>'+reported(facts,available)+'<p>'+e(note)+'</p>'
            rows=[('Operating scope','Lloyds Banking Group disclosure; legal operating / contracting entity Unknown'),('Business capability',e(capability)),
                  ('Installation / version',e(status)+'; version Unknown'),('Provider relationship','Google Cloud collaboration disclosed' if key=='envoy' and 'LBG-ENVOY-GOOGLE' in facts else 'Product brand disclosed; contracting counterparty Unknown'),
                  ('Contracted service','Unknown'),('Support expiry','Unknown'),('Contract end / renewal','Unknown'),
                  ('Programme dependency','No verified installation-to-programme or contract dependency'),('Ownership / confidence','Attributed public disclosure; no canonical installation or contract assertion')]
            body+=table(('Field','Established boundary'),rows,'Application detail · Unknown means no supported assertion')
            body+='<p class="gold-related">'+link(state,'Evidence & dates',detail='sources')+'</p></section>'
    return body


def partners(state,facts):
    body='<p class="le-deck">A collaboration, a product licence and a contract are different relationships.</p>'
    rows=[]
    if 'LBG-ENVOY-GOOGLE' in facts:rows.append((link(state,'Google Cloud',detail='google'),'Disclosed Envoy collaborator','No contracting entity, spend, workshare or renewal established'))
    if 'LBG-AR25-COPILOT' in facts:rows.append((link(state,'Microsoft Copilot',detail='microsoft'),'Disclosed licences; product context','No supplier contract or service-term inference'))
    body+=table(('Provider / product','Supported connection','Boundary'),rows,'Disclosed connections · not a contract or dependency graph') if rows else ''
    body+=reported(facts,FOCUS_FACTS['partners'])
    if state.detail in {'google','microsoft'}:body+=applications(state,facts)
    return body


def programmes(state,data,facts):
    body='<p class="le-deck">Different kinds of change, at different points in delivery.</p>'
    names={'legacy':'PROG-LBG-LEGACY','ai':'PROG-LBG-AI','brand':'PROG-LBG-BRAND','colleague':'PROG-LBG-COLLEAGUE','curve':'PROG-LBG-CURVE'}
    rows=[]
    for key,ident in names.items():
        row=next((r for r in data.get('programmes',()) if r['id']==ident),None)
        keys=tuple(k for k in row['claim_ids'] if k in facts) if row and not source_import.working_restricted(row) else ()
        if not keys:continue
        phase='Completion reported; integration unverified' if key=='curve' else 'Reported licences; adoption unverified' if key=='colleague' else 'Published plan or platform disclosure; delivery progress unverified'
        rows.append((link(state,row['title'],detail=key),phase))
        if state.detail==key:
            body+='<section class="gold-dossier"><h2>'+e(row['title'])+'</h2>'+reported(facts,keys)
            body+=table(('Accountability','Commercial boundary','Outcome'),[('Programme owner Unknown','Funding, procurement, external scope and dates Unknown','Delivery and realised benefit Unknown')],'Programme detail · no work package or buying intent inferred')+'</section>'
    return body+table(('Change','What is actually established'),rows,'Transformation portfolio · evidence-backed disclosures, not project status')


def analysis(state,facts):
    body='<p class="le-deck">Eight strategic themes. Four familiar quadrants.</p><div class="gold-swot" aria-label="Four-quadrant SWOT">'
    for quadrant in ('Strength','Weakness','Opportunity','Threat'):
        cards=[]
        for index,(title,keys,_) in enumerate(SWOT):
            if title.startswith(quadrant+' · ') and all(k in facts for k in keys):
                cards.append(link(state,title.split(' · ',1)[1],detail='theme-'+str(index)))
        body+='<section><h2>'+quadrant+'</h2>'+''.join(cards)+'</section>'
    body+='</div><p class="le-limit">FLORA analysis, not qualified sales opportunities. Theme availability follows its underlying sources.</p>'
    if state.detail.startswith('theme-'):
        index=int(state.detail.split('-')[1]); title,keys,text=SWOT[index]
        if all(k in facts for k in keys):
            body+='<section class="gold-dossier"><h2>'+e(title)+'</h2>'+interpretation(facts,keys,text)+reported(facts,keys)
            body+='<h3>Counter-evidence and decision boundary</h3><p>'+e({0:'An existing governed platform and controls are a capability already in place; no effectiveness result is established.',
             1:'Published renewal work is a management response; it does not establish an estate failure or missed milestone.',2:'Acquisition completion is already a decision taken. Adoption, integration and open external scope are not established.',
             3:'No Lloyds-specific outage or reporting-readiness failure is established by the external timetable.',4:'Aggregate deposit stocks do not reveal account mix, organic flows or cost of funding.',
             5:'The reported contribution is evidence of existing capability; net benefit and later actual delivery are not established.',6:'Controls and a stated data priority already exist; no unserved customer need is established.',7:'Management has a renewal response. No overrun, disruption or causal savings shortfall is established.'}[index])+'</p>'
            body+='<h3>Next commercial investigation</h3><p>'+e((
                'Which Envoy controls have been independently tested, and what adoption or service result accompanies them?',
                'Which customer service depends on an application scheduled for retirement, and what recovery evidence exists for its cutover?',
                'What customer adoption or integration milestone follows the completed Curve transaction, and which decisions remain open?',
                'Which regulated entity and critical service falls within the dated reporting scope, and what readiness evidence exists?',
                'What deposit mix and repricing data would distinguish balance growth from lower-cost funding?',
                'Which costs, baselines and attribution rules reconcile reported AI contribution to net realised benefit?',
                'Which customer service outcome is measured against the data priority, and what existing capability already addresses it?',
                'Which retirement milestone limits dual running, and what continuity constraint determines its pace?'
            )[index])+' No buyer mandate, budget or procurement is inferred.</p></section>'
    return body


GOALS = (
    ('Current performance context', 'Investment at the end of the strategic cycle', 'LBG-Q326-INVESTMENT',
     'Compare delivered milestones, spend and service continuity on the same reporting basis.'),
    ('Medium-term transformation', 'Reduce legacy platforms', 'LBG-A2030-PLATFORMS',
     'Which services can retire old platforms, and what evidence supports a safe cutover?'),
    ('Medium-term transformation', 'Invest in change', 'LBG-A2030-INVESTMENT',
     'Which investments are committed, and which depend on delivery or future decisions?'),
    ('Longer-term ambition', 'Improve cost efficiency', 'LBG-A2030-CIR',
     'Use a comparable period and cost basis before judging progress.'),
    ('Longer-term ambition', 'Deliver gross savings', 'LBG-A2030-SAVINGS',
     'Which recurring costs are removed after implementation and parallel running?'),
    ('Medium-term transformation', 'Develop wallet and payment propositions', 'LBG-A2030-WALLET',
     'Which customer outcome is measured, and what would distinguish adoption from delivery?'),
)


def strategy_goals(facts):
    body = '<p class="le-deck">Read each management commitment alongside the evidence needed to judge delivery.</p>'
    groups = {}
    for row in GOALS:
        if row[2] in facts:
            groups.setdefault(row[0], []).append(row)
    if not groups:
        return body + '<p>No eligible strategy disclosures are available for this view.</p>'
    anchors = {horizon: horizon.lower().replace(' ', '-') for horizon in groups}
    body += '<nav class="gold-related" aria-label="Strategy horizons">' + ' · '.join(
        f'<a href="#strategy-{anchors[horizon]}">{e(horizon)}</a>' for horizon in groups
    ) + '</nav>'
    for horizon, rows in groups.items():
        body += f'<section class="gold-dossier" id="strategy-{anchors[horizon]}"><h2>{e(horizon)}</h2>'
        for _, title, key, question in rows:
            body += '<h3>' + e(title) + '</h3>' + reported(facts, (key,))
            if key == 'LBG-A2030-PLATFORMS' and 'LBG-AR25-MIGRATION' in facts:
                body += '<p><strong>Earlier disclosed progress</strong> · A separate historical milestone on a different reporting horizon.</p>'
                body += reported(facts, ('LBG-AR25-MIGRATION',))
            body += '<p><strong>Test progress</strong> · ' + e(question) + '</p>'
        body += '</section>'
    return body + '<p class="le-limit">Comparable actuals and named delivery owners are shown only when established. A Group objective does not establish work-package ownership or supplier demand.</p>'


def forces(state,facts):
    if state.focus=='analysis':return analysis(state,facts)
    if state.focus=='strategy':
        if state.detail == 'goals':
            return strategy_goals(facts)
        body='<p class="le-deck">Management direction and the sequence of change.</p>'+preview.timeline(facts)
        body+=reported(facts,('LBG-A2030-SAVINGS','LBG-Q326-INVESTMENT','LBG-A2030-INVESTMENT'))
        if state.detail=='options':
            for title,keys,text in next(rows for key,_,rows in flagship.VIEWS if key=='options'):
                if all(k in facts for k in keys):body+='<h2>'+e(title)+'</h2>'+interpretation(facts,keys,text)
        else:body+='<p class="gold-related">'+link(state,'Goals & tests of progress',detail='goals')+' · '+link(state,'Strategic alternatives & trade-offs',detail='options')+'</p>'
        return body
    keys=FOCUS_FACTS[state.focus]
    deck={'markets':'Funding and asset repricing can move at different speeds.',
          'resilience':'A regulatory timetable is dated context; enterprise exposure needs its own evidence.',
          'competition':'Payments and AI can change the route to the customer.'}[state.focus]
    body='<p class="le-deck">'+deck+'</p>'+reported(facts,keys)
    if state.focus=='markets':
        body+=interpretation(facts,('UK-RATE-NOV26',),'If funding costs reprice before asset yields, spread can narrow; the reverse timing can widen it. No Lloyds-specific sensitivity, profit effect or response is established by the rate decision.')
    elif state.focus=='resilience':
        body+=interpretation(facts,('UK-PRA-REPORT27','LBG-A2030-PLATFORMS'),'A reporting timetable and a core-renewal priority make service continuity a relevant analytical connection. They do not establish Lloyds readiness, a control failure or a mandated remediation programme.')
    else:
        body+=interpretation(facts,('LBG-A2030-WALLET','treasury-payments'),'A management payments priority and a historical policy pilot describe potential competition for customer interaction. Neither establishes adoption, a new entrant launch or supplier demand.')
    if state.detail:
        body+=table(('Layer','Conclusion'),[('External condition','Use the dated source statement above; policy scope is not a firm-level finding'),
            ('Enterprise applicability','Conditional mechanism; exposure not measured'),('Qualified Material Pressure','No qualification or promotion performed'),
            ('Management response','Only the independently attributed Group disclosures shown above'),('Commercial interpretation','An analytical connection; no causal loss or customer need asserted'),
            ('Opportunity','No qualified opportunity, budget, buying group or procurement inferred')],'Pressure reasoning · distinct authorities and certainty')
    else:body+='<p class="gold-related">'+link(state,'Applicability & decision boundaries',detail=DETAILS[state.focus][0])+'</p>'
    return body


def main(state,data,facts,issues=()):
    title=SUBJECTS[state.focus]
    body='<section class="gold-content" data-level="'+('3' if state.detail=='sources' else '2' if state.detail else '0' if state.focus=='group' else '1')+'">'
    body+='<p class="eyebrow">Lloyds Banking Group plc'+(' · From '+e(SUBJECTS[state.subject]) if state.subject!=state.focus else '')+'</p>'
    if state.detail:body+='<p class="gold-back">'+link(state,'← '+title)+'</p>'
    body+='<h1>'+e(title)+'</h1>'
    if state.detail=='sources':
        items=[facts[k] for k in FOCUS_FACTS[state.focus] if k in facts]
        if state.focus in {'operations','economics'}:
            concern='service-recovery' if state.focus=='operations' else 'funding-base'
            row=next((row for row in issues if row.key==concern),None)
            if row:items.extend(item for item in row.facts if p.eligible(item))
        body+='<h2>Evidence, dates & boundaries</h2>'+flagship._source_rows(item for item in items if item.semantic_type!='calculated')
        for item in items:
            if item.semantic_type=='calculated':body+='<h3>Calculated · method</h3>'+p.render(item,compact=True)+'<p>'+e(item.method)+'</p>'
        body+='<p class="le-limit">Lloyds attribution links to the issuer homepage. Direct PDF links remain deferred. These statements remain analytical public research, not canonical acceptance.</p>'
        return body+'</section>'
    if state.stream=='landscape':
        if state.focus=='group' and not state.detail:
            body+='<p class="le-deck">Three customer businesses. Funding, earnings and the work of running the bank.</p>'
            body+='<div class="gold-divisions">'+''.join('<article>'+link(state,title,focus=key,subject=key)+'<p>'+e(customer)+'</p></article>' for title,customer,_,_,key in twin.DIVISIONS)+'</div>'
            body+='<div class="le-measures">'+preview.measures(facts)+'</div>'
            body+=interpretation(facts,('LBG-AR25-MIGRATION','LBG-A2030-CIR'),'The efficiency ambition and platform-renewal priority put the sequencing of change alongside service continuity. They establish strategic direction, not a project-level saving or open buying programme.')
            body+='<p class="gold-related">'+link(state,'Funding, income & earnings',focus='economics')+' · '+link(state,'Organisation & workforce',stream='inside',focus='operations',detail='people')+' · '+link(state,'Management goals',stream='forces',focus='strategy',detail='goals')+'</p>'
        elif state.focus in {'group','economics'}:body+=economics(state,facts,issues)
        else:body+=division(state,facts)
    elif state.stream=='inside':
        if state.focus=='operations':body+=operating(state,data,facts,issues)
        elif state.focus=='capabilities':body+=capabilities(state,data,facts)
        elif state.focus=='applications':body+=applications(state,facts)
        elif state.focus=='partners':body+=partners(state,facts)
        else:body+=programmes(state,data,facts)
    else:body+=forces(state,facts)
    if state.focus not in {'group','analysis'} or state.detail:
        body+='<footer class="gold-inspect">'+link(state,'Evidence & boundaries',detail='sources')+'</footer>'
    return body+'</section>'


@ds.view_scope
def render(query,headers=None):
    state=resolve(query);ctx=v.Context('lloyds',state.stream)
    with p.editorial_view(),public_read():
        data=v.current_data(ctx)
        if data.get('enterprise_twin_id')!='BK-ENT-001' or source_import.working_restricted(data):
            raise PermissionError('Lloyds public research unavailable')
        facts=facts_for(data);issues=agenda.agenda(ctx.scope,data)
        notice=('<section class="le-preview-notice" aria-label="Gold Standard evaluation"><strong>Gold Standard · owner evaluation</strong>'
                '<span><a href="'+preview.PATH+'">Original preview</a> · <a href="'+e(v.url(ctx),quote=True)+'">Current experience</a></span></section>')
        top=panels._top(ctx,headers)
        for stream in REGIONS:
            old=e(v.stream_url(ctx,stream)+'#stream-'+stream,quote=True)
            top=top.replace('href="'+old+'"','href="'+e(href(state,stream=stream),quote=True)+'"')
        markup=panels._frame(ctx,headers,data,issues,(),notice+main(state,data,facts,issues),top=top,left=scene(state,facts),show_layers=False)
        assets=('<link rel="stylesheet" href="'+preview.PATH+'/assets/styles"><link rel="stylesheet" href="'+PATH+'/assets/styles">'
                '<script defer src="'+preview.PATH+'/assets/interactions"></script>')
        return markup.replace('</head>',assets+'</head>').replace('<title>','<title>Gold Standard evaluation · ',1).replace('class="ds-page vp-page"','class="ds-page vp-page le-page gold-page" data-preview="gold-standard" data-focus="'+state.focus+'" data-subject="'+state.subject+'"')


def stylesheet():
    assets=Path(__file__).with_name('visual_stream_assets');path=assets/'lloyds-gold.css'
    if path.is_symlink() or not path.resolve().is_relative_to(assets.resolve()):raise ValueError('Unavailable asset')
    return path.read_bytes(),'text/css; charset=utf-8'
