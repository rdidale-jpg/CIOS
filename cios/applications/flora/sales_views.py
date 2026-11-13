"""Visual discovery, qualification and pipeline views using the Banking Explorer shell."""
from . import design_system as ds
import json
from datetime import datetime, timezone
from decimal import Decimal
from textwrap import shorten
from html import escape as e
from urllib.parse import urlencode

from .banking_explorer import ROOT, _crumb, _map, _page
from .banking_portfolio import BANKS
from .research_intelligence.registry import enterprise_reference, landscape_url
from .sales_pipeline import (STAGES, CRITERIA, hypothesis, qualification, maturity, evidence_maturity, totals,
                             get_opportunity, list_opportunities)

BASE = '/flora/sales'
CSS = """
.sales-compact{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:16px 0}.explorer .sales-compact h1{font-size:clamp(1.7rem,3vw,2.4rem);line-height:1.15;margin:6px 0}.sales-compact p{margin:6px 0}.sales-register .sales-banner{padding:10px 14px;font-size:.8rem;margin:10px 0}.sales-totals{display:flex;gap:12px;flex-wrap:wrap;margin:14px 0}.sales-totals>div{border:1px solid #bdcfc1;border-radius:12px;padding:10px 14px;font-size:.82rem}.sales-totals h2{font-size:1.2rem;margin:3px 0}.sales-totals p{margin:3px 0}.sales-filters>summary{min-height:44px;align-content:center;cursor:pointer}.sales-evidence{background:#eef0e2;border:1px solid #c3d2bf;border-radius:14px;padding:18px;margin:18px 0}.sales-evidence h2{font-size:1.2rem;margin:3px 0 12px}.sales-evidence ul{padding-left:20px;line-height:1.7}.sales-evidence p{font-size:.85rem;line-height:1.5}.sales-evidence-label{font-size:.8rem;display:block;margin:9px 0;color:#335c4c}.sales-row a{display:inline-block;min-height:44px;align-content:center}.sales-row p{overflow-wrap:anywhere}.sales-register a:focus-visible,.sales-register summary:focus-visible{outline:3px solid #875622;outline-offset:3px}@media(max-width:600px){.sales-compact{display:block}.sales-totals>div{flex:1 1 130px}}@media(pointer:coarse){.sales-grid label:has(input[type=checkbox]){min-height:44px;display:flex;align-items:center}.sales-theme a{min-height:44px;align-content:center}}@media(prefers-reduced-motion:reduce){.sales-register *{scroll-behavior:auto!important}}@media print{.sales-filters form,.sales-compact .ex-button{display:none}.sales-row,.sales-evidence{break-inside:avoid}}.sales-banner{background:#e1ede4;border-left:4px solid #164d48;padding:14px 20px;margin:16px 0;border-radius:8px}.sales-maturity{font-size:.78rem;padding:5px 10px;border-radius:20px;background:#ffe0ca;color:#6d3c20;display:inline-block}.sales-maturity.closed{background:#e4e4df;color:#4f5a50}.sales-maturity.qualified{background:#d3e9de;color:#174d3f}.sales-maturity.pursuit{background:#dddff3;color:#38386b}.sales-grid{display:grid;grid-template-columns:1.5fr 1fr;gap:22px}.sales-grid input,.sales-grid select,.sales-grid textarea,.sales-filter input,.sales-filter select{font:inherit;width:100%;min-width:0;border:1px solid #bccdc1;border-radius:8px;background:white;color:#173c36;padding:11px;min-height:44px}.sales-grid textarea{min-height:95px;resize:vertical}.sales-grid label{display:block;font-size:.88rem;font-weight:700;margin:14px 0 6px}.sales-grid small{display:block;color:#566b65}.sales-grid input[type=checkbox]{width:20px;min-height:20px;vertical-align:middle;margin-right:10px}.sales-fields{display:grid;grid-template-columns:1fr 1fr;gap:16px}.sales-filter{display:flex;gap:10px;flex-wrap:wrap;padding:20px;background:#e9eee5;border-radius:16px}.sales-filter label{font-size:.78rem;flex:1 1 140px}.sales-filter button{align-self:end}.sales-board{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.sales-lane{border:1px solid #ccd9cd;background:#e9eee5;border-radius:16px;padding:16px;min-width:0}.sales-lane .sales-row{display:block}.sales-lane .sales-row>div{margin:14px 0}.sales-row>*{min-width:0}.explorer h1,.sales-row h3{overflow-wrap:anywhere}.sales-lane h2{font-size:1.1rem}.sales-lane .ex-card{padding:16px;margin:12px 0}.sales-row{display:grid;grid-template-columns:2fr 1fr 1fr;gap:20px;align-items:start}.sales-row h3{margin-top:6px}.sales-error{background:#fff0e7;border-left:4px solid #ad502c;padding:18px}.sales-progress{height:8px;background:#dce5da;border-radius:8px;overflow:hidden}.sales-progress span{display:block;height:100%;background:#33866a}.sales-criterion{border:1px solid #d5dfd4;padding:18px;border-radius:14px;margin:14px 0}.sales-missing{color:#8b482e}.sales-history{font-size:.88rem}.sales-history pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f2eb;padding:14px}.sales-theme{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}.sales-theme a{padding:9px 14px;border:1px solid #bdcdbf;border-radius:20px;text-decoration:none}.sales-theme a[aria-current]{background:#164d48;color:white}.sales-opportunity-map svg a:nth-of-type(-n+3) rect{fill:#ffeadb;stroke:#d29978}.sales-map-key{display:flex;gap:15px;flex-wrap:wrap;margin:14px 0;font-size:.8rem}.sales-observation{border-left:3px solid #7da68a;padding-left:18px}.sales-action{border-top:1px solid #d8e0d4;padding-top:16px;margin-top:20px}@media(max-width:900px){.sales-grid{grid-template-columns:1fr}.sales-board{grid-template-columns:repeat(2,minmax(0,1fr))}.sales-row{grid-template-columns:1fr 1fr}.sales-row>div:first-child{grid-column:1/-1}}@media(max-width:520px){.sales-fields,.sales-board,.sales-row{grid-template-columns:1fr}.sales-row>div:first-child{grid-column:auto}}
"""


