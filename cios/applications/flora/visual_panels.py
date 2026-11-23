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
from . import reading_views as reading
from . import banking_ecosystem as ecosystem
from . import banking_cohort as cohort
from . import experience_composition as experience
from . import lloyds_recovery as recovery
from . import easyjet_capabilities as easyjet
from .security import verified_service_read

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
    if ctx.scope=='easyjet':
        return text+'<a href="/industries/aviation">Aviation</a><span aria-hidden="true">/</span><span>easyJet</span>'
    if ctx.scope=='banking':
        if ctx.selected in cohort.SUBJECTS:
            return text+'<a href="/industries/banking">Banking</a><span aria-hidden="true">/</span><span>'+e(cohort.SUBJECTS[ctx.selected][0])+'</span>'
        return text+'<span>Banking</span>'
    bank=v.url(v.Context('banking','landscape',ctx.layer,'lloyds'))
    return text+'<a href="'+e(bank,quote=True)+'">Banking</a><span aria-hidden="true">/</span><span>Lloyds Banking Group</span>'


def _top(ctx,headers):
    body='<header id="top" data-region="top"><a class="skip" href="#visual-content">Skip to main content</a><div class="global">'
    body+=ds.header(headers=headers,compact=True,embedded=True,research_tools=__import__('cios.applications.flora.access',fromlist=['is_cios_owner']).is_cios_owner(headers))+'<span class="identity" aria-label="Current account role">'+_role(headers)+'</span>'+('<a class="account-entry" href="/auth/sign-in">Sign in</a>' if _role(headers)=='Guest' else '')+'</div>'
    body+='<div class="context"><nav aria-label="Current scope">'+_trail(ctx)+'</nav><nav class="stream-switcher" aria-label="Insight streams">'
    streams=cohort.STREAMS if ctx.scope=='banking' and ctx.selected in cohort.SUBJECTS and not (ctx.detail or ctx.agenda) else v.PRESENTATIONS[ctx.scope]['streams']
    for stream in streams:
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
    if ctx.scope=='banking' and sid in ecosystem.STAGES:return False
    return ((ctx.layer=='regulators'and(sid in v.ROLE_CONTEXT or sid=='economics'))
        or(ctx.layer=='suppliers'and sid in {'technology','customers','operations','payments'}))


def _scene(ctx,rows,suffix,issues):
    scene=ctx.scope+'-'+ctx.stream;positions=POSITIONS[scene]
    ecosystem_scene=scene=='banking-landscape' and p.is_editorial()
    if ecosystem_scene:
        positions=ecosystem.POSITIONS
        rows=rows+ecosystem.extra_entries(ctx)
        illustration=('<img src="'+_asset(v.BANKING_ART_SMALL)+'" srcset="'+_asset(v.BANKING_ART_SMALL)
                      +' 384w, '+_asset(v.BANKING_ART)+' 768w" sizes="(min-width:1000px) 310px, 100vw"'
                      ' alt="Conceptual riverside town showing customers, banking, oversight and infrastructure"'
                      ' width="768" height="1152" loading="lazy" decoding="async">')
    else:
        illustration=_image(scene)
    body='<figure class="portrait" aria-label="'+e(scene.replace('-',' '),quote=True)+'">'+illustration
    body+='<figcaption class="sr-only">Conceptual illustration, not actual premises, a legal hierarchy, systems topology or a quantitative pressure map. Labelled navigation remains available without artwork.</figcaption>'
    body+=''.join(_entry(r,ctx,primary=True,position=positions[r['id']],suffix=suffix)for r in rows if r['id']in positions and r['href'])
    if scene=='lloyds-inside'and issues:
        href=v.url(ctx,detail='',agenda=ctx.agenda or issues[0].key)+'#agenda-insight'
        body+='<a class="subject spot" data-label-id="leadership-agenda" href="'+e(href,quote=True)+'" style="--x:51%;--y:85%">Leadership Agenda</a>'
    body+='</figure><p class="art-fallback">All subjects remain available below.</p>'
    if ecosystem_scene:body+=ecosystem.stage_links(ctx,include_payments=True)
    # UK keeps all twenty original section labels, with only three researched
    # exits. Other scenes disclose only supplementary/inert labels once.
    extra=rows if scene=='uk-landscape'else[r for r in rows if r['id']not in positions or not r['href']]
    if extra:
        body+='<details class="text-view"'+(' open'if any(r['selected']or _layer_focus(ctx,r['id'])for r in extra)else'')+'><summary>'+('All 20 industries'if scene=='uk-landscape'else'Explore deeper')+'</summary><nav aria-label="All scene subjects">'
        body+=''.join(_entry(r,ctx,suffix=suffix+'-text')for r in extra)+'</nav></details>'
    # Compact extra nav does not serialize intelligence or owner metadata.
    return body


