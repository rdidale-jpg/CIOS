"""VP-2 three-region presentation over the existing visual-stream owners.

No source import, private model lookup, analysis/matching service, persistence,
frozen design facts or date override. Context and destinations belong to
visual_streams; semantic/source eligibility belongs to its existing adapters.
"""
from dataclasses import replace
from html import escape as e
import hashlib
import json
from pathlib import Path
from types import MappingProxyType

from . import visual_streams as v, design_system as ds, leadership_agenda as agenda
from . import intelligence_presentation as p

DESIGN='f4059a34a55277adbd2a2337239827cab96d962e'
SCENES=frozenset({'uk-landscape','uk-forces','banking-landscape','banking-forces',
    'lloyds-inside','lloyds-landscape','lloyds-forces'})


def asset_manifest():
    data=json.loads((v.ASSETS/'panels-artwork.json').read_text())
    if data.get('design_commit')!=DESIGN or set(data['portraits'])!=SCENES:
        raise ValueError('Accepted portrait assets unavailable')
    for name,row in data['files'].items():
        ext='.webp'if row['mime']=='image/webp'else'.svg'if row['mime']=='image/svg+xml'else''
        if (not ext or Path(row['file']).name!=row['file']
                or row['file']!=name+ext or not name.endswith('-'+row['sha256'][:12])):
            raise ValueError('Unsafe portrait asset manifest')
    return data


def _asset(name):return v.ASSET_BASE+name


def _image(scene):
    rows=asset_manifest()['portraits'][scene]['variants']
    return ('<img src="'+_asset(rows[0]['file'].removesuffix('.webp'))+'" srcset="'
        +', '.join(_asset(r['file'].removesuffix('.webp'))+' '+str(r['width'])+'w'for r in rows)
        +'" sizes="(min-width:1000px) 320px, (min-width:700px) 350px, 100vw" width="1024" height="1536" alt="" loading="lazy" decoding="async">')


def _role(headers):
    from .access import blueprint_upload_authorisation
    decision=blueprint_upload_authorisation(headers or {})
    return 'Owner'if decision.owner_recognised else'Member'if decision.user_id else'Guest'


def _trail(ctx):
    root=v.url(v.Context('uk','landscape',selected='banking'))
    if ctx.scope=='uk':return '<span>United Kingdom</span>'
    text='<a href="'+e(root,quote=True)+'">UK</a><span aria-hidden="true">/</span>'
    if ctx.scope=='banking':return text+'<span>Banking</span>'
    bank=v.url(v.Context('banking','landscape',ctx.layer,'lloyds'))
    return text+'<a href="'+e(bank,quote=True)+'">Banking</a><span aria-hidden="true">/</span><span>Lloyds Banking Group</span>'


def _top(ctx,headers):
    body='<header id="top" data-region="top"><a class="skip" href="#visual-content">Skip to main content</a><div class="global">'
    body+=ds.header(headers=headers,compact=True,embedded=True)+'<span class="identity" aria-label="Current account role">'+_role(headers)+'</span></div>'
    body+='<div class="context"><nav aria-label="Current scope">'+_trail(ctx)+'</nav><nav class="stream-switcher" aria-label="Insight streams">'
    for stream in v.SCOPES[ctx.scope]['streams']:
        body+='<a id="stream-'+stream+'" href="'+e(v.stream_url(ctx,stream)+'#stream-'+stream,quote=True)+'"'+(' aria-current="page"'if ctx.stream==stream else'')+'>'+stream.title()+'</a>'
    return body+'</nav></div><!--flora-system-notice--></header>'


# Presentation placement only. All addresses and eligibility come from the
# unchanged accepted scene owner; absent positions go into contextual text.
POSITIONS=MappingProxyType({
    'uk-landscape':{'uk-sic07-h':(69,30),'uk-sic07-j':(55,48),'uk-sic07-k':(32,66)},
    'uk-forces':{'economic':(46,16),'technological':(53,38),'legal':(46,61),'environmental':(52,84)},
    'banking-landscape':{'boe':(50,19),'lloyds':(45,52),'payments':(52,84)},
    'banking-forces':{'UK-RATE-NOV26':(48,17),'UK-PRA-REPORT27':(51,39),'LBG-ENVOY-CONTROLS':(47,62),'UK-VALUE':(52,84)},
    'lloyds-inside':{'economics':(48,29),'technology':(53,57)},
    'lloyds-landscape':{'businesses':(49,21),'economics':(48,53),'technology':(53,83)},
    'lloyds-forces':{'LBG-A2030-PLATFORMS':(48,17),'LBG-A2030-CIR':(50,39),'LBG-ENVOY-CONTROLS':(48,62),'LBG-BRAND26-TIMING':(51,84)},
})