def _date(value):
    return datetime.fromisoformat(value).astimezone(timezone.utc).strftime('%d %b %Y, %H:%M UTC')


def _money(value):
    return format(Decimal(value), ',.2f')


def page(title, body, headers=None):
    return _page(title, f'<style>{CSS}</style>'+body, headers, active='pipeline')


def _input(name, label, value='', kind='text', help_text='', required=False):
    required_attr = ' required' if required else ''
    field = (f"<textarea id='{name}' name='{name}' maxlength='2000'{required_attr}>{e(value)}</textarea>" if kind=='textarea'
             else f"<input id='{name}' name='{name}' type='{kind}' value='{e(value,quote=True)}' maxlength='2000'{required_attr}>")
    return f"<label for='{name}'>{e(label)}</label>{field}" + (f'<small>{e(help_text)}</small>' if help_text else '')


def _select(name, label, options, value='', blank=False):
    options = ([''] if blank else [])+list(options)
    items = ''.join(f"<option value='{e(v,quote=True)}' {'selected' if v==value else ''}>{e(v or 'All')}</option>" for v in options)
    return f"<label>{e(label)}<select name='{name}'>{items}</select></label>"


def _demo():
    return "<aside class='sales-banner'><strong>Demonstration commercial workspace.</strong> Public market context → opportunity hypothesis → evidence-backed potential → user-qualified opportunity → active pursuit. A stage change never makes an AI inference a confirmed customer requirement. All records in this Banking slice remain labelled demonstration data.</aside>"