def _left(ctx,data,rows,issues):
    if ctx.scope=='easyjet':return easyjet.left(ctx)
    return ('<aside id="left" data-region="left" aria-label="Visual exploration"><div class="wide-scene">'
        +_scene(ctx,rows,'',issues)+'</div><details class="compact-scene"><summary>Explore the scene</summary>'
        +_scene(ctx,rows,'-compact',issues)+'</details></aside>')


def _facts(data,ids):
    if data is None:return []
    return [row for claim in v.claim_rows(data,ids)if(row:=p.claim_view(data,claim))is not None]


def _basis(facts,extra=''):
    if p.is_editorial(): return ''
    return '<details class="financial-basis"><summary>Sources &amp; basis</summary>'+''.join(p.render(f)for f in facts)+extra+'</details>'if facts else''


def _metrics(rows):
    return '<div class="metrics">'+''.join('<div><span class="metric-label">'+e(label)+'</span><strong>'+e(value)+'</strong><span class="metric-period">'+e(period)+'</span></div>'for label,value,period in rows)+'</div>'if rows else''


def _issue_preview(issues,key):
    """Recompose one already resolved agenda view; never admit or infer facts."""
    row=next((row for row in issues if row.key==key),None)
    if row is None:return ''
    statements=row.facts if p.is_editorial() else (row.facts[0] if key=='cyber-resilience' else row.conclusion,)
    return ('<section class="editorial-issue" data-intelligence="'+key+'" aria-labelledby="preview-'+key+'">'
        +'<h2 id="preview-'+key+'">'+e(row.title)+'</h2>'+''.join(p.render(item) for item in statements)
        +('' if p.is_editorial() else agenda.basis(row))+'</section>')


def _shares(basis):
    districts=[d for d in basis['districts']if d['sic']in {'C','J','K','Q'}]
    body='<figure class="chart"><figcaption>Four comparable sector shares</figcaption><div class="bars" role="group" aria-label="2024 sector shares of UK GVA">'
    for row in districts:
        value=row['weight_per_thousand']/10
        body+='<div class="bar-row"><span>'+e(row['label'])+'</span><div class="track" aria-hidden="true"><i style="--value:'+str(value/15*100)+'%"></i></div><strong>'+str(value)+'%</strong></div>'
    if p.is_editorial():return body+'</div><p class="chart-note">Calculated · 2024 UK GVA shares. Finance &amp; insurance covers more than Banking.</p></figure>'
    return body+'</div><p class="chart-note">Calculated · published 2024 SIC 2007 weights ÷ 10, current basic prices. Linear 0–15% scale; Finance &amp; insurance includes more than Banking.</p></figure>'