def _entry(row,ctx,*,primary=False,position=None,suffix=''):
    label=row['research']if primary and row['research']else row['label']
    attrs=' data-label-id="'+e(row['id'],quote=True)+'" id="label-'+e(row['id']+suffix,quote=True)+'"'
    if not primary and row['sic']:attrs+=' data-sic="'+row['sic']+'"'
    if primary and row['research']:attrs+=' data-research="'+row['research'].lower()+'" aria-label="'+e(row['research']+': open available industry experience; '+row['label']+' is its broader section',quote=True)+'"'
    cls='subject spot'if primary else'exploration-link'
    cls+=(' available active'if row['href']else' inert')+(' selected'if row['selected']else'')
    if _layer_focus(ctx,row['id']):
        cls+=' layer-focus';attrs+=' aria-description="Highlighted for '+e(v.LAYERS[ctx.layer],quote=True)+' context"'
    if position:attrs+=' style="--x:'+str(position[0])+'%;--y:'+str(position[1])+'%"'
    if row['selected']:attrs+=' aria-current="true"'
    tag='a'if row['href']else'span'
    return '<'+tag+' class="'+cls+'"'+attrs+(' href="'+e(row['href'],quote=True)+'"'if row['href']else'')+'>'+e(label)+'</'+tag+'>'


def _layer_focus(ctx,sid):
    return ((ctx.layer=='regulators'and(sid in v.ROLE_CONTEXT or sid=='economics'))
        or(ctx.layer=='suppliers'and sid in {'technology','customers','operations','payments'}))


def _scene(ctx,rows,suffix,issues):
    scene=ctx.scope+'-'+ctx.stream;positions=POSITIONS[scene]
    body='<figure class="portrait" aria-label="'+e(scene.replace('-',' '),quote=True)+'">'+_image(scene)
    body+='<figcaption class="sr-only">Conceptual illustration, not actual premises, a legal hierarchy, systems topology or a quantitative pressure map. Labelled navigation remains available without artwork.</figcaption>'
    body+=''.join(_entry(r,ctx,primary=True,position=positions[r['id']],suffix=suffix)for r in rows if r['id']in positions and r['href'])
    if scene=='lloyds-inside'and issues:
        href=v.url(ctx,detail='',agenda=ctx.agenda or issues[0].key)+'#agenda-insight'
        body+='<a class="subject spot" data-label-id="leadership-agenda" href="'+e(href,quote=True)+'" style="--x:51%;--y:85%">Leadership Agenda</a>'
    body+='</figure><p class="art-fallback">All subjects remain available below.</p>'
    # UK keeps all twenty original section labels, with only three researched
    # exits. Other scenes disclose only supplementary/inert labels once.
    extra=rows if scene=='uk-landscape'else[r for r in rows if r['id']not in positions or not r['href']]
    if extra:
        body+='<details class="text-view"'+(' open'if any(r['selected']or _layer_focus(ctx,r['id'])for r in extra)else'')+'><summary>'+('All 20 industries'if scene=='uk-landscape'else'Explore deeper')+'</summary><nav aria-label="All scene subjects">'
        body+=''.join(_entry(r,ctx,suffix=suffix+'-text')for r in extra)+'</nav></details>'
    # Compact extra nav does not serialize intelligence or owner metadata.
    return body


def _left(ctx,data,rows,issues):
    return ('<aside id="left" data-region="left" aria-label="Visual exploration"><div class="wide-scene">'
        +_scene(ctx,rows,'',issues)+'</div><details class="compact-scene"><summary>Explore the scene</summary>'
        +_scene(ctx,rows,'-compact',issues)+'</details></aside>')


def _facts(data,ids):
    if data is None:return []
    return [row for claim in v.claim_rows(data,ids)if(row:=p.claim_view(data,claim))is not None]


def _basis(facts,extra=''):
    return '<details class="financial-basis"><summary>Sources &amp; basis</summary>'+''.join(p.render(f)for f in facts)+extra+'</details>'if facts else''


def _metrics(rows):
    return '<div class="metrics">'+''.join('<div><span class="metric-label">'+e(label)+'</span><strong>'+e(value)+'</strong><span class="metric-period">'+e(period)+'</span></div>'for label,value,period in rows)+'</div>'if rows else''


def _issue_preview(issues,key):
    """Recompose one already resolved agenda view; never admit or infer facts."""
    row=next((row for row in issues if row.key==key),None)
    if row is None:return ''
    statement=row.facts[0]if key=='cyber-resilience'else row.conclusion
    return ('<section class="editorial-issue" data-intelligence="'+key+'" aria-labelledby="preview-'+key+'">'
        +'<h2 id="preview-'+key+'">'+e(row.title)+'</h2>'+p.render(statement)
        +agenda.basis(row)+'</section>')


