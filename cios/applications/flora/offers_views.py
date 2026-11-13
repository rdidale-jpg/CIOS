"""Small authenticated Offers UI; browser controls convey no service authority."""
from html import escape as e
from urllib.parse import urlencode

from . import offers
from .research_intelligence.unified_views import page

CSS = """
.offers{--ink:#173e32;--paper:#faf8f2;max-width:1160px;margin:auto;color:var(--ink);padding:30px 22px 70px}.offers *{box-sizing:border-box}.offers h1{font:clamp(2.4rem,5vw,4.4rem)/1.06 Georgia,serif;letter-spacing:-.035em;margin:16px 0}.offers h2{font:1.7rem Georgia,serif}.offers p{max-width:74ch;line-height:1.65}.offers nav{display:flex;gap:10px 22px;flex-wrap:wrap;border-bottom:1px solid #d6ddd3;padding:12px 0 20px}.offers a{color:#174e3d}.offers a[aria-current=page]{font-weight:bold;text-decoration-thickness:3px}.offer-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin:30px 0}.offer-card{background:#fffdf8;border:1px solid #dce1d5;border-radius:18px;padding:24px;min-width:0}.offer-card h2{margin-top:8px}.offer-card small,.offers .muted{color:#59675e}.offers .eyebrow{text-transform:uppercase;font-size:.76rem;letter-spacing:.13em}.offers label{display:block;margin:14px 0}.offers input:not([type=checkbox]),.offers textarea,.offers select{display:block;width:100%;font:inherit;padding:11px;border:1px solid #a9b5aa;border-radius:7px;background:white;color:#183a2e}.offers textarea{min-height:90px;resize:vertical}.offers button,.offers .offer-button{display:inline-block;background:#174e3d;color:white;border:0;border-radius:7px;padding:11px 17px;font:inherit;cursor:pointer;text-decoration:none;margin:8px 10px 8px 0}.offers .quiet{background:#e9eee4;color:#173e32}.offers :focus-visible{outline:3px solid #bb731c;outline-offset:4px}.offers details{border-top:1px solid #dce1d5;margin:18px 0;padding-top:16px}.offers summary{cursor:pointer;font-weight:600}.offers .split{display:grid;grid-template-columns:1.5fr 1fr;gap:24px}.offers form{margin:10px 0}.offers .pair{border-top:1px solid #d7ddce;padding:28px 0}.offers .pair h2{margin:0 0 10px}.offers .status{display:inline-block;font-size:.77rem;border:1px solid #b6c6b3;border-radius:20px;padding:4px 10px}.offers .explanation{background:#eff2e9;padding:18px;border-radius:12px}.offers .source-list{overflow-wrap:anywhere}.offers .actions{display:flex;gap:8px;flex-wrap:wrap}.offers fieldset{border:1px solid #d6ddd3;border-radius:12px;padding:16px}.offers .inline{display:flex;gap:16px;align-items:end;flex-wrap:wrap}.offers .inline label{flex:1;min-width:180px}.offers .notice{border-left:3px solid #8a9f78;padding-left:16px}.offers .history{font-size:.9rem}.offers code{overflow-wrap:anywhere}@media(max-width:950px){.offer-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:620px){.offers{padding:20px 12px 50px}.offer-grid,.offers .split{grid-template-columns:1fr}.offer-card{padding:19px}.offers nav{gap:12px}.offers .inline{display:block}.offers h1{font-size:2.7rem}}
"""
LABELS = {'name': 'Offer name', 'outcome': 'Customer outcome', 'icp': 'Target industries (comma separated)',
    'buyers': 'Buyer roles', 'trigger': 'Buying trigger / structural pattern', 'entry_play': 'First entry play',
    'next_test': 'Validation question / next test', 'capabilities': 'Delivery capabilities and proof required',
    'partners': 'Partner and rights dependencies', 'constraints': 'Delivery constraints / limitations',
    'evidence': 'Evidence references and approved asset links', 'exclusions': 'Exclusions / what not to claim', 'trigger_pattern': 'Trigger pattern'}