def _uk(ctx,issues):
    basis=v.visual_v2.basis();valid=agenda.fingerprint(basis)==agenda._pins().get('existing_economy')
    body='<p class="eyebrow">'+('Economic landscape'if ctx.stream=='landscape'else'National forces')+'</p><h1>'+('The shape of the UK economy'if ctx.stream=='landscape'else'The UK’s economic context')+'</h1>'
    if valid:
        p.note_editorial_sources(p.Source(s['title'],s['url'],s.get('publisher','Office for National Statistics')) for s in basis['sources'])
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
    p.note_editorial_sources(s for f in facts for s in f.sources)
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
        body+='</div><p class="chart-note">Reported · GBP billion, linear 0–600bn scale. Published balances; composition and transfer effects are not reconciled. No organic-flow claim.</p>'
        if not p.is_editorial():
            body+='<details class="chart-data"><summary>Chart data</summary><table><caption>Group customer-deposit stocks · GBP billion</caption><tbody>'
            body+=''.join('<tr><th scope="row">'+label+'</th><td>'+str(row.value)+'</td></tr>'for row,label in [(opening,'31 December 2025'),(stock,'30 September 2026')])+'</tbody></table></details>'
        body+='</figure>'
    funding=next((row for row in issues if row.key=='funding-base'),None)
    if funding:
        movement=funding.facts[-1]
        if movement.semantic_type=='calculated'and p.eligible(movement):
            body+='<div data-intelligence="funding-base">'+p.render(movement)+'</div>'
    body+='<div class="analysis-grid">'
    for key,title in [('LBG-A2030-CIR','Efficiency ambition'),('LBG-A2030-INVESTMENT','Investment discipline')]:
        if by[key] and (key!='LBG-A2030-INVESTMENT' or not p.is_editorial()):body+='<section><h2>'+title+'</h2>'+p.render(by[key])+'</section>'
    body+='</div><p class="material">Deposits and statutory pretax profit do not establish an investment allocation or external supplier budget.</p>'
    return body+_basis([f for f in facts if f not in [by['LBG-A2030-CIR'],by['LBG-A2030-INVESTMENT']]])


def _forces(ctx,data):
    body='<div class="forces-editorial">'
    for spot in v.geometry()[ctx.scope+'-forces']['spots']:
        fact=v.force_view(replace(ctx,stream='forces'),spot['id'],data)
        if fact and p.eligible(fact):
            body+='<section><h2>'+e(spot['label'])+'</h2>'+p.render(fact)+('' if p.is_editorial() else '<p class="perspective">'+e(v.FORCE_POLICY[spot['id']][1])+'</p>')+'</section>'
    return body+'</div>'