def _shares(basis):
    districts=[d for d in basis['districts']if d['sic']in {'C','J','K','Q'}]
    body='<figure class="chart"><figcaption>Four comparable sector shares</figcaption><div class="bars" role="group" aria-label="2024 sector shares of UK GVA">'
    for row in districts:
        value=row['weight_per_thousand']/10
        body+='<div class="bar-row"><span>'+e(row['label'])+'</span><div class="track" aria-hidden="true"><i style="--value:'+str(value/15*100)+'%"></i></div><strong>'+str(value)+'%</strong></div>'
    return body+'</div><p class="chart-note">Calculated · published 2024 SIC 2007 weights ÷ 10, current basic prices. Linear 0–15% scale; Finance &amp; insurance includes more than Banking.</p></figure>'


def _uk(ctx,issues):
    basis=v.visual_v2.basis();valid=agenda.fingerprint(basis)==agenda._pins().get('existing_economy')
    body='<p class="eyebrow">'+('Economic landscape'if ctx.stream=='landscape'else'National forces')+'</p><h1>'+('The shape of the UK economy'if ctx.stream=='landscape'else'The UK’s economic context')+'</h1>'
    if valid:
        body+=_metrics([('Reported · UK GVA',basis['display_total'],str(basis['year'])+' · current basic prices'),
            ('Reported · real GDP growth','+'+str(basis['growth']['value_pct'])+'%',basis['growth']['period']+' · versus previous three months')])+_shares(basis)
        body+='<p class="material">GVA is not company revenue. Real GDP growth is a separate national volume measure, not industry or enterprise growth.</p>'
    if ctx.stream=='forces':body+=_forces(ctx,None)
    else:body+=_issue_preview(issues,'cyber-resilience')
    return body


def _financial(ctx,data,issues=()):
    ids=['LBG-Q326-DEPOSITS','LBG-Q326-PROFIT','LBG-AR25-DEPOSITS','LBG-A2030-CIR','LBG-A2030-INVESTMENT']
    group='Lloyds Banking Group plc, consolidated Group unless stated'
    facts=[r for r in _facts(data,ids)if r.scope==group]
    by={key:(r if r and r.scope==group else None)for key,claim in zip(ids,v.claim_rows(data,ids))for r in [p.claim_view(data,claim)]}
    body='<p class="eyebrow">Financial analysis · consolidated Group</p><h1>Customer funding and earnings</h1><p class="lead">Published balances and reported earnings, alongside the Group’s efficiency ambition.</p>'
    values=[];stock=by['LBG-Q326-DEPOSITS'];profit=by['LBG-Q326-PROFIT'];opening=by['LBG-AR25-DEPOSITS']
    def numeric(row,unit,period):
        return bool(row and p.eligible(row)and row.semantic_type=='reported'and row.value is not None
            and row.unit==unit and row.period==period and row.measurement_state in {'not_applicable','actual'})
    stock_ok=numeric(stock,'GBP billion; balance at 30 September 2026','Nine months ended / balance sheet at 30 September 2026')
    profit_ok=numeric(profit,'GBP billion; nine-month statutory pretax profit','Nine months ended / balance sheet at 30 September 2026')
    if stock_ok:values.append(('Reported · Group customer deposits','£'+str(stock.value)+'bn','30 September 2026 · balance-sheet stock'))
    if profit_ok:values.append(('Reported · Group statutory pretax profit','£'+str(profit.value)+'bn','Nine months to 30 September 2026 · nine-month flow'))
    body+=_metrics(values)
    if stock_ok and numeric(opening,'GBP billion; year-end balance','31 December 2025')and opening.scope==stock.scope:
        body+='<figure class="chart"><figcaption>Customer-deposit stocks · Group</figcaption><input class="reference-control" id="deposit-reference" type="checkbox" checked><label class="reference-label" for="deposit-reference">2025 reference</label><div class="bars" role="group" aria-label="Group customer deposits in GBP billion">'
        for row,label in [(opening,'31 December 2025'),(stock,'30 September 2026')]:
            body+='<div class="bar-row"><span>'+label+'</span><div class="track" aria-hidden="true"><i style="--value:'+str(row.value/600*100)+'%"></i></div><strong>'+str(row.value)+'bn</strong></div>'
        body+='</div><p class="chart-note">Reported · GBP billion, linear 0–600bn scale. Published balances; composition and transfer effects are not reconciled. No organic-flow claim.</p><details class="chart-data"><summary>Chart data</summary><table><caption>Group customer-deposit stocks · GBP billion</caption><tbody>'
        body+=''.join('<tr><th scope="row">'+label+'</th><td>'+str(row.value)+'</td></tr>'for row,label in [(opening,'31 December 2025'),(stock,'30 September 2026')])+'</tbody></table></details></figure>'
    funding=next((row for row in issues if row.key=='funding-base'),None)
    if funding:
        movement=funding.facts[-1]
        if movement.semantic_type=='calculated'and p.eligible(movement):
            body+='<div data-intelligence="funding-base">'+p.render(movement)+'</div>'
    body+='<div class="analysis-grid">'
    for key,title in [('LBG-A2030-CIR','Efficiency ambition'),('LBG-A2030-INVESTMENT','Investment discipline')]:
        if by[key]:body+='<section><h2>'+title+'</h2>'+p.render(by[key])+'</section>'
    body+='</div><p class="material">Deposits and statutory pretax profit do not establish an investment allocation or external supplier budget.</p>'
    return body+_basis([f for f in facts if f not in [by['LBG-A2030-CIR'],by['LBG-A2030-INVESTMENT']]])


