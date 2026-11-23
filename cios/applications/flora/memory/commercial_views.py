"""Perspective sections for the existing isolated factual workspace replay."""
from html import escape
from collections import defaultdict
from decimal import Decimal

from ..blueprint_import.mapping import evidence_is_current
from ..research_intelligence.commercial_factory import PERSPECTIVES
from .repository import EnterpriseModelRepository, EvidenceRepository, ObservationRepository


def _change_card(row, observation):
    change = row['commercial_change']
    return (
        '<aside class="card" aria-label="Recent enterprise change" data-commercial-change>'
        f'<p><small>{escape(row["period"])} · {escape(change["confidence"])}</small></p>'
        f'<h2>{escape(change["headline"])}</h2>'
        f'<p>{escape(change["meaning"])}</p>'
        f'<p><strong>Investigate</strong> · {escape(change["next_question"])}</p>'
        '<details><summary>What supports this?</summary>'
        f'<p>{escape(observation.atomic_statement)}</p>'
        f'<p>{escape(change["relationship"])} · {escape(row["publisher"])}</p>'
        f'<p>{escape(row["caveat"])}</p></details></aside>'
    )


def replay_sections(enterprise, workspace, *, perspective=None, insight=False, native=False):
    """Render accepted memory for an explicitly scoped isolated preview."""
    model = EnterpriseModelRepository().get(enterprise)
    observations = {o.observation_id: o for o in ObservationRepository().list()
                    if o.enterprise_id == enterprise and o.lifecycle_state in {'accepted', 'Validated'}
                    and not o.retired_at}
    evidence = {e['evidence_id']: e for e in EvidenceRepository().list()
                if e.get('enterprise_id') == enterprise
                and e.get('governed_source_scope', {}).get('workspace_id') == workspace
                and e.get('use_scope') == 'isolated_commercial_replay'
                and not e.get('withdrawn') and e.get('status') not in {'withdrawn', 'restricted'}
                and evidence_is_current(e)}
    cards = {p: [] for p in PERSPECTIVES}
    analyses = []
    metrics = defaultdict(list)
    for attribute in model.attributes.values():
        if attribute.contradiction_state != 'none':
            continue
        for observation_id in attribute.observation_ids:
            observation = observations.get(observation_id)
            if not observation or observation.observation_date != attribute.last_observed_date:
                continue
            for ref in observation.supporting_evidence_ids:
                row = evidence.get(ref)
                if (not row or row.get('statement') != observation.atomic_statement
                        or row.get('affected_attribute') != observation.affected_attribute
                        or row.get('perspective') not in cards):
                    continue
                change = row.get('commercial_change')
                if native or change:
                    required = ('headline', 'meaning', 'next_question', 'relationship', 'confidence')
                    if (native and isinstance(change, dict)
                            and all(isinstance(change.get(key), str) and change[key] for key in required)):
                        cards[row['perspective']].append(_change_card(row, observation))
                    continue
                metric = row.get('metric')
                if metric and metric.get('group') == 'revenue_mix' and metric.get('unit') == 'USD million':
                    metrics[row['reporting_scope'], row['period'], row['source_content_sha256']].append(metric)
                cards[row['perspective']].append(
                    f"<article class='card'><h3>{escape(row['family'])}</h3>"
                    f"<p>{escape(observation.atomic_statement)}</p>"
                    f"<p>{escape(row['period'])} · {escape(row['reporting_scope'])}</p>"
                    f"<details><summary>Source and limits</summary>"
                    f"<p>{escape(row['publisher'])} · {escape(row['source_locator'])}</p>"
                    f"<p>{escape(row['caveat'])}</p></details></article>")
    for (scope, period, _), items in metrics.items():
        if len(items) != 2 or {m['axis'] for m in items} != {'licensing', 'royalties'}:
            continue
        amounts = {m['axis']: m['amount'] for m in items}
        if not all(type(amount) is int and amount > 0 for amount in amounts.values()):
            continue
        share = Decimal(amounts['licensing']) * 100 / sum(amounts.values())
        analyses.append(
            f"<article class='card'><h3>Enterprise Economics · Partial</h3>"
            f"<p>Licensing and other revenue was {share:.1f}% of the sum of these reported licensing-and-other and royalty amounts.</p>"
            f"<p>{escape(scope)} · {escape(period)}. Same USD-million reporting basis. "
            "This mix does not establish margin or future revenue.</p></article>")
    if native:
        return ''.join(cards[perspective])
    if perspective is not None:
        items = analyses if insight and perspective == 'landscape' else (
            [] if insight else cards[perspective])
        if not items:
            return ''
        return (f'<section class="card" data-factory-perspective="{perspective}">'
                '<h2>Governed evidence · isolated preview</h2>' + ''.join(items) + '</section>')
    cards['landscape'].extend(analyses)
    nav = ''.join(f'<a href="#factory-{p}">{p.title()}</a> ' for p in PERSPECTIVES)
    return '<nav aria-label="Isolated evidence perspectives">' + nav + '</nav>' + ''.join(
        f'<section id="factory-{p}"><h2>{p.title()}</h2>'
        + (''.join(cards[p]) or '<p>No current scoped evidence in this replay.</p>') + '</section>'
        for p in PERSPECTIVES)


