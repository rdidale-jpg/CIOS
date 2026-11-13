"""Native, progressively disclosed onboarding over existing commercial owners."""
from html import escape as e
from . import offer_library as library, offers
from .commercial_mission import resolve_commercial_mission


def playbook_details(row):
    """Original authored method, distinct from editable seller declarations."""
    body = '<details><summary>See the sales playbook</summary>'
    body += '<p>' + e(row['ideal_customer_profile']) + '</p><p><strong>Delivery & commercial model</strong> · ' + e(row['delivery_model'] + '. ' + row['commercial_model']) + '</p>'
    for key, label in (('structural_triggers', 'Structural conditions to validate'), ('event_triggers', 'Buying events to verify')):
        body += '<h3>' + label + '</h3><ul>'
        for p in row[key]:
            body += '<li><strong>' + e(p['condition']) + '</strong><p>' + e(p['observable']) + '</p><p>Alternative explanation: ' + e(p['rival_explanation']) + '</p><p>' + e(p['decay']) + '</p></li>'
        body += '</ul>'
    body += '<h3>Two ways to start</h3>'
    for p in row['entry_plays']:
        body += '<section><h4>' + e(p['name']) + '</h4><p>' + e(p['buyer'] + ' · ' + p['point_of_view']) + '</p><p>' + e(p['conversation']) + '</p><p>' + e(p['workshop_or_proof']) + '</p><p><strong>Test the fit</strong> · ' + e(p['disconfirming_question']) + '</p><p>Evidence needed: ' + e('; '.join(p['evidence_needed'])) + '</p><p>Stop if: ' + e('; '.join(p['stop_conditions'])) + '</p><p>' + e(p['follow_on']) + '</p></section>'
    body += '<h3>Differentiate with proof</h3><ul>' + ''.join('<li>' + e(t) + '</li>' for t in row['differentiation_to_validate']) + '</ul>'
    body += '<p>Seller proof required: ' + e('; '.join(row['seller_validation']['proof_required'])) + '</p><p>Constraints: ' + e('; '.join(row['constraints'])) + '</p><p>Do not claim: ' + e('; '.join(row['exclusions'])) + '</p>'
    return body + '</details>'


def register_sources(rows):
    from . import design_system as ds
    sources = {s['id']: s for row in rows for s in row['source_lineage']}
    refs = ''.join('<li><a href="' + e(s['url'], quote=True) + '">' + e(s['title']) + '</a> — ' + e(s['supports']) + '. Reviewed ' + e(s['reviewed_on']) + '.</li>' for s in sources.values())
    ds.source_note('<h2>Authored example offers</h2><p>Public categories inform vocabulary only. Playbooks are authored commercial methods, not company capabilities, account demand or seller proof. UK applicability, delivery rights and exclusions require review. No automatic Pipeline write or paid research runs.</p><ul>' + refs + '</ul>')