def _forces(ctx,data):
    body='<div class="forces-editorial">'
    for spot in v.geometry()[ctx.scope+'-forces']['spots']:
        fact=v.force_view(replace(ctx,stream='forces'),spot['id'],data)
        if fact and p.eligible(fact):
            body+='<section><h2>'+e(spot['label'])+'</h2>'+p.render(fact)+'<p class="perspective">'+e(v.FORCE_POLICY[spot['id']][1])+'</p></section>'
    return body+'</div>'


def _banking(ctx,data,issues):
    body='<p class="eyebrow">'+('Industry landscape'if ctx.stream=='landscape'else'Industry forces')+'</p><h1>'+('The UK Banking ecosystem'if ctx.stream=='landscape'else'Funding conditions and resilience')+'</h1>'
    if ctx.stream=='forces':return body+_forces(ctx,data)
    independent = ctx.selected in agenda.BANK_SERVICE and not agenda.BANK_SERVICE[ctx.selected][2]
    selected = agenda.bank_service_issue(ctx.selected, data) if independent or any(r.key=='service-landscape' for r in issues) else None
    if selected:
        return ('<p class="eyebrow">Banking · enterprise intelligence</p><h1>'+e(agenda.BANK_SERVICE[ctx.selected][0])+'</h1>'
                +'<section class="editorial-issue" data-intelligence="service-landscape">'+p.render(selected.conclusion)+'<details><summary>Measurements and sources</summary>'+''.join(p.render(f) for f in selected.facts)+'</details></section>'
                +agenda.bank_service_navigation(ctx,v.url,issues,data))
    facts=_facts(data,['UK-RATE-NOV26','UK-PRA-REPORT27','UK-FCA-REPORT27','UK-VALUE'])
    rate=next((f for f in facts if f.unit=='percent; policy rate at decision'),None)
    values=[]
    if rate and rate.value is not None:values.append(('Reported · Bank Rate',str(rate.value)+'%',rate.period))
    basis=v.visual_v2.basis()
    if agenda.fingerprint(basis)==agenda._pins().get('existing_economy'):
        district=next(d for d in basis['districts']if d['sic']=='K')
        values.append(('Calculated · '+district['label'],str(district['weight_per_thousand']/10)+'%',str(basis['year'])+' · share of UK GVA; broader than Banking'))
    body+=_metrics(values)
    body+='<div class="value-chain" aria-label="Conceptual banking value system"><span>Deposits</span><b aria-hidden="true">→</b><span>Credit &amp; payments</span><b aria-hidden="true">→</b><span>Households &amp; businesses</span></div><p class="chart-note">FLORA Insight · sector functions, not bilateral contracts or quantified value flows.</p>'
    body+='<div class="analysis-grid"><section><h2>Funding economics</h2><p>Deposit pricing, lending and operating resilience connect the banking system with the wider economy.</p><p class="perspective">A rate decision does not establish a particular bank’s margin loss or buying demand.</p></section><section><h2>Distinct responsibilities</h2><dl class="roles"><dt>Bank of England</dt><dd>Central-bank and monetary-policy context.</dd><dt>PRA</dt><dd>Prudential supervision; part of the Bank of England.</dd><dt>FCA</dt><dd>Conduct supervision, distinct from prudential supervision.</dd></dl></section></div>'
    return body+_basis(facts)+_issue_preview(issues,'provider-oversight')+_issue_preview(issues,'service-landscape')+agenda.bank_service_navigation(ctx,v.url,issues,data)