def url(path='', **query):
    return offers.BASE + path + ('?' + urlencode({k: v for k, v in query.items() if v}) if any(query.values()) else '')


def link(path, label, **query):
    return f'<a href="{e(url(path, **query), quote=True)}">{e(label)}</a>'


def hidden(name, value):
    return f'<input type="hidden" name="{e(name)}" value="{e(str(value), quote=True)}">'


def form(path, content, label, quiet=False):
    return f'<form method="post" action="{url(path)}">{content}<button class="{"quiet" if quiet else ""}" type="submit">{e(label)}</button></form>'


def field(name, value='', label=None, area=False, required=False):
    tag = (f'<textarea name="{e(name)}" {"required" if required else ""}>{e(value)}</textarea>' if area else
        f'<input name="{e(name)}" value="{e(value, quote=True)}" maxlength="2400" {"required" if required else ""}>')
    return f'<label>{e(label or LABELS.get(name, name))}{tag}</label>'


def _record(state, offer_id):
    record = next((r for r in state['offers'] if r['id'] == offer_id and r['current']), None)
    if not record:
        raise PermissionError('Offer unavailable')
    return record


def render(path, query, headers):
    allowed = {'offer', 'parent', 'template', 'mode', 'selected', 'cutoff'}
    if set(query) - allowed or any(len(v) != 1 for v in query.values()):
        raise ValueError('Unsupported offer selector')
    q = {k: v[0] for k, v in query.items()}
    state = offers.snapshot(headers=headers)
    current = path.removeprefix(offers.BASE)
    nav = ''.join(f'<a href="{url(s)}"'+ (' aria-current="page"' if current == s else '') + f'>{label}</a>'
        for s, label in (('', 'My offers'), ('/company', 'My company'), ('/discover', 'Discover'), ('/review', 'Reviews'), ('/studio', 'Creative Studio')))
    if path == url('/company'):
        title, body = 'My company', company(state, headers)
    elif not state['selected']:
        title, body = 'Choose your company', '<p>Select an authorised employer before creating or discovering offers.</p>' + company(state, headers)
    elif path == url('/edit'):
        title, body = 'Shape an offer', editor(state, q)
    elif path == url('/review'):
        title, body = 'Offer reviews', reviews(state)
    elif path == url('/discover'):
        title, body = 'Find a useful first move', discovery(state, q, headers)
    elif path == url('/studio'):
        title, body = 'Creative Offers Studio', studio(state, headers)
    else:
        title, body = 'What can you help customers achieve?', catalogue(state)
    company_name = state['selected']['organisation'] if state['selected'] else 'Your commercial workspace'
    content = f'<style>{CSS}</style><section class="offers" id="offers-content" aria-label="Offers workspace"><p class="eyebrow">FLORA / Offers pilot · {e(company_name)}</p><nav aria-label="Offers">{nav}</nav><h1>{e(title)}</h1>{body}</section>'
    return page('Offers — ' + title, content, headers, 'opportunities', path)


def company(state, headers):
    choices = ''.join(f'<option value="{e(c["id"])}" {"selected" if state["selected"] and state["selected"]["id"] == c["id"] else ""}>{e(c["organisation"])}</option>' for c in state['employers'])
    body = '<p>Your company context shapes recommendations. It does not change shared enterprise intelligence.</p>'
    if choices:
        body += form('/select', f'<label>Represented employer<select name="employer_id">{choices}</select></label>', 'Use this company')
    else:
        body += '<p class="notice">No employer authorisation has been configured for this workspace. An owner must review the binding first.</p>'
    if state['selected']:
        selected = state['selected']
        body += f'<details><summary>Employer authorisation</summary><p>Binding revision {selected["version"]}. Canonical participant identity remains unbound in this pilot.</p><p>Reviewers: {e(", ".join(selected["approvers"]))}</p></details>'
        if state['owner']:
            body += form('/revoke', hidden('employer_id', selected['id']), 'Revoke employer binding', True)
    if state['owner']:
        from .commercial_mission import resolve_employer_context
        profile = resolve_employer_context(headers)
        body += '<details><summary>Owner: authorise company context</summary><p>First configure your declared Employer Context in existing My Company settings. This explicit binding authorises only named active workspace members. It does not certify company capabilities or canonical identity. A separate person must approve offers.</p><a href="/blueprint-import">Open existing commercial settings</a>'
        body += '<p>Configured employer: ' + e(profile.organisation if profile else 'Not configured') + '</p>'
        body += form('/bind', field('sellers', state['user_id'], 'Seller user IDs (comma separated)', required=True)
            + field('approvers', '', 'Delegated approver user IDs (comma separated)', required=True)
            + field('approval_reference', '', 'Explicit employer-binding review reference', required=True), 'Authorise named members') + '</details>'
    return body