def route_replay(html, path, query, headers):
    """Opt-in non-production proof on existing routes with existing Canvas access."""
    import os
    import re
    from ..access import active_workspace_membership
    from ..enterprise_canvas.access import EnterpriseCanvasAccessRepository, can_access_canvas_record

    if (os.getenv('FLORA_ENVIRONMENT') != 'development'
            or os.getenv('FLORA_FACTORY_ROUTE_REPLAY') != '1'):
        return html
    route_bindings = {
        '/enterprises/lloyds': 'lloyds',
        '/enterprises/easyjet/preview': 'easyjet',
        '/enterprises/easyjet': 'easyjet',
        '/digital-twins/bt-group-plc/canvas': 'bt-group-plc',
    }
    binding = route_bindings.get(path)
    technology = path == '/industries/technology/experience/enterprise'
    if technology and query.get('enterprise') == ['arm']:
        binding = 'arm'
    if not binding or 'lens' in query or 'analysis' in query:
        return html
    membership = active_workspace_membership(headers)
    if not membership:
        return html
    matches = [record for record in EnterpriseCanvasAccessRepository().list()
               if binding in {record.enterprise_id, record.canvas_id}
               and record.workspace_id == membership.workspace_id]
    if len(matches) != 1:
        return html
    record = matches[0]
    if not can_access_canvas_record(headers, record.enterprise_id, record.workspace_id):
        return html
    selected = query.get('stream', ['landscape'])
    if len(selected) != 1 or selected[0] not in PERSPECTIVES:
        return html
    reading = query.get('reading', ['facts'])
    if reading not in (['facts'], ['insight']):
        return html
    # Insert the small change into the existing main reading surface. Keep the
    # legacy isolated projection for records without reviewed commercial copy.
    has_specialist_selection = any(key in query for key in ('detail', 'agenda', 'selected'))
    if not has_specialist_selection:
        current = replay_sections(record.enterprise_id, record.workspace_id,
                                  perspective=selected[0], native=True)
        if current:
            # Place the change alongside each destination's existing context,
            # after its controls or heading rather than below the page.
            if technology:
                anchor = r'<p class="commercial-perspective">[^<]*</p>'
            elif binding == 'bt-group-plc':
                anchor = r'</h1>'
            else:
                anchor = r'<nav class="reading-mode"[^>]*>.*?</nav>'
            html = re.sub(anchor, lambda match: match[0] + current, html, count=1, flags=re.S)
    sections = replay_sections(record.enterprise_id, record.workspace_id,
                               perspective=selected[0], insight=reading == ['insight'])
    if technology and reading == ['facts']:
        sections = ''.join(replay_sections(record.enterprise_id, record.workspace_id, perspective=stream)
                           for stream in PERSPECTIVES)
    if not sections:
        return html
    # Keep the existing route, shell, artwork and selectors. Existing specialist
    # routes are untouched. The renderer owns the appended scoped section.
    return re.sub(r'</main\s*>', lambda match: sections + match[0], html, count=1, flags=re.I)