@ds.view_scope
def discovery_page(slug, theme='', headers=None):
    bank = BANKS.get(slug)
    if bank is None:
        return page('Enterprise unavailable', "<h1>Choose an existing bank</h1><a href='/flora/banking/explorer'>Banking Explorer</a>", headers),404
    base = f'{ROOT}/{slug}/opportunities'
    nodes = []
    for index, source in enumerate(bank.opportunities):
        nodes.append((f'Opportunity {index+1:02}', shorten(source.theme.replace(' transformation', '').replace(' modernisation', ''), width=28, placeholder='...'), f'{base}/{source.id}'))
    nodes += [('Business capabilities','Customer, operations, finance',base+'?theme=business'),
              ('Technology & data','Platforms, cloud, data and AI',base+'?theme=technology'),
              ('Supplier relationships','Unverified; investigate scope',base+'?theme=suppliers')]
    selected = [o for o in bank.opportunities if not theme or theme=='suppliers'
                or (theme=='technology' and any(w in (o.category+' '+o.theme+' '+o.title).lower() for w in ('cloud','data','ai','platform','resilience')))
                or (theme=='business' and any(w in (o.category+' '+o.theme+' '+o.title).lower() for w in ('customer','cost','service','deposit','operating')))]
    choices = [('','All areas'),('business','Business capabilities'),('technology','Technology & data'),('suppliers','Supplier context')]
    tabs = ''.join(f"<a href='{base}{'?'+urlencode({'theme':key}) if key else ''}' {'aria-current=page' if key==theme else ''}>{label}</a>" for key,label in choices)
    cards = ''.join(f"""<a class='ex-card ex-bank' href='{base}/{o.id}'>
<span class='sales-maturity'>Demonstration hypothesis</span><h3>{e(o.title)}</h3>
<p>{e(o.problem)}</p><p><strong>Timing:</strong> Unknown — {e(o.horizon_label)} is a scenario, not a procurement date.</p>
<p><strong>Value:</strong> Unknown. Existing illustrative sizing is not a customer budget.</p>
<span class='ex-arrow'>Inspect opportunity & evidence →</span></a>""" for o in selected)
    research_link=("<section class='ex-card'><h2>Research-led reassessment</h2><p>Connect the existing Lloyds research to eight provisional commercial questions, source quotations and explicit customer evidence gaps.</p><a href='/flora/banking/research/opportunities'>Inspect new research priorities and changes to these hypotheses →</a></section>" if slug=='lloyds' else '')
    body = _crumb(bank)+research_link+f"""<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Opportunity discovery / Banking</p>
<h1>{e(bank.name)}<br>Where could change create value?</h1><p>Start with the business problem. Follow the evidence. Build a proposition worth validating with the customer.</p>
<a class='ex-button' href='{BASE}/pipeline'>Open your pipeline →</a></section>{_demo()}
<section class='ex-section'><p class='ex-kicker'>Operating landscape → Commercial hypotheses</p><h2>Explore the opportunity landscape.</h2>
<div class='sales-map-key'><span class='sales-maturity'>Hypothesis</span><span class='sales-maturity qualified'>Qualified — private workspace</span><span class='sales-maturity pursuit'>Pursuit — user confirmed</span></div>
<div class='sales-opportunity-map'>{_map(bank.name+' opportunity landscape','Commercial landscape',nodes)}</div>
<p class='ex-notice'>Business and technology nodes select related hypotheses below. Supplier relationships are unverified; the supplier lens identifies research dependencies, not contracts or incumbents.</p>
<nav class='sales-theme' aria-label='Opportunity areas'>{tabs}</nav>
<div class='ex-grid'>{cards or '<p>No hypotheses match this area. Select All areas or investigate additional evidence.</p>'}</div></section>
<section class='ex-card'><h2>Have a different opportunity hypothesis?</h2><p>Create a demonstration record without inventing a requirement, budget or buyer.</p>
<a href='{BASE}/new?{urlencode({'enterprise':slug})}'>Create an opportunity →</a></section>"""
    return page(bank.name+' opportunity landscape',body,headers),200