def catalogue(state):
    records = [r for r in state['offers'] if r['current']]
    cards = ''
    for r in records:
        content = r['content']
        controls = link('/edit', 'Open offer', offer=r['id'])
        if r['eligible']:
            controls += ' · ' + link('/discover', 'Discover accounts', mode='offer', selected=r['id'])
        if r['state'] == 'employer_approved' and r['eligible']:
            controls += ' · ' + link('/edit', 'Create private variation', parent=r['id'])
        status = r['state'].replace('_', ' ')
        if not r['eligible'] and r['state'] in {'private_draft', 'employer_approved'}:
            status += ' · review dependency changes'
        cards += f'<article class="offer-card"><span class="status">{e(status)} · v{r["version"]}</span><h2>{e(content["name"])}</h2><p>{e(content["outcome"])}</p><p class="muted">{e(content["buyers"])}</p><p>{controls}</p></article>'
    body = '<p>Start with the outcome. Choose an offer, explore a customer, then test the fit.</p>'
    body += '<div class="actions">' + link('/edit', 'Create private offer') + '</div>'
    if cards:
        body += '<div class="offer-grid">' + cards + '</div>'
    else:
        body += '<p>No offers yet. Start with an illustrative template or create your own.</p>'
    body += '<details' + ('' if records else ' open') + '><summary>Three illustrative starting points</summary><p>Templates are private starting points, not approved company propositions or live leads. Add your delivery proof and constraints before review.</p><div class="offer-grid">'
    for key, c in offers.TEMPLATES.items():
        body += f'<article class="offer-card"><p class="eyebrow">Illustrative / {e(key)}</p><h2>{e(c["name"])}</h2><p>{e(c["outcome"])}</p>{link("/edit", "Use private template", template=key)}</article>'
    return body + '</div></details>'