def _overview(ctx,data,issues):
    if ctx.scope=='uk':return _uk(ctx,issues)
    if ctx.scope=='banking':return _banking(ctx,data,issues)
    if ctx.stream=='inside':return _financial(ctx,data,issues)+_issue_preview(issues,'service-recovery')
    if ctx.stream=='forces':return '<p class="eyebrow">Enterprise forces</p><h1>Strategy and existing capabilities</h1>'+_forces(ctx,data)
    supplier=v.detail_claims(ctx,{'id':'technology'},data)
    facts=[r for c in supplier if(r:=p.claim_view(data,c))is not None]+_facts(data,['LBG-Q326-DEPOSITS','LBG-A2030-PLATFORMS'])
    return '<p class="eyebrow">Enterprise landscape</p><h1>An enterprise within a wider ecosystem</h1>'+''.join('<section class="editorial-issue">'+p.render(f)+'</section>'for f in facts)


def render(ctx,headers=None,*,financial_run_id=''):
    if financial_run_id:
        from .financial_intelligence import analyst
        return analyst.render_selected(ctx,financial_run_id,headers=headers)
    data=v.current_data(ctx);issues=agenda.agenda(ctx.scope,data,selected=ctx.selected);entries=v.destinations(ctx,data)
    body=''
    if ctx.agenda and any(r.key==ctx.agenda for r in issues):
        body='<h1>Leadership Agenda</h1>'+agenda.detail(ctx,v.url,issues)
        if ctx.agenda=='service-landscape':body+=agenda.bank_service_navigation(ctx,v.url,issues,data)
    elif ctx.detail:
        spot=next(s for s in v.geometry()[ctx.scope+'-'+ctx.stream]['spots']if s['id']==ctx.detail)
        if ctx.scope=='lloyds'and ctx.stream=='inside'and ctx.detail=='economics'and v.has_detail(ctx,spot,data):
            body='<section class="focus" id="insight" tabindex="-1" aria-labelledby="insight-title"><a class="close close-insight" href="'+e(v.url(ctx,detail='')+'#visual-content',quote=True)+'" aria-label="Close Financial performance">×</a>'+_financial(ctx,data,issues).replace('<h1>','<h1 id="insight-title">',1)+'</section>'
        elif v.has_detail(ctx,spot,data):
            content=v._detail(ctx,spot,data)
            body=content.replace('<h2 id="insight-title">','<h1 id="insight-title">',1).replace('</h2>','</h1>',1)
    if not body:body=_overview(ctx,data,issues)
    from .financial_intelligence import analyst
    body+=analyst.navigation(ctx,headers)
    return _frame(ctx,headers,data,issues,entries,body)


def _frame(ctx,headers,data,issues,entries,body):
    """Accepted Top/Left/Main shell shared by public and authorised Main views."""
    body+=agenda.navigation(ctx,v.url,issues)
    if ctx.scope!='uk':
        body+='<details class="layer-options"><summary>Context layers</summary><nav aria-label="Context layers">'+''.join('<a href="'+e(v.url(ctx,layer=k),quote=True)+'"'+(' aria-current="page"'if ctx.layer==k else'')+'>'+e(label)+'</a>'for k,label in v.LAYERS.items())+'</nav></details>'
    body+=v._proof(ctx,data)
    scene=ctx.scope+'-'+ctx.stream;manifest=asset_manifest();watermark=manifest['watermarks'][scene]
    identity=v.SCOPES[ctx.scope].get('identity')or data[v.SCOPES[ctx.scope]['identity_key']]
    title='United Kingdom'if ctx.scope=='uk'else data['industry_name'if ctx.scope=='banking'else'enterprise_name']
    head=ds.head()+'<link rel="stylesheet" href="'+v.ASSET_BASE+'panel-styles"><script defer src="'+v.ASSET_BASE+'interactions"></script>'
    return ('<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+e(title)+' · '+ctx.stream.title()+' · FLORA</title>'+"<link rel='canonical' href='"+v.SCOPES[ctx.scope]['route']+"'>"+head+'</head><body class="ds-page vp-page">'
        +_top(ctx,headers)+_left(ctx,data,entries,issues)+'<main id="visual-content" tabindex="-1" data-region="main" data-market="GB" data-scope="'+ctx.scope+'" data-identity="'+e(identity,quote=True)+'" data-stream="'+ctx.stream+'" data-layer="'+ctx.layer+'"><img class="watermark" src="'+_asset(watermark)+'" alt="" aria-hidden="true"><article class="workspace">'+body+'</article></main></body></html>')