def capture_controls(slug, origin, headers=None):
    bank=enterprise_reference(slug)
    if bank is None: raise ValueError('Unknown enterprise')
    action = f'{BASE}/capture'
    from .access import require_capability, require_resource_scope
    try:
        actor = require_capability(headers, 'commercial_context.edit')
        require_resource_scope(headers, 'commercial_context.edit', bank.id, actor.workspace, require_acl=False)
        capture_action = f"<form method='post' action='{action}'><input type='hidden' name='enterprise' value='{slug}'><input type='hidden' name='origin' value='{origin}'><button type='submit'>Add to pipeline & qualify →</button></form>"
    except PermissionError:
        capture_action = "<p>Saving needs a verified identity and an authorised selected workspace.</p><a class='ex-button' href='/auth/sign-in'>Sign in to develop this opportunity</a><p><a href='/auth/workspace'>Select your workspace</a></p>"

    return capture_action


@ds.view_scope
def opportunity_page(slug, origin, headers=None):
    bank, source = hypothesis(slug, origin)
    capture_action = capture_controls(slug, origin, headers)

    body = _crumb(bank)+f"""<p><a href='{ROOT}/{slug}/opportunities'>← Opportunity landscape</a> · <a href='{BASE}/pipeline'>Workspace pipeline</a></p>
<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Potential opportunity / {e(bank.name)}</p><h1>{e(source.title)}</h1><p>{e(source.problem)}</p></section>
{_demo()}<div class='sales-grid'><section class='ex-section'><h2>From signal to commercial relevance.</h2>
<article class='ex-card ex-insight'><dl><dt>Observation</dt><dd>{e('; '.join(source.signals))} — recorded scenario signals, not verified customer requirements.</dd>
<dt>Interpretation</dt><dd>{e(source.problem)}</dd><dt>Commercial implication</dt><dd>{e(source.description)}</dd>
<dt>Potential opportunity</dt><dd>{e(', '.join(source.components))}</dd><dt>Evidence</dt><dd>{e('; '.join(bank.analyst_sources))}. Source-context labels only; claim-level Evidence confidence is Unknown.</dd>
<dt>Recommended action</dt><dd>{e(source.next_action)}</dd></dl>
<p><a href='/flora/banking/{slug}/evidence'>Inspect supporting source context →</a></p>
<p><a href='/flora/banking/{slug}/opportunity/{origin}'>Inspect full hypothesis, assumptions and disconfirming signals →</a></p></article>
<article class='ex-card'><h3>Commercial framing</h3><p><strong>Industry:</strong> Banking · <strong>Enterprise:</strong> {e(bank.name)}</p>
<p><strong>Business driver:</strong> {e(source.pressure_driver)}</p><p><strong>Potential solution:</strong> {e(source.scope)} · {e(', '.join(source.components))}</p>
<p><strong>Indicative value:</strong> Unknown. The detailed scenario contains illustrative external-services sizing with assumptions; it is excluded from pipeline totals until a user explicitly records a value basis.</p>
<p><strong>Procurement timing:</strong> Unknown. Existing horizon: {e(source.horizon_label)}, a strategic scenario only.</p>
<p><strong>Evidence confidence:</strong> Unknown; editorial conviction ({e(source.conviction)}) is not calibrated evidence confidence or qualification.</p></article></section>
<aside class='ex-section'><article class='ex-card'><p class='ex-kicker'>Capture → Qualify → Manage</p><h2>Develop this hypothesis.</h2><p>Save a private, workspace-scoped copy. Existing source provenance remains immutable. No automatic qualification.</p>
{capture_action}
<p class='ex-notice'>Sign in and select an authorised workspace to save. Anonymous exploration stays read-only.</p><a href='/auth/sign-in'>Sign in</a></article></aside></div>"""
    return page(source.title,body,headers)