def editor(state, q):
    record = _record(state, q['offer']) if q.get('offer') else None
    parent = _record(state, q['parent']) if q.get('parent') else None
    if q.get('template') and q['template'] not in offers.TEMPLATES:
        raise ValueError('Template unavailable')
    content = deepcopy_content(record or parent) if record or parent else dict(offers.TEMPLATES.get(q.get('template'), {k: '' for k in offers.FIELDS}))
    can_revise = bool(record and record['state'] == 'employer_approved' and state['user_id'] in state['selected']['approvers'])
    can_edit = bool(record and record['author'] == state['user_id'] and record['state'] in {'private_draft', 'changes_requested', 'rejected'})
    locked = bool(record and not (can_revise or can_edit))
    values = hidden('offer_id', record['id'] if record else '') + hidden('expected_version', record['version'] if record else 0)
    if parent:
        values += hidden('parent_id', parent['id']) + hidden('parent_version', parent['version'])
    variation = bool(parent or (record and record['parent']))
    body = '<p>Private drafts express a hypothesis and a first conversation. Organisational publication needs a separate reviewer.</p>'
    if record:
        body += f'<p><span class="status">{e(record["state"].replace("_", " "))} · v{record["version"]}</span></p>'
    if record and record['state'] == 'employer_approved' and record['eligible']:
        body += '<p>' + link('/edit', 'Create private variation', parent=record['id']) + '</p>'
    for name in offers.FIELDS:
        if locked or (variation and name not in offers.VARIATION_FIELDS):
            values += f'<section><h2>{e(LABELS[name])}</h2><p>{e(content[name])}</p></section>'
        elif name == 'trigger_pattern':
            options = ''.join(f'<option value="{key}" '+ ('selected' if content.get(name) == key else '') + f'>{e(value[0])}</option>' for key, value in offers.PATTERNS.items())
            values += '<label>Trigger pattern<select name="trigger_pattern">' + options + '</select></label>'
        else:
            values += field(name, content[name], area=name != 'name', required=name in {'name', 'outcome', 'icp', 'buyers', 'trigger', 'entry_play', 'next_test', 'capabilities', 'constraints'})
    if locked:
        body += values
    else:
        body += form('/save', values, 'Save new private version')
    if record and record['author'] == state['user_id']:
        if record['state'] in {'private_draft', 'changes_requested'}:
            body += form('/transition', hidden('offer_id', record['id']) + hidden('expected_version', record['version']) + hidden('action', 'submit'), 'Submit for employer review', True)
        if record['state'] != 'retired' and (record['state'] != 'employer_approved' or state['user_id'] in state['selected']['approvers']):
            body += form('/transition', hidden('offer_id', record['id']) + hidden('expected_version', record['version']) + hidden('action', 'retire'), 'Retire / reject this draft', True)
        history = [r for r in state['offers'] if r['id'] == record['id']]
        body += '<details class="history"><summary>Version lineage and review history</summary>' + ''.join(f'<p>v{r["version"]} · {e(r["state"])} · {e(r["review"]["action"] if r["review"] else "saved privately")}</p>' for r in history)
        if record['parent']:
            body += '<p>Protected parent: ' + e(str(record['parent'])) + '</p>'
        if record['components']:
            body += '<p>Component versions: ' + e(str(record['components'])) + '</p>'
            body += '<p>Target reference: ' + e(str(record.get('target_context', {}))) + '</p>'
            body += ''.join('<p><strong>' + e(k.replace('_', ' ').capitalize()) + ':</strong> ' + e(v) + '</p>' for k, v in record.get('composition_review', {}).items())
        body += '</details>'
    if record and record['author'] != state['user_id'] and record['state'] == 'employer_approved' and state['user_id'] in state['selected']['approvers']:
        body += form('/transition', hidden('offer_id', record['id']) + hidden('expected_version', record['version']) + hidden('action', 'retire'), 'Withdraw employer-approved version', True)
    return body


def deepcopy_content(record):
    return dict(record['content'])


def reviews(state):
    if state['user_id'] not in state['selected']['approvers']:
        return '<p>Employer review requires a delegated approver. Your private drafts remain in My offers.</p>'
    body = '<p>Review delivery proof, partner rights, protected parent claims and approved scope. Approval publishes the proposition to bound employer sellers; it does not accept evidence or create a lead.</p>'
    for r in state['offers']:
        if not r['current'] or r['state'] != 'submitted_for_review' or r['author'] == state['user_id']:
            continue
        body += f'<article class="offer-card"><h2>{e(r["content"]["name"])}</h2><p>{e(r["content"]["outcome"])}</p>{link("/edit", "Inspect full offer and evidence", offer=r["id"])}'
        options = '<option value="changes">Request changes</option><option value="reject">Reject</option><option value="approve">Approve for employer catalogue</option>'
        body += form('/transition', hidden('offer_id', r['id']) + hidden('expected_version', r['version'])
            + '<label>Decision<select name="action">' + options + '</select></label>'
            + field('approval_reference', '', 'Review and rights approval reference', required=True), 'Record separate review') + '</article>'
    return body


