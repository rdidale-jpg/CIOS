"""Lloyds CEO composition and compatible Gold route, using existing owners.

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
CANONICAL = '/enterprises/lloyds'
LEGACY = '/enterprises/lloyds/legacy'
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
SUBJECTS['people']='Organisation & workforce'
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
DETAILS['people']=('leadership','structure','workforce','sources')
DETAILS['operations']+=tuple('journey-'+key for key in ('credit','payments','service','insurance','risk','data','platforms','finance','support'))
DETAILS['strategy']+=tuple('objective-'+key for key in ('renewal','ai','access','reporting','investment','efficiency','payments'))
DETAILS['economics']+=('funding','income','costs','capital','divisions')
FOCUS_FACTS = {
 'group':('CEO1-ROLE-NUNN-20260322','LBG-Q326-PROFIT','LBG-Q326-DEPOSITS','LBG-AR25-MIGRATION','LBG-A2030-CIR'), 'economics':tuple(recovery.MEASURES)+('LBG-A2030-CIR','LBG-A2030-SAVINGS','LBG-Q326-INVESTMENT','LBG-A2030-INVESTMENT'),
 'retail':('LBG-BRAND26-TIMING','LBG-BRAND26-NO-ROLES'), 'commercial':(), 'retirement':(),
 'people':('LBG-AR25-COPILOT','LBG-BRAND26-NO-ROLES','CEO1-ROLE-NUNN-20260322'),
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
    route: str = PATH


def resolve(query):
    if (set(query)-{'stream','focus','subject','detail'}
            or any(not isinstance(a,list) or len(a)!=1 or not isinstance(a[0],str) for a in query.values())):
        raise ValueError('Unsupported enterprise view')
    stream=query.get('stream',['landscape'])[0]
    if stream not in REGIONS:raise ValueError('Unsupported perspective')
    focus=query.get('focus',[REGIONS[stream][0][0]])[0]
    subject=query.get('subject',[focus])[0]; detail=query.get('detail',[''])[0]
    if (focus not in (set(dict(REGIONS[stream]))|({'people'} if stream=='inside' else set())) or subject not in SUBJECTS
            or (detail and detail not in DETAILS[focus])):raise ValueError('Unsupported selection')
    return State(stream,focus,subject,detail)


def canonical_query(query):
    """Bridge ordinary legacy context without admitting private selectors.

    Historical detail, agenda, specialist and Financial paths keep their owners.
    New focus/subject state is finite and never a canonical model identifier.
    """
    if any(k in query for k in ('analysis','agenda','lens')):return None
    # Legacy contextual overlays retain their existing finite resolver/renderer.
    # Mixed new selectors are not routed around canonical validation.
    if not {'focus','subject'} & set(query) and query.get('layer') in (['regulators'],['suppliers']):return None
    if 'detail' in query and 'focus' not in query:return None
    allowed={'stream','focus','subject','detail','market','layer','selected','reading'}
    if set(query)-allowed or any(not isinstance(a,list) or len(a)!=1 or not isinstance(a[0],str) for a in query.values()):
        raise ValueError('Unsupported enterprise state')
    for key,values in {'market':{'GB'},'layer':{'enterprises'},'selected':{'','lloyds'},'reading':{'facts','insight'}}.items():
        if key in query and query[key][0] not in values:raise ValueError('Enterprise context mismatch')
    result={k:a for k,a in query.items() if k in {'stream','focus','subject','detail'}}
    resolve(result)
    return result


def href(state, *, stream=None, focus=None, detail=None, subject=None):
    target=stream or state.stream
    if focus is None:
        # Preserve the originating subject, so switching back restores division.
        choices=set(dict(REGIONS[target]))|({'people'} if target=='inside' else set())
        focus=state.subject if state.subject in choices else state.focus if state.focus in choices else REGIONS[target][0][0]
    if detail is None:detail=state.detail if target==state.stream and focus==state.focus else ''
    return state.route+'?'+urlencode({'stream':target,'focus':focus,'subject':subject or state.subject,'detail':detail})+'#visual-content'


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
    role=source_import.public_enterprise_role()
    if role:
        src,row=role
        ref=p.Source(src['title'],src['url'],src['publisher'],src['publication_date'],src['reporting_period'],locator=src['excerpts'][0]['locator'])
        facts[row['id']]=p.Statement(row['statement'],'reported',recovery.GROUP,row['period'],(ref,),'reviewed_excerpt','candidate_intelligence',caveats=('Dated role attribution only; current mandate and procurement authority are not established.','Contains public sector information licensed under the Open Government Licence v3.0.'))
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
    regions=REGIONS[state.stream]
    if state.stream=='inside' and (state.route==CANONICAL or state.focus=='people'):
        regions=tuple(('people','Organisation & people') if key=='partners' else (key,label) for key,label in regions)
    for (key,label),(points,x,y) in zip(regions,GEOMETRY):
        words=label.split(' & ') if len(label)>22 else [label]
        if key=='retirement':words=['Insurance, Pensions','& Investments']
        if key=='competition':words=['Competition','& technology']
        text=''.join(f'<tspan x="{x}" dy="{0 if i==0 else 27}">{e(word)}</tspan>' for i,word in enumerate(words))
        areas.append(f'<a data-region-key="{key}" aria-label="{e(label,quote=True)}" href="{e(href(state,focus=key,subject=key,detail=''),quote=True)}"'
                     +(' aria-current="true"' if key==({'partners':'applications'}.get(state.focus,state.focus) if state.route==CANONICAL else state.focus) else '')+f'><polygon class="area" points="{points}"/>'
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
    body+='<div class="gold-economic-map" aria-label="Conceptual Group economic mechanism">'+''.join('<span>'+link(state,title,focus='economics',detail=key)+'<small>'+desc+'</small></span>' for key,title,desc in (('funding','Funding','Deposits & other sources'),('income','Lending & income','Interest & fees'),('costs','Costs & impairment','Running the bank and credit risk'),('capital','Capital & returns','Risk capacity and returns')))+'</div>'
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
    body+='<p class="ceo-unavailable">Reported segment contribution and matched comparisons are unavailable.</p>'
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
            if 'LBG-Q326-CURVE' in facts:
                body+='<section class="ceo-change"><span class="eyebrow">Reported change</span><h2>Curve acquisition reported complete</h2>'+reported(facts,('LBG-Q326-CURVE',))+'<p class="le-limit">Completion is not integration progress or open supplier scope.</p></section>'
            if 'CEO1-ROLE-NUNN-20260322' in facts:
                p.note_editorial_sources(facts['CEO1-ROLE-NUNN-20260322'].sources)
                body+='<p class="ceo-lead-context">'+link(state,'Leadership evidence',stream='inside',focus='people',detail='leadership')+' · Charlie Nunn was identified as Group Chief Executive in March 2026; current mandate verification is unavailable.</p><p class="ceo-attribution">Contains public sector information licensed under the Open Government Licence v3.0.</p>'
            # Keep the existing EAI agenda destinations discoverable, with their
            # current eligibility owner deciding whether each link may appear.
            related=[]
            funding=next((row for row in issues if row.key=='funding-base'),None)
            if funding and funding.facts[-1].semantic_type=='calculated' and p.eligible(funding.facts[-1]):
                body+='<div data-intelligence="funding-base">'+p.render(funding.facts[-1])+'</div>'
                related.append('<a href="/enterprises/lloyds?agenda=funding-base#agenda-insight">Funding comparison</a>')
            if any(row.key=='service-recovery' for row in issues):
                related.append('<a href="/enterprises/lloyds?agenda=service-recovery#agenda-insight">Customer outcomes</a>')
            if related:body+='<p class="gold-related">'+' · '.join(related)+'</p>'
            body+='<p class="gold-related">'+link(state,'Funding, income & earnings',focus='economics')+' · '+link(state,'Organisation & workforce',stream='inside',focus='people',detail='leadership')+' · '+link(state,'Management goals',stream='forces',focus='strategy',detail='goals')+'</p>'
        elif state.focus in {'group','economics'}:body+=_ceo_financial(state,facts,issues)
        else:body+=division(state,facts)
    elif state.stream=='inside':
        if state.focus=='people' or state.focus=='operations' and state.detail=='people':body+=_ceo_people(state,facts)
        elif state.focus=='operations' and state.detail!='service':body+=_ceo_journey(state,data,facts)
        elif state.focus=='operations':body+=operating(state,data,facts,issues)
        elif state.focus=='capabilities':body+=capabilities(state,data,facts)
        elif state.focus=='applications':body+=applications(state,facts)
        elif state.focus=='partners':body+=partners(state,facts)
        else:body+=programmes(state,data,facts)
    elif state.focus=='strategy' and (state.detail=='goals' or state.detail.startswith('objective-')):body+=_ceo_goals(state,facts)
    else:body+=forces(state,facts)
    if state.focus not in {'group','analysis'} or state.detail:
        body+='<footer class="gold-inspect">'+link(state,'Evidence & boundaries',detail='sources')+'</footer>'
    return body+'</section>'


@ds.view_scope
def render(query,headers=None,*,canonical=False):
    state=replace(resolve(query),route=CANONICAL if canonical else PATH);ctx=v.Context('lloyds',state.stream)
    with p.editorial_view(),public_read():
        data=v.current_data(ctx)
        if data.get('enterprise_twin_id')!='BK-ENT-001' or source_import.working_restricted(data):
            raise PermissionError('Lloyds public research unavailable')
        facts=facts_for(data);issues=agenda.agenda(ctx.scope,data)
        notice=('<section class="le-preview-notice" aria-label="Gold Standard evaluation"><strong>Gold Standard · owner evaluation</strong>'
                '<span><a href="'+preview.PATH+'">Original preview</a> · <a href="'+e(v.url(ctx),quote=True)+'">Current experience</a></span></section>')
        if canonical:notice=''
        top=panels._top(ctx,headers)
        for stream in REGIONS:
            old=e(v.stream_url(ctx,stream)+'#stream-'+stream,quote=True)
            top=top.replace('href="'+old+'"','href="'+e(href(state,stream=stream),quote=True)+'"')
        # Preserve the existing opt-in, authorised non-production Canvas replay
        # slot. The existing service owns environment/ACL/lifecycle checks.
        change=''
        if canonical and not state.detail and state.focus==REGIONS[state.stream][0][0]:
            from .memory.commercial_views import commercial_change
            change=commercial_change('lloyds',state.stream,headers)
        markup=panels._frame(ctx,headers,data,issues,(),change+notice+main(state,data,facts,issues),top=top,left=scene(state,facts),show_layers=False)
        assets=('<link rel="stylesheet" href="'+preview.PATH+'/assets/styles"><link rel="stylesheet" href="'+PATH+'/assets/styles">'
                '<script defer src="'+preview.PATH+'/assets/interactions"></script>')
        markup=markup.replace('</head>',assets+'</head>')
        if not canonical:markup=markup.replace('<title>','<title>Gold Standard evaluation · ',1)
        mode='data-experience="lloyds-ceo"' if canonical else 'data-preview="gold-standard"'
        return markup.replace('class="ds-page vp-page"','class="ds-page vp-page le-page gold-page" '+mode+' data-focus="'+state.focus+'" data-subject="'+state.subject+'"')


def stylesheet():
    assets=Path(__file__).with_name('visual_stream_assets');path=assets/'lloyds-gold.css'
    if path.is_symlink() or not path.resolve().is_relative_to(assets.resolve()):raise ValueError('Unavailable asset')
    return path.read_bytes(),'text/css; charset=utf-8'


# Presentation configuration over current owners, not enterprise-model records.
# A role to verify is not a mandate; a conceptual connection is not an estate edge.
JOURNEYS = {
 'credit': ('Lending & credit','Retail / Commercial Banking','Originate → assess affordability and risk → book → service → recover',
            ('CAP-LENDING','CAP-RISK','CAP-FINANCE','CAP-TECH'),('LBG-AR25-MIGRATION',),
            'Loan and funding economics depend on credit quality, repricing and capital. No portfolio-level yield, loss or allocation is established here.',
            'Which credit-service hand-off has a measured customer or control outcome, and which operating entity owns it?'),
 'payments': ('Payments','Retail / Commercial Banking','Initiate payment → authorise → clear and settle → service exceptions',
              ('CAP-PAYMENTS','CAP-RISK','CAP-TECH','CAP-DATA'),('LBG-A2030-WALLET','LBG-Q326-CURVE'),
              'A completed acquisition and a payments priority are decisions already taken. They do not establish integration, adoption or open supplier scope.',
              'What adoption or integration result follows the completed Curve transaction, and which decision remains open?'),
 'service': ('Customer operations','Customer-facing businesses','Receive request → identify need → resolve or escalate → close and learn',
             ('CAP-SERVICE','CAP-CHANNEL','CAP-DATA','CAP-RISK'),('LBG-BRAND26-TIMING','LBG-BRAND26-NO-ROLES'),
             'Access changes can alter the service route. The announcement is not evidence of reduced staffing or a realised service outcome.',
             'Which customer outcome and service channel would distinguish a successful change from displaced demand?'),
 'insurance': ('Insurance, pensions & wealth','Insurance, Pensions & Investments','Design proposition → distribute → administer policies and assets → meet obligations',
               ('CAP-STRATEGY','CAP-SERVICE','CAP-FINANCE','CAP-RISK'),(),
               'Policyholder obligations and long-term asset administration have different economics from banking margin. Allocation and system ownership are unavailable.',
               'Which policy or servicing outcome has a matched financial and operational baseline?'),
 'risk': ('Risk & control','Group / relevant regulated entity','Set risk appetite → assess exposure → apply controls → monitor → remediate',
          ('CAP-RISK','CAP-DATA','CAP-TECH'),('LBG-ENVOY-CONTROLS',),
          'Disclosed controls are an existing management capability. Effectiveness and coverage require evidence; a policy date does not establish a failure.',
          'Which critical service and legal entity is in scope, and what independent control or recovery evidence exists?'),
 'data': ('Data & AI','Group disclosures; divisional ownership unavailable','Prepare data → develop → deploy with controls → monitor outcomes',
          ('CAP-DATA','CAP-TECH','CAP-RISK'),('LBG-A2030-DATA','LBG-ENVOY-CONTROLS','LBG-AI26-REPORTED','LBG-AI26-EXPECTED'),
          'Existing platforms and reported contributions are counter-evidence to an assumed capability gap. Net value, adoption and divisional attribution are unavailable.',
          'Which full-cost baseline and attribution method reconciles AI contribution to net realised customer or operating benefit?'),
 'platforms': ('Platforms & modernisation','Group disclosures; workload ownership unavailable','Identify dependency → sequence retirement → migrate → test recovery → decommission',
               ('CAP-TECH','CAP-DATA','CAP-RISK'),('LBG-AR25-MIGRATION','LBG-A2030-PLATFORMS'),
               'Renewal is already a published management response. No system inventory, cutover commitment, contract workshare or overrun is established.',
               'Which retirement milestone limits dual running, and what continuity evidence constrains its pace?'),
 'finance': ('Finance & treasury','Group and distinct reporting businesses','Manage funding → price risk and capital → report → reconcile → allocate under governance',
             ('CAP-FINANCE','CAP-DEPOSITS','CAP-RISK'),('LBG-Q326-DEPOSITS','LBG-Q326-PROFIT'),
             'Funding stocks, period profit and capital are different measures. Group results cannot be allocated to a product, capability or legal bank.',
             'Which matched-period income, cost, credit and capital inputs would explain the change in economic return?'),
 'support': ('People, organisation & suppliers','Group; accountable functions unavailable','Define role and skills → provide shared services → assure delivery → review outcomes',
             ('CAP-STRATEGY','CAP-SERVICE','CAP-TECH'),('LBG-AR25-COPILOT','LBG-ENVOY-GOOGLE'),
             'Licences and collaboration are not employee counts, an outsourced-function map, contract scope or renewal timing.',
             'Which function owns the service outcome, and what evidence establishes the internal/external delivery boundary?'),
}
OBJECTIVES = (
 ('renewal','2026 priority','Retire applications while maintaining service',('LBG-AR25-MIGRATION','LBG-A2030-PLATFORMS'),'Technology / service owner to verify','legacy','platforms'),
 ('ai','FY2025 reported / 2026 expectation','Turn AI capability into measured benefit',('LBG-AI26-REPORTED','LBG-AI26-EXPECTED','LBG-ENVOY-CONTROLS'),'Business benefit and control owners to verify','ai','data'),
 ('access','Changes planned through 2027','Keep the customer route to service clear',('LBG-BRAND26-TIMING','LBG-BRAND26-NO-ROLES'),'Customer service / channel owner to verify','brand','service'),
 ('reporting','18 March 2027 regulatory timetable','Prepare incident and third-party reporting',('UK-PRA-REPORT27','UK-FCA-REPORT27'),'Applicable regulated entity / risk owner to verify',None,'risk'),
 ('investment','2027 investment plan','Sequence investment against delivery and returns',('LBG-Q326-INVESTMENT','LBG-A2030-INVESTMENT'),'Finance and programme sponsor to verify','legacy','finance'),
 ('efficiency','2030 management ambition','Improve efficiency without confusing gross and net',('LBG-A2030-CIR','LBG-A2030-SAVINGS'),'Executive objective; delegated owner unavailable','legacy','platforms'),
 ('payments','2027–2030 strategic priority','Develop payments and customer interaction',('LBG-A2030-WALLET','LBG-Q326-CURVE'),'Payments / proposition owner to verify','curve','payments'),
)


GOAL_DECISIONS = {
 'renewal': ('Existing migration and platform plans are management responses, not evidence of an unawarded modernisation programme.', 'Which remaining retirement decision controls dual-running cost, and which recovery test limits its timing?'),
 'ai': ('Reported contribution and deployed controls demonstrate existing capability; gross contribution does not establish full-cost net benefit.', 'Which realised benefit survives model, infrastructure, change and control costs, and who signs off the attribution?'),
 'access': ('Planned brand changes do not establish job cuts, customer attrition or a procurement event.', 'How will service continuity and customer comprehension be measured through the announced brand transition?'),
 'reporting': ('A regulatory timetable establishes a requirement only for its applicable perimeter; it does not establish a Lloyds control failure.', 'Which regulated entity must report which incident, and what evidence shows its existing provider inventory and reporting process meet the deadline?'),
 'investment': ('An announced investment plan is a management commitment; external scope and unallocated supplier spend are not established.', 'Which sequencing choice is still open between committed programmes, and what return or service evidence would change that choice?'),
 'efficiency': ('A cost/income ambition and gross savings target do not establish realised net savings or a service-quality improvement.', 'Which expense, income and remediation movements explain efficiency on a consistent basis, after the cost of change?'),
 'payments': ('The completed Curve acquisition is an existing management response; integration scope, vendor selection and unallocated external work are unproven.', 'Which customer interaction or payments outcome would establish value from the existing strategy, without assuming a new buying programme?'),
}


def _ceo_people(state,facts):
    body='<p class="le-deck">Leadership, reporting businesses and shared capabilities are different organisational views.</p>'
    role=facts.get('CEO1-ROLE-NUNN-20260322')
    if state.detail in {'','leadership','people'}:
        if role:
            body+='<section class="ceo-leader"><span class="eyebrow">Dated leadership evidence</span><h2>Charlie Nunn</h2>'+reported(facts,('CEO1-ROLE-NUNN-20260322',))+'<p class="le-limit">This source establishes the role attribution in March 2026, not a verified current mandate or purchasing authority.</p><p class="ceo-attribution">Contains public sector information licensed under the Open Government Licence v3.0.</p></section>'
        body+=table(('Dimension','Available view'),[
          ('Group executive leadership','Current roster / delegated mandates: Unavailable'),
          ('Board and governance','Current public role projection: Unavailable'),
          ('Reporting businesses','Retail; Commercial Banking; Insurance, Pensions & Investments'),
          ('Legal entities','Not interchangeable with reporting segments; legal ownership map unavailable'),
        ],'Organisation · no inferred reporting lines')
    if state.detail=='structure':
        body+='<div class="ceo-hierarchy"><strong>Lloyds Banking Group plc</strong><span>Reporting businesses · not legal subsidiaries</span><div>'+''.join('<article>'+link(state,title,stream='landscape',focus=key,subject=key)+'<p>'+e(customer)+'</p></article>' for title,customer,_,_,key in twin.DIVISIONS)+'</div></div>'
        body+=table(('Function view','Durable capability','Accountability'),[
         ('Finance / treasury','Finance and funding','Named owner / mandate unavailable'),('Customer operations','Servicing and channels','Named owner / mandate unavailable'),
         ('Risk and control','Risk assessment and controls','Named owner / mandate unavailable'),('Technology / data','Platforms, data and AI','Named owner / mandate unavailable'),
        ],'Conceptual function lenses · not a verified organisation chart')
    if state.detail=='workforce':
        body+='<h2>Workforce measures</h2><p class="ceo-unavailable">Comparable workforce totals and distribution are unavailable in this view.</p>'
        body+=table(('Measure','Current eligible result'),[(x,'Unavailable') for x in ('Employee headcount / FTE','Prior-period movement','Business / function / geography split','Technology and AI workforce','Workforce cost / productivity','Internal / supplier-delivered split')],'Workforce · no proxy values or invented trend')
        if 'LBG-AR25-COPILOT' in facts:body+='<h2>Separate tool footprint</h2>'+reported(facts,('LBG-AR25-COPILOT',))+'<p class="le-limit">Licences are not people, active adoption or productivity. No headcount or workforce chart is derived from them.</p>'
        body+=reported(facts,('LBG-BRAND26-NO-ROLES',))
    body+='<p class="gold-related">'+link(state,'Leadership',focus='people',detail='leadership')+' · '+link(state,'Businesses & functions',focus='people',detail='structure')+' · '+link(state,'Workforce',focus='people',detail='workforce')+'</p>'
    return body


def _ceo_journey(state,data,facts):
    selected=state.detail.removeprefix('journey-') if state.detail.startswith('journey-') else None
    if selected not in JOURNEYS:
        return ('<p class="le-deck">Explore the work that delivers customer and economic outcomes.</p>'
                +table(('Value stream / function','Business perimeter','Supported operating context'),[(link(state,row[0],detail='journey-'+key),e(row[1]),'Dated Group disclosures available' if row[4] else 'Conceptual orientation; measured operating evidence unavailable') for key,row in JOURNEYS.items()],
                       'Operating architecture · conceptual until the specific dependency is evidenced'))
    title,division,activities,caps,keys,meaning,question=JOURNEYS[selected]
    names={row['id']:row['title'] for row in data.get('capabilities',()) if not source_import.working_restricted(row)}
    body='<p class="eyebrow">'+e(division)+'</p><h2>'+e(title)+'</h2><p class="le-deck">'+e(activities)+'</p><p class="le-limit">Conceptual activity sequence; no verified application, role or supplier dependency is inferred.</p>'
    body+=table(('Layer','Established boundary'),[
      ('Business / value stream',e(division)+' · '+e(title)),('Activities',e(activities)),
      ('Durable capabilities',e(' · '.join(names[k] for k in caps if k in names))),('Organisation / accountable role','Unavailable; function association is conceptual'),
      ('Applications / data','Only the separately disclosed examples below; stream assignment unavailable'),('Technology / infrastructure','Installed topology and workload criticality unavailable'),
      ('Suppliers / contracts','Only disclosed collaboration / product context; contracted service and dates unavailable'),
    ],'From business to delivery · factual edges are not implied by navigation')
    body+=reported(facts,keys)+interpretation(facts,keys,meaning) if keys else '<p class="le-limit">'+e(meaning)+'</p>'
    body+='<section class="gold-dossier"><h3>Commercial significance</h3><p>'+e(meaning)+'</p><h3>Account investigation</h3><p>'+e(question)+'</p><p class="le-limit">Potential intervention must add to existing capabilities. No buyer need, budget, procurement event or supplier demand is established.</p></section>'
    body+='<p class="gold-related">'+link(state,'Applications & disclosed suppliers',focus='applications')+' · '+link(state,'Transformation disclosures',focus='programmes')+' · '+link(state,'Related strategy',stream='forces',focus='strategy',detail='goals')+'</p>'
    return body


def _ceo_goals(state,facts):
    selected=state.detail.removeprefix('objective-') if state.detail.startswith('objective-') else None
    available=[row for row in OBJECTIVES if all(key in facts for key in row[3])]
    if selected:
        row=next((row for row in available if row[0]==selected),None)
        if row is None:return '<p class="ceo-unavailable">This objective is unavailable.</p>'
        key,horizon,title,keys,owner,programme,journey=row
        body='<p class="eyebrow">'+e(horizon)+'</p><h2>'+e(title)+'</h2>'+reported(facts,keys)
        body+=table(('Decision dimension','Evidence boundary'),[
          ('Accountability',e(owner)+' · role hypothesis, not verified buying authority'),
          ('Starting position / latest progress','Only the dated statements above; matched baseline and current progress unavailable'),
          ('Target / horizon',e(horizon)+' · distinguish actuals, commitments and expectations'),
          ('Investment / programme','Published priorities only; work package, spend and delivery obligations unavailable'),
          ('Capability connection',e(JOURNEYS[journey][0])+' · conceptual association'),
          ('Counter-evidence',e(GOAL_DECISIONS[key][0])),
        ],'Goal scorecard · no inferred progress percentage or causal benefit')
        body+='<h3>Commercial investigation</h3><p>'+e(GOAL_DECISIONS[key][1])+'</p><p class="le-limit">External intervention is a hypothesis only; procurement, budget and sponsor mandate are unproven.</p>'
        body+='<p class="gold-related">'+link(state,'Operating context',stream='inside',focus='operations',detail='journey-'+journey)
        if programme:body+=' · '+link(state,'Existing programme disclosure',stream='inside',focus='programmes',detail=programme)
        return body+'</p>'
    body='<p class="le-deck">Management objectives, on their own reporting horizons.</p><div class="ceo-goals">'
    for key,horizon,title,keys,owner,programme,journey in available:
        body+='<article><span class="eyebrow">'+e(horizon)+'</span><h2>'+link(state,title,detail='objective-'+key)+'</h2>'+reported(facts,keys[:1])+'</article>'
    if 'LBG-Q326-INVESTMENT' in facts and not all(key in facts for key in ('LBG-Q326-INVESTMENT','LBG-A2030-INVESTMENT')):
        body+='<section><h2>Separate investment context</h2>'+reported(facts,('LBG-Q326-INVESTMENT',))+'</section>'
    body+='</div><p class="le-limit">No measured progress-to-target chart is shown without a matched baseline and actual. A prior-year contribution and a later expectation are different states, not a percentage achieved.</p>'
    return body


def _ceo_financial(state,facts,issues):
    if state.detail not in {'funding','income','costs','capital','divisions'}:return economics(state,facts,issues)
    title={'funding':'Funding & interest economics','income':'Income & profit','costs':'Costs, impairment & remediation','capital':'Capital, liquidity & returns','divisions':'Reporting businesses & contribution'}[state.detail]
    body='<h2>'+title+'</h2>'
    if state.detail=='funding':
        body+=economics(replace(state,detail='funding'),facts,issues)
    elif state.detail=='income':
        body+='<div class="le-measures">'+preview.measures({k:s for k,s in facts.items() if k=='LBG-Q326-PROFIT'})+'</div>'
        body+=table(('Financial measure','Period / basis','Eligible result'),[
          ('Net interest income','Group; statutory and underlying are distinct','Unavailable'),('Fees / other income','Matched Group reporting period','Unavailable'),
          ('Underlying profit / statutory bridge','Same period and consolidation perimeter','Unavailable'),
        ],'Income · no lending yield, residual or allocation inferred')
    elif state.detail=='costs':
        body+=table(('Component','Treatment','Eligible actual'),[
          ('Operating costs','Separate ordinary costs from remediation','Unavailable'),('Credit impairment','A charge over a period; not an arrears stock','Unavailable'),
          ('Remediation','Separate current charge and prior-period comparison','Unavailable'),('Efficiency ambition','Management target is not current cost or net saving','See attributed ambition below'),
        ],'Cost and risk · no manufactured financial bridge')
        body+=reported(facts,('LBG-A2030-CIR','LBG-A2030-SAVINGS'))
    elif state.detail=='capital':
        body+=table(('Measure','Financial meaning','Eligible result'),[
          ('CET1 / risk-weighted assets','Actual and pro-forma bases must not be mixed','Unavailable'),('Liquidity','Dated stocks / ratios, not investment budget','Unavailable'),
          ('Return on tangible equity','Profit and capital on a matched basis','Unavailable'),('Capital generation / distributions','Separate generation from announced return plans','Unavailable'),
        ],'Capital and returns · no proxy for deployable supplier budget')
    else:
        body+=table(('Reporting business','Current eligible contribution'),[(e(row[0]),'Reported segment measures unavailable') for row in twin.DIVISIONS]+[('Equity / Central','Reconciliation unavailable')],
                    'Division economics · no Group-to-segment allocation')
    return body