def _record_card(record):
    progress=qualification(record)
    label=maturity(record)
    colour=('closed' if record['stage']=='Lost' else 'qualified' if record['stage']=='Won'
            else 'pursuit' if label=='Active pursuit' else 'qualified' if label=='Qualified sales opportunity' else '')
    last=record.get('history',[])[-1] if record.get('history') else {}
    last_activity=last.get('changes',{}).get('activity') or last.get('action','Not recorded')
    amount = 'Unknown' if not record['amount'] else f"{record['currency']} {_money(record['amount'])} · {record['value_basis']}"
    return f"""<article class='ex-card'><div class='sales-row'><div><span class='sales-maturity {colour}'>{e(label)} · Demo</span>
<h3><a href='{BASE}/{record['id']}'>{e(record['title'])}</a></h3><p>{e(record['enterprise'])} · {e(record['industry'])}</p>
<p><strong>Next action:</strong> {e(record['next_action'] or 'Missing — define a next action')}</p></div>
<div><strong>Pipeline stage: {e(record['stage'])}</strong><p><strong>Value:</strong> {e(amount)}</p><p>{e(record['priority'])} priority · Owner {e(record['owner'])}</p></div>
<div><p>Qualification {progress['percent']}% complete</p><div class='sales-progress'><span style='width:{progress['percent']}%'></span></div>
<span class='sales-evidence-label'>{e(evidence_maturity(record)['research'])}</span><p>Customer validation: not established</p><p>Evidence assessment: {e(record['confidence'])}</p><small>Updated {e(_date(record['updated_at']))}</small><p><strong>Last activity:</strong> {e(shorten(last_activity,width=160,placeholder='…'))}</p></div></div></article>"""


@ds.view_scope
def pipeline_page(headers=None, filters=None, board=False, error=''):
    filters=filters or {}
    rows=list_opportunities(headers=headers, filters=filters)
    all_rows=list_opportunities(headers=headers)
    summary=totals(rows)
    controls=''.join(_select(k,label,sorted({r[k] for r in all_rows}),filters.get(k,''),blank=True) for k,label in
                     [('industry','Industry'),('enterprise','Enterprise'),('owner','Owner')])
    controls+=_select('stage','Stage',STAGES,filters.get('stage',''),blank=True)
    controls+=_select('confidence','Evidence assessment',['Unknown','Low','Moderate','High'],filters.get('confidence',''),blank=True)
    controls+=_select('value_basis','Value basis',['Unknown','Estimate','Customer-confirmed amount'],filters.get('value_basis',''),blank=True)
    controls+=_select('currency','Currency',['GBP','EUR','USD'],filters.get('currency',''),blank=True)
    controls+=f"<label>Minimum stated amount<input name='min_value' value='{e(filters.get('min_value',''),quote=True)}' inputmode='decimal'></label>"
    controls+=f"<input type='hidden' name='view' value='{'board' if board else 'list'}'><button>Apply filters</button><a href='{BASE}/pipeline'>Reset</a>"
    amounts=''.join(f"<div><span class='ex-kicker'>{e(key)}</span><h2>{e(_money(value))}</h2><p>Unweighted open pipeline; no currency conversion.</p></div>" for key,value in summary['amounts'].items())
    amounts+=f"<div><span class='ex-kicker'>Visible records</span><h2>{len(rows)}</h2><p>{summary['unknown']} open records with unknown value · {summary['closed']} closed records excluded from open totals.</p></div>"
    if board:
        content="<div class='sales-board'>"+''.join(f"<section class='sales-lane'><h2>{stage} · {sum(r['stage']==stage for r in rows)}</h2>"+''.join(_record_card(r) for r in rows if r['stage']==stage)+"</section>" for stage in STAGES)+"</div>"
    else:
        content=''.join(_record_card(r) for r in rows)
    query={k:v for k,v in filters.items() if v}
    ds.context_link(BASE+'/pipeline?'+urlencode(dict(query,view='list')), 'Pipeline list')
    ds.context_link(BASE+'/pipeline?'+urlencode(dict(query,view='board')), 'Stage board')
    body=f"""
<div class='sales-register'><header class='sales-compact' id='explorer-content'><div><p class='eyebrow'>Workspace opportunity pipeline</p><h1>Your commercial pipeline</h1><p>Stage tracks the sales process. Evidence maturity tracks what is established.</p></div><a class='ex-button' href='{BASE}/new'>Create an opportunity →</a></header><aside class='sales-banner'><strong>Demonstration commercial workspace.</strong> Stage and evidence maturity are separate. No customer validation or real revenue forecast is implied.</aside>
<section><div class='sales-totals'>{amounts}</div><details class='sales-filters' {'open' if any(filters.values()) or error else ''}><summary>Filters & value discipline</summary><p class='ex-notice'>Known amounts mean user-recorded customer-confirmed amounts with references; they are not independently verified. Estimates remain separate with assumptions. Demonstration records are never a real-world revenue forecast.</p>
{f"<p class='sales-error' role='alert'>Filters were not applied: {e(error)}</p>" if error else ''}<form class='sales-filter' method='get' action='{BASE}/pipeline'>{controls}</form></details>

{content or '<div class="ex-empty">Your pipeline is empty. Explore a Banking hypothesis or create a record to start qualification.</div>'}</section></div>"""
    return page('Commercial opportunity pipeline',body,headers)