def onboarding(state, q, headers):
    from .offers_views import form, hidden, url, link
    employer = state['selected']
    if not employer:
        choices = ''.join('<option value="' + e(c['id']) + '">' + e(c['organisation']) + '</option>' for c in state['employers'])
        return ('<p>Choose the company you are authorised to represent.</p>' + form('/onboard-company', '<label>Employer<select name="employer_id">' + choices + '</select></label>', 'Continue') if choices else '<p>Your workspace owner needs to authorise an employer and an independent reviewer first.</p>' + link('/company', 'Company setup'))
    mission = resolve_commercial_mission(headers)
    selected = list(mission.technology_subindustries) if mission and mission.offer_library_employer_id == employer['id'] else []
    if selected:
        selected = library.categories(selected)
    data = library.catalogue()
    common = hidden('employer_id', employer['id']) + hidden('employer_version', employer['version']) + hidden('mission_version', mission.version if mission else 0)
    options = ('<option value="">Choose a category</option>' if not selected else '') + ''.join('<option value="' + e(c['id']) + '" ' + ('selected' if selected and selected[0] == c['id'] else '') + '>' + e(c['label']) + '</option>' for c in data['subindustries'])
    checks = ''.join('<label class="library-check"><input type="checkbox" name="additional" value="' + e(c['id']) + '" ' + ('checked' if c['id'] in selected[1:] else '') + '><span>' + e(c['label']) + '</span></label>' for c in data['subindustries'])
    category_form = form('/onboard-preferences', common + '<label>Primary technology category<select name="primary" required>' + options + '</select></label><details><summary>Also work in other categories?</summary>' + checks + '</details>', 'Find relevant offers')
    if not selected:
        return '<p class="eyebrow">1 · Your business</p><p>Choose what your company works on. You can select more than one category.</p>' + category_form
    body = '<p class="eyebrow">2 · Choose your starting points</p><p>Select examples to shape into your own offers. Add delivery proof before independent company review.</p><details><summary>Change business categories</summary>' + category_form + '</details>'
    body += '<form method="get" action="' + url('/start') + '"><label>Find an offer<input name="search" maxlength="120" value="' + e(q.get('search', ''), quote=True) + '" type="search"></label><button class="quiet" type="submit">Search</button></form>'
    rows = library.suggestions(selected, q.get('search', ''))
    register_sources(rows)
    cards = ''
    family_labels = {c['id']: c['label'] for c in data['subindustries']}
    for row in rows:
        token = row['id'] + ':' + str(row['version']) + ':' + library.fingerprint(row)
        cards += '<article class="offer-card"><p class="eyebrow">Example offer · ' + e(family_labels[row['family']]) + '</p><h2>' + e(row['name']) + '</h2><p>' + e(row['outcome']) + '</p><p class="muted">' + e(' · '.join(row['buyer_roles'][:2])) + '</p>' + playbook_details(row) + '<label class="library-check"><input type="checkbox" name="templates" value="' + e(token, quote=True) + '" aria-label="Add to my offers: ' + e(row['name'], quote=True) + '"><span>Add to my offers</span></label></article>'
    if cards:
        body += form('/onboard-adopt', common + '<div class="offer-grid">' + cards + '</div><label class="library-check"><input type="checkbox" name="confirmed" value="yes" required><span>I will validate these private examples against my company’s capabilities and rights.</span></label>', 'Create my private example offers')
    else:
        body += '<p>No developed playbook matches that search. Try a broader term or another business category.</p>'
    body += '<details><summary>Full library · 84 offer types, 24 developed playbooks</summary><p>Catalogue-only types are shown for coverage and cannot yet be adopted. Each developed playbook appears once, even when it spans categories.</p>'
    for category in data['subindustries']:
        body += '<h3>' + e(category['label']) + '</h3><ul>' + ''.join('<li>' + e(r['name']) + (' · developed' if r['stage'] == 'deep' else ' · catalogue only') + '</li>' for r in data['offers'] if r['family'] == category['id']) + '</ul>'
    return body + '</details>'


def submit(suffix, values, headers):
    from .offers_views import url
    schemas = {'/onboard-company': {'employer_id'}, '/onboard-preferences': {'employer_id', 'employer_version', 'mission_version', 'primary', 'additional'}, '/onboard-adopt': {'employer_id', 'employer_version', 'mission_version', 'templates', 'confirmed'}}
    if suffix not in schemas or set(values) - (schemas[suffix] | {'csrf'}):
        raise ValueError('Unsupported onboarding fields')
    multiple = {'additional'} if suffix == '/onboard-preferences' else ({'templates'} if suffix == '/onboard-adopt' else set())
    if any(not isinstance(v, list) or not 1 <= len(v) <= (12 if k in multiple else 1) or any(not isinstance(x, str) or len(x) > 240 for x in v) for k, v in values.items()):
        raise ValueError('Invalid or duplicate onboarding fields')
    def one(k):
        if k not in values: raise ValueError('Complete the onboarding selection')
        return values[k][0]
    if suffix == '/onboard-company':
        offers.select_employer(one('employer_id'), headers=headers)
        return url('/start')
    args = (one('employer_id'), int(one('employer_version')), int(one('mission_version')))
    if suffix == '/onboard-preferences':
        primary = one('primary')
        additional = values.get('additional', [])
        if len(set(additional)) != len(additional): raise ValueError('Duplicate business category')
        offers.configure_library([primary] + [v for v in additional if v != primary], *args, headers=headers)
        return url('/start')
    refs = []
    for token in values.get('templates', []):
        parts = token.split(':')
        if len(parts) != 3: raise ValueError('Invalid library reference')
        refs.append({'id': parts[0], 'version': int(parts[1]), 'digest': parts[2]})
    offers.adopt_library(refs, *args, confirmed=one('confirmed') == 'yes', headers=headers)
    return url()
