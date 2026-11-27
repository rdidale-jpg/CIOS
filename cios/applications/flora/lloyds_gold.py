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
 'analysis': tuple('theme-'+str(i) for i in range(8))+tuple('quadrant-'+q for q in ('strength','weakness','opportunity','threat'))+('sources',),
}
DETAILS['people']=('leadership','structure','workforce','sources')
DETAILS['operations']+=tuple('journey-'+key for key in ('credit','payments','service','insurance','risk','data','platforms','finance','support'))
DETAILS['strategy']+=tuple('objective-'+key for key in ('renewal','ai','access','reporting','investment','efficiency','payments'))
DETAILS['economics']+=('funding','income','costs','capital','divisions')
DETAILS['economics']+=('service-workload',)+tuple('service-'+key for key,_ in agenda.LLOYDS_SERVICE_PRODUCTS[:-1])
DETAILS['operations']+=('service-workload',)+tuple('service-'+key for key,_ in agenda.LLOYDS_SERVICE_PRODUCTS[:-1])
DETAILS['commercial']+=('transactions','transaction-customers','transaction-delivery','transaction-value','transaction-investigation')
DETAILS['applications']+=('envoy-build','envoy-controls','envoy-value','envoy-investigation')
FOCUS_FACTS = {
 'group':('CEO1-ROLE-NUNN-20260322','LBG-Q326-PROFIT','LBG-Q326-DEPOSITS','LBG-AR25-MIGRATION','LBG-A2030-CIR'), 'economics':tuple(recovery.MEASURES)+('LBG-A2030-CIR','LBG-A2030-SAVINGS','LBG-Q326-INVESTMENT','LBG-A2030-INVESTMENT'),
 'retail':('LBG-BRAND26-TIMING','LBG-BRAND26-NO-ROLES'),
 'commercial':('LBG-A2030-WALLET','LBG-Q326-CURVE','treasury-payments','CEO1-ROLE-NUNN-20260322'), 'retirement':(),
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
FOCUS_FACTS['strategy']+=('LBG-AI26-REPORTED','LBG-AI26-EXPECTED','LBG-ENVOY-CONTROLS')

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
    if kw['detail']=='sources':
        return '<a class="canvas-inspection-link" data-canvas-exception="inspection" href="'+e(href(state,**kw),quote=True)+'">'+e(label)+'</a>'
    if label.startswith('←'):
        return '<a class="canvas-return" data-canvas-region="return" href="'+e(href(state,**kw),quote=True)+'">'+e(label)+'</a>'
    focus=kw.get('focus',state.focus)
    kind='money' if focus in {'economics','group'} else 'organisation' if focus=='people' else 'timeline' if focus in {'programmes','strategy'} else 'technology' if focus in {'applications','partners','capabilities'} else 'analysis' if focus=='analysis' else 'operating'
    return region(state,label,kind=kind,**kw)


def region(state,title,content='',*,kind='topic',caption='',mark=None,**kw):
    """A native whole-region target over existing state, not a data owner."""
    kw.setdefault('detail','')
    target=href(state,**kw)
    selected=target==href(state,detail=state.detail)
    return ('<a class="canvas-region canvas-'+kind+'" data-canvas-region="'+kind+'" href="'+e(target,quote=True)+'" aria-label="'+e(title,quote=True)+'"'
            +(' aria-current="page"' if selected else '')+'>'+visual_mark(mark or kind)+'<span class="canvas-title">'+e(title)+'</span>'
            +('<span class="canvas-caption">'+e(caption)+'</span>' if caption else '')+content+'<span class="canvas-arrow" aria-hidden="true">↗</span></a>')


def visual_mark(kind):
    # Small explanatory diagrams, not company premises, quantitative scales or
    # asserted dependencies. All navigation information also exists in text.
    paths={
      'business':'M5 28H30M30 12V44M30 12H82M30 28H82M30 44H82',
      'retail':'M8 20A9 9 0 1 1 26 20A9 9 0 1 1 8 20M2 49C2 31 32 31 32 49M45 13H91M83 5L91 13L83 21M91 43H45M53 35L45 43L53 51',
      'commercial':'M4 19H29V42H4ZM64 6H91V24H64ZM64 34H91V52H64ZM29 30H47V15H64M47 30V44H64',
      'retirement':'M20 13L48 4L76 13V30C76 42 61 49 48 54C35 49 20 42 20 30ZM34 26H62M48 15V39',
      'money':'M3 30H27M36 30H60M69 30H93M21 24L27 30L21 36M54 24L60 30L54 36M87 24L93 30L87 36',
      'organisation':'M48 5V19M12 19H84M12 19V35M48 19V35M84 19V35M3 35H21V49H3ZM39 35H57V49H39ZM75 35H93V49H75Z',
      'operating':'M3 12H70V23H3ZM15 29H82V40H15ZM27 46H94',
      'technology':'M7 8H88V20H7ZM7 28H88V40H7ZM19 20V28M76 20V28M48 40V51',
      'timeline':'M4 30H92M12 21V39M38 14V46M64 21V39M88 10V50',
      'analysis':'M5 5H90V50H5ZM48 5V50M5 28H90',
      'change':'M8 45L30 29L49 35L74 12H91M81 4L91 12L81 20',
      'topic':'M5 15H57M5 29H85M5 43H68',
    }
    return '<svg class="canvas-mark" viewBox="0 0 98 56" aria-hidden="true" focusable="false"><path d="'+paths.get(kind,paths['topic'])+'"/></svg>'


def business_regions(state,*,central=False):
    body='<div class="canvas-businesses" role="group" aria-label="Reporting businesses · not financial shares">'
    for title,customer,activity,driver,key in twin.DIVISIONS:
        body+=region(state,title,'<span class="canvas-business-purpose">'+e(driver)+'</span>'+('<span class="canvas-business-boundary">'+e({'retail':'No Group balance or profit allocated to Retail','commercial':'Transfer pricing and risk costs matter','retirement':'Insurance accounting is not banking net interest margin'}[key])+'</span>' if central else ''),kind='business',mark={'retail':'retail','commercial':'commercial','retirement':'retirement'}[key],caption=customer,stream='landscape',focus=key,subject=key)
    if central:body+=region(state,'Central / Equity',kind='money',caption='Central items and consolidation · no residual allocation; underlying segments must reconcile to the statutory Group',focus='economics',detail='central')
    return body+'</div>'


def financial_regions(state,facts):
    return '<div class="le-measures canvas-financials">'+''.join(region(state,label,preview.measures({key:facts[key]}),kind='money',focus='economics',detail=detail)
       for key,label,detail in [('LBG-Q326-DEPOSITS','Customer funding','funding'),('LBG-Q326-PROFIT','Reported earnings','income')] if key in facts)+'</div>'


def operating_regions(state):
    groups=(('Customer value streams',('credit','payments','service','insurance')),('Assure and enable delivery',('risk','data','platforms')),('Supporting organisation',('finance','support')))
    body='<div class="canvas-value-system v2-operating-model">'
    for title,keys in groups:
        body+='<section class="canvas-operating-band"><h2>'+e(title)+'</h2><div>'
        for key in keys:
            row=JOURNEYS[key]
            if key=='service':
                body+=region(state,'Customer operations',kind='operating',caption='Complaints & service · activity and outcomes',detail='service');continue
            body+=region(state,row[0],kind='operating',caption=row[1]+' · select the work, capabilities and supporting evidence',detail='journey-'+key)
        body+='</div></section>'
    return body+'</div><p class="le-limit">Conceptual operating architecture; grouping and navigation do not assert verified dependencies.</p>'


def capability_regions(state,data):
    targets={'CAP-STRATEGY':('forces','strategy','goals'),'CAP-CHANNEL':('inside','operations','journey-service'),
      'CAP-SERVICE':('inside','operations','service'),'CAP-DEPOSITS':('landscape','economics','funding'),
      'CAP-FINANCE':('inside','operations','journey-finance'),'CAP-LENDING':('inside','operations','journey-credit'),
      'CAP-PAYMENTS':('inside','operations','journey-payments'),'CAP-RISK':('inside','capabilities','risk'),
      'CAP-TECH':('inside','capabilities','technology'),'CAP-DATA':('inside','capabilities','data')}
    rows={r['id']:r for r in data.get('capabilities',()) if not source_import.working_restricted(r)}
    body='<div class="canvas-capabilities">'
    for title,ids in [('Customer and money',('CAP-CHANNEL','CAP-SERVICE','CAP-DEPOSITS','CAP-LENDING','CAP-PAYMENTS')),
                      ('Control and shared capabilities',('CAP-RISK','CAP-DATA','CAP-TECH','CAP-FINANCE','CAP-STRATEGY'))]:
        body+='<section><h2>'+title+'</h2><div>'
        for key in ids:
            if key not in rows:continue
            stream,focus,detail=targets[key]
            body+=region(state,rows[key]['title'],kind='technology' if key in {'CAP-DATA','CAP-TECH'} else 'operating',caption='Conceptual capability · select its existing context',stream=stream,focus=focus,detail=detail)
        body+='</div></section>'
    return body+'</div>'


def transformation_regions(state,data,facts):
    names={'legacy':'PROG-LBG-LEGACY','ai':'PROG-LBG-AI','brand':'PROG-LBG-BRAND','colleague':'PROG-LBG-COLLEAGUE','curve':'PROG-LBG-CURVE'}
    rows=[]
    for key,ident in names.items():
        row=next((r for r in data.get('programmes',()) if r['id']==ident),None)
        keys=tuple(k for k in row['claim_ids'] if k in facts) if row and not source_import.working_restricted(row) else ()
        if not keys:continue
        dates=sorted({ref.published for k in keys for ref in facts[k].sources if ref.published})
        date=dates[0] if dates else ''
        phase='Completion reported; integration unverified' if key=='curve' else 'Reported licences; adoption unverified' if key=='colleague' else 'Published plan or platform disclosure; delivery progress unverified'
        rows.append((date,key,row,keys,phase))
    body='<div class="canvas-timeline" aria-label="Transformation disclosures by publication date">'
    for date,key,row,keys,phase in sorted(rows,key=lambda r:r[0]):
        content=('<time class="canvas-date">'+e(date)+'</time>' if date else '')+'<span class="canvas-phase">'+e(phase)+'</span>'
        body+=region(state,row['title'],content,kind='timeline',caption='First displayed source date · not a delivery milestone',detail=key)
    return body+'</div>',rows


def strategy_regions(state,facts):
    # These horizons and statements are the existing disclosed objectives. The
    # rail expresses distinct reporting horizons, not a fabricated progress axis.
    available=[row for row in OBJECTIVES if all(key in facts for key in row[3])]
    body='<div class="canvas-goal-rail" aria-label="Management objectives on their published horizons">'
    for key,horizon,title,keys,owner,programme,journey in available:
        body+=region(state,title,'<div class="canvas-goal-fact">'+reported(facts,keys[:1])+'</div>',kind='timeline',caption=horizon,focus='strategy',detail='objective-'+key)
    return body+'</div>'


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
    if agenda.lloyds_service_products():
        body+=region(state,'Service workload',kind='operating',caption='Service context · no financial impact established',stream='inside',focus='operations',detail='service')
    body+='<div class="gold-economic-map" aria-label="Conceptual Group economic mechanism">'+''.join(region(state,title,kind='money',caption=desc,focus='economics',detail=key) for key,title,desc in (('funding','Funding','Deposits & other sources'),('income','Lending & income','Interest & fees'),('costs','Costs & impairment','Running the bank and credit risk'),('capital','Capital & returns','Risk capacity and returns')))+'</div>'
    body+='<p class="le-limit">Conceptual model · not a measured allocation or accounting reconciliation.</p>'
    body+=financial_regions(state,facts)
    stocks=[(key,label) for key,label in [('LBG-AR25-DEPOSITS','31 December 2025'),('LBG-Q326-DEPOSITS','30 September 2026')] if key in facts]
    if stocks:
        # Presentation only over existing typed, validated statements; no recipe,
        # new values, canonical facts or Financial runs are created.
        maximum=max(facts[key].value for key,_ in stocks)
        body+='<figure class="gold-stocks"><figcaption>Group customer deposits · GBP billion</figcaption>'
        for key,label in stocks:
            item=facts[key];p.note_editorial_sources(item.sources)
            body+='<a class="canvas-region canvas-stock" data-canvas-region="financial-chart" href="'+e(href(state,focus='economics',detail='comparison'),quote=True)+'" aria-label="Compare customer deposits at '+label+'" data-claim-id="'+key+'"><span>'+label+'</span><meter min="0" max="'+str(maximum)+'" value="'+str(item.value)+'" aria-label="Deposits at '+label+'">'+str(item.value)+'</meter><strong>£'+str(item.value)+'bn</strong></a>'
        body+='<p class="le-limit">Reported stocks at two dates. Zero-based bars; a stock difference is not an adjusted deposit flow. Profit above covers nine months and uses a different unit of time.</p></figure>'
    funding=next((row for row in issues if row.key=='funding-base'),None)
    if funding and all(key in facts for key in ('LBG-AR25-DEPOSITS','LBG-Q326-DEPOSITS')):
        body+=''.join('<div data-owner-item="funding-stock-change">'+p.render(item,compact=True)+'</div>'
                      for item in funding.facts if item.semantic_type=='calculated' and p.eligible(item))
        body+='<p class="le-limit">Arithmetic comparison of published stocks; not adjusted for consolidation, transfers or other balance-sheet effects. Not an organic inflow or earnings measure.</p>'
    if state.detail=='central':
        body+='<h2>Central / Equity and the Group tie-out</h2><p>Segment underlying profit and Group statutory profit have different accounting bases. Central items and the statutory bridge must remain separate; no residual is allocated to a business.</p><p>New segment and reconciliation figures are not published in this view.</p>'
    else:
        body+=business_regions(state,central=True)
    if state.detail=='comparison':
        body+=economic_decisions()
        body+=reported(facts,('LBG-A2030-CIR','LBG-A2030-SAVINGS','LBG-Q326-INVESTMENT','LBG-A2030-INVESTMENT'))
        body+=interpretation(facts,('LBG-A2030-CIR','LBG-A2030-SAVINGS'),'Gross savings and a future cost ratio are management ambitions, not current net profit or money available to suppliers. Revenue, implementation costs and parallel running can change the result.')
    elif not state.detail:body+='<p class="gold-related">'+link(state,'Earnings, efficiency & capital decisions',focus='economics',detail='comparison')+'</p>'
    return body


def service_context(state):
    """Contextual reference to the single operational presentation home."""
    if not agenda.lloyds_service_products():return ''
    return region(state,'Customer operations',kind='operating',
        caption='Complaints & service · Lloyds Bank PLC · H1 2026',
        stream='inside',focus='operations',detail='service')


def service_workload(state, *, inspection=False, data=None):
    """A finite view over existing Source service profiles; no monetary estimate.

    A workload share is arithmetic over a common legal-bank period, not a
    cost allocation. Nothing is cached, exported or discovered from private runs.
    """
    from decimal import Decimal, ROUND_HALF_UP
    rows=agenda.lloyds_service_products()
    if not rows:return ''
    # These retained excerpts describe the same FCA document and legal-bank
    # return as the existing release. A restriction there must not be escaped
    # by switching to the product excerpt of that same source.
    basis=agenda._claims(data if data is not None else v.current_data(v.Context('lloyds','inside')),
        ('LBG-FCA-H126-RECEIVED','EAI-LBG-CLOSED','EAI-LBG-UPHELD'))
    if len(basis)!=3:return ''
    if tuple(item.value for item in basis)!=tuple(item.value for item in rows[-1][2]):return ''
    total=rows[-1][2][0]; maximum=max(row[2][0].value for row in rows[:-1])
    for _,_,facts in rows:
        for item in facts:p.note_editorial_sources(item.sources)
    shares={key:p.Statement(
        label+' accounts for '+str((facts[0].value/total.value*100).quantize(Decimal('.1'),rounding=ROUND_HALF_UP))+'% of complaints received.',
        'calculated',total.scope,total.period,tuple(dict.fromkeys((*facts[0].sources,*total.sources))),
        'derived_from_inputs','derived_view_not_canonical','actual',
        value=(facts[0].value/total.value*100).quantize(Decimal('.1'),rounding=ROUND_HALF_UP),unit='percent of complaints received',
        method=str(facts[0].value)+' / '+str(total.value)+' × 100; rounded to one decimal place',
        dependencies=(facts[0].text,total.text),dependency_types=('reported',),
        input_authorities=(facts[0].canonical_status,total.canonical_status),caveats=total.caveats)
        for key,label,facts in rows[:-1]}
    if not all(p.eligible(item) for item in shares.values()):return ''
    if inspection:
        body='<h2>Reported complaint activity · source and calculation</h2>'
        body+=flagship._source_rows(f for _,_,facts in rows for f in facts)
        for item in shares.values():
            body+='<p><strong>Calculated</strong> '+e(item.text)+' '+e(item.method)+'</p>'
        for _,label,facts in rows[:-1]:
            body+='<p><strong>Calculated · closed-case mix</strong> '+e(label)+': '+str(facts[1].value)+' / '+str(rows[-1][2][1].value)+' × 100; one decimal place. Same legal bank and period; different product cohorts.</p>'
        return body
    active=state.detail.removeprefix('service-')
    body='<section class="gold-service-workload" data-intelligence="lloyds-product-workload"><p class="eyebrow">Lloyds Bank PLC · January–June 2026</p><h2>Complaints &amp; service</h2>'
    body+='<p class="gold-workload-headline"><strong>'+e(str(shares['bankcards'].value))+'%</strong> of received complaints concerned banking and credit cards.</p>'
    body+='<figure><figcaption>Reported complaints received · select a product group</figcaption><div class="gold-workload-bars">'
    for key,label,facts in rows[:-1]:
        share_text='&lt;0.1%' if facts[0].value>0 and shares[key].value==0 else str(shares[key].value)+'%'
        body+='<a class="canvas-region gold-workload-row" data-canvas-region="service-workload" href="'+e(href(state,stream='inside',focus='operations',detail='service-'+key),quote=True)+'"'+(' aria-current="page"' if active==key else '')+'><span class="gold-workload-label">'+e(label)+'</span><span class="gold-workload-track" aria-hidden="true"><span style="width:'+str(facts[0].value/maximum*100)+'%"></span></span><strong>'+format(facts[0].value,',')+'</strong><span class="gold-workload-share">'+share_text+' <span class="sr-only">calculated share</span></span></a>'
    body+='</div></figure><p class="le-limit">Five product groups reconcile to '+format(total.value,',')+' received complaints. Shares are calculated. This legal bank is not the consolidated Group or Retail division; volumes are not cost or customer incidence. Received and closed complaints are different cohorts.</p>'
    selected=next((row for row in rows[:-1] if row[0]==active),None)
    if selected:
        _,label,facts=selected
        body+='<section class="gold-workload-detail"><h3>'+e(label)+'</h3><dl>'
        for title,item,suffix in zip(('Received','Closed','Firm-upheld share of closed'),facts,('','','%')):
            body+='<div><dt>'+title+'</dt><dd>'+format(item.value,',')+suffix+'</dd></div>'
        body+='</dl><p>Reported · '+e(total.period)+'. Received and closed are different cohorts. Firm-upheld is not independent adjudication; their difference is not backlog clearance.</p></section>'
    if selected:
        closed_share=(facts[1].value/rows[-1][2][1].value*100).quantize(Decimal('.1'),rounding=ROUND_HALF_UP)
        body+='<p class="gold-cohort-mix"><strong>Calculated · '+str(closed_share)+'%</strong> of the legal bank’s closed complaints were in this product group. </p>'
        body+='<section class="gold-workload-interpretation"><h3>Activity, outcome and consequence</h3><p>The product-specific firm-upheld rate describes decisions on closed cases. It is not the share of customers harmed, a cost measure or a comparison of service quality across products.</p><h3>Possible explanations</h3><p><strong>Hypotheses.</strong> Product scale, case mix and repeat contact could each affect the pattern. These returns do not establish which explanation applies, or quantify handling effort.</p><h3>Management response</h3><p>The FCA return records case handling and firm decisions; it does not identify a complaints-specific remedy or its effectiveness. Closing a case is not proof of an improved customer outcome.</p><h3>Commercial investigation</h3><p>Do any '+e(label.lower())+' case types recur after a firm-upheld decision, and what measured customer outcome follows the current remedy? Establish the responsible service owner, case mix and existing response before proposing an intervention. No supplier need, budget or open procurement is established.</p></section>'
    else:
        body+='<p class="gold-cohort-mix">The all-product firm-upheld rate is <strong>'+str(rows[-1][2][2].value)+'%</strong> across '+format(rows[-1][2][1].value,',')+' closed cases. Product mix matters: select a product to distinguish its activity, outcome and the evidence needed to explain it.</p>'
    body+='<p class="le-limit">The return establishes complaint activity and firm decisions, not the financial or customer impact.</p>'
    body+='</section>'
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


def exploration_rail(state, rows, active, *, kind):
    """Presentation links over existing state; no claims, storage or new owner."""
    selected=replace(state,detail=active)
    return '<div class="gold-exploration-rail">'+''.join(
        region(selected,title,kind=kind,caption=caption,detail=key)
        for key,title,caption in rows)+'</div>'


def transaction_banking(state,facts):
    evidence=v2_reported(facts,'TRANSACTIONREMIT','CONDON','CONDONREPORT')
    body='<p class="le-deck">Help a business collect, hold and move money while managing the timing of payments and receipts.</p>'
    body+=evidence
    if not state.detail:
        body+=region(state,'Transaction Banking',kind='commercial',caption='Explore customer economics, delivery and commercial interpretation',detail='transactions')
        body+='<p class="le-limit">Business-model lens within Commercial Banking; not a verified Lloyds organisation or revenue allocation.</p>'
        body+=link(state,'Group funding & earnings',focus='economics',detail='comparison')
        return body
    active=state.detail if state.detail!='transactions' else 'transaction-customers'
    body+='<h2>Transaction Banking</h2><p class="le-limit">Conceptual service model. The stages do not assert Lloyds process ownership, installed systems or a specific customer problem.</p>'
    rows=(('transaction-customers','Customer economics','Cash timing and working capital'),
          ('transaction-delivery','Service delivery','Instructions, controls and completion'),
          ('transaction-value','Bank economics','Fees, funding and risk'),
          ('transaction-investigation','Commercial perspective','A bounded, testable hypothesis'))
    body+=exploration_rail(state,rows,active,kind='commercial')
    if active=='transaction-customers':
        body+='<section class="gold-activation-story"><h2>Cash timing is the customer problem to understand</h2><p>A business can be profitable yet face a cash gap between paying suppliers and receiving customer money. Collections, payment timing, balance visibility and short-term finance affect that gap in different ways.</p><div class="gold-value-path"><span>Customer receipts</span><span>Cash visibility</span><span>Supplier payments</span><span>Working capital</span></div><p>Faster processing alone does not prove an economic benefit. Customer terms, inventory, payment certainty and the cost of funding can matter more. These are economic mechanisms, not measured Lloyds customer outcomes.</p></section>'
    elif active=='transaction-delivery':
        body+='<section class="gold-activation-story"><h2>Completion depends on the hand-offs</h2><div class="gold-value-path"><span>Client instruction</span><span>Checks & exceptions</span><span>Settlement</span><span>Reconciliation</span></div><p>Client implementation, operations, risk controls and technology need a shared view of what an instruction means and whether it completed. An apparent technology delay may instead come from incomplete documents, authorisation or a client process.</p><p>Business/product leadership, client operations, technology, risk and treasury/finance are relevant role hypotheses. No named Transaction Banking executive or delegated buying authority is asserted here.</p></section>'
    elif active=='transaction-value':
        body+='<section class="gold-activation-story"><h2>Different services earn value differently</h2><div class="gold-value-path"><span>Service fees</span><span>Operating balances</span><span>Credit exposure</span><span>Cost to serve</span></div><p>Transaction fees and balance-related income can support the bank’s economics; credit, liquidity, capital and servicing costs reduce the contribution. Pricing, transfer pricing and risk allocation determine the result.</p><p>No transaction volumes, divisional margin or share of Group profit is inferred. More payment activity is not automatically more profitable activity.</p></section>'
    else:
        body+='<section class="gold-activation-story"><h2>Investigate one real service hand-off</h2><p><strong>Hypothesis.</strong> Improving a customer-confirmed exception or implementation hand-off could reduce repeat work or improve payment certainty. It is not an established Lloyds need.</p><p>Establish the actual service owner, customer effect, exception baseline and current remedy before suggesting a diagnostic. Existing teams, tools or suppliers may already cover the issue; a settled delivery plan can leave no useful external role.</p><p>Commercial qualification requires customer evidence and an open decision. A payment strategy, appointment or policy announcement does not establish procurement, budget or a sales opportunity.</p></section>'
    context=reported(facts,('LBG-A2030-WALLET','LBG-Q326-CURVE'))
    if context:
        body+='<aside class="gold-subject-context"><h2>Separate Group payments context</h2>'+context+'<p>These are Group disclosures. They do not place Curve, a wallet programme or a supplier contract within Transaction Banking.</p></aside>'
    if active=='transaction-delivery' and 'treasury-payments' in facts:
        body+='<aside class="gold-subject-context"><h2>Historical UK payments policy · 2024</h2>'+reported(facts,('treasury-payments',))+'<p>A historical policy pilot is not proof of adoption by Lloyds or a specific business customer.</p></aside>'
    if active=='transaction-delivery' and 'CEO1-ROLE-NUNN-20260322' in facts:
        body+='<aside class="gold-subject-context"><h2>Dated Group leadership context</h2>'+reported(facts,('CEO1-ROLE-NUNN-20260322',))+'<p>This establishes the dated Group attribution, not a Transaction Banking reporting line or buying authority.</p><p class="ceo-attribution">Contains public sector information licensed under the Open Government Licence v3.0.</p></aside>'
    body+='<p class="gold-related">'+link(state,'Group economics',focus='economics')+link(state,'Payment operating model',stream='inside',focus='operations',detail='journey-payments')+'</p>'
    return body


def envoy_exploration(state,facts):
    # Both existing issuer claims must remain eligible. Never admit the recovered
    # fraud/Export Assist/leadership candidates or invent original source bytes.
    active=state.detail if state.detail!='envoy' else 'envoy-build'
    body='<h2>Envoy</h2><p class="le-deck">An existing AI platform changes the starting point: investigate the value of a workflow, rather than assume a platform is missing.</p>'
    dates=sorted({source.published for key in APPS['envoy'][2] for source in facts[key].sources if source.published})
    if dates:body+='<p class="canvas-date">Company announcement · '+e(dates[0])+'</p>'
    body+=reported(facts,APPS['envoy'][2])
    rows=(('envoy-build','Build & reuse','Platform and business process'),
          ('envoy-controls','Operate & oversee','Monitoring and accountability'),
          ('envoy-value','Value & adoption','Reported contribution versus expectation'),
          ('envoy-investigation','Commercial perspective','Validate an incremental contribution'))
    body+=exploration_rail(state,rows,active,kind='technology')
    if active=='envoy-build':
        body+='<section class="gold-activation-story"><h2>Platform capability is a starting point</h2><div class="gold-value-path"><span>Business workflow</span><span>AI capability</span><span>Information & access</span><span>Service outcome</span></div><p>The disclosed Google Cloud collaboration provides platform context. It does not establish a contracting entity, an exclusive cloud estate or the application used by any particular division.</p><p>Workflow ownership, information quality and integration determine whether platform capability becomes a repeatable service. This is an operating interpretation, not an asserted Lloyds architecture.</p></section>'
        body+=interpretation(facts,('LBG-ENVOY-CONTROLS','LBG-A2030-DATA'),'A disclosed platform and a stated enterprise-data priority make process and information readiness relevant to AI execution. They do not prove a missing data platform or an unmet supplier requirement.')
    elif active=='envoy-controls':
        body+='<section class="gold-activation-story"><h2>Designed controls are different from demonstrated outcomes</h2><div class="gold-value-path"><span>Controlled release</span><span>Monitoring</span><span>Exception handling</span><span>Accountability</span></div><p>Lloyds describes controls and monitoring. Their disclosure weakens a greenfield-control pitch; it does not independently establish effectiveness or reveal a control failure.</p><p>Business operations, technology and risk need clear decision responsibilities. Human review, overrides and service quality are useful evaluation dimensions, not confirmed features or deficiencies of every Envoy workflow.</p></section>'
    elif active=='envoy-value':
        body+='<section class="gold-activation-story"><h2>Platform capability is not an attributed financial result</h2><p>Envoy is an existing platform with disclosed controls. The Group AI contribution and expectation belong to the Group strategy view; neither establishes an Envoy result, adoption level or net return.</p></section>'
        if all(k in facts for k in ('LBG-AI26-REPORTED','LBG-AI26-EXPECTED')):
            body+=region(state,'Group AI performance',kind='timeline',caption='Reported contribution, expectation and management response',stream='forces',focus='strategy',detail='objective-ai')
        if 'LBG-AR25-COPILOT' in facts:
            body+=region(state,'Colleague technology',kind='technology',caption='Copilot disclosure · not Envoy users or measured workforce productivity',focus='applications',detail='copilot')
    else:
        body+='<section class="gold-activation-story"><h2>Start with one agreed workflow</h2><p><strong>Hypothesis.</strong> A contribution may exist in measuring or improving a customer-agreed workflow, including service quality and full control, run and change costs.</p><p>Validate the baseline, outcome attribution, exceptions and existing management response. Faster tasks can be offset by review effort or parallel running; an existing team may already have adequate measurement and remedies.</p><p>No reported platform, contribution or expectation establishes customer demand, open procurement, external scope or supplier budget. A commercial conversation is justified only after confirming an unresolved customer issue and a useful role.</p></section>'
    body+='<p class="gold-related">'+link(state,'Enterprise data capability',focus='capabilities',detail='data')+link(state,'AI transformation disclosure',focus='programmes',detail='ai')+link(state,'Group costs & efficiency',stream='landscape',focus='economics',detail='costs')+'</p>'
    body+='<p class="gold-inspect">'+link(state,'Evidence & dates',detail='sources')+'</p>'
    return body


def division(state,facts):
    if state.focus=='commercial' and not state.detail:return executive_commercial(state,facts)
    if state.focus=='commercial' and state.detail.startswith('transaction'):
        return transaction_banking(state,facts)
    _,customers,activities,driver,_=next(row for row in twin.DIVISIONS if row[-1]==state.focus)
    body='<p class="le-deck">'+e(customers)+'. '+e(activities)+'.</p>'
    body+='<div class="gold-business"><h2>How value is created</h2><p>'+e(driver)+'.</p><p class="le-limit">Business-model orientation. Group disclosures below do not establish divisional outcomes or allocations.</p></div>'
    keys={'retail':('BANK','BOS','MBNA','BLACKHORSE','LEX','TUSKER'),'retirement':('WIDOWS','WEALTH')}.get(state.focus,())
    body+='<div class="v2-business-evidence">'+v2_reported(facts,*keys)+'</div>'
    body+='<div class="v2-economic-sequence">'+''.join('<span>'+e(x)+'</span>' for x in ({'retail':('Customer deposits','Lending, fees and asset services','Funding, servicing and credit costs','Banking return'),'retirement':('Policies and long-term savings','Protection, distribution and administration','Claims, service and capital requirements','Insurance and investment return')}.get(state.focus,())))+'</div><p class="le-limit">Conceptual economic mechanism; no capability-level allocation or cross-business profit comparison.</p>'
    rows={'retail':(('Originate & service credit','Assess affordability; book and service credit','Risk assessment, servicing and controls'),('Support the customer','Resolve requests; correct accounts','Customer operations and access controls')),
          'commercial':(('Finance businesses','Evaluate and service business credit','Lending, risk and finance · conceptual'),('Move money','Provide payment and cash-management services','Payments, technology and operations · conceptual')),
          'retirement':(('Build long-term savings','Pensions and investment products','Product, servicing and risk · conceptual'),('Meet obligations','Administer policies and customer outcomes','Operations, finance and data · conceptual'))}
    body+=table(('Value stream','Activities','Durable capabilities'),[(e(a),e(b),e(c)) for a,b,c in rows[state.focus]],'Operating interpretation · not a verified workflow or organisation chart')
    body+='<p class="ceo-unavailable">Reported segment contribution and matched comparisons are unavailable.</p>'
    body+=reported(facts,FOCUS_FACTS[state.focus])
    body+='<p class="gold-related">'+link(state,'Group economic context',focus='economics')+link(state,'Related operating capabilities',stream='inside',focus='capabilities')+'</p>'
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
    if state.detail=='service' or state.detail.startswith('service-'):
        service=service_workload(state,data=data)
        if service:return service
        if state.detail!='service':return '<p class="le-deck">Product-level service measures cannot be shown for this selection.</p>'+region(state,'Customer operations',kind='operating',caption='Return to available service context',detail='service')
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
        body += '<p class="gold-related">' + ''.join(
            link(state, label, focus=focus, detail=detail) for label, focus, detail in targets
        ) + '</p>'
        body+='<h3>Commercial investigation</h3><p>Which hand-off causes avoidable repeat work, and what measured customer outcome would demonstrate an improvement? This is an investigation question, not established customer pain or demand.</p>'
    else:body+='<p class="gold-related">'+link(state,'Credit journey detail',detail='credit')+link(state,'Customer service detail',detail='service')+'</p>'
    body+=reported(facts,FOCUS_FACTS['operations'])
    if state.detail=='service':
        if agenda.lloyds_service_products():
            body=region(state,'Explore product workload',kind='operating',caption='Five reported product groups · Lloyds Bank PLC · H1 2026',stream='inside',focus='operations',detail='service')+body
        service=next((row for row in issues if row.key=='service-recovery'),None)
        if service:
            outcome='<section class="gold-dossier"><h2>Service outcomes · Lloyds Bank PLC</h2><p>January–June 2026 · this legal bank only, not consolidated Group or Retail reporting segment.</p>'
            outcome+=''.join('<div data-owner-item="'+key+'">'+p.render(item,compact=True)+'</div>'
                          for key,item in zip(('LBG-FCA-H126-RECEIVED','EAI-LBG-CLOSED','EAI-LBG-UPHELD'),service.facts) if p.eligible(item))
            outcome+='<p class="le-limit">Received and closed complaints are different cohorts. Firm-upheld is not independent adjudication. These figures establish no backlog clearance, harm rate, service-quality ranking, avoidable cost or external supplier need.</p></section>'
            body=outcome+body
    return body


def capabilities(state,data,facts):
    body='<p class="le-deck">Capabilities describe what the bank must be able to do; value streams describe how work delivers an outcome.</p>'
    body+=capability_regions(state,data)
    body+='<p class="le-limit">Conceptual capability grouping; no organisation, application ownership or installed dependency is asserted.</p>'
    if state.detail:
        keys={'risk':('LBG-ENVOY-CONTROLS',),'technology':('LBG-AR25-MIGRATION',),'data':('LBG-A2030-DATA',)}.get(state.detail,())
        body+=reported(facts,keys)
        body+='<h2>Capability accountability</h2><p>Accountable team, process ownership, application installation and service-level measures: Unknown. The conceptual association does not establish an enterprise dependency.</p>'
    return body


def applications(state,facts):
    if (state.detail=='envoy' or state.detail.startswith('envoy-')) and all(k in facts for k in APPS['envoy'][2]):
        return envoy_exploration(state,facts)
    body='<p class="le-deck">Technology disclosures, with different kinds of evidence.</p>'
    rows=[]
    for key,(name,status,keys,capability,note) in APPS.items():
        available=tuple(k for k in keys if k in facts)
        if len(available)!=len(keys):continue
        rows.append(region(state,name,kind='technology',caption=status,content='<span class="canvas-sequence">'+e(capability)+'</span>',focus='applications',detail=key))
    if 'LBG-V2-MSAGREEMENT' in facts:rows.append(region(state,'Microsoft Frontier Suite',kind='technology',caption='June agreement, reported adoption and engineering tools',focus='applications',detail='frontier'))
    if 'LBG-V2-FRAUDWORKFLOW' in facts:rows.append(region(state,'Fraud decision support',kind='operating',caption='A disclosed Envoy workflow with human accountability',focus='applications',detail='fraud'))
    body+='<div class="gold-technology-list">'+''.join(rows)+'</div><p class="le-limit">Source-supported examples · not an installed estate inventory.</p>' if rows else ''
    if all(k in facts for k in ('LBG-AI26-REPORTED','LBG-AI26-EXPECTED')):body+=region(state,'Group AI performance',kind='timeline',caption='Reported contribution and later expectation, in their strategy home',stream='forces',focus='strategy',detail='objective-ai')
    key={'google':'envoy','microsoft':'copilot'}.get(state.detail,state.detail)
    if key in APPS:
        name,status,keys,capability,note=APPS[key]
        available=tuple(k for k in keys if k in facts)
        if len(available)==len(keys):
            body+='<section class="gold-dossier"><h2>'+e(name)+'</h2>'+reported(facts,available)+'<p>'+e(note)+'</p>'
            body+='<p class="le-limit">The disclosure does not establish a complete installation map, contracting entity, contract value, support expiry, renewal date or programme workshare.</p>'
            if key=='copilot' and 'LBG-V2-MSAGREEMENT' in facts:body+=region(state,'Later Microsoft agreement and adoption',kind='technology',caption='June 2026 announcement; separate from the FY2025 footprint',focus='applications',detail='frontier')
            body+='<p class="gold-inspect">'+link(state,'Evidence & dates',detail='sources')+'</p></section>'
    return body


def partners(state,facts):
    body='<p class="le-deck">A collaboration, a product licence and a contract are different relationships.</p><div class="gold-technology-list">'
    if 'LBG-ENVOY-GOOGLE' in facts:body+=region(state,'Google Cloud',kind='technology',caption='Disclosed Envoy collaborator',content='<span class="canvas-sequence">No contracting entity, spend, workshare or renewal established</span>',detail='google')
    if 'LBG-V2-MSAGREEMENT' in facts:body+=region(state,'Microsoft agreement',v2_reported(facts,'MSAGREEMENT'),kind='technology',caption='Announced multi-year agreement · June 2026; workshare, price and expiry not disclosed',focus='applications',detail='frontier')
    elif 'LBG-AR25-COPILOT' in facts:body+=region(state,'Microsoft Copilot',kind='technology',caption='Disclosed licences; product context',content='<span class="canvas-sequence">No supplier contract or service-term inference</span>',detail='microsoft')
    body+='</div>'+reported(facts,FOCUS_FACTS['partners'])
    if state.detail in {'google','microsoft'}:body+=applications(state,facts)
    return body


def programmes(state,data,facts):
    body='<p class="le-deck">Different kinds of change, at different points in delivery.</p>'
    timeline,rows=transformation_regions(state,data,facts)
    body+=timeline
    for date,key,row,keys,phase in rows:
        if state.detail==key:
            body+='<section class="gold-dossier"><h2>'+e(row['title'])+'</h2>'+reported(facts,keys)
            body+='<p>The dated plan, licence disclosure or acquisition state is the established response. A later milestone, measured customer outcome and remaining delivery obligation need separate evidence.</p>'+region(state,'Relevant leadership and operating context',kind='organisation',caption='Published roles are not delegated programme sponsorship',focus='people',detail='leadership')+'<p class="le-limit">No programme budget, contracted work package or verified outcome is inferred.</p></section>'
    return body


def analysis(state,facts):
    body='<p class="le-deck">Eight strategic themes. Four familiar quadrants.</p><div class="gold-swot" aria-label="Four-quadrant SWOT">'
    selected_quadrant=state.detail.removeprefix('quadrant-') if state.detail.startswith('quadrant-') else None
    for quadrant in ('Strength','Weakness','Opportunity','Threat'):
        cards=[]
        for index,(title,keys,_) in enumerate(SWOT):
            if title.startswith(quadrant+' · ') and all(k in facts for k in keys):
                cards.append(region(state,title.split(' · ',1)[1],kind='theme',detail='theme-'+str(index)))
        body+='<section class="canvas-quadrant canvas-'+quadrant.lower()+'">'
        if cards:
            body+=region(state,quadrant,kind='quadrant',caption={'Strength':'Existing capabilities','Weakness':'Execution constraints','Opportunity':'Conditional possibilities','Threat':'External and delivery risks'}[quadrant],detail='quadrant-'+quadrant.lower())
            body+='<div class="canvas-themes">'+''.join(cards)+'</div>'
        else:body+='<h2>'+quadrant+'</h2>'
        body+='</section>'
    body+='</div><p class="le-limit">FLORA analysis, not qualified sales opportunities. Theme availability follows its underlying sources.</p>'
    if selected_quadrant:
        body+='<section class="gold-dossier"><h2>'+e(selected_quadrant.title())+' themes</h2>'
        for index,(title,keys,text) in enumerate(SWOT):
            if title.lower().startswith(selected_quadrant+' · ') and all(k in facts for k in keys):
                body+=region(state,title.split(' · ',1)[1],interpretation(facts,keys,text),kind='theme',detail='theme-'+str(index))
        body+='</section>'
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
        f'<a class="canvas-region canvas-timeline" data-canvas-region="timeline" href="#strategy-{anchors[horizon]}" aria-label="{e(horizon,quote=True)}">'+visual_mark('timeline')+f'<span class="canvas-title">{e(horizon)}</span></a>' for horizon in groups
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
    if state.focus=='markets' and not state.detail:return experience_forces(state,facts)
    if state.focus=='analysis':return analysis(state,facts)
    if state.focus=='strategy':
        if state.detail == 'goals':
            return strategy_goals(facts)
        body='<p class="le-deck">Management direction and the sequence of change.</p>'+strategy_regions(state,facts)
        body+=reported(facts,('LBG-A2030-SAVINGS','LBG-Q326-INVESTMENT','LBG-A2030-INVESTMENT'))
        if state.detail=='options':
            for title,keys,text in next(rows for key,_,rows in flagship.VIEWS if key=='options'):
                if all(k in facts for k in keys):body+='<h2>'+e(title)+'</h2>'+interpretation(facts,keys,text)
        else:body+='<p class="gold-related">'+link(state,'Goals & tests of progress',detail='goals')+link(state,'Strategic alternatives & trade-offs',detail='options')+'</p>'
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
    facts=executive_facts(data,facts)
    title=SUBJECTS[state.focus]
    body='<section class="gold-content" data-canvas="visual" data-level="'+('3' if state.detail=='sources' else '2' if state.detail else '0' if state.focus=='group' else '1')+'">'
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
        if state.focus in {'operations','economics'}:body+=service_workload(state,inspection=True,data=data)
        body+='<p class="le-limit">Lloyds attribution links to the issuer homepage. Direct PDF links remain deferred. These statements remain analytical public research, not canonical acceptance.</p>'
        return body+'</section>'
    if state.stream=='landscape':
        if state.focus=='group' and not state.detail:
            body+=experience_landscape(state,facts,issues)
        elif state.focus=='group' and state.detail=='brands':body+=executive_brands(state,facts)
        elif state.focus=='economics' and state.detail in {'','funding','income','costs','capital'}:body+=experience_economic_mechanism(state,facts,issues)
        elif state.focus in {'group','economics'}:body+=_ceo_financial(state,facts,issues)
        else:body+=experience_business(state,facts) if not state.detail else division(state,facts)
    elif state.stream=='inside':
        if state.focus=='people' or state.focus=='operations' and state.detail=='people':body+=executive_people(state,facts)
        elif state.focus=='operations' and not state.detail:body+=experience_inside(state,data,facts)
        elif state.focus=='operations' and state.detail.startswith('journey-'):body+=experience_activity(state,data,facts)
        elif state.focus=='operations' and state.detail!='service' and not state.detail.startswith('service-'):body+=_ceo_journey(state,data,facts)
        elif state.focus=='operations':body+=operating(state,data,facts,issues)
        elif state.focus=='capabilities':body+=experience_capability(state,data,facts) if state.detail else experience_inside(state,data,facts)
        elif state.focus=='applications':body+=executive_technology(state,facts) if state.detail in {'frontier','fraud'} else applications(state,facts)
        elif state.focus=='partners':body+=partners(state,facts)
        else:body+=executive_programme(state,facts) if state.detail in {'frontier','fraud','skills'} else programmes(state,data,facts)+executive_programme(state,facts)
    elif state.focus=='strategy' and (state.detail=='goals' or state.detail.startswith('objective-')):body+=_ceo_goals(state,facts)
    else:body+=forces(state,facts)
    owns_inspection=(state.focus=='applications' and (state.detail=='envoy' or state.detail.startswith('envoy-'))
                     and all(k in facts for k in APPS['envoy'][2]))
    if (state.focus not in {'group','analysis'} or state.detail) and not owns_inspection:
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
 ('ai','FY2025 reported / 2026 expectation','Turn AI capability into measured benefit',('LBG-AI26-REPORTED','LBG-AI26-EXPECTED'),'Business benefit and control owners to verify','ai','data'),
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
        body+='<div class="ceo-hierarchy"><strong>Lloyds Banking Group plc</strong><span>Reporting businesses · not legal subsidiaries</span>'+business_regions(state)+'</div>'
        body+='<div class="canvas-function-map" aria-label="Conceptual function lenses">'+''.join(region(state,title,kind='operating',caption=caption,stream='inside',focus='operations',detail='journey-'+key) for key,title,caption in (
          ('finance','Finance / treasury','Finance and funding · Named owner / mandate unavailable'),('service','Customer operations','Servicing and channels · Named owner / mandate unavailable'),
          ('risk','Risk and control','Risk assessment and controls · Named owner / mandate unavailable'),('platforms','Technology / data','Platforms, data and AI · Named owner / mandate unavailable')))+'</div><p class="le-limit">Conceptual function lenses · not a verified organisation chart.</p>'
    if state.detail=='workforce':
        body+='<h2>People, tools and organisational change</h2><p class="le-deck">Workforce capacity, a product deployment and a brand transition are different signals.</p>'
        if 'LBG-AR25-COPILOT' in facts:
            body+=region(state,'Colleague technology',kind='technology',caption='Disclosed Copilot footprint · not headcount, active use or productivity',focus='applications',detail='copilot')
        if 'LBG-BRAND26-NO-ROLES' in facts:
            body+=interpretation(facts,('LBG-BRAND26-NO-ROLES',),'The brand-transition announcement rules out related role reductions. That narrow statement does not establish Group-wide workforce growth, a hiring plan or an outsourcing decision.')
            body+=region(state,'Brand transition and service access',kind='change',caption='The disclosed change and its specific workforce boundary',focus='programmes',detail='brand')
        body+='<p class="le-limit">Comparable employee/FTE totals, business and function distribution, and workforce productivity cannot be established from these disclosures. Licences are not people.</p>'
        if all(k in facts for k in ('LBG-AI26-REPORTED','LBG-AI26-EXPECTED')):
            body+=region(state,'AI value and work',kind='timeline',caption='Group benefit evidence and the measurement needed before inferring capacity changes',stream='forces',focus='strategy',detail='objective-ai')
    body+='<p class="gold-related">'+link(state,'Leadership',focus='people',detail='leadership')+link(state,'Businesses & functions',focus='people',detail='structure')+link(state,'Workforce',focus='people',detail='workforce')+'</p>'
    return body


def _ceo_journey(state,data,facts):
    selected=state.detail.removeprefix('journey-') if state.detail.startswith('journey-') else None
    if selected=='service':return service_context(state)
    if selected not in JOURNEYS:
        return '<p class="le-deck">Explore the work that delivers customer and economic outcomes.</p>'+executive_operating_context(state,facts)+operating_regions(state)
    title,division,activities,caps,keys,meaning,question=JOURNEYS[selected]
    names={row['id']:row['title'] for row in data.get('capabilities',()) if not source_import.working_restricted(row)}
    body='<p class="eyebrow">'+e(division)+'</p><h2>'+e(title)+'</h2><p class="le-deck">'+e(activities)+'</p><p class="le-limit">Conceptual activity sequence; no verified application, role or supplier dependency is inferred.</p>'
    body+='<div class="canvas-layer-stack" aria-label="Conceptual operating layers">'
    body+=region(state,'Business / value stream',kind='business',caption=division+' · '+title,stream='landscape',focus=state.subject if state.subject in {'retail','commercial','retirement'} else 'group')
    body+=region(state,'Durable capabilities',kind='operating',caption=' · '.join(names[k] for k in caps if k in names),focus='capabilities')
    body+=region(state,'Organisation / accountable role',kind='organisation',caption='Unavailable; function association is conceptual',focus='people',detail='structure')
    body+=region(state,'Applications / data',kind='technology',caption='Disclosed examples only; stream assignment unavailable',focus='applications')
    body+=region(state,'Technology / infrastructure',kind='technology',caption='Installed topology and workload criticality unavailable',focus='capabilities',detail='technology')
    body+=region(state,'Suppliers / contracts',kind='technology',caption='Disclosed collaboration only; contracted service and dates unavailable',focus='partners')
    body+='</div>'
    body+=reported(facts,keys)+interpretation(facts,keys,meaning) if keys else '<p class="le-limit">'+e(meaning)+'</p>'
    body+='<section class="gold-dossier"><h3>Commercial significance</h3><p>'+e(meaning)+'</p><h3>Account investigation</h3><p>'+e(question)+'</p><p class="le-limit">Potential intervention must add to existing capabilities. No buyer need, budget, procurement event or supplier demand is established.</p></section>'
    body+='<p class="gold-related">'+link(state,'Applications & disclosed suppliers',focus='applications')+link(state,'Transformation disclosures',focus='programmes')+link(state,'Related strategy',stream='forces',focus='strategy',detail='goals')+'</p>'
    return body


def ai_performance(state,facts):
    """One strategy home for Group AI outcomes; no platform allocation or forecast."""
    keys=('LBG-AI26-REPORTED','LBG-AI26-EXPECTED')
    if not all(key in facts for key in keys):
        return '<p class="le-deck">A comparable AI performance view cannot be shown for this selection.</p>'
    body='<h2>Turn AI capability into measured benefit</h2><p class="le-deck">Separate the earlier reported contribution from the later management expectation.</p>'
    body+='<div class="gold-benefit-horizons" aria-label="Group AI reporting horizons">'
    for key,label in zip(keys,('FY2025 · management-reported contribution','2026 · management expectation')):
        body+='<section><h3>'+label+'</h3>'+reported(facts,(key,))+'</section>'
    body+='</div>'
    body+=interpretation(facts,keys,'The disclosed contribution and expectation are different periods and states. They do not establish realised 2026 growth, a percentage of target delivered or net benefit after model, infrastructure, change and control costs. No amount is attributed to Envoy, a division or a supplier.')
    if 'LBG-ENVOY-CONTROLS' in facts:
        body+='<section class="gold-subject-context"><h3>Management response already in place</h3>'+reported(facts,('LBG-ENVOY-CONTROLS',))+'<p>A disclosed controlled platform is existing capability. Its presence is not independent proof of effectiveness or the cause of the reported Group contribution.</p></section>'
        body+=region(state,'Envoy operating capability',kind='technology',caption='Disclosed controls, collaboration and operating questions',stream='inside',focus='applications',detail='envoy-controls')
    body+='<h3>The unresolved business decision</h3><p>The eligible disclosures do not reconcile gross contribution to full-cost net value or show which customer workflows produced it. A platform gap or a supplier opportunity cannot be inferred.</p><h3>Commercial investigation</h3><p>'+e(GOAL_DECISIONS['ai'][1])+' Confirm who owns the outcome and whether any decision remains open before proposing a diagnostic. External intervention remains a hypothesis; no buyer mandate or budget is established.</p>'
    return body


def _ceo_goals(state,facts):
    selected=state.detail.removeprefix('objective-') if state.detail.startswith('objective-') else None
    available=[row for row in OBJECTIVES if all(key in facts for key in row[3])]
    if selected:
        row=next((row for row in available if row[0]==selected),None)
        if row is None:return '<p class="ceo-unavailable">This objective is unavailable.</p>'
        key,horizon,title,keys,owner,programme,journey=row
        if key=='ai':return ai_performance(state,facts)+executive_goal_context(state,facts,key)
        body='<p class="eyebrow">'+e(horizon)+'</p><h2>'+e(title)+'</h2>'+reported(facts,keys)
        body+='<p class="le-limit">A matched baseline and current actual are not established for this objective. Published priorities and future ambitions are not a percentage achieved.</p>'
        body+=executive_goal_context(state,facts,key)
        body+='<h3>Commercial investigation</h3><p>'+e(GOAL_DECISIONS[key][1])+'</p><p class="le-limit">External intervention is a hypothesis only; procurement, budget and sponsor mandate are unproven.</p>'
        body+='<p class="gold-related">'+link(state,'Operating context',stream='inside',focus='operations',detail='journey-'+journey)
        if programme:body+=link(state,'Existing programme disclosure',stream='inside',focus='programmes',detail=programme)
        return body+'</p>'
    body='<p class="le-deck">Management objectives, on their own reporting horizons.</p>'+strategy_regions(state,facts)
    if 'LBG-Q326-INVESTMENT' in facts and not all(key in facts for key in ('LBG-Q326-INVESTMENT','LBG-A2030-INVESTMENT')):
        body+='<section><h2>Separate investment context</h2>'+reported(facts,('LBG-Q326-INVESTMENT',))+'</section>'
    body+='<p class="le-limit">No measured progress-to-target chart is shown without a matched baseline and actual. A prior-year contribution and a later expectation are different states, not a percentage achieved.</p>'
    return body


def _ceo_financial(state,facts,issues):
    if state.detail.startswith('service-'):
        return service_context(state) or '<p class="le-deck">Product-level service measures cannot be shown for this selection.</p>'
    if state.detail not in {'funding','income','costs','capital','divisions'}:return economics(state,facts,issues)
    title={'funding':'Funding & interest economics','income':'Income & profit','costs':'Costs, impairment & remediation','capital':'Capital, liquidity & returns','divisions':'Reporting businesses & contribution'}[state.detail]
    body='<h2>'+title+'</h2>'
    if state.detail!='funding':
        body+=exploration_rail(state,(('funding','Funding','Dated balances and repricing'),
            ('income','Income & profit','Interest, fees and the profit bridge'),
            ('costs','Costs & impairment','Efficiency, remediation and credit risk'),
            ('capital','Capital & returns','Risk capacity and distributions')),state.detail,kind='money')
    if state.detail=='funding':
        body+=economics(replace(state,detail='funding'),facts,issues)
    elif state.detail=='income':
        body+='<div class="le-measures">'+preview.measures({k:s for k,s in facts.items() if k=='LBG-Q326-PROFIT'})+'</div>'
        body+='<section class="gold-activation-story"><h2>Follow the earnings bridge</h2><div class="gold-value-path"><span>Interest earned less paid</span><span>Fees & other income</span><span>Costs & credit losses</span><span>Profit</span></div><p>Loan volumes alone do not explain income: pricing, asset mix and funding repricing also matter. Fees and other income have different drivers from net interest income.</p><p>The reported Group statutory profit is a flow over nine months. It is not segment contribution, underlying profit, a lending yield or an amount available for investment. A matched accounting bridge is needed to attribute any movement.</p></section>'
    elif state.detail=='costs':
        body+=service_context(state)
        body+='<section class="gold-activation-story"><h2>Three different pressures on earnings</h2><div class="gold-value-path"><span>Run & change costs</span><span>Remediation</span><span>Credit impairment</span></div><p>Ordinary operating expense, remediation and credit losses need separate explanations. An impairment charge covers a period; arrears and allowances are different stocks. A favourable prior-period comparison is not automatically a structural improvement.</p></section>'
        if all(k in facts for k in ('LBG-A2030-CIR','LBG-A2030-SAVINGS')):
            body+=region(state,'Efficiency objectives',kind='timeline',caption='Management ambitions, not reported cost performance',stream='forces',focus='strategy',detail='objective-efficiency')
        body+='<p class="le-limit">A lower cost-to-income ratio can reflect income growth as well as cost reduction. Gross savings are not net profit. A matched income, expense and remediation comparison is needed before judging progress.</p>'
    elif state.detail=='capital':
        body+='<section class="gold-activation-story"><h2>Growth uses capacity as well as funding</h2><div class="gold-value-path"><span>Risk-weighted assets</span><span>Capital generation</span><span>Buffers</span><span>Distributions</span></div><p>New lending can consume risk capacity. Capital generation, regulatory and management buffers, and distributions influence how much capacity remains. More deposits do not by themselves establish more capital or a larger investment budget.</p><p>Return on tangible equity needs a matched profit and capital basis. Actual and pro-forma ratios must remain separate; no capital ratio or return is inferred from the earnings and funding context shown here.</p></section>'
        body+=financial_regions(state,facts)
    else:
        body+=business_regions(state,central=True)
        body+='<p class="le-limit">Group profit cannot be allocated to businesses by customer count, deposit balance or visual area. Reporting segments, regulated legal entities and operating capabilities have different boundaries; underlying segment profit needs its statutory Group bridge.</p>'
    return body

# Gold v2 editorial composition over the existing research/Source owners.
# No model, score, qualification decision, Financial run or persisted projection.
V2_LEADERS = (
 ('NUNN','Charlie Nunn','Group CEO','Group direction','strategy'),
 ('CHALMERS','William Chalmers','Finance','Earnings, capital and investment','finance'),
 ('KEMENADE','Ron van Kemenade','Operations','Platforms, operations and delivery','platforms'),
 ('DOHERTY','Sharon Doherty','People & places','Skills and organisational change','support'),
 ('BARUA','Chirantan Barua','Scottish Widows / Wealth & Insurance','Protection, saving and investing','insurance'),
 ('LANGLEY','John Langley','Corporate & Institutional Banking','Corporate finance and transaction services','payments'),
 ('MURPHY','Amanda Murphy','Business & Commercial Banking','Business customers and commercial banking','credit'),
 ('SINGH','Jasjyot Singh OBE','Consumer','Consumer business','service'),
 ('WILLIAMS','Nick Williams','Connected Finance','Connected financial propositions','payments'),
 ('RISK','Javier Rodríguez de Colmenares','Risk','Risk management','risk'),
 ('LEGAL','Kate Cheetham','Legal & company secretariat','Legal and corporate governance','risk'),
 ('AUDIT','Laura Needham','Internal audit','Independent internal assurance','risk'),
 ('SUSTAINABILITY','Andrew Walton','Sustainability & corporate affairs','Sustainability and external affairs','strategy'),
)
V2_CLAIMS = ('LEGAL','AUDIT','SUSTAINABILITY','NUNN','CHALMERS','KEMENADE','DOHERTY','BARUA','LANGLEY','MURPHY','SINGH','WILLIAMS','RISK',
 'IDENTITY','CUSTOMERS','COLLEAGUES','SHAREHOLDERS','BANK','BOS','WIDOWS','MBNA','WEALTH','BLACKHORSE','LEX','TUSKER','BRANDWORKFORCE',
 'MSAGREEMENT','MSADOPTION','ENGINEERS','ASSISTANT','AIRECRUIT','AITEAMS','AITRAINING','FRAUDWORKFLOW','HUMANCONTROL','FRAUDOWNER',
 'CONDON','CONDONREPORT','TRANSACTIONREMIT')
LLOYDS_IDS += tuple('LBG-V2-'+key for key in V2_CLAIMS)
DETAILS['group'] += ('brands',)
DETAILS['people'] += tuple('leader-'+key.lower() for key,*_ in V2_LEADERS)
DETAILS['programmes'] += ('frontier','fraud','skills')
DETAILS['applications'] += ('frontier','fraud')
FOCUS_FACTS['group'] += tuple('LBG-V2-'+k for k in ('IDENTITY','CUSTOMERS','SHAREHOLDERS'))
FOCUS_FACTS['people'] += tuple('LBG-V2-'+k for k in (*[r[0] for r in V2_LEADERS],'COLLEAGUES','BRANDWORKFORCE','AIRECRUIT','AITEAMS','AITRAINING'))
FOCUS_FACTS['partners'] += tuple('LBG-V2-'+k for k in ('MSAGREEMENT','ENGINEERS'))
FOCUS_FACTS['programmes'] += tuple('LBG-V2-'+k for k in ('MSAGREEMENT','MSADOPTION','ASSISTANT','FRAUDWORKFLOW','HUMANCONTROL','AIRECRUIT','AITEAMS'))
FOCUS_FACTS['applications'] += tuple('LBG-V2-'+k for k in ('MSAGREEMENT','MSADOPTION','ENGINEERS','ASSISTANT','FRAUDWORKFLOW','HUMANCONTROL'))
FOCUS_FACTS['commercial'] += tuple('LBG-V2-'+k for k in ('CONDON','CONDONREPORT','TRANSACTIONREMIT'))
FOCUS_FACTS['operations'] += tuple('LBG-V2-'+k for k in ('FRAUDWORKFLOW','HUMANCONTROL','FRAUDOWNER','TRANSACTIONREMIT'))
FOCUS_FACTS['strategy'] += tuple('LBG-V2-'+k for k in ('MSAGREEMENT','FRAUDWORKFLOW','AIRECRUIT'))
# Every new statement also has a home in the existing optional inspection view.
# This is navigation metadata, not another Evidence owner or admission decision.
for _focus,_keys in {
 'group':('BANK','BOS','WIDOWS','MBNA','WEALTH','BLACKHORSE','LEX','TUSKER'),
 'retail':('BANK','BOS','MBNA','BLACKHORSE','LEX','TUSKER'),
 'retirement':('WIDOWS','WEALTH'),
 'commercial':('MURPHY','LANGLEY'),
 'people':('CONDON','CONDONREPORT'),
 'partners':('MSADOPTION','ASSISTANT'),
 'applications':('FRAUDOWNER',),
 'programmes':('ENGINEERS','FRAUDOWNER','AITRAINING'),
 'strategy':('KEMENADE','SINGH','RISK','CHALMERS','LANGLEY','MSADOPTION','CUSTOMERS','HUMANCONTROL','TRANSACTIONREMIT'),
}.items():
    FOCUS_FACTS[_focus] += tuple('LBG-V2-'+k for k in _keys)



def executive_facts(data, facts):
    """Finite presentation binding checks; Source still owns the actual research.

    Exact statements, role/period/perimeter and source bindings cannot be changed
    by a viewer. These are factual integrity checks, not per-claim approvals.
    """
    result=dict(facts);sources={s['id']:s for s in data.get('sources',())}
    claims={c['id']:c for c in data.get('claims',())}
    allowed={'LGV2-LEADERS','LGV2-PROFILE','LGV2-BRANDS','LGV2-FRONTIER','LGV2-AIPEOPLE','LGV2-FRAUD','LGV2-TRANSACTIONS'}
    fields=('statement','kind','entity_scope','asset_id','reporting_period','primary_quotes')
    for ident in ('LBG-V2-'+key for key in V2_CLAIMS):
        claim=claims.get(ident,{});refs=claim.get('source_ids',());valid=False
        if ident in result and len(refs)==1 and refs[0] in allowed:
            src=sources.get(refs[0],{});rights=src.get('rights',{})
            bindings=[b for b in src.get('disclosure_bindings',()) if b.get('claim_id')==ident]
            expected_url,expected_date=V2_SOURCE_URLS[refs[0]]
            valid=(not source_import.working_restricted(src) and not src.get('restrictions')
                and src.get('url')==src.get('retrieval_url')==expected_url
                and src.get('publication_date')==expected_date
                and src.get('content_kind')=='reviewed_web_excerpt'
                and src.get('primary_content_sha256')is None
                and rights.get('status')=='permitted_public_factual_category'
                and rights.get('policy_reference')=='https://github.com/rdidale-jpg/CIOS/pull/698/commits/9a7181fbcc43c23188c3f4ce7b7b1dea9d41977e'
                and rights.get('attribution_url')=='https://www.lloydsbankinggroup.com/'
                and rights.get('homepage_conditions_met')is True
                and claim.get('reporting_period')==src.get('reporting_period')
                and len(bindings)==1 and all(bindings[0].get(k)==claim.get(k) for k in fields)
                and result[ident].scope==recovery.GROUP and claim.get('asset_id')=='BK-ENT-001')
        if not valid:result.pop(ident,None)
    return result


def v2_reported(facts,*keys):
    return reported(facts,tuple('LBG-V2-'+k for k in keys))


def executive_overview(state,facts,issues):
    body='<p class="le-deck">A UK financial group: everyday banking, business finance, and long-term saving and protection.</p>'
    if 'LBG-V2-CUSTOMERS' in facts:
        body+='<div class="v2-enterprise-scale">'+v2_reported(facts,'CUSTOMERS')+'</div>'
    body+=business_regions(state)+financial_regions(state,facts)
    body+='<section class="v2-value-thread"><h2>One Group, different economic engines</h2><p>Retail earns from lending, fees and asset services. Commercial combines credit with cash, trade and payment services. Insurance and investments earn through protection, distribution and long-term asset administration.</p><p class="le-limit">Business-model explanation, not a measured profit split. Segment profit, statutory Group profit and legal-bank results have different boundaries.</p></section>'
    body+='<div class="v2-executive-agenda" aria-label="Published executive priorities"><h2>Leadership’s agenda</h2>'
    for title,keys,caption,detail in (
      ('Simplify while protecting service',('LBG-AR25-MIGRATION','LBG-A2030-CIR'),'Application retirement and the 2030 efficiency ambition','objective-renewal'),
      ('Turn AI adoption into economic return',('LBG-AI26-REPORTED','LBG-AI26-EXPECTED'),'Reported contribution, expectation and full-cost attribution','objective-ai'),
      ('Connect more customer activity',('LBG-A2030-WALLET','LBG-Q326-CURVE'),'Payments direction and an acquisition reported complete','objective-payments')):
        if all(k in facts for k in keys):body+=region(state,title,kind='timeline',caption=caption,stream='forces',focus='strategy',detail=detail)
    body+='</div>'
    funding=next((row for row in issues if row.key=='funding-base'),None)
    if funding and funding.facts[-1].semantic_type=='calculated' and all(k in facts for k in ('LBG-AR25-DEPOSITS','LBG-Q326-DEPOSITS')):
        body+='<div data-intelligence="funding-base">'+p.render(funding.facts[-1],compact=True)+'</div>'
    body+='<div class="gold-related">'+link(state,'Funding comparison',focus='economics',detail='comparison')+link(state,'Group brands & identity',focus='group',detail='brands')+link(state,'Organisation & workforce',stream='inside',focus='people',detail='leadership')+'</div>'
    if 'LBG-Q326-CURVE' in facts:
        body+=region(state,'Curve acquisition reported complete',reported(facts,('LBG-Q326-CURVE',)),kind='change',caption='Completion is not integration progress or open supplier scope',stream='inside',focus='programmes',detail='curve')
    # A neutral operating destination, never an attention or pressure marker.
    body+='<div class="gold-related">'+link(state,'Customer operations',stream='inside',focus='operations',detail='service')+link(state,'Management goals',stream='forces',focus='strategy',detail='goals')+'</div>'
    return body


def executive_brands(state,facts):
    body='<h2>The Group and its customer brands</h2>'+v2_reported(facts,'IDENTITY','SHAREHOLDERS')
    body+='<div class="v2-brand-ribbon" aria-label="Disclosed brand and product families">'
    for key,title,focus in (('BANK','Lloyds Bank','retail'),('BOS','Bank of Scotland','retail'),('MBNA','MBNA','retail'),('BLACKHORSE','Black Horse','retail'),('LEX','Lex Autolease','retail'),('TUSKER','Tusker','retail'),('WIDOWS','Scottish Widows','retirement'),('WEALTH','Lloyds Wealth','retirement')):
        if 'LBG-V2-'+key in facts:body+=region(state,title,v2_reported(facts,key),kind='business',caption='Product-family navigation; not a legal ownership or exclusive segment allocation',focus=focus,subject=focus)
    body+='</div><p class="le-limit">A brand is not necessarily a legal entity, and a reporting business is not a subsidiary. Lloyds Bank and Bank of Scotland serve more than one customer business. The current ownership percentages and voting-control structure are not established here.</p>'
    return body


def executive_people(state,facts):
    if state.detail=='workforce':return executive_workforce(state,facts)
    if not any('LBG-V2-'+r[0] in facts for r in V2_LEADERS):return _ceo_people(state,facts)
    body='<p class="le-deck">Who leads the businesses, and who enables the Group.</p><p class="eyebrow">Published executive membership · observed 27 November 2026</p>'
    chosen=state.detail.removeprefix('leader-').upper() if state.detail.startswith('leader-') else None
    body+='<div class="v2-organisation" aria-label="Group executive membership; reporting lines not inferred">'
    for title,keys in (('Group direction',('NUNN',)),('Customer businesses',('SINGH','MURPHY','LANGLEY','BARUA','WILLIAMS')),('Group-wide functions',('CHALMERS','KEMENADE','DOHERTY','RISK','LEGAL','AUDIT','SUSTAINABILITY'))):
        available=[r for r in V2_LEADERS if r[0] in keys and 'LBG-V2-'+r[0] in facts]
        if not available:continue
        body+='<section><h2>'+title+'</h2><div>'
        for key,name,role,remit,journey in available:
            body+=region(state,name,'<span class="v2-role">'+e(role)+'</span>',kind='organisation',caption=remit,focus='people',detail='leader-'+key.lower())
        body+='</div></section>'
    body+='</div><p class="le-limit">Executive membership and role remit are reported. The layout does not assert who reports to whom, delegated spending authority, or a one-to-one match to financial segments.</p>'
    if chosen:
        row=next((r for r in V2_LEADERS if r[0]==chosen and 'LBG-V2-'+r[0] in facts),None)
        if row:
            key,name,role,remit,journey=row;body+='<section class="v2-selected"><h2>'+e(name)+' · '+e(role)+'</h2>'+v2_reported(facts,key)
            body+='<p>'+e(remit)+' is the relevant functional context, not a verified purchase mandate.</p>'
            if journey in JOURNEYS:
                body+=region(state,'Operating responsibilities to understand',kind='operating',caption='Relevant capability context; delegated ownership remains to be confirmed',focus='operations',detail='journey-'+journey)
            else:
                body+=region(state,'Published strategic priorities',kind='timeline',caption='Group strategy context; no delegated goal or buying authority is inferred',stream='forces',focus='strategy',detail='goals')
            body+='</section>'
        else:body+='<p class="le-deck">The selected role cannot be shown from the available evidence.</p>'
    if 'LBG-V2-CONDONREPORT' in facts:
        body+='<section class="v2-reported-line"><h2>One explicitly disclosed reporting line</h2>'+v2_reported(facts,'CONDON','CONDONREPORT')+region(state,'Transaction Banking',kind='commercial',caption='Cash, working capital, trade and payments within CIB',stream='landscape',focus='commercial',detail='transactions')+'</section>'
    if state.detail=='structure':
        body+='<h2>Financial reporting businesses</h2>'+business_regions(state)+'<p class="le-limit">Consumer, Connected Finance and named executive remits are management views. Retail, Commercial Banking and Insurance, Pensions & Investments are financial reporting views; no unsupported mapping is imposed.</p>'
    return body+'<div class="gold-related">'+link(state,'Leadership',focus='people',detail='leadership')+link(state,'Businesses & functions',focus='people',detail='structure')+link(state,'Workforce',focus='people',detail='workforce')+'</div>'


def executive_workforce(state,facts):
    body='<h2>People, skills and capacity</h2><div class="v2-workforce"><section><h3>Group scale</h3>'+v2_reported(facts,'COLLEAGUES')+'<p class="le-limit">This is an undated issuer profile, not audited FTE or a current-year employee count.</p></section><section><h3>Building specialist capacity</h3>'+v2_reported(facts,'AIRECRUIT','AITEAMS')+'</section><section><h3>Developing existing colleagues</h3>'+v2_reported(facts,'AITRAINING')+'</section></div>'
    if 'LBG-V2-BRANDWORKFORCE' in facts:body+=v2_reported(facts,'BRANDWORKFORCE')
    body+='<p class="le-limit">Course completions, trained people, licence holders and employees have different denominators. Licences are not people. No workforce reduction, net hiring, FTE distribution, salary cost or productivity saving is calculated from these disclosures.</p>'
    body+=region(state,'Colleague technology',kind='technology',caption='Microsoft deployment and licensed-user adoption; separate from employee counts',focus='applications',detail='frontier')
    if 'LBG-BRAND26-NO-ROLES' in facts:body+=interpretation(facts,('LBG-BRAND26-NO-ROLES',),'The brand-transition announcement rules out related role reductions. That narrow statement does not establish Group-wide workforce growth, a hiring plan or an outsourcing decision.')+region(state,'Brand transition and service access',kind='change',caption='The disclosed change and its specific workforce boundary',focus='programmes',detail='brand')
    return body+region(state,'AI value and work',kind='timeline',caption='Group contribution and expectation; no net return or automatic capacity claim',stream='forces',focus='strategy',detail='objective-ai')


def executive_operating_context(state,facts):
    body='<section class="v2-operating-evidence"><h2>Where operating change is actually disclosed</h2>'
    for key,title,detail,caption in (
      ('FRAUDWORKFLOW','Fraud decisions with human accountability','fraud','Envoy-built workflow; disclosed delivery teams and colleague override'),
      ('MSAGREEMENT','Colleague and engineering tools','frontier','Announced Microsoft agreement; deployment and reported adoption')):
        if 'LBG-V2-'+key in facts:body+=region(state,title,kind='operating',caption=caption,focus='applications',detail=detail)
    if 'LBG-V2-TRANSACTIONREMIT' in facts:body+=region(state,'Corporate cash, trade and payments',kind='commercial',caption='Actual Transaction Banking remit; not an inferred revenue allocation',stream='landscape',focus='commercial',detail='transactions')
    return body+'</section>'


def executive_technology(state,facts):
    fraud=state.detail=='fraud';keys=('FRAUDWORKFLOW','HUMANCONTROL','FRAUDOWNER') if fraud else ('MSAGREEMENT','MSADOPTION','ENGINEERS','ASSISTANT')
    available=[k for k in keys if 'LBG-V2-'+k in facts]
    if not available:return '<p class="le-deck">This disclosed operating example cannot be shown for this selection.</p>'
    title='Fraud decision support' if fraud else 'Colleague and engineering AI'
    body='<h2>'+title+'</h2>'+v2_reported(facts,*available)
    stages=('Customer interaction','Parallel checks','Colleague judgement','Override and outcome') if fraud else ('Licensed access','Reported activity','Task result','Full-cost benefit')
    body+='<div class="v2-operating-sequence" aria-label="Conceptual evaluation sequence">'+''.join('<span>'+e(s)+'</span>' for s in stages)+'</div><p class="le-limit">An explanatory sequence, not a verified system topology or measured conversion funnel.</p>'
    if fraud:
        body+='<h3>Why this matters</h3><p>There is an actual cross-functional workflow to investigate, rather than an assumed missing AI platform. Fraud, technology, data and risk participation and human override are disclosed. False positives, prevented losses, handling time and full costs are not independently established.</p><h3>Management response and next decision</h3><p>The disclosed response already uses Envoy and existing colleague tools. The useful next question is which outcome or exception remains unresolved after that response, and what evidence would change the decision to expand it.</p>'
        body+=region(state,'Envoy operating capability',kind='technology',caption='Existing platform disclosure; the example does not map the entire cloud estate',focus='applications',detail='envoy-controls')
    else:
        body+='<h3>Adoption is stronger evidence than availability</h3><p>The June announcement supplies a licensed-user activity percentage, beyond the earlier FY2025 licence count. It still does not define the activity threshold, independent service improvement or net economic return. Engineer and colleague populations must not be added together.</p><h3>Commercial investigation</h3><p>Which named workflow shows a sustained task, customer or control improvement after run, change and supervision costs? Confirm what existing Microsoft and internal delivery already cover before suggesting external scope.</p>'
    return body+region(state,'Group AI performance',kind='timeline',caption='Different reporting horizons; no platform-level allocation',stream='forces',focus='strategy',detail='objective-ai')


def executive_programme(state,facts):
    rows={'frontier':('Microsoft deployment','4 June 2026',('MSAGREEMENT','MSADOPTION','ASSISTANT'),'An agreement and deployment announcement; the assistant is a plan, not a proven live outcome.','Licensed-user activity, service outcomes and run/change costs need a matched definition.'),
          'fraud':('Fraud operating workflow','8 June 2026',('FRAUDWORKFLOW','HUMANCONTROL'),'A disclosed decision-support workflow with human accountability.','Which false-positive, customer and fraud outcome remains unresolved after the current response?'),
          'skills':('AI skills and roles','22 June 2026',('AIRECRUIT','AITEAMS','AITRAINING'),'A combination of existing teams, training activity and planned roles; not net hiring.','Which capabilities need new skills, and what outcome demonstrates the benefit of retraining?')}
    if state.detail not in rows:
        body='<div class="v2-programme-sequence" aria-label="Dated operating developments">'
        for key,(title,date,keys,meaning,question) in rows.items():
            if any('LBG-V2-'+k in facts for k in keys):body+=region(state,title,'<time>'+date+'</time>',kind='timeline',caption=meaning,focus='programmes',detail=key)
        return body+'</div>'
    title,date,keys,meaning,question=rows[state.detail]
    if not any('LBG-V2-'+k in facts for k in keys):return '<p class="le-deck">This programme disclosure cannot be shown for this selection.</p>'
    body='<p class="eyebrow">'+date+'</p><h2>'+title+'</h2>'+v2_reported(facts,*keys)+'<p>'+meaning+'</p>'
    body+='<dl class="v2-decision"><div><dt>Existing response</dt><dd>'+meaning+'</dd></div><div><dt>Decision and evidence</dt><dd>'+question+'</dd></div><div><dt>Delivery boundary</dt><dd>Named executive remit is not delegated programme sponsorship. No contract value, external workshare or unallocated budget is established.</dd></div></dl>'
    return body+region(state,'Supporting operating example',kind='technology',caption='Capabilities, adoption and outcome distinctions',focus='applications',detail='fraud' if state.detail=='fraud' else 'frontier')


def executive_goal_context(state,facts,key):
    role={'renewal':'KEMENADE','ai':'KEMENADE','access':'SINGH','reporting':'RISK','investment':'CHALMERS','efficiency':'CHALMERS','payments':'LANGLEY'}[key]
    body='<section class="v2-goal-logic"><h3>From goal to executive decision</h3>'
    if 'LBG-V2-'+role in facts:body+='<div class="v2-role-context">'+v2_reported(facts,role)+'<p class="le-limit">Relevant published role; ownership of this decision and delegated authority remain hypotheses.</p></div>'
    current={'renewal':('FRAUDWORKFLOW','An actual Envoy workflow is evidence of delivered capability, not proof that legacy retirement is complete.'),
      'ai':('MSADOPTION','Reported activity adds adoption evidence; it does not reconcile Group contribution to net return.'),
      'access':('CUSTOMERS','Group scale explains why continuity matters, not the outcome of a particular brand change.'),
      'reporting':('HUMANCONTROL','A disclosed fraud control is existing capability, not evidence of readiness for every regulatory reporting duty.'),
      'investment':('MSAGREEMENT','An existing agreement is committed direction, not unallocated supplier spend.'),
      'efficiency':('AIRECRUIT','Specialist role investment can coexist with efficiency ambitions; it is not a verified net headcount or cost change.'),
      'payments':('TRANSACTIONREMIT','CIB Transaction Banking has a disclosed remit and leadership, separate from unproven customer demand.')}[key]
    if 'LBG-V2-'+current[0] in facts:body+=v2_reported(facts,current[0])+'<p>'+current[1]+'</p>'
    dependencies={'renewal':('Live-service dependency mapping','Recovery evidence and dual running','Which cutover can safely retire cost?'),
      'ai':('Data, colleague adoption and oversight','Outcome attribution and full costs','Which workflow merits further scaling?'),
      'access':('Customer communication and service routes','Displaced demand and comprehension','Which cohorts require a different transition?'),
      'reporting':('Legal-entity scope and provider inventory','Existing control/reporting evidence','Which applicable reporting gap remains?'),
      'investment':('Committed change capacity and capital','Return evidence and competing programmes','Which sequencing choice is still open?'),
      'efficiency':('Income, expenses, remediation and delivery','Gross savings versus net service outcome','Which matched cost bridge explains progress?'),
      'payments':('Cash management, trade, working capital and payments','Adoption, integration and risk-adjusted return','Which existing client decision can be improved?')}[key]
    body+='<dl class="v2-decision">'+''.join('<div><dt>'+label+'</dt><dd>'+e(value)+'</dd></div>' for label,value in zip(('Dependencies to establish','Risks and counter-evidence','Next decision'),dependencies))+'</dl><p class="le-limit">These are analytical connections to published direction, not qualified Material Pressures, buyer needs or opportunities.</p></section>'
    return body


def executive_force_overview(state,facts):
    body='<p class="le-deck">Protect today’s earnings while building a simpler, more connected Group.</p>'
    body+='<div class="v2-horizons" aria-label="Published strategy horizons">'
    for horizon,title,keys,caption,detail in (
      ('2026','Finish the current transformation',('LBG-AR25-MIGRATION',),'Retire applications and migrate carefully; delivery is not proved by the priority','objective-renewal'),
      ('2027','Sequence the next investment cycle',('LBG-A2030-INVESTMENT',),'A planned increase followed by discipline; no supplier allocation','objective-investment'),
      ('2030','Create lasting operating leverage',('LBG-A2030-CIR','LBG-A2030-SAVINGS'),'Efficiency ambition and gross savings, distinct from achieved net benefit','objective-efficiency')):
        if all(k in facts for k in keys):body+=region(state,title,'<time>'+horizon+'</time>'+reported(facts,keys[:1]),kind='timeline',caption=caption,focus='strategy',detail=detail)
    body+='</div><h2>Executive choices</h2><div class="v2-choice-map">'
    for title,keys,caption,focus,detail in (
      ('Earnings and funding',('LBG-Q326-PROFIT','LBG-Q326-DEPOSITS'),'Group profit and funding are real; repricing, costs and capital explain the mechanism','markets','mechanism'),
      ('AI value beyond deployment',('LBG-AI26-REPORTED','LBG-AI26-EXPECTED'),'A reported contribution, a later expectation and a full-cost attribution question','strategy','objective-ai'),
      ('Connected customer propositions',('LBG-A2030-WALLET','LBG-Q326-CURVE'),'Payments direction and completed acquisition; adoption is not established','strategy','objective-payments'),
      ('Resilience through change',('LBG-AR25-MIGRATION','UK-PRA-REPORT27'),'A transition priority and dated regulation; no control failure inferred','resilience','applicability')):
        if all(k in facts for k in keys):body+=region(state,title,kind='timeline',caption=caption,focus=focus,detail=detail)
    body+='</div><p class="le-limit">Published priorities and analytical trade-offs. None is automatically a qualified Material Pressure or sales opportunity.</p>'
    body+='<div class="gold-related">'+link(state,'Eight-theme SWOT',focus='analysis')+link(state,'Strategic alternatives',focus='strategy',detail='options')+link(state,'All management goals',focus='strategy',detail='goals')+'</div>'
    return body

# Broader CEO agenda at the existing Forces destination; no new stream/route.
REGIONS['forces']=(('markets','Executive agenda'),)+REGIONS['forces'][1:]
SUBJECTS['markets']='Executive agenda'


def executive_commercial(state,facts):
    body='<p class="le-deck">Business lending and deposits sit alongside corporate financing, trade, cash management and payments.</p><div class="v2-commercial-businesses">'
    for key,title,context in (('MURPHY','Business & Commercial Banking','Business customer relationships and commercial banking'),('LANGLEY','Corporate & Institutional Banking','Corporate and institutional relationships, including Transaction Banking')):
        if 'LBG-V2-'+key in facts:body+=region(state,title,v2_reported(facts,key),kind='business',caption=context,stream='inside',focus='people',detail='leader-'+key.lower())
    body+='</div><div class="v2-economic-sequence"><span>Lending and liquidity</span><span>Transaction and risk services</span><span>Funding, credit and capital cost</span><span>Commercial return</span></div><p class="le-limit">Conceptual economic mechanism. Executive business remits are not a verified split of reported Commercial Banking profit, capital or customer balances.</p>'
    if 'LBG-V2-TRANSACTIONREMIT' in facts:body+=v2_reported(facts,'TRANSACTIONREMIT')
    body+=region(state,'Transaction Banking',kind='commercial',caption='Cash, working capital, trade and payments: actual remit and leadership, then customer economics',detail='transactions')
    return body+region(state,'Group funding & earnings',kind='money',caption='Keep reporting period, legal bank and management business separate',focus='economics',detail='comparison')

V2_SOURCE_URLS = {
 'LGV2-LEADERS':('https://www.lloydsbankinggroup.com/who-we-are/group-overview/group-executive-committee.html',None),
 'LGV2-PROFILE':('https://www.lloydsbankinggroup.com/who-we-are.html',None),
 'LGV2-BRANDS':('https://www.lloydsbankinggroup.com/who-we-are/our-brands.html',None),
 'LGV2-FRONTIER':('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds-banking-group/microsoft-365-frontier-suite.html','2026-06-04'),
 'LGV2-AIPEOPLE':('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds-banking-group/1000-new-ai-roles.html','2026-06-22'),
 'LGV2-FRAUD':('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds-banking-group/lloyds-banking-group-deploys-agentic-ai-to-strengthen-real-time-.html','2026-06-08'),
 'LGV2-TRANSACTIONS':('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds/lloyds-appoints-natasha-condon-global-head-transaction-banking.html','2026-11-18'),
}


# Finite presentation compositions over the same current, eligible facts.
# Coordinates describe the picture only: never allocations, reporting lines,
# installation maps, scores, or new enterprise-model relationships.
def experience_node(state, label, content, geometry, *, kind='operating', shape='river', caption='', **target):
    x,y,w,h=geometry
    selected=(target.get('focus',state.focus)==state.focus and target.get('detail','')==state.detail)
    return ('<a class="canvas-region ce-node ce-'+shape+'" data-canvas-region="'+kind+'" '
            'style="--x:'+str(x)+'%;--y:'+str(y)+'%;--w:'+str(w)+'%;--h:'+str(h)+'%" '
            'href="'+e(href(state,**target),quote=True)+'" aria-label="'+e(label,quote=True)+'"'
            +(' aria-current="page"' if selected else '')+'><span class="canvas-title">'+e(label)+'</span>'
            +('<span class="ce-node-copy">'+content+'</span>' if content else '')
            +('<span class="canvas-caption">'+e(caption)+'</span>' if caption else '')+'</a>')


def experience_map(kind, label, paths, nodes, legend):
    drawing='<svg class="ce-connections" viewBox="0 0 800 800" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
    floors={
      'operating':'<path class="ce-floor" d="M0 22 Q400 -20 800 22 L800 164 Q400 215 0 164Z"/><path class="ce-floor" d="M0 390 Q400 330 800 390 L800 484 Q400 528 0 484Z"/><path class="ce-floor ce-floor-light" d="M0 542 L800 542 L800 646 Q400 682 0 646Z"/>',
      'strategy':'<path class="ce-terrain" d="M0 38 Q130 -8 265 38 T535 38 T800 38 L800 186 Q400 237 0 186Z"/><path class="ce-strategy-current" d="M0 285 Q400 230 800 275 L800 664 Q400 720 0 665Z"/>',
      'economy':'<path class="ce-economy-current" d="M30 410 Q400 550 770 410 L740 540 Q400 665 60 540Z"/>',
    }.get(kind,'')
    drawing+=floors+''.join('<path d="'+path+'"/>' for path in paths)+'</svg>'
    return ('<div class="ce-map ce-'+kind+'" role="group" aria-label="'+e(label,quote=True)+'">'+drawing+''.join(nodes)
            +'</div><p class="ce-legend">'+e(legend)+'</p>')


def experience_landscape(state,facts,issues):
    body='<p class="le-deck">Households, businesses and long-term savers. Three economic engines; one Group balance sheet.</p>'
    nodes=[]
    if 'LBG-Q326-DEPOSITS' in facts:
        p.note_editorial_sources(facts['LBG-Q326-DEPOSITS'].sources)
        nodes.append(experience_node(state,'Customer funding','<strong class="ce-number">£'+str(facts['LBG-Q326-DEPOSITS'].value)+'bn</strong><span>Group customer deposits · reported stock</span><time>30 September 2026</time>',(0,0,29,21),kind='money',shape='reservoir',focus='economics',detail='funding'))
    if 'LBG-V2-CUSTOMERS' in facts:
        nodes.append(experience_node(state,'Customer relationships',p.render(facts['LBG-V2-CUSTOMERS'],compact=True),(34,0,32,24),shape='island',detail='brands'))
    if 'LBG-Q326-PROFIT' in facts:
        p.note_editorial_sources(facts['LBG-Q326-PROFIT'].sources)
        nodes.append(experience_node(state,'Reported earnings','<strong class="ce-number">£'+str(facts['LBG-Q326-PROFIT'].value)+'bn</strong><span>Group statutory pretax profit · reported flow</span><time>Nine months to 30 September 2026</time>',(71,0,29,21),kind='money',shape='reservoir',focus='economics',detail='income'))
    for i,(title,customer,activity,driver,key) in enumerate(twin.DIVISIONS):
        offer={'retail':'Borrow, save, pay and finance assets','commercial':'Lend, manage cash, trade and payments','retirement':'Protect, invest and administer long-term savings'}[key]
        nodes.append(experience_node(state,title,'<span class="ce-customer">'+e(customer)+'</span><span>'+e(offer)+'</span><strong>'+e(driver)+'</strong>',(i*34,27,32,32),kind='business',shape='business',caption='Select the business economics',stream='landscape',focus=key,subject=key))
    nodes.append(experience_node(state,'Costs, credit and capital','<span>Funding price · operating costs · credit losses · risk capacity</span><strong>Economic growth must earn its cost of risk and delivery</strong>',(4,64,92,15),kind='money',shape='foundation',focus='economics',detail='capital'))
    choices=[('Simplify while protecting service',('LBG-AR25-MIGRATION','LBG-A2030-CIR'),'2030 efficiency ambition','objective-renewal'),
             ('Turn AI adoption into economic return',('LBG-AI26-REPORTED','LBG-AI26-EXPECTED'),'Contribution versus full-cost return','objective-ai'),
             ('Connect more customer activity',('LBG-A2030-WALLET','LBG-Q326-CURVE'),'Payments direction and Curve completion','objective-payments')]
    for i,(title,keys,caption,detail) in enumerate(choices):
        if all(k in facts for k in keys):nodes.append(experience_node(state,title,'',(i*34,84,32,14),kind='timeline',shape='current',caption=caption,stream='forces',focus='strategy',detail=detail))
    body+='<h2 class="ce-map-title">One Group, different economic engines</h2>'
    # Retain the existing business-region semantics and deep destinations.
    body+='<div class="canvas-businesses ce-portfolio">'+experience_map('economy','Reporting businesses · not financial shares',
        ('M110 150 C110 190 120 200 130 235','M110 160 C250 190 390 180 400 235','M685 155 C685 195 660 200 665 235','M130 470 Q130 515 400 530','M400 470 L400 530','M670 470 Q670 515 400 530','M400 630 L400 680'),nodes,
        'Conceptual economic relationships. Geometry does not encode business size, funding allocation or profit contribution. Group, reporting businesses and legal entities remain separate.')+'</div>'
    body+='<div class="ce-context-controls">'+link(state,'Funding comparison',focus='economics',detail='comparison')+link(state,'Organisation & workforce',stream='inside',focus='people',detail='leadership')+link(state,'Customer operations',stream='inside',focus='operations',detail='service')+'</div>'
    return body


def experience_inside(state,data,facts):
    body='<p class="le-deck">Customer value at the front. Information, controls, technology and people connect the enterprise underneath.</p>'
    nodes=[]
    streams=[('credit','Lending & credit','Households and businesses','Origination, risk decisions and servicing'),
             ('payments','Payments','Business and personal customers','Cash, trade, authorisation and settlement'),
             ('insurance','Insurance, pensions & wealth','Protection and long-term saving','Distribution, policy and asset administration')]
    for i,(key,title,customer,mechanism) in enumerate(streams):
        nodes.append(experience_node(state,title,'<span class="ce-customer">'+customer+'</span><strong>'+mechanism+'</strong>',(i*34,0,32,23),shape='value',focus='operations',detail='journey-'+key))
    nodes.append(experience_node(state,'Customer operations','<span>Service channels, requests and exceptions</span><strong>'+('Actual legal-bank service outcomes available' if agenda.lloyds_service_products() else 'Customer access and exception handling')+'</strong>',(8,28,84,13),shape='service',focus='operations',detail='service'))
    for i,(key,title,desc) in enumerate([('risk','Risk & controls','Credit, service continuity and human accountability'),('data','Data & AI','Information, models and controlled decisions'),('platforms','Platforms & change','Applications, resilience and retirement')]):
        nodes.append(experience_node(state,title,'<span>'+desc+'</span>',(i*34,46,32,16),shape='enabler',focus='operations',detail='journey-'+key))
    if all(k in facts for k in ('LBG-V2-FRAUDWORKFLOW','LBG-V2-HUMANCONTROL')):
        nodes.append(experience_node(state,'Envoy in fraud operations','<span>Disclosed fraud, technology, data and risk teams</span><strong>Human judgement and override remain</strong>',(0,67,49,15),kind='technology',shape='example',focus='applications',detail='fraud'))
    if 'LBG-V2-MSADOPTION' in facts:
        nodes.append(experience_node(state,'Microsoft in colleague work','<strong>Licensed-user adoption disclosed</strong><span>June 2026; activity is not a measured full-cost return</span>',(51,67,49,15),kind='technology',shape='example',focus='applications',detail='frontier'))
    count=sum('LBG-V2-'+r[0] in facts for r in V2_LEADERS)
    if count:nodes.append(experience_node(state,'Organisation & workforce','<strong>'+str(count)+' issuer-listed executive members</strong><span>Business leadership, Group functions and skills</span>',(0,87,49,12),kind='organisation',shape='people',focus='people',detail='leadership'))
    nodes.append(experience_node(state,'Finance & shared services','<span>Capital, performance, people and delivery capacity</span>',(51,87,49,12),shape='people',focus='operations',detail='journey-finance'))
    body+=experience_map('operating','Connected enterprise operating model',
        ('M130 184 C130 215 210 225 260 240','M400 184 L400 240','M670 184 C670 215 570 225 540 240','M400 328 L400 370','M130 365 Q400 320 670 365','M130 495 L130 535','M400 495 Q400 520 200 535','M670 495 L670 535','M200 657 L200 698','M600 657 L600 698'),nodes,
        'Conceptual value streams and enabling associations, not reporting lines or verified system dependencies. The two operating examples are separately supported issuer disclosures.')
    body+='<div class="ce-context-controls">'+link(state,'People & shared services',focus='operations',detail='journey-support')+link(state,'Capability relationships',focus='capabilities',detail='data')+link(state,'Transformation programmes',focus='programmes')+'</div>'
    return body


def experience_forces(state,facts):
    body='<p class="le-deck">Protect today’s earnings. Simplify safely. Turn new capability into enduring customer and economic value.</p>'
    nodes=[]
    for i,(horizon,title,keys,meaning,detail) in enumerate([
      ('2026','Retire applications while maintaining service',('LBG-AR25-MIGRATION',),'Current-cycle priority; retirement is not completion','objective-renewal'),
      ('2027','Sequence the next investment cycle',('LBG-A2030-INVESTMENT',),'Management investment plan, not free supplier budget','objective-investment'),
      ('2030','Create lasting operating leverage',('LBG-A2030-CIR','LBG-A2030-SAVINGS'),'Efficiency and gross-savings ambitions; not achieved net return','objective-efficiency')]):
        if all(k in facts for k in keys):nodes.append(experience_node(state,title,'<time class="ce-horizon">'+horizon+'</time><span>'+meaning+'</span>',(i*34,0,32,24),kind='timeline',shape='horizon',focus='strategy',detail=detail))
    if all(k in facts for k in ('LBG-Q326-PROFIT','LBG-Q326-DEPOSITS')):
        nodes.append(experience_node(state,'Earnings and funding','<strong>£'+str(facts['LBG-Q326-PROFIT'].value)+'bn nine-month Group profit</strong><span>£'+str(facts['LBG-Q326-DEPOSITS'].value)+'bn deposits at September 2026</span><span>Funding price, credit and capital constrain economic choices</span>',(0,33,100,12),kind='money',shape='tension',focus='economics',stream='landscape',detail='capital'))
    if all(k in facts for k in ('LBG-AI26-REPORTED','LBG-AI26-EXPECTED')):
        nodes.append(experience_node(state,'AI value beyond deployment','<span>FY2025 contribution / 2026 expectation</span><span>Existing platforms, tools and controls</span><strong>Adoption and full-cost net return remain distinct</strong>',(0,48,100,12),kind='technology',shape='tension',focus='strategy',detail='objective-ai'))
    if all(k in facts for k in ('LBG-AR25-MIGRATION','UK-PRA-REPORT27')):
        nodes.append(experience_node(state,'Resilience through change','<span>Retirement + March 2027 timetable</span><span>Migration and controlled operations</span><strong>Continuity and reporting require their own evidence</strong>',(0,63,100,12),shape='tension',focus='strategy',detail='objective-reporting'))
    if all(k in facts for k in ('LBG-A2030-WALLET','LBG-Q326-CURVE')):
        nodes.append(experience_node(state,'Connected customer propositions','<span>Payments ambition + completed Curve transaction</span><span>Acquisition already completed</span><strong>Integration and adoption determine customer value</strong>',(0,78,100,12),shape='tension',focus='strategy',detail='objective-payments'))
    nodes.append(experience_node(state,'Eight-theme SWOT','<span>Capabilities, constraints, alternatives and counter-evidence</span>',(4,94,92,9),kind='theme',shape='foundation',focus='analysis'))
    body+=experience_map('strategy','Strategic change and executive choices',
        ('M120 190 C120 230 160 240 190 260','M400 194 Q400 235 210 259','M670 194 L670 258','M190 363 Q400 373 600 380','M600 483 Q400 493 190 500','M190 603 Q400 613 600 620','M400 723 L400 748'),nodes,
        'Dotted connections are FLORA analytical associations, not proven causes or ranked Material Pressures. Published actuals, plans and ambitions retain their own periods and boundaries.')
    body+='<div class="ce-context-controls">'+link(state,'All management goals',focus='strategy',detail='goals')+link(state,'Strategic alternatives',focus='strategy',detail='options')+'</div>'
    return body


def experience_activity(state,data,facts):
    key=state.detail.removeprefix('journey-')
    if key not in JOURNEYS:return _ceo_journey(state,data,facts)
    if key=='service':return service_context(state)
    title,business,sequence,capids,keys,meaning,question=JOURNEYS[key]
    body='<p class="le-deck">'+e(title)+' connects '+e(business.lower())+' to the wider operating system.</p>'
    body+='<div class="ce-activity-thread" aria-label="Conceptual value-stream activities">'+''.join('<span>'+e(part.strip())+'</span>' for part in sequence.split('→'))+'</div>'
    body+='<p class="ce-legend">Conceptual activity sequence. Durable capabilities, role remits and installed systems are separate kinds of information.</p>'
    actual={'credit':('TRANSACTIONREMIT','MURPHY'),'payments':('TRANSACTIONREMIT','CONDON','CONDONREPORT'),
      'insurance':('WIDOWS','WEALTH','BARUA'),'risk':('HUMANCONTROL','FRAUDOWNER','RISK'),
      'data':('FRAUDWORKFLOW','HUMANCONTROL','AITEAMS'),'platforms':('MSAGREEMENT','ENGINEERS','KEMENADE'),
      'finance':('CHALMERS',),'support':('COLLEAGUES','AIRECRUIT','AITRAINING','DOHERTY'),
      'service':('HUMANCONTROL','SINGH')}[key]
    body+='<section class="ce-evidence-story"><h2>Lloyds context</h2>'+v2_reported(facts,*actual)+reported(facts,keys)+'</section>'
    body+='<section class="ce-economic-meaning"><h2>Economic and operational significance</h2><p>'+e(meaning)+'</p></section>'
    caps={c['id']:c for c in data.get('capabilities',()) if not source_import.working_restricted(c)}
    body+='<h2>Capabilities behind the activity</h2><p>'+e(' · '.join(caps[c]['title'] for c in capids if c in caps))+'</p>'
    current={
      'credit':('Credit growth must be considered with funding transfer price, credit loss and risk capacity. A Group deposit stock cannot supply a loan-cohort return.','A customer or portfolio outcome can improve without requiring a new external platform.'),
      'payments':('Cash, working capital, trade and payments are distinct parts of a conceptual transaction-banking model. Acquisition, integration and product adoption are separate kinds of change.','Acquisition completion, when reported, cannot establish service adoption or remaining supplier scope.'),
      'insurance':('Insurance obligations, distribution and asset administration have different time horizons and accounting from banking interest margin.','Brand/product descriptions do not prove a subsidiary structure, segment cost allocation or installation map.'),
      'risk':('Human accountability and override require explicit control definitions. Control operation and independently demonstrated effectiveness are different tests.','Any existing teams and controls must be considered before asserting a missing risk capability.'),
      'data':('An AI-enabled decision workflow needs business, technology, information and risk participation. Source quality, model control and exception handling are dependencies, not proof of a Group data defect.','Deployment alone does not reconcile prevented loss, false positives, customer outcomes and full costs.'),
      'platforms':('Application retirement and colleague-tool adoption concern different parts of the estate. Fewer applications can reduce complexity while migration and dual running temporarily add work.','A tool reference, product licence or collaboration does not describe the entire estate or an unawarded contract.'),
      'finance':('Funding stocks, period earnings, credit losses and capital use must be reconciled on matched definitions. Growth in deposits can coexist with a higher funding price.','Neither profit nor deposit growth is an unrestricted transformation budget; divisional and capital bridges remain unpresented.'),
      'support':('Workforce scale, trained colleagues, course completions and planned roles have different populations and dates. Delivery capacity depends on skills, work redesign and control coverage.','Recruiting internally or externally is not net hiring, while licence counts cannot establish FTE or staff savings.'),
      'service':('Service access, exception handling and redress affect customer outcomes. Existing FCA product measures belong to Lloyds Bank PLC, not every Group brand or division.','Complaint mix alone cannot quantify customer incidence, service cost, root cause or enterprise materiality.')
    }[key]
    body+='<div class="ce-tension-note"><h2>Dependencies and counter-evidence</h2><p>'+current[0]+'</p><p>'+current[1]+'</p></div>'
    body+='<h2>Commercial investigation</h2><p>'+e(question)+'</p><p class="ce-legend">Relevant roles are published remits, not verified process ownership or purchase mandates. Conceptual association; no verified application, role or supplier dependency is inferred.</p>'
    body+='<div class="ce-context-controls">'+link(state,'Business / value stream',focus='operations',detail='journey-'+key)+link(state,'Durable capabilities',focus='capabilities',detail='data' if key in {'data','platforms'} else 'risk')+link(state,'Organisation / accountable role',focus='people',detail='leadership')+link(state,'Applications / data',focus='applications',detail='fraud' if key in {'risk','data','service'} else 'frontier')+link(state,'Technology / infrastructure',focus='operations',detail='journey-platforms')+link(state,'Suppliers / contracts',focus='partners')+'</div>'
    return body


def experience_capability(state,data,facts):
    key=state.detail if state.detail in {'risk','data','technology'} else 'data'
    selected={'risk':('Risk and service continuity','risk',('HUMANCONTROL','FRAUDOWNER','RISK')),
              'data':('Data as a controlled decision capability','data',('FRAUDWORKFLOW','HUMANCONTROL','AITEAMS')),
              'technology':('Technology as enterprise delivery capacity','platforms',('MSAGREEMENT','ENGINEERS','KEMENADE'))}[key]
    title,journey,ids=selected
    return ('<p class="le-deck">'+title+'</p><h2>From capability to business outcome</h2><p>A capability describes an enduring ability. An activity uses that ability; an application or supplier may enable it. These are not interchangeable, and a research association does not establish ownership or an installed dependency.</p>'
            +experience_activity(replace(state,focus='operations',detail='journey-'+journey),data,facts))


def experience_business(state,facts):
    key=state.focus
    descriptions={
      'retail':('Everyday relationships and asset finance','Households borrow, save and pay. Motor and vehicle finance add asset-service economics alongside traditional banking.',('BANK','BOS','MBNA','BLACKHORSE','LEX','TUSKER'),
        'Interest spread and fees are different revenue mechanisms. In an asset-finance proposition, income must also cover funding, depreciation, servicing and the eventual asset value; no Lloyds cohort return is inferred.',
        'Brand transition is a disclosed management response. It does not establish a Group staffing reduction or a customer outcome.',
        'Which customer or asset cohort has a matched income, funding, credit and service-cost history, and what existing mitigation already protects its return?'),
      'commercial':('Finance the business; support its daily flows','Lending and liquidity support business customers. Cash, trade, working capital and payments support their operating cycles.',('MURPHY','LANGLEY','TRANSACTIONREMIT'),
        'A lending relationship consumes funding, credit and capital capacity. Transaction services can add service revenue and recurring customer interaction, but no contribution or cross-sell uplift is allocated here.',
        'Amanda Murphy and John Langley have distinct published business remits. CIB Transaction Banking leadership is separately disclosed; these remits are not a financial segment split.',
        'Which existing client process has a measurable working-capital, payment-exception or control consequence, and what bank capability already addresses it?'),
      'retirement':('Protection and long-term financial commitments','Insurance, pensions and investment propositions combine distribution, administration and long-duration customer obligations.',('WIDOWS','WEALTH','BARUA'),
        'Policy obligations, investment performance, distribution and administration do not follow a banking net-interest-margin model. Accounting profit, cash generation and capital available for distribution are different views.',
        'Scottish Widows and Lloyds Wealth provide supported brand/product context. The published executive remit does not establish an exclusive legal subsidiary or reporting-segment allocation.',
        'Which policy or asset-administration outcome can be reconciled with servicing cost and capital use on a consistent perimeter and period?'),
    }
    title,purpose,keys,mechanism,response,question=descriptions[key]
    body='<p class="le-deck">'+title+'</p><div class="ce-business-portrait ce-business-'+key+'"><div class="ce-business-purpose"><h2>Customer value</h2><p>'+purpose+'</p></div><section class="ce-business-engine"><h2>How the economics work</h2><p>'+mechanism+'</p></section></div>'
    body+='<section class="ce-evidence-story"><h2>Actual Lloyds businesses and responsibilities</h2>'+v2_reported(facts,*keys)+'</section>'
    response_keys={'retail':('LBG-BRAND26-TIMING',),'commercial':('LBG-V2-MURPHY','LBG-V2-LANGLEY'),'retirement':('LBG-V2-WIDOWS','LBG-V2-WEALTH')}[key]
    if all(k in facts for k in response_keys):body+='<h2>Current response and boundary</h2><p>'+response+'</p>'
    body+='<div class="ce-tension-note"><h2>Commercial investigation</h2><p>'+question+'</p></div>'
    if key=='commercial':body+=region(state,'Transaction Banking',kind='commercial',caption='Disclosed remit and leadership; actual source context before any buying hypothesis',detail='transactions')
    elif key=='retail' and 'LBG-BRAND26-TIMING' in facts:body+=region(state,'Brand transition and service access',reported(facts,('LBG-BRAND26-TIMING','LBG-BRAND26-NO-ROLES')),kind='change',stream='inside',focus='programmes',detail='brand')
    body+='<div class="ce-context-controls">'+link(state,'Group economics',focus='economics')+link(state,'Operating activities',stream='inside',focus='operations',detail='journey-'+{'retail':'credit','commercial':'payments','retirement':'insurance'}[key])+link(state,'Published executive roles',stream='inside',focus='people',detail='leadership')+'</div>'
    body+='<p class="ce-legend">FLORA economic interpretation, with reported brand/role context. No measured profit split, supplier need, buyer mandate, capital allocation or commercial opportunity is asserted.</p>'
    return body


def experience_economic_mechanism(state,facts,issues):
    nodes=[]
    areas=[('funding','Funding','Deposits, price and maturity',(0,0,45,27)),
           ('income','Lending & income','Asset yield, fees and customer mix',(55,0,45,27)),
           ('costs','Costs & impairment','Run, change, remediation and credit',(0,63,45,27)),
           ('capital','Capital & returns','Risk capacity, buffers and distributions',(55,63,45,27))]
    for key,title,meaning,geometry in areas:
        content='<span>'+meaning+'</span>'
        if key=='funding' and 'LBG-Q326-DEPOSITS' in facts:
            item=facts['LBG-Q326-DEPOSITS'];p.note_editorial_sources(item.sources)
            content+='<strong>£'+str(item.value)+'bn</strong><time>Group customer deposits · reported stock · 30 September 2026</time>'
        nodes.append(experience_node(state,title,content,geometry,kind='money',shape='economic-lobe',focus='economics',detail=key))
    if 'LBG-Q326-PROFIT' in facts:
        item=facts['LBG-Q326-PROFIT'];p.note_editorial_sources(item.sources)
        nodes.append(experience_node(state,'Group statutory profit','<strong class="ce-number">£'+str(item.value)+'bn</strong><span>Nine months to 30 September 2026</span><span>Reported Group flow, not divisional allocation</span>',(19,31,62,27),kind='money',shape='profit',focus='economics',detail='income'))
    body=experience_map('capital','Banking earnings, funding and risk capacity',
      ('M170 200 Q100 400 170 520','M630 200 Q700 400 630 520','M360 100 L440 100','M360 630 L440 630','M200 205 L300 255','M600 205 L500 255','M200 510 L300 460','M600 510 L500 460'),nodes,
      'Conceptual financial mechanism. No area, line width or connector measures an allocation, accounting bridge or causal profit effect.')
    selected=state.detail if state.detail in {'funding','income','costs','capital'} else 'income'
    if selected=='funding':
        body+='<h2>Balance growth is not a funding-price explanation</h2>'+experience_funding_stocks(state,facts)
        row=next((r for r in issues if r.key=='funding-base'),None)
        if row and all(k in facts for k in ('LBG-AR25-DEPOSITS','LBG-Q326-DEPOSITS')):body+='<div data-intelligence="funding-base" data-owner-item="funding-stock-change">'+''.join(p.render(i,compact=True) for i in row.facts if i.semantic_type=='calculated' and p.eligible(i))+'</div>'
        body+='<p>The two reported stocks show scale and change at their dates. The difference is not an organic inflow and is not adjusted for consolidation. These stocks do not separate product mix or the price paid to retain balances. Deposit repricing and asset-yield repricing can move at different speeds.</p><h3>Executive decision</h3><p>Compare retention and product migration with matched deposit rates, loan resets and transfer pricing. A stable or lower effective funding cost would weaken a thesis of margin pressure.</p>'
    elif selected=='income':
        body+='<h2>The earnings equation</h2><div class="ce-profit-equation"><span>Net interest income</span><b>+</b><span>Fees & other income</span><b>−</b><span>Operating costs and credit losses</span><b>±</b><span>Statutory adjustments</span></div><p>The reported Group profit is the result, not segment contribution, a lending yield, underlying profit or an available investment budget. Banking spread, transaction fees and insurance/asset economics need separate operational explanations.</p><h3>Executive decision</h3><p>Require a like-for-like bridge before attributing performance to volume, price, productivity or a single technology intervention. A favourable income mix or comparator can improve the result without proving structural cost improvement.</p>'
    elif selected=='costs':
        body+='<h2>Three distinct earnings effects</h2><p>Ordinary run-and-change expense, remediation and credit impairment need separate baselines. Impairment charges cover a period; loss allowances and arrears are different stocks. A lower cost/income ratio can reflect income growth as well as lower expense.</p>'+reported(facts,('LBG-A2030-CIR','LBG-A2030-SAVINGS'))
        body+='<h3>Management response and trade-off</h3><p>Migration, colleague tools and specialist skills are different possible responses. Parallel running can add near-term work while removing future complexity. Gross savings are not realised net profit; the applicable reported responses remain available in their dated programme views.</p><h3>Executive decision</h3><p>Which recurring cost actually disappears, after implementation, supervision and continuity costs, while the customer/control outcome is maintained?</p>'
    else:
        body+='<h2>Funding is not capital</h2><p>Deposits support balance-sheet funding. Capital absorbs risk. Lending can grow risk-weighted exposures, while retained earnings, buffers, business mix and distributions influence remaining capacity. Deposit growth alone cannot prove additional capital or a larger change budget.</p><h3>Group and business trade-offs</h3><p>Commercial credit must earn its funding, loss and capital cost; Retail combines lending, deposits and asset services; Insurance has distinct obligations and capital economics. Central items and statutory adjustments are not a residual to allocate across these businesses.</p><h3>Executive decision</h3><p>Which comparable portfolio return remains attractive after risk, delivery and capital costs, and what would change the investment sequence? Current capital ratios, RWA and divisional return bridges are not presented here; no capital ratio or return is inferred.</p>'
    if 'LBG-V2-CHALMERS' in facts:body+='<section class="ce-evidence-story"><h2>Published finance remit</h2>'+v2_reported(facts,'CHALMERS')+'<p>Relevant Group role, not verified delegated authority for a product, portfolio or procurement decision.</p></section>'
    body+='<div class="ce-context-controls">'+link(state,'Funding comparison',focus='economics',detail='comparison')+link(state,'Efficiency objectives',stream='forces',focus='strategy',detail='objective-efficiency')+link(state,'Investment choices',stream='forces',focus='strategy',detail='objective-investment')+link(state,'Customer operations',stream='inside',focus='operations',detail='service')+'</div>'
    return body

FOCUS_FACTS['economics'] += ('LBG-V2-CHALMERS',)


def experience_funding_stocks(state,facts):
    rows=[(k,label) for k,label in [('LBG-AR25-DEPOSITS','31 December 2025'),('LBG-Q326-DEPOSITS','30 September 2026')] if k in facts]
    if not rows:return ''
    maximum=max(facts[k].value for k,_ in rows)
    body='<figure class="gold-stocks"><figcaption>Group customer deposits · GBP billion · reported stocks</figcaption>'
    for key,label in rows:
        item=facts[key];p.note_editorial_sources(item.sources)
        body+='<a class="canvas-region canvas-stock" data-canvas-region="financial-chart" data-claim-id="'+key+'" href="'+e(href(state,focus='economics',detail='comparison'),quote=True)+'" aria-label="Compare customer deposits at '+label+'"><span>'+label+'</span><meter min="0" max="'+str(maximum)+'" value="'+str(item.value)+'" aria-label="Deposits at '+label+'">'+str(item.value)+'</meter><strong>£'+str(item.value)+'bn</strong></a>'
    return body+'<p class="ce-legend">Zero-based comparison of reported stocks at two dates, not an organic inflow, income or capital measure.</p></figure>'