@ds.view_scope
def new_page(slug='lloyds', headers=None, error=''):
    bank=enterprise_reference(slug) or BANKS['lloyds']
    choices=''.join(f"<option value='{b.slug}' {'selected' if b.slug==bank.slug else ''}>{e(b.name)}</option>" for b in [*BANKS.values(),enterprise_reference('easyjet')])
    fields=_input('title','Opportunity title',required=True)+_input('problem','Business problem',kind='textarea',required=True)+_input('solution','Potential solution',kind='textarea')+_input('next_action','Next action',kind='textarea')
    body=_enterprise_crumb(bank)+_demo()+f"<section class='ex-card' id='explorer-content'><h1>Create a demonstration hypothesis</h1><p>Starts at Discovered with unknown value and evidence confidence.</p><p class='sales-error'>{e(error)}</p><form class='sales-grid' method='post' action='{BASE}/create'><div><label>Enterprise<select name='enterprise'>{choices}</select></label>{fields}<button>Create & qualify →</button></div></form></section>"
    return page('Create opportunity',body,headers)


def evidence_panel(state):
    return ("<section class='sales-evidence' aria-label='Saved evidence maturity'><h2>Evidence maturity · separate from Pipeline stage</h2><ul>"
            +''.join('<li>'+e(state[k])+'</li>' for k in ('research','customer','pursuit'))
            +'</ul><p>'+e(state['limitation'])+'</p><p>Based on the saved record. Unsaved inputs do not change this status.</p></section>')