def discovery(state, q, headers):
    mode = q.get('mode', 'offer')
    targets = offers.accounts()
    from .access import can_access_enterprise
    # Only expose bound account choices permitted by the existing evaluator.
    targets = {k: a for k, a in targets.items() if a['id'].startswith('presentation:') or can_access_enterprise(headers, a['id'])}
    eligible = [r for r in state['offers'] if r['current'] and r['eligible']]
    choices = eligible if mode == 'offer' else list(targets.values())
    selected = q.get('selected', '')
    options = '<option value="">All authorised ' + ('offers' if mode == 'offer' else 'accounts') + '</option>'
    options += ''.join(f'<option value="{e(r["id"] if mode == "offer" else r["slug"])}" {"selected" if selected == (r["id"] if mode == "offer" else r["slug"]) else ""}>{e(r["content"]["name"] if mode == "offer" else r["name"])}</option>' for r in choices)
    cutoff = q.get('cutoff', '2026-11-13')
    body = '<p>Start with your offer or with an account. The same assessment answers why this customer, why this offer, and the next useful test.</p>'
    body += '<p>' + link('/discover', 'Offer-led discovery', mode='offer') + ' · ' + link('/discover', 'Account-led discovery', mode='account') + '</p>'
    body += f'<form method="get" action="{url("/discover")}" class="inline">{hidden("mode", mode)}<label>{"Offer" if mode == "offer" else "Account"}<select name="selected">{options}</select></label><label>Evidence cutoff<input type="date" name="cutoff" value="{e(cutoff, quote=True)}" required></label><button>Explore matches</button></form>'
    results = offers.discover(mode, selected, cutoff, headers=headers)
    for r in results:
        offer = next(o for o in eligible if o['id'] == r['offer_id'])
        body += f'<article class="pair" data-assessment-id="{e(r["assessment_id"])}"><p class="eyebrow">{e(r["recommended_posture"])} · hypothesis to test</p><h2>{e(r["enterprise_name"])} × {e(offer["content"]["name"])}</h2><div class="split"><div><p><strong>Why this customer</strong><br>{e(r["why_account"])}</p><p><strong>Why this offer</strong><br>{e(r["why_offer"])}</p><p><strong>Why now</strong><br>{e(r["why_now"])}</p></div><div class="explanation"><h3>First move</h3><p>{e(r["entry_play"])}</p><p><strong>Test next</strong><br>{e(r["next_validation_action"])}</p></div></div>'
        body += '<p class="muted">Access and delivery fit need validation. No buying intent or funding established.</p>'
        body += '<details><summary>Assessment, uncertainty and sources</summary>'
        for k in ('capability_fit', 'credibility', 'relationship_access', 'trigger_evaluation', 'delivery_risk'):
            body += f'<p><strong>{e(k.replace("_", " ").capitalize())}:</strong> {e(r[k])}</p>'
        body += '<p><strong>Unknowns:</strong> ' + e('; '.join(r['unknowns'])) + '</p><p><strong>Counter-indicators:</strong> ' + e('; '.join(r['contradictions'])) + '</p>'
        body += '<p><strong>Alternatives:</strong> ' + e('; '.join(r['competitive_alternatives'])) + '</p><p><strong>Do not claim:</strong> ' + e('; '.join(r['what_not_to_claim'])) + '</p>'
        body += '<div class="source-list">'
        for ref in r['evidence_lineage']:
            body += f'<p>{e(ref["statement"])} <small>({e(ref["classification"])})</small></p>'
            for source in ref['source_refs']:
                body += f'<p><a href="{e(source["url"], quote=True)}" rel="noreferrer">{e(source["title"])}</a> · {e(source.get("verification", ""))}</p>'
                body += '<p class="muted">' + e(source.get('limitation', 'Existing source verification and rights limitations retained.')) + '</p>'
        body += '</div><p>Offer evidence / seller declaration: ' + e(r['offer_evidence']) + '</p><p>' + e('; '.join(r['limitations'])) + '</p>'
        body += f'<p>Assessment <code>{e(r["assessment_id"])}</code> · cutoff {e(r["source_cut_off"])} · {e(r["policy_version"])}. Proposed hypothesis; no accepted APPA or canonical promotion.</p></details>'
        body += f'<p><a href="{e(targets[r["enterprise_slug"]]["url"], quote=True)}">Explore account</a> · <a href="/flora/sales/pipeline">Open existing Pipeline</a></p>'
        if r['enterprise_slug'] in {'lloyds', 'easyjet'}:
            body += f'<p><a href="/flora/sales/new?enterprise={r["enterprise_slug"]}">Open manual Pipeline qualification</a> — separate seller-authorised action; no offer data is copied or saved by this link.</p>'
        else:
            body += '<p class="muted">No canonical account binding or manual Pipeline capture is enabled for this Technology presentation account.</p>'
        body += '</article>'
    if not results:
        body += '<p>No eligible pairs. Save an offer, choose target sectors and check account permissions or parent review.</p>'
    return body


