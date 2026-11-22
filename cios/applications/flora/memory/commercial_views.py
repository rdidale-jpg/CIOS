"""Perspective sections for the existing isolated factual workspace replay."""
from html import escape
from collections import defaultdict
from decimal import Decimal

from ..blueprint_import.mapping import evidence_is_current
from ..research_intelligence.commercial_factory import PERSPECTIVES
from .repository import EnterpriseModelRepository, EvidenceRepository, ObservationRepository


def replay_sections(enterprise, workspace):
    """Render an explicitly scoped isolated replay. No public route calls this."""
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
    cards = {perspective: [] for perspective in PERSPECTIVES}
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
        cards['landscape'].append(
            f"<article class='card'><h3>Enterprise Economics · Partial</h3>"
            f"<p>Licensing was {share:.1f}% of the sum of these reported licensing and royalty amounts.</p>"
            f"<p>{escape(scope)} · {escape(period)}. Same USD-million reporting basis. "
            "This mix does not establish margin or future revenue.</p></article>")
    nav = ''.join(f'<a href="#factory-{p}">{p.title()}</a> ' for p in PERSPECTIVES)
    return '<nav aria-label="Isolated evidence perspectives">' + nav + '</nav>' + ''.join(
        f'<section id="factory-{p}"><h2>{p.title()}</h2>'
        + (''.join(cards[p]) or '<p>No current scoped evidence in this replay.</p>') + '</section>'
        for p in PERSPECTIVES)