@ds.view_scope
def record_page(identifier, headers=None, error='', draft=None):
    r=get_opportunity(identifier,headers=headers)
    saved_evidence=evidence_maturity(r)
    bank=enterprise_reference(r['enterprise_slug'])
    if bank is None: raise ValueError('Unknown enterprise')
    from .access import require_capability
    try:
        require_capability(headers, 'commercial_context.edit')
        fieldset_open='<fieldset style="border:0;padding:0;min-width:0">'
    except PermissionError:
        fieldset_open='<p class="sales-banner">Read-only access: your workspace role cannot edit commercial records.</p><fieldset disabled style="border:0;padding:0;min-width:0">'
    draft_stage=r['stage']
    draft_notice=''
    if draft:
        submitted={k:v[0][:2000] for k,v in draft.items() if k!='csrf' and len(v)==1}
        if submitted.get('version') == str(r['version']):
            for key in ('title','problem','solution','next_action','owner','priority','timing','amount','currency','value_basis','value_reference','confidence','confidence_rationale'):
                if key in submitted: r[key]=submitted[key]
            r['qualification']={k:{'note':submitted.get('q_'+k,''),'source':submitted.get('s_'+k,'')} for k in CRITERIA}
            r['evidence_reviewed']=submitted.get('evidence_reviewed')=='yes'
            draft_stage=submitted.get('stage',r['stage'])
            draft_notice="<p class='sales-banner'>Your unsaved form has been restored below. The displayed pipeline stage is the last saved stage; rejected changes were not committed.</p>"
        else:
            draft_notice="<details class='ex-card'><summary>Recover your unsaved draft (record changed; review current fields before retrying)</summary><pre style='white-space:pre-wrap;overflow-wrap:anywhere'>"+e(json.dumps(submitted,indent=2))+"</pre></details>"
    progress=qualification(r)
    info=''.join(f"<li>{e(CRITERIA[k][0])}</li>" for k in progress['missing'])
    sections=[]
    for key,(label,help_text) in CRITERIA.items():
        item=r['qualification'].get(key,{})
        sections.append(f"<details class='sales-criterion' {'open' if key=='problem' else ''}><summary>{'✓' if key in progress['complete'] else 'Missing'} · {e(label)}</summary><p>{e(help_text)}</p>"+_input('q_'+key,label,item.get('note',''),'textarea')+_input('s_'+key,'Supporting reference for '+label,item.get('source',''),help_text='Document/page, research observation or customer activity reference. A label alone is not independent verification.')+'</details>')
    edit=''.join(_input(k,label,r[k],kind) for k,label,kind in [('title','Opportunity title','text'),('problem','Business problem','textarea'),('solution','Potential solution','textarea'),('next_action','Next action','textarea'),('owner','Commercial owner (does not grant access)','text'),('timing','Procurement / investment timing','text')])
    edit+=_select('priority','Priority',['High','Normal','Low'],r['priority'])
    value_fields=_input('amount','Indicative amount',r['amount'],help_text='Blank when unknown. No inferred budget or automatic scenario import.')+_select('currency','Currency',['GBP','EUR','USD'],r['currency'])+_select('value_basis','Value basis',['Unknown','Estimate','Customer-confirmed amount'],r['value_basis'])+_input('value_reference','Estimate assumptions / customer amount reference',r['value_reference'],'textarea')
    evidence_fields=_select('confidence','User evidence assessment',['Unknown','Low','Moderate','High'],r['confidence'])+_input('confidence_rationale','Evidence assessment rationale',r['confidence_rationale'],'textarea')
    history=''.join(f"<details><summary>{e(_date(h['at']))} · {e(h['actor'])} · v{h['version']} · {e(h['action'])}</summary><pre>{e(json.dumps(h['changes'],indent=2,ensure_ascii=False))}</pre></details>" for h in reversed(r['history']))
    body=_enterprise_crumb(bank)+f"<p><a href='{BASE}/pipeline'>← Pipeline</a> · <a href='{landscape_url(bank.slug)}'>Opportunity landscape</a></p>"+f"""<section class='ex-hero' id='explorer-content'><p class='eyebrow'>{e(r['stage'])} / Demonstration opportunity</p><h1>{e(r['title'])}</h1><p>{e(maturity(r))} · {e(r['enterprise'])} · {e(r['industry'])}</p></section>{_demo()}
{f"<p class='sales-error' role='alert'>{e(error)}</p>" if error else ''}{draft_notice}
{evidence_panel(saved_evidence)}
<form method='post' action='{BASE}/{identifier}/save'>{fieldset_open}<input type='hidden' name='version' value='{r['version']}'>
<div class='sales-grid'><div><section class='ex-section ex-card'><h2>Commercial brief</h2>{edit}<h3>Value & timing discipline</h3>{value_fields}</section>
<section class='ex-section ex-card' id='qualification'><p class='ex-kicker'>MEDDICC-informed / Capture planning</p><h2>What supports qualification?</h2><p>{e(progress['rationale'])}</p>{''.join(sections)}
<label><input type='checkbox' name='evidence_reviewed' value='yes' {'checked' if r['evidence_reviewed'] else ''}>I have reviewed these supporting references and their applicability.</label></section></div>
<aside><section class='ex-section ex-card'><h2>Qualification readiness</h2><h3>{progress['percent']}% inputs complete</h3><div class='sales-progress'><span style='width:{progress['percent']}%'></span></div>
<p>Completeness is not win probability or AI confidence.</p><h3>Missing information</h3><ul class='sales-missing'>{info or '<li>All ten inputs supplied. Verify quality before confirming qualification.</li>'}</ul>
{evidence_fields}<p><strong>Provenance:</strong> {e('; '.join(r['provenance']['source_labels']) or 'User-entered demonstration')}</p><p>{e(r['provenance']['limitations'])}</p>
<p><a href='{e(r['provenance']['evidence_url'],quote=True)}'>Inspect source context →</a></p><p><a href='{e(r['provenance']['origin_url'],quote=True)}'>Originating hypothesis / enterprise →</a></p></section>
<section class='ex-section ex-card'><h2>Manage the next move</h2>{_select('stage','Pipeline stage',STAGES,draft_stage)}
<label><input type='checkbox' name='confirm' value='yes'>I explicitly confirm this stage change and its evidence basis.</label>
{_input('activity','Record commercial activity',kind='textarea',help_text='Conversation, research, customer feedback or a committed next step. Recorded with actor and date.')}
{_input('closure_evidence','Won / Lost outcome evidence',r.get('closure_evidence',''),'textarea',help_text='Required with explicit confirmation when closing. Demo status remains unchanged.')}
<p><button type='submit'>Save opportunity & activity</button></p><p class='ex-notice'>Qualified and active stages require all ten evidence-supported inputs and explicit confirmation. No automatic promotion.</p>
<p>Version {r['version']} · Updated {e(_date(r['updated_at']))}</p></section></aside></div></fieldset></form>
<section class='ex-section ex-card sales-history'><h2>Traceable change history</h2><p>Source provenance and workspace are immutable. Each substantive update records actor, UTC timestamp, version and before/after fields.</p>{history}</section>"""
    from .research_intelligence.commercial_views import pipeline_context
    body=pipeline_context(r)+body
    return page(r['title']+' | Qualification workspace',body,headers)


