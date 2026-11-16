"""F2 finite presentation adapter over current Financial-owner projections.

No persistence, acquisition, source grants, intelligence engine or result cache.
Private selection is a locator; existing verified services remain authoritative.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from html import escape as e
from urllib.parse import parse_qsl, urlsplit

from . import candidate_analytics as financial
from .. import intelligence_presentation as semantics
from ..security import verified_context, verified_service_read

SELECTOR = 'analysis'
PATHS = frozenset({'/industries/banking', '/enterprises/lloyds'})


def selection(path, query):
    """Reuse existing visual grammar; no change to the public query catalogue."""
    from .. import visual_streams as visual
    from ..access import valid_financial_intelligence_run_id
    if (path not in PATHS or SELECTOR not in query or len(query[SELECTOR]) != 1
            or not valid_financial_intelligence_run_id(query[SELECTOR][0])):
        raise PermissionError('Financial analysis unavailable')
    remaining = {k:v for k,v in query.items() if k != SELECTOR}
    ctx = visual.resolve(path, remaining)
    if ctx.detail or ctx.agenda or ctx.stream != visual.SCOPES[ctx.scope]['streams'][0]:
        raise PermissionError('Financial analysis unavailable')
    return ctx, query[SELECTOR][0]


def _resource(ctx, data):
    from .. import visual_streams as visual
    if ctx.scope not in {'banking','lloyds'}:
        raise PermissionError('Financial analysis unavailable')
    return data[visual.SCOPES[ctx.scope]['identity_key']]


def _current(ctx, run_id, headers):
    from .. import document_review as review, visual_streams as visual
    data = visual.current_data(ctx)
    run = review.read_run(run_id, headers=headers)
    if (run.get('run_id') != run_id or run.get('workflow') != financial.WORKFLOW
            or run.get('enterprise_id') != _resource(ctx, data) or not run.get('analysis')):
        raise PermissionError('Financial analysis unavailable')
    return data, run['analysis']


@verified_service_read('package.inspect')
def authorise_request(target, *, headers=None):
    """Narrow private-read admission; no anonymous selector or forged identity."""
    try:
        if (not isinstance(target,str) or len(target)>4096
                or any(ord(c)<32 or ord(c)==127 for c in target)):
            return False
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or parsed.fragment or parsed.path not in PATHS:
            return False
        pairs = parse_qsl(parsed.query, keep_blank_values=True, strict_parsing=True,
                          encoding='utf-8', errors='strict', max_num_fields=16)
        if len({k for k,v in pairs}) != len(pairs) or any(len(v)>1024 for k,v in pairs):
            return False
        query = {k:[v] for k,v in pairs}
        ctx, run_id = selection(parsed.path, query)
        _current(ctx, run_id, headers)
        return True
    except (OSError, ValueError, TypeError, KeyError, PermissionError):
        return False


def navigation(ctx, headers=None):
    """One contextual entry, only for an already-existing scoped current run.

    No global/latest scan, filenames from the browser, or creation on GET. A
    source-denied/missing/foreign record contributes no link, title or count.
    """
    if ctx.scope not in {'banking','lloyds'} or verified_context(headers) is None:
        return ''
    from .. import visual_streams as visual
    try:
        data = visual.current_data(ctx)
        resource = _resource(ctx, data)
        links = []
        for key in financial.permitted_selection_keys():
            run_id = financial.find_existing_run(key, resource, headers=headers)
            if run_id:
                # Recheck the exact selected run/context before serializing ID.
                _, projection = _current(ctx, run_id, headers)
                title = 'Financial analysis' if key == 'boe-household-deposit-stocks' else projection['title']
                links.append('<p class="financial-entry"><a href="'+e(visual.url(ctx,stream=visual.SCOPES[ctx.scope]['streams'][0],detail='',agenda='')+'&analysis='+run_id,quote=True)+'">'+e(title)+'</a></p>')
        from ..access import require_resource_scope, active_flora_workspace
        from ..security_store import cookie_token
        from ..security_web import form, CSRF_COOKIE
        try:
            require_resource_scope(headers, 'package.upload', resource, active_flora_workspace(headers))
            if ctx.scope == 'banking' and cookie_token(headers, CSRF_COOKIE):
                links.append(form('/financial-research/refresh', cookie_token(headers, CSRF_COOKIE), '', 'Refresh published research'))
        except PermissionError:
            pass
        return ''.join(links)
    except (OSError, ValueError, TypeError, KeyError, PermissionError):
        pass
    return ''


def _period(m):
    p = m.period
    return p.as_at.strftime('%d %b %Y') if p.kind=='instant' else p.start.strftime('%d %b %Y')+' – '+p.end.strftime('%d %b %Y')


def _kind(m):
    label = semantics.LABELS[m.semantic_type]
    return label + (' · '+m.state.title() if m.state!='actual' else '')


def _display_scale(measurements):
    largest = max((abs(m.base_amount) for m in measurements), default=Decimal(0))
    return ('billions',Decimal('1e9'),'bn') if largest>=Decimal('1e9') else ('millions',Decimal('1e6'),'m') if largest>=Decimal('1e6') else ('units',Decimal(1),'')


def _number(value, places=3):
    # Display only; input/reproducible output precision stays in the owner.
    if value and abs(value)<Decimal('0.001'):
        return format(value.normalize(),'f') if value.adjusted()>=-6 else format(value.normalize(),'E')
    text = format(value, ',.'+str(places)+'f')
    return text.rstrip('0').rstrip('.') if '.' in text else text


def _money(amount, currency, suffix, places=3):
    sign = '−' if amount<0 else ''
    return sign+('£' if currency=='GBP' else currency+' ')+_number(abs(amount), places)+suffix


def _nice(value):
    if value<=0:
        return Decimal(1)
    power = Decimal(10) ** value.adjusted()
    return next(n*power for n in map(Decimal,('1','2','5','10')) if n*power>=value)


def _group_key(m):
    # No implicit cross-company/basis/currency/state or stock/flow comparison.
    common = (m.subject_id,m.subject_name,m.perimeter,m.value.currency,m.value.scale,m.value.unit,m.accounting_basis,m.state,m.period.kind)
    if m.period.kind=='instant':
        return common+(m.metric,m.definition)
    return common+(m.period.start,m.period.end,m.period.fiscal_year_end)


def chart(measurements, index, *, show_perimeter=False):
    """Finite signed bar family, zero-inclusive linear axis and exact data table."""
    ms = list(measurements)
    if not ms or len(ms)>48 or len({_group_key(m) for m in ms})!=1:
        raise ValueError('Incompatible chart family')
    seen={};definitions={}
    for m in ms:
        if m.metric in definitions and definitions[m.metric]!=m.definition:
            raise ValueError('Ambiguous financial definition')
        definitions[m.metric]=m.definition
        key=(m.metric,str(m.period.as_at),str(m.period.start),str(m.period.end))
        if m.semantic_type=='reported':
            if key in seen and seen[key]!=m.value.amount:
                raise ValueError('Conflicting reported chart measurements')
            seen[key]=m.value.amount
    scale,factor,suffix = _display_scale(ms)
    values = [m.base_amount/factor for m in ms]
    if any(not v.is_finite() or abs(v)>Decimal('1e30') for v in values):
        raise ValueError('Unsupported chart magnitude')
    low = -_nice(abs(min(values))) if min(values)<0 else Decimal(0)
    high = _nice(max(values)) if max(values)>0 else Decimal(0)
    if high==low: high=Decimal(1)
    x = lambda value: (value-low)/(high-low)*100
    uid = 'financial-chart-'+str(index)
    unit = ms[0].value.currency+' '+scale
    title = ('Published stocks' if ms[0].period.kind=='instant' else 'Financial statement amounts')+' · '+unit
    context = ms[0].subject_name+' · '+ms[0].accounting_basis.replace('_',' ')
    if show_perimeter:context+=' · '+ms[0].perimeter
    if ms[0].period.kind=='duration':context+=' · '+_period(ms[0])
    graphic = '<div class="analyst-bars" role="group" aria-labelledby="'+uid+'-title '+uid+'-desc">'
    for m,value in zip(ms,values):
        label = _period(m) if m.period.kind=='instant' else m.metric.replace('_',' ').capitalize()
        start=min(x(value),x(Decimal(0))); length=abs(x(value)-x(Decimal(0)))
        graphic+='<div class="analyst-row"><span>'+e(label)+'<small>'+e(_kind(m))+'</small></span><strong>'+e(_money(value,m.value.currency,suffix))+'</strong><div class="analyst-track" aria-hidden="true"><i class="financial-bar '+('weaker' if m.semantic_type!='reported' else'reported')+'" style="left:'+str(start)+'%;width:'+str(length)+'%"></i><b class="zero" style="left:'+str(x(Decimal(0)))+'%"></b></div></div>'
    ticks=[low+(high-low)*Decimal(n)/4 for n in range(5)]
    graphic+='<div class="analyst-axis" aria-hidden="true"><div>'+''.join('<span>'+e(_number(t))+'</span>' for t in ticks)+'</div></div></div>'
    table = '<details class="chart-data"><summary>Measurements and chart data</summary><table><caption>'+e(title)+' · original reported scale retained</caption><thead><tr><th>Measure</th><th>Type</th><th>Period</th><th>Original amount</th></tr></thead><tbody>'
    for m in ms:
        table += '<tr><th scope="row">'+e(m.metric.replace('_',' ').capitalize())+'</th><td>'+e(_kind(m))+'</td><td>'+e(_period(m))+'</td><td>'+e(m.original_display)+'</td></tr>'
    table += '</tbody></table></details>'
    description = 'Dates are balance-sheet stocks; a stock difference is not an adjusted flow.' if ms[0].period.kind=='instant' else 'Signed amounts over the stated duration; no annualisation.'
    return '<figure class="analyst-chart"><figcaption id="'+uid+'-title">'+e(title)+'</figcaption><p class="chart-note">'+e(context)+'</p>'+graphic+'<p class="chart-note" id="'+uid+'-desc">Linear axis '+e(_number(low))+'–'+e(_number(high))+' '+e(unit)+' including zero. '+e(description)+'</p>'+table+'</figure>'


def _result_card(result, by_id):
    if result.get('formula') not in {'difference','percent_change','signed_bridge'}:
        raise ValueError('Unknown financial recipe')
    inputs = []
    for ref in result['inputs']:
        m = by_id.get(ref['measurement_id'])
        if m is None or m.revision != ref['revision']:
            raise ValueError('Result input revision unavailable')
        inputs.append(m)
    expected = 'estimated' if any(m.semantic_type!='reported' for m in inputs) else 'calculated'
    if result['semantic_type']!=expected or result['canonical_status']!='derived_view_not_canonical':
        raise ValueError('Derived authority/semantic mismatch')
    amount = Decimal(result['value'])
    if not amount.is_finite(): raise ValueError('Invalid result')
    if result['unit']=='%':
        text=_number(amount,4)+'%'; label='Relative stock difference' if inputs[0].period.kind=='instant' else 'Relative annual difference' if result.get('comparison')=='duration_dates' else 'Relative difference'
    else:
        _,factor,suffix = _display_scale(inputs)
        # Calculation's original result uses the original common source scale.
        from .normalisation import SCALE_FACTORS
        text = _money(amount*SCALE_FACTORS[inputs[0].value.scale]/factor,inputs[0].value.currency,suffix,3)
        label = 'Stock difference' if inputs[0].period.kind=='instant' else 'Reconciled endpoint' if result['formula']=='signed_bridge' else 'Annual difference' if result.get('comparison')=='duration_dates' else 'Absolute difference'
    if result['formula']=='signed_bridge':
        endpoint=inputs[-1]
        label=endpoint.metric.replace('_',' ').capitalize()
        if endpoint.accounting_basis=='statutory': label='Statutory '+label.lower()
    state = '' if result['measurement_state']=='actual' else ' · '+result['measurement_state'].title()
    period=_period(inputs[0]) if _period(inputs[0])==_period(inputs[-1]) else _period(inputs[0])+' → '+_period(inputs[-1])
    return '<div'+(' data-method="Reconciled endpoint"' if result['formula']=='signed_bridge' else '')+'><span class="metric-label">'+semantics.LABELS[expected]+e(state)+' · '+e(label)+'</span><strong>'+e(text)+'</strong><span class="metric-period">'+e(period)+'</span></div>'


def compose(projection, *, statements=()):
    """Pure finite view composition, never a source/IAM acceptance function.

    External routes must use render_selected, which obtains a fresh owner read.
    Synthetic contract callers can exercise the same families without creating
    live eligible data. No issuer/metric-specific renderer conditions.
    """
    ms = [financial.Measurement.model_validate(m) for m in projection['measurements']]
    if not ms or len(ms)>48 or len({m.measurement_id for m in ms})!=len(ms):
        raise ValueError('Invalid measurement composition')
    by_id={m.measurement_id:m for m in ms}
    groups=defaultdict(list)
    for m in ms: groups[_group_key(m)].append(m)
    scope=ms[0].perimeter if len({m.perimeter for m in ms})==1 else 'Distinct reporting subjects and accounting bases; each chart retains its own boundary.'
    body='<p class="eyebrow">Financial analysis</p><h1 id="financial-title">'+e(projection['title'])+'</h1><p class="lead">'+e(scope)+'</p>'
    if projection['results']:body+='<div class="metrics financial-results">'+''.join(_result_card(r,by_id) for r in projection['results'])+'</div>'
    body+=''.join(chart(group,index,show_perimeter=len({m.perimeter for m in ms})>1) for index,group in enumerate(groups.values()))
    # Existing presentation semantics handles all six kinds; empty/unqualified
    # intelligence slots are omitted rather than invented for visual fullness.
    urls={s['url'] for s in projection['sources']}
    for statement in statements:
        if (statement.scope in {m.perimeter for m in ms} and semantics.eligible(statement)
                and all(s.url in urls for s in statement.sources)
                and not (statement.semantic_type in {'reported','calculated'}
                         and {'estimated','assumed'}.intersection(statement.dependency_types))):
            body+=semantics.render(statement)
    for insight in projection.get('insights', []):
        statement = semantics.Statement(insight['text'], insight['type'], ms[0].perimeter, _period(ms[0]),
            tuple(semantics.Source(s['title'], s['url'], ms[0].source.publisher, s['published'], locator=s['locator']) for s in projection['sources']),
            'reviewed_excerpt', 'candidate_intelligence', reasoning=insight['reasoning'],
            caveats=ms[0].caveats, dependencies=tuple(insight.get('dependencies', ())),
            counter_evidence=tuple(insight.get('counter_evidence', ())),
            dependency_types=tuple(m.semantic_type for m in ms))
        if semantics.eligible(statement): body += semantics.render(statement)
    caveats=list(dict.fromkeys(c for m in ms for c in m.caveats))
    if caveats: body+='<p class="material">'+e(caveats[0])+'</p>'
    sources=''
    for s in projection['sources']:
        sources+='<section class="source-entry"><a href="'+e(s['url'],quote=True)+'" rel="noreferrer">'+e(s['title'])+'</a><p>'+e(s['locator'])+'</p><p>Retrieved '+e(s['retrieved_at'][:10])+'. '+e(s['extent'])+'</p>'
        if s.get('published'): sources+='<p>Published '+e(s['published'])+'</p>'
        else: sources+='<p>The original publication day and release vintage are not established.</p>'
        sources+='<p>'+e(s['attribution'])+' <a href="'+e(s['licence_url'],quote=True)+'">Source-use basis</a></p></section>'
    methods=''.join('<li>'+e(r['method'])+' · '+e(r['unit'])+' · version '+e(r['formula_version'])+'</li>' for r in projection['results'])
    definitions=''.join('<li>'+e(m.definition)+' · '+e(m.accounting_basis)+' · '+e(m.rounding)+'; '+str(m.precision_dp)+' decimal places at source scale</li>' for m in ms)
    assumptions=''.join('<li>'+e(m.metric.replace('_',' '))+': '+e(m.assumption_owner)+' · version '+e(m.assumption_version)+' · '+e(m.original_display)+'</li>' for m in ms if m.semantic_type in {'estimated','assumed'})
    if assumptions:
        assumptions='<h2>Assumptions</h2><p>Calculated arithmetic retains the weaker Estimated basis of these inputs.</p><ul>'+assumptions+'</ul>'
    return body+'<details class="financial-basis"><summary>Sources, method and limitations</summary><p>Analytical working view; no Enterprise record is updated by this analysis.</p>'+sources+('<h2>Method</h2><ul>'+methods+'</ul>' if methods else '')+'<h2>Definitions</h2><ul>'+definitions+'</ul>'+assumptions+'<ul>'+''.join('<li>'+e(c)+'</li>' for c in caveats)+'</ul></details>'


STYLE = '''<style>
.financial-entry{margin:22px 0}.financial-entry a{display:inline-flex;min-height:44px;align-items:center;border-bottom:1px solid #a38a4f;text-decoration:none}
.analyst-chart{margin:30px 0;border-bottom:1px solid var(--line);padding-bottom:20px}.analyst-chart figcaption{font:24px Georgia,serif;margin-bottom:18px}
.analyst-bars{display:grid;grid-template-columns:minmax(120px,1fr) minmax(100px,2fr) max-content;gap:20px 18px;grid-auto-flow:row dense;align-items:center}.analyst-row,.analyst-axis{display:contents}.analyst-row>span{grid-column:1;font-size:14px;line-height:1.5}.analyst-row small{display:block;font-size:12px;color:var(--muted)}.analyst-row strong{grid-column:3;font-size:15px;font-weight:600}.analyst-track{grid-column:2;height:20px;background:#e8eadf;position:relative;min-width:0}.financial-bar{position:absolute;top:0;height:100%;background:#355b46;border-right:2px solid #ac9256;box-sizing:border-box}.financial-bar.weaker{background:repeating-linear-gradient(45deg,#927b47,#927b47 3px,#baa56f 3px,#baa56f 5px);border:1px dashed #38513f}.zero{position:absolute;height:28px;top:-4px;border-left:1px solid #38513f}.analyst-axis>div{grid-column:2;display:flex;justify-content:space-between;font-size:11px;color:var(--muted)}
.financial-basis li,.financial-basis p{overflow-wrap:anywhere}.financial-basis h2{font-size:19px!important}.financial-results{display:grid!important;grid-template-columns:repeat(auto-fit,minmax(min(100%,16em),1fr))!important}.financial-results>div{min-width:0}.financial-results strong{white-space:nowrap;overflow-wrap:normal}
@media(max-width:700px){.analyst-bars{grid-template-columns:minmax(0,1fr) max-content;gap:10px}.analyst-row .analyst-track{grid-column:1/-1}.analyst-row strong{grid-column:2}.analyst-axis>div{grid-column:1/-1}}
@media(max-width:600px){.analyst-bars{min-width:0}.analyst-chart .chart-data table,.analyst-chart .chart-data tbody{display:block}.analyst-chart .chart-data caption{display:block;width:auto;text-align:left;margin:14px 0}.analyst-chart .chart-data thead{position:absolute;width:1px;height:1px;clip-path:inset(50%);overflow:hidden}.analyst-chart .chart-data tr{display:grid;grid-template-columns:minmax(0,1fr);padding:14px 0;border-bottom:1px solid var(--line)}.analyst-chart .chart-data th,.analyst-chart .chart-data td{padding:3px 0;border:0;overflow-wrap:anywhere}.analyst-chart .chart-data td:last-child{font-weight:600;white-space:nowrap}}
@media(forced-colors:active){.analyst-track{border:1px solid CanvasText}.financial-bar{background:CanvasText;border-color:CanvasText}.financial-bar.weaker{background:Canvas;border:2px dashed CanvasText}}
</style>'''


@verified_service_read('package.inspect')
def render_selected(ctx, run_id, *, headers=None):
    """Hold existing verified read authority across the entire three-panel view."""
    from .. import visual_streams as visual, visual_panels as panels, leadership_agenda as agenda
    data,projection=_current(ctx,run_id,headers)
    issues=agenda.agenda(ctx.scope,data,selected=ctx.selected)
    entries=visual.destinations(ctx,data)
    close='<a class="close close-insight" href="'+e(visual.url(ctx),quote=True)+'" aria-label="Close financial analysis">×</a>'
    from ..access import is_cios_owner
    from .. import design_system
    if is_cios_owner(headers):design_system.context_link(visual.url(ctx)+'&analysis='+run_id+'&lens=inspection','Financial research')
    body='<section class="focus financial-analyst" id="insight" tabindex="-1" aria-label="Financial analysis">'+close+compose_editorial(projection)+'</section>'
    return panels._frame(ctx,headers,data,issues,entries,body)


@verified_service_read('package.inspect')
def _selected_financial(ctx, *, headers=None):
    """Only current, own-workspace Financial data; no creation or discovery."""
    from ..access import require_resource_scope, active_flora_workspace
    if ctx.scope!='banking' or ctx.selected!='nationwide': return None
    workspace=active_flora_workspace(headers)
    require_resource_scope(headers,'package.inspect','BK-IND-002',workspace)
    identity=financial.find_existing_run('nationwide-fy2026','BK-IND-002',headers=headers)
    return _current(ctx,identity,headers)[1] if identity else None


def selected_financial(ctx, *, headers=None):
    try: return _selected_financial(ctx,headers=headers)
    except (PermissionError,OSError,ValueError,KeyError,TypeError): return None


@verified_service_read('package.upload')
def _prepare_action(ctx, *, headers=None):
    from ..access import is_cios_owner, require_resource_scope, active_flora_workspace
    from ..security_store import cookie_token
    from ..security_web import form, CSRF_COOKIE
    if ctx.scope!='banking' or ctx.selected!='nationwide' or not is_cios_owner(headers): return ''
    require_resource_scope(headers,'package.upload','BK-IND-002',active_flora_workspace(headers))
    # No promise of availability from a withdrawn/denied Source.
    financial._current_inputs('nationwide-fy2026')
    csrf=cookie_token(headers,CSRF_COOKIE)
    return (form('/financial-research/refresh',csrf,'<input type="hidden" name="selected" value="nationwide">','Prepare financial view') if csrf else '')


def prepare_action(ctx, *, headers=None):
    try:return _prepare_action(ctx,headers=headers)
    except (PermissionError,OSError,ValueError,KeyError,TypeError):return ''


def compose_editorial(projection, *, heading=True):
    """Concise generic Financial view over validated existing owner output.

    Endpoints remain Reported; bridge outputs remain Calculated. Source IDs,
    URLs, methodology, run IDs and inspector controls are never serialized.
    """
    ms=[financial.Measurement.model_validate(m) for m in projection['measurements']]
    if not ms:raise ValueError('No current financial measurements')
    semantics.note_editorial_sources(semantics.Source(s['title'],s['url'],ms[0].source.publisher,s.get('published','')) for s in projection['sources'])
    by_id={m.measurement_id:m for m in ms}
    # Check every recipe/input through the existing finite composer as well.
    for r in projection['results']:_result_card(r,by_id)
    stocks=all(m.period.kind=='instant' for m in ms)
    name=projection['title'] if stocks else projection['title'].split(' · ')[0]
    eyebrow='Published balances' if stocks else 'Earnings & member value' if any(m.metric=='member_reward_payments' for m in ms) else 'Financial overview'
    body=('<p class="eyebrow">'+e(eyebrow)+'</p><h1>'+e(name)+'</h1>' if heading else '')
    shared_period=len({_period(m) for m in ms})==1
    scope=('Consolidated Group · FY'+str(ms[0].period.end.year) if not stocks and 'consolidated Group'in ms[0].perimeter else ms[0].perimeter)
    body+='<p class="lead">'+e(scope)+'</p>'+('<p class="shared-period">'+e(_period(ms[0]))+'</p>' if shared_period else '')
    chosen=[m for m in ms if m.metric in {'total_income','revenue','underlying_profit_before_tax','profit_before_tax'}]
    if not chosen:chosen=ms[:3]
    body+='<div class="metrics earnings-metrics">'
    for m in chosen:
        _,factor,suffix=_display_scale(chosen)
        label=m.metric.replace('_',' ').capitalize()
        if m.metric=='total_income' and m.accounting_basis=='underlying':label='Underlying income'
        if m.accounting_basis=='statutory': label='Statutory '+label.lower()
        if stocks:label=_period(m)
        body+='<div data-semantic-type="'+m.semantic_type+'"><span class="metric-label">'+e(label)+'</span><strong>'+e(_money(m.base_amount/factor,m.value.currency,suffix))+'</strong><span class="metric-period">'+e(_kind(m)+(' · '+_period(m) if not shared_period and not stocks else ''))+'</span></div>'
    body+='</div>'
    if stocks and projection['results']:
        body+='<div class="metrics stock-movements">'+''.join(_result_card(r,by_id) for r in projection['results'])+'</div><p class="material">Difference between published balances, not an adjusted deposit flow.</p>'
    bridge=next((r for r in projection['results'] if r['formula']=='signed_bridge' and r.get('basis')=='statutory'),None)
    if bridge:
        inputs=[by_id[r['measurement_id']]for r in bridge['inputs']]
        opening,endpoint=inputs[0],inputs[-1]
        terms=[]
        for i,m in enumerate(inputs[:-1]):
            sign='− 'if m.value.amount<0 else '+ 'if i else ''
            suffix={'units':'','thousands':'k','millions':'m','billions':'bn'}[m.value.scale]
            terms.append(sign+_money(abs(m.value.amount),m.value.currency,suffix,m.precision_dp))
        suffix={'units':'','thousands':'k','millions':'m','billions':'bn'}[endpoint.value.scale]
        equation=' '.join(terms)+' = '+_money(endpoint.value.amount,endpoint.value.currency,suffix,endpoint.precision_dp)
        body+='<section class="earnings-story"><h2>'+('Member rewards and integration' if any(m.metric=='member_reward_payments' for m in ms) else 'Earnings and returns')+'</h2><p>'+('Member rewards and acquisition-related adjustments explain the two profit bases.' if any(m.metric=='member_reward_payments' for m in ms) else 'The disclosed adjustments reconcile the reported bases.')+'</p><p class="earnings-equation" data-semantic-type="'+bridge['semantic_type']+'"><span class="intelligence-label">'+semantics.LABELS[bridge['semantic_type']]+'</span> '+e(equation)+'</p></section>'
    for insight in projection.get('insights',[]):
        if insight['type']=='reported': body+='<p class="earnings-context">'+e(insight['text'])+'</p>'
    caveats=list(dict.fromkeys(c for m in ms for c in m.caveats))
    if caveats:body+='<p class="material">'+e('Virgin Money contributes a full year; the previous reporting period included six months.' if any(m.metric=='member_reward_payments' for m in ms) else caveats[0])+'</p>'
    return '<section class="financial-editorial" aria-label="Financial overview">'+body+'</section>'