def _banking(ctx,data,issues):
    body='<p class="eyebrow">'+('Industry landscape'if ctx.stream=='landscape'else'Industry forces')+'</p><h1>'+('The UK Banking ecosystem'if ctx.stream=='landscape'else'Funding conditions and resilience')+'</h1>'
    if ctx.stream=='forces':return body+_forces(ctx,data)
    independent = ctx.selected in agenda.BANK_SERVICE and not agenda.BANK_SERVICE[ctx.selected][2]
    selected = agenda.bank_service_issue(ctx.selected, data) if independent or any(r.key=='service-landscape' for r in issues) else None
    if selected:
        return ('<p class="eyebrow">Banking · enterprise intelligence</p><h1>'+e(agenda.BANK_SERVICE[ctx.selected][0])+'</h1>'
                +'<section class="editorial-issue" data-intelligence="service-landscape">'+''.join(p.render(fact) for fact in selected.facts)+'<details><summary>Measurements and sources</summary>'+''.join(p.render(f) for f in selected.facts)+'</details></section>'
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
    return _financial(ctx,data,issues)+_issue_preview(issues,'service-recovery')+''.join('<section class="editorial-issue">'+p.render(f)+'</section>'for f in facts)


def _research_render(ctx,headers=None,*,financial_run_id=''):
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
    return _research_frame(ctx,headers,data,issues,entries,body)


def _research_frame(ctx,headers,data,issues,entries,body):
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


EDITORIAL_STYLE='''<style>
.account-entry{font-size:13px;text-decoration:underline;white-space:nowrap}.identity{margin-left:auto}.account-entry+.identity{margin-left:0}
.editorial-lead{font:clamp(20px,2vw,28px)/1.4 Georgia,serif;max-width:42ch;margin:0 0 26px}.editorial-topics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;margin:28px 0}.editorial-topics section{border-top:1px solid var(--line);padding-top:18px;margin:0}.editorial-topics h2{font-size:25px;margin:0 0 12px}.editorial-topics p{font-size:16px}.editorial-topics .timing{font-size:12px;margin-top:12px}
.bank-picker{display:flex;gap:8px;flex-wrap:wrap;margin:25px 0 0;padding:20px 0;border-top:1px solid var(--line)}.bank-picker a{min-height:44px;display:flex;align-items:center;padding:8px 13px;border:1px solid var(--line);border-radius:22px;text-decoration:none;font-size:13px;line-height:1.3}.bank-picker a[aria-current]{background:var(--forest);color:white;border-color:var(--forest)}
.force-stories{display:grid;grid-template-columns:1fr;gap:0;margin-top:26px}.force-story{display:grid;grid-template-columns:50px minmax(0,1fr);gap:20px;border-top:1px solid var(--line);padding:16px 0;margin:0}.force-number{font:32px Georgia,serif;color:#8c794e}.force-story h2{font-size:26px;margin:0 0 8px}.force-story .intelligence-statement{margin-bottom:0!important}.force-story .timing{margin-top:12px;font-size:12px}
.earnings-metrics{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:22px!important;margin:25px 0!important}.earnings-metrics strong{font-size:clamp(25px,3vw,40px)!important;white-space:nowrap;letter-spacing:-.04em}.earnings-story{border-top:1px solid var(--line);padding-top:20px;margin:24px 0}.earnings-story h2{font-size:28px}.earnings-equation{font:clamp(15px,1.4vw,20px)/1.6 Georgia,serif;margin:16px 0;overflow-wrap:anywhere}.earnings-context,.shared-period{font-size:14px;color:var(--muted);margin:12px 0}.financial-editorial .lead{font-size:17px}.service-context{border-top:1px solid var(--line);margin-top:28px;padding-top:18px}.service-context h2{font-size:22px}.service-context p{font-size:14px}.workspace-setup{margin:24px 0;padding:20px 0;border-top:1px solid var(--line)}.workspace-setup button{min-height:44px;padding:10px 18px;background:var(--forest);color:white;border:1px solid var(--forest);border-radius:24px;font:inherit}
.legal-notice{border-top:1px solid var(--line);margin-top:36px;padding-top:12px;font-size:11px!important;line-height:1.5;color:var(--muted);max-width:78ch}.legal-notice a{font-weight:400}.context-nav{display:flex;flex-wrap:wrap;gap:14px;margin:22px 0 0;font-size:12px}.context-nav a{min-height:44px;display:flex;align-items:center}.context-nav a[aria-current]{font-weight:700;text-decoration-thickness:2px}
@media(max-width:700px){.editorial-topics{grid-template-columns:1fr}.earnings-metrics{grid-template-columns:1fr!important;gap:18px!important}.earnings-metrics>div{padding:7px 0;border-bottom:1px solid var(--line);display:grid;grid-template-columns:minmax(0,1fr) max-content;gap:5px 12px;align-items:center}.earnings-metrics>div strong{grid-column:2;grid-row:1/3;font-size:27px!important}.earnings-metrics>div .metric-period{grid-column:1;font-size:11px}.earnings-metrics{gap:5px!important}.force-story{grid-template-columns:26px minmax(0,1fr);gap:12px}.force-number{font-size:24px}.force-story h2{font-size:25px}.account-entry{font-size:12px}}
@media print{.focus,.focus:focus,[tabindex]:focus{outline:none!important}.close-insight{display:none!important}.force-story{padding:12px 0}.bank-picker,.context-nav,.account-entry,.workspace-setup{display:none!important}.workspace{padding:15px!important}.force-story,.earnings-story,.earnings-metrics{break-inside:avoid}.legal-notice{font-size:9px!important}.legal-notice a:after{content:none!important}}
@media(forced-colors:active){.bank-picker a[aria-current]{background:Highlight;color:HighlightText}.force-number{color:CanvasText}}
</style>'''


def _bank_picker(ctx,data,issues):
    rows=[(slug,name) for slug,(name,_,ids) in agenda.BANK_SERVICE.items()
          if (not ids or any(r.key=='service-landscape' for r in issues)) and agenda.bank_service_issue(slug,data)]
    if not rows:return ''
    return '<nav class="bank-picker" data-intelligence="service-landscape" aria-label="Banking enterprises">'+''.join(
        '<a href="'+e(v.url(ctx,selected=slug,detail='',agenda=''),quote=True)+'"'+(' aria-current="page"' if ctx.selected==slug else '')+'>'+e(name)+'</a>' for slug,name in rows)+'</nav>'


def _editorial_banking(ctx,data,issues,headers):
    from .financial_intelligence import analyst
    if ctx.selected=='nationwide' and ctx.stream=='landscape':
        pass  # Private composition is held within its verified read below.
    selected=agenda.bank_service_issue(ctx.selected,data) if (ctx.selected in agenda.BANK_SERVICE and
        (not agenda.BANK_SERVICE[ctx.selected][2] or any(r.key=='service-landscape' for r in issues))) else None
    if selected and ctx.stream=='landscape':
        name=agenda.BANK_SERVICE[ctx.selected][0]
        body='<p class="eyebrow">UK Banking</p><h1>'+e(name)+'</h1>'
        body+='<p class="editorial-lead">Customer complaints, in perspective.</p>'
        body+=''.join(p.render(fact) for fact in selected.facts)
        body+='<p class="material">'+e(selected.facts[0].scope)+'. Received and closed complaints are different cohorts; upheld outcomes are the firm’s own decisions.</p>'
        if ctx.selected=='nationwide':
            action=analyst.prepare_action(ctx,headers=headers)
            if action:body+='<section class="workspace-setup"><h2>Your financial view</h2>'+action+'</section>'
        return body+_bank_picker(ctx,data,issues)
    if ctx.stream=='forces':
        body='<p class="eyebrow">Banking · Forces</p><h1>The forces reshaping banking</h1><div class="force-stories">'
        items=[('funding-economics','Rates and customer choice'),('reporting-change','A new reporting timetable'),('provider-oversight','Critical providers, closer oversight')]
        n=0
        for key,title in items:
            row=next((r for r in issues if r.key==key),None)
            if row:
                n+=1;body+='<section class="force-story" data-intelligence="'+key+'"><span class="force-number" aria-hidden="true">0'+str(n)+'</span><div><h2>'+e(title)+'</h2>'+(p.render(row.facts[0]))+'</div></section>'
        fact=v.force_view(ctx,'LBG-ENVOY-CONTROLS',data)
        if fact and p.eligible(fact):
            body+='<section class="force-story"><span class="force-number" aria-hidden="true">0'+str(n+1)+'</span><div><h2>Lloyds: AI in the operating model</h2>'+p.render(fact)+'</div></section>'
        return body+'</div>'+reading.provider_pulse(issues)+reading.banking_links()+_bank_picker(ctx,data,issues)
    body='<p class="eyebrow">UK Banking · Landscape</p><h1>Where money meets the economy</h1><p class="editorial-lead">Deposits fund lending. Payments connect households and businesses.</p>'
    facts=_facts(data,['UK-RATE-NOV26']);rate=next((f for f in facts if f.value is not None),None)
    metrics=[]
    if rate:p.note_editorial_sources(rate.sources)
    if rate:metrics.append(('Reported · Bank Rate',str(rate.value)+'%',rate.period))
    basis=v.visual_v2.basis()
    if agenda.fingerprint(basis)==agenda._pins().get('existing_economy'):
        p.note_editorial_sources(p.Source(s['title'],s['url'],s.get('publisher','Office for National Statistics')) for s in basis['sources'])
        row=next(d for d in basis['districts']if d['sic']=='K');metrics.append(('Calculated · Finance & insurance',str(row['weight_per_thousand']/10)+'%',str(basis['year'])+' UK GVA · broader than Banking'))
    body+=_metrics(metrics)+'<div class="editorial-topics">'
    for key,title in [('provider-oversight','Resilience spans the ecosystem'),('reporting-change','The reporting landscape is changing')]:
        row=next((r for r in issues if r.key==key),None)
        if row:body+='<section data-intelligence="'+key+'"><h2>'+title+'</h2>'+p.render(row.facts[0])+'</section>'
    return body+'</div>'+ecosystem.overview()+reading.banking_links()+_bank_picker(ctx,data,issues)


def _legal_notice(ctx,data):
    sources=p.editorial_sources()
    names=[]
    if any('fca.org.uk/data/'in s.url for s in sources):names.append('Financial Conduct Authority')
    if any('bankofengland.co.uk/boeapps/database/'in s.url for s in sources):names.append('Bank of England')
    if any('ons.gov.uk/'in s.url for s in sources):names.append('Office for National Statistics (Crown copyright)')
    governed_public_urls={package['source']['url'] for key in ('cyber','provider') if (package:=agenda._eai_release(key)) is not None and package['source'].get('rights',{}).get('status') in {'permitted_numerical_data','permitted_ogl_factual_extract'}}
    if any(s.url in governed_public_urls for s in sources):names.append('public sector information')
    text=''
    if names:
        text='Data: '+e('; '.join(names))+'. Licensed public-sector data under the <a href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/" rel="noreferrer">Open Government Licence v3.0</a>.'
        if 'Bank of England'in names:text+=' Copyright the Governor and Company of the Bank of England.'
    if any('nationwide.co.uk/'in s.url for s in sources):text+=' Financial facts: Nationwide Building Society, FY2026 preliminary results. No issuer endorsement.'
    if not text:return ''
    return '<footer class="legal-notice" aria-label="Legal attribution">'+text+'</footer>'


def _frame(ctx,headers,data,issues,entries,body,*,show_commercial=False):
    """Ordinary three-panel frame emits no research disclosures or source URLs."""
    scene=replace(ctx,stream='landscape') if ctx.scope=='banking' and ctx.stream=='inside' else ctx
    if __import__('cios.applications.flora.access',fromlist=['is_cios_owner']).is_cios_owner(headers):
        ds.context_link(v.url(scene)+'&lens=inspection' if ctx.scope in {'banking','lloyds'} else '/research','Research inspection')
    binding=v.PRESENTATIONS[ctx.scope]
    identity=binding.get('identity')or data[binding['identity_key']]
    title=binding['title'] if ctx.scope in {'uk','easyjet'} else data['industry_name'if ctx.scope=='banking'else'enterprise_name']
    watermark=''
    if ctx.scope!='easyjet':
        asset=asset_manifest()['watermarks'][ctx.scope+'-'+scene.stream]
        watermark='<img class="watermark" src="'+_asset(asset)+'" alt="" aria-hidden="true">'
    layers='' if ctx.scope in {'uk','easyjet'} else '<nav class="context-nav" aria-label="Context layers">'+''.join('<a href="'+e(v.url(ctx,layer=k),quote=True)+'"'+(' aria-current="page"'if ctx.layer==k else'')+'>'+e(label)+'</a>' for k,label in v.LAYERS.items())+'</nav>'
    head=ds.head()+'<link rel="stylesheet" href="'+v.ASSET_BASE+'panel-styles"><script defer src="'+v.ASSET_BASE+'interactions"></script>'+EDITORIAL_STYLE+reading.STYLE+experience.STYLE
    if ctx.scope=='easyjet':head+=easyjet.STYLE
    if ctx.scope=='banking':head+=ecosystem.STYLE+cohort.STYLE
    if ctx.scope=='lloyds':head+=recovery.STYLE
    change = ''
    if show_commercial and ctx.scope in {'lloyds', 'easyjet'} and not (ctx.detail or ctx.agenda or ctx.selected):
        from .memory.commercial_views import commercial_change
        change = commercial_change(ctx.scope, ctx.stream, headers)
    return ('<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+e(title)+' · '+ctx.stream.title()+' · FLORA</title>'+"<link rel='canonical' href='"+binding['route']+"'>"+head+'</head><body class="ds-page vp-page">'+_top(ctx,headers)+_left(scene,data,entries,issues)+'<main id="visual-content" tabindex="-1" data-region="main" data-market="GB" data-scope="'+ctx.scope+'" data-identity="'+e(identity,quote=True)+'" data-stream="'+ctx.stream+'" data-layer="'+ctx.layer+'">'+watermark+'<article class="workspace editorial-workspace">'+reading.selector(ctx)+change+body+layers+_legal_notice(ctx,data)+'</article></main></body></html>')


def render(ctx,headers=None,*,financial_run_id=''):
    from .supabase_identity import public_read
    with p.editorial_view(ctx.reading), public_read():
        if ctx.scope=='easyjet':return _frame(ctx,headers,None,(),(),easyjet.main(ctx),show_commercial=True)
        if financial_run_id:
            from .financial_intelligence import analyst
            return analyst.render_selected(ctx,financial_run_id,headers=headers)
        if ctx.scope=='banking' and ctx.selected=='nationwide' and ctx.stream=='landscape' and not ctx.detail and not ctx.agenda:
            try:
                private=_authorised_nationwide(ctx,headers) if ctx.reading=='facts' else None
                if private:return private
            except (PermissionError,OSError,ValueError,KeyError,TypeError):pass
            from .financial_intelligence import candidate_analytics as financial, analyst
            public = financial.public_nationwide_projection()
            if public:
                data=v.current_data(ctx);issues=agenda.agenda(ctx.scope,data,selected=ctx.selected)
                body=(reading.nationwide_insight(public) if ctx.reading=='insight' else
                      analyst.compose_editorial(public)+reading.nationwide_facts_bridge(public)+_nationwide_service(data))
                from .enterprise_economics import annual_statement_view, statement_summary
                from .financial_intelligence.public_statements import statement_series, nationwide_lines
                lines = statement_series(('research-subject:nationwide-building-society-group', 'Nationwide Building Society Group'))
                if lines:
                    context = ('FY2025 covers 361 days and includes six months of Virgin Money. '
                               'FY2026 includes a full year. This limits direct comparisons of income and cash flows. '
                               'Balance sheet dates are 31 March 2026 and 31 March 2025.')
                    body += annual_statement_view(
                        lines, insight=ctx.reading=='insight', context=context,
                        comparison_keys=('assets','cash_central','loans','debt_securities'),
                    )
                else:
                    body += statement_summary(nationwide_lines(public), insight=ctx.reading=='insight', inspection=False)
                action=analyst.prepare_action(ctx,headers=headers) if ctx.reading=='facts' else ''
                if action:body+='<section class="workspace-setup"><h2>Workspace analysis</h2>'+action+'</section>'
                return _frame(ctx,headers,data,issues,v.destinations(ctx,data),cohort.landscape(ctx,body,data,issues)+_bank_picker(ctx,data,issues))
        data=v.current_data(ctx);issues=agenda.agenda(ctx.scope,data,selected=ctx.selected)
        scene=replace(ctx,stream='landscape') if ctx.scope=='banking' and ctx.stream=='inside' else ctx
        entries=v.destinations(scene,data)
        if ctx.scope=='banking' and ctx.selected in cohort.SUBJECTS and not (ctx.detail or ctx.agenda) and (ctx.selected!='nationwide' or ctx.stream!='landscape'):
            body=cohort.render(ctx,data,issues)
            if ctx.stream=='landscape' and ctx.reading=='facts' and ctx.selected!='boe':body+=_bank_picker(ctx,data,issues)
        elif ctx.scope=='banking' and ctx.stream=='landscape' and ctx.detail in ecosystem.STAGES:
            body=ecosystem.render(ctx,data,issues)
        elif ctx.scope=='lloyds' and not ctx.agenda and (not ctx.detail or (
                (ctx.stream=='inside' and ctx.detail in recovery.INSIDE_DETAILS) or
                (ctx.stream=='landscape' and ctx.detail in (*recovery.LANDSCAPE_COMPONENTS,'economics','flagship')))):
            if ctx.stream=='inside':
                body=recovery.inside(ctx,data)
            elif ctx.stream=='landscape':
                body=recovery.landscape(ctx,data,issues,headers=headers)
            else:
                body=recovery.forces(ctx,data)
        elif ctx.scope=='uk' and ctx.stream=='forces' and not ctx.agenda:
            body=experience.uk_forces(ctx,data)
        elif ctx.scope=='banking' and ctx.stream=='forces' and not (ctx.agenda or ctx.selected) and (
                not ctx.detail or ctx.detail in experience.BANKING_FORCES):
            body=(_editorial_banking(ctx,data,issues,headers) if ctx.reading=='facts' and not ctx.detail
                  else '<h1>The forces reshaping banking</h1>')
            body+=experience.banking_forces(ctx)
            if ctx.reading=='insight' and not ctx.detail:
                context=ecosystem.forces(ctx,data,issues)
                if context:body+='<section aria-label="Separate funding and oversight context"><h2>Funding and oversight context</h2>'+context+'</section>'
        elif ctx.reading=='insight':body=reading.insight(ctx,data,issues)
        elif ctx.scope=='banking' and ctx.detail=='payments' and ctx.stream=='landscape':
            body=reading.payments(ctx,data)
        elif ctx.scope=='banking' and not ctx.detail and not ctx.agenda:
            body=_editorial_banking(ctx,data,issues,headers)
            if ctx.stream=='landscape' and not ctx.selected:body+=cohort.navigation(ctx,data,issues)
        elif ctx.agenda:
            row=next((r for r in issues if r.key==ctx.agenda),None)
            body=('<section class="focus agenda-focus" id="agenda-insight" tabindex="-1" aria-label="Leadership insight"><a class="close close-insight" aria-label="Close Leadership Agenda" href="'+e(v.url(ctx,agenda=''),quote=True)+'">×</a><h1>'+e(row.title)+'</h1>'+reading.agenda_facts(row)+'</section>') if row else _overview(ctx,data,issues)
            if ctx.scope=='banking':
                if ctx.agenda=='provider-oversight':body+=reading.provider_pulse(issues)
                body+=_bank_picker(ctx,data,issues)
        elif ctx.detail:
            spot=next(s for s in v.geometry()[ctx.scope+'-'+ctx.stream]['spots']if s['id']==ctx.detail)
            body=v._detail(ctx,spot,data).replace('<h2 id="insight-title">','<h1 id="insight-title">',1).replace('</h2>','</h1>',1)
            if ctx.scope=='lloyds' and ctx.stream=='inside' and ctx.detail=='technology':
                if not body:body='<h1>Technology &amp; data</h1><p>No eligible disclosures for this selection.</p>'
                body+=reading.lloyds_capability(data,insight=False)
        else:body=_overview(ctx,data,issues)
        return _frame(ctx,headers,data,issues,entries,body,show_commercial=True)


@verified_service_read('package.inspect')
def research_inspection(path,query,headers=None):
    """Existing owner inspection boundary; never grants access to a private run."""
    from .access import is_cios_owner
    if not is_cios_owner(headers):raise PermissionError('Research access unavailable')
    query={k:v for k,v in query.items()if k!='lens'}
    if 'analysis'in query:
        from .financial_intelligence import analyst
        ctx,identity=analyst.selection(path,query)
        data,projection=analyst._current(ctx,identity,headers)
        issues=agenda.agenda(ctx.scope,data,selected=ctx.selected)
        return _research_frame(ctx,headers,data,issues,v.destinations(ctx,data),analyst.STYLE+'<section class="financial-analyst">'+analyst.compose(projection)+'</section>')
    ctx=v.resolve(path,query)
    if ctx.scope=='banking' and ctx.stream=='inside':ctx=replace(ctx,stream='landscape')
    if ctx.scope=='banking' and ctx.detail in ecosystem.STAGES:ctx=replace(ctx,detail='')
    return _research_render(ctx,headers)


def _nationwide_service(data):
    service=agenda.bank_service_issue('nationwide',data)
    if not service:return ''
    return '<section class="service-context"><h2>Customer complaints · Society</h2>'+''.join(p.render(fact) for fact in service.facts)+'<p class="material">Received and closed cases are different cohorts; upheld outcomes are the firm’s own decisions. Separate from Group earnings.</p></section>'


@verified_service_read('package.inspect')
def _authorised_nationwide(ctx,headers):
    from .financial_intelligence import analyst
    projection=analyst._selected_financial(ctx,headers=headers)
    if not projection:return None
    data=v.current_data(ctx);issues=agenda.agenda(ctx.scope,data,selected=ctx.selected);entries=v.destinations(ctx,data)
    from .access import is_cios_owner
    if is_cios_owner(headers):
        identity=analyst.financial.find_existing_run('nationwide-fy2026','BK-IND-002',headers=headers)
        ds.context_link(v.url(ctx)+'&analysis='+identity+'&lens=inspection','Financial research')
    return _frame(ctx,headers,data,issues,entries,analyst.compose_editorial(projection)+reading.nationwide_facts_bridge(projection)+_nationwide_service(data)+_bank_picker(ctx,data,issues))