def submit(path, form, headers):
    """Called inside the existing CSRF/verified mutation envelope."""
    from .sales_pipeline import create_opportunity, update_opportunity, SalesValidationError
    if any(len(v)!=1 for v in form.values()):
        raise SalesValidationError('Repeated form fields are not supported.')
    fields={k:v[0] for k,v in form.items()}
    if path in {BASE+'/capture', BASE+'/create'}:
        allowed={'csrf','enterprise','origin','title','problem','solution','next_action'}
        if set(fields)-allowed:
            raise SalesValidationError('Only commercial creation fields are accepted.')
        slug=fields.get('enterprise','')
        values={k:fields[k] for k in ('title','problem','solution','next_action') if k in fields}
        record=create_opportunity(slug,fields.get('origin',''),values,headers=headers)
    else:
        identifier=path.split('/')[-2]
        allowed={'csrf','version','stage','title','problem','solution','next_action','owner','priority','timing',
                 'amount','currency','value_basis','value_reference','confidence','confidence_rationale',
                 'confirm','evidence_reviewed','activity','closure_evidence'}|{'q_'+k for k in CRITERIA}|{'s_'+k for k in CRITERIA}
        if set(fields)-allowed:
            raise SalesValidationError('Unknown commercial form field.')
        try:
            version=int(fields.get('version',''))
        except ValueError:
            raise SalesValidationError('Reload the opportunity before editing.')
        values={k:v for k,v in fields.items() if k not in {'csrf','version'} and not k.startswith(('q_','s_'))}
        values['qualification']={k:{'note':fields.get('q_'+k,''),'source':fields.get('s_'+k,'')} for k in CRITERIA}
        values['evidence_reviewed']=fields.get('evidence_reviewed','no')
        record=update_opportunity(identifier,version,values,headers=headers)
    return BASE+'/'+record['id']+'#qualification'


@ds.view_scope
def error_page(path, message, headers, draft=None):
    if path == BASE+'/pipeline':
        return pipeline_page(headers=headers,error=message)
    if path.endswith('/save'):
        return record_page(path.split('/')[-2],headers=headers,error=message,draft=draft)
    return page('Opportunity update needs attention',f"<section class='ex-card' id='explorer-content'><h1>Check your opportunity update</h1><p class='sales-error' role='alert'>{e(message)}</p><p>No rejected changes were saved.</p><a href='{BASE}/new'>Create an opportunity</a> · <a href='{ROOT}'>Return to Banking Explorer</a></section>",headers)


def _enterprise_crumb(bank):
    if bank.slug not in ('lloyds','easyjet'):
        return _crumb(bank)
    from .research_intelligence.model import load_assessment
    from .research_intelligence.unified_views import breadcrumb
    return breadcrumb(True,load_assessment('aviation') if bank.slug=='easyjet' else load_assessment())