def studio(state, headers):
    enabled = state['studio_enabled']
    body = '<p>Explore a grounded combination of existing offers. Keep the simpler offer if a bundle adds no measurable customer value.</p>'
    body += f'<p class="status">{"Enabled for you" if enabled else "Off by default"} · deterministic · no model cost</p>'
    body += form('/studio-toggle', hidden('enabled', 'no' if enabled else 'yes'), 'Disable Studio' if enabled else 'Enable for me in this workspace', True)
    if not enabled:
        return body + '<p>No creative suggestions or paid calls run while Studio is disabled.</p>'
    eligible = [r for r in state['offers'] if r['current'] and r['eligible'] and r['state'] == 'employer_approved' and r['content']['evidence']]
    options = ''.join(f'<option value="{e(r["id"])}:{r["version"]}">{e(r["content"]["name"])} · v{r["version"]}</option>' for r in eligible)
    if len(eligible) < 2:
        return body + '<p>Two current employer-approved offers with evidence references are required. Add proof and obtain separate review first.</p>'
    body += '<p class="notice">The new proposal remains private. Component approval does not approve the combination or partner rights.</p>'
    from .access import can_access_enterprise
    target_options = ''.join(f'<option value="{e(a["slug"])}">{e(a["name"])}</option>' for a in offers.accounts().values() if a['id'].startswith('presentation:') or can_access_enterprise(headers, a['id']))
    return body + form('/compose', '<label>Account context to test<select name="enterprise_slug">' + target_options + '</select></label><label>First component<select name="first">' + options + '</select></label><label>Second component<select name="second">' + options + '</select></label>', 'Save private combination draft')


def submit(path, form_values, headers):
    def one(key, default=''):
        values = form_values.get(key, [default])
        if len(values) != 1:
            raise ValueError('Duplicate form field')
        return values[0]
    permitted = {'csrf'}
    schemas = {'/bind': {'sellers', 'approvers', 'approval_reference'}, '/select': {'employer_id'},
        '/revoke': {'employer_id'}, '/save': set(offers.FIELDS) | {'offer_id', 'expected_version', 'parent_id', 'parent_version'},
        '/transition': {'offer_id', 'expected_version', 'action', 'approval_reference'}, '/studio-toggle': {'enabled'},
        '/compose': {'first', 'second', 'enterprise_slug'}}
    suffix = path.removeprefix(offers.BASE)
    if suffix not in schemas or set(form_values) - (schemas[suffix] | permitted):
        raise ValueError('Unsupported offer action')
    if suffix == '/bind':
        offers.bind_employer([s.strip() for s in one('sellers').split(',')], [s.strip() for s in one('approvers').split(',')], one('approval_reference'), headers=headers)
        return url('/company')
    if suffix == '/select':
        offers.select_employer(one('employer_id'), headers=headers)
        return url()
    if suffix == '/revoke':
        offers.revoke_employer(one('employer_id'), headers=headers)
        return url('/company')
    if suffix == '/save':
        r = offers.save_offer({k: one(k) for k in offers.FIELDS if k in form_values}, one('offer_id'), int(one('expected_version', '0')), one('parent_id'), int(one('parent_version', '0')), headers=headers)
        return url('/edit', offer=r['id'])
    if suffix == '/transition':
        offers.transition(one('offer_id'), int(one('expected_version')), one('action'), one('approval_reference'), headers=headers)
        return url('/review') if one('action') in {'approve', 'reject', 'changes'} else url()
    if suffix == '/studio-toggle':
        if one('enabled') not in {'yes', 'no'}:
            raise ValueError('Explicit Studio choice required')
        offers.studio_toggle(one('enabled') == 'yes', headers=headers)
        return url('/studio')
    parts = [one(k).rsplit(':', 1) for k in ('first', 'second')]
    if any(len(p) != 2 for p in parts):
        raise ValueError('Invalid component reference')
    r = offers.compose(parts, one('enterprise_slug'), headers=headers)
    return url('/edit', offer=r['id'])
