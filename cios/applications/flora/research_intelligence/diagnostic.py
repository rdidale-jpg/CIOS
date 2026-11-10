"""Read-only research evidence diagnostics for registered public assessment overlays.

This is a coverage and evidence inventory, NOT the IT-001 maturity decision.
No canonical Twin, governed Evidence, Pipeline or workspace records are read or mutated.
"""
from __future__ import annotations

from collections import Counter
from html import escape


def assess(data):
    """Derive reproducible inventory indicators from an already validated overlay."""
    sources = data['sources']
    claims = data['claims']
    relationships = data['relationships']
    gaps = data['gaps']
    source_ids = {source['id'] for source in sources}
    claims_by_id = {claim['id']: claim for claim in claims}
    verification = Counter(source['verification'] for source in sources)
    supported = [claim for claim in claims if claim['verification'] == 'source_supported']
    unverified = [claim for claim in claims if claim['verification'] != 'source_supported']
    invalid_refs = [claim['id'] for claim in claims if not set(claim['source_ids']) <= source_ids]
    verified_edges = [edge for edge in relationships if edge.get('verified') is True]
    interpretive_edges = [edge for edge in relationships if edge.get('verified') is not True]
    active_gaps = [gap for gap in gaps if gap.get('status') not in ('resolved', 'closed')]
    priority = {'High': 0, 'Medium': 1, 'Low': 2}
    active_gaps.sort(key=lambda gap: (priority.get(gap.get('priority'), 3), gap['id']))
    high = [gap for gap in active_gaps if gap.get('priority') == 'High']
    programme_unknowns = {
        key: sum(str(row.get(key, '')).strip().lower() in ('', 'unknown', 'not known')
                 for row in data['programmes'])
        for key in ('owner', 'funding', 'procurement')
    }
    return {
        'authority': 'candidate_intelligence',
        'maturity': 'Not assessed against the full IT-001 / Intelligence Density Matrix',
        'enterprise': data['enterprise_name'],
        'industry': data['industry_name'],
        'assessed_at': data['assessed_at'],
        'effective_at': data['upstream_research_effective_date'],
        'source_count': len(sources),
        'source_verification': dict(sorted(verification.items())),
        'claim_count': len(claims),
        'supported_claim_count': len(supported),
        'unverified_claim_count': len(unverified),
        'invalid_source_refs': invalid_refs,
        'claim_domains': dict(sorted(Counter(c.get('domain', 'unspecified') for c in claims).items())),
        'relationship_count': len(relationships),
        'verified_relationship_count': len(verified_edges),
        'interpretive_relationship_count': len(interpretive_edges),
        'programme_count': len(data['programmes']),
        'programme_unknowns': programme_unknowns,
        'candidate_count': len(data['candidates']),
        'active_gaps': active_gaps,
        'high_priority_gap_count': len(high),
        'gap_ids_linked_to_candidates': sorted({
            identifier for candidate in data['candidates']
            for identifier in candidate.get('gap_ids', ())
        }),
        'orphan_claim_count': sum(
            not any(c['id'] in row.get('claim_ids', ()) for group in
                    ('relationships', 'frameworks', 'programmes', 'candidates')
                    for row in data[group])
            for c in claims
        ),
    }


def render(data):
    """Accessible HTML fragment only; caller owns the existing page shell."""
    x = assess(data)
    esc = lambda value: escape(str(value), quote=True)
    def stat(label, value):
        return (f"<article class='ux-card'><h3>{esc(label)}</h3>"
                f"<p><strong>{esc(value)}</strong></p></article>")
    cards = ''.join((
        stat('Primary-supported claims', f"{x['supported_claim_count']} / {x['claim_count']}"),
        stat('Source records', x['source_count']),
        stat('Verified graph relationships', f"{x['verified_relationship_count']} / {x['relationship_count']}"),
        stat('Open / partly resolved gaps', len(x['active_gaps'])),
        stat('High-priority gaps', x['high_priority_gap_count']),
        stat('Programme owner / funding / procurement unknowns',
             ' / '.join(str(v) for v in x['programme_unknowns'].values())),
    ))
    domains = ''.join(
        f"<li>{esc(key)}: {esc(value)} claims</li>" for key, value in x['claim_domains'].items()
    )
    verification = ''.join(
        f"<li>{esc(key)}: {esc(value)} source records</li>"
        for key, value in x['source_verification'].items()
    )
    gaps = ''.join(
        "<article class='ux-claim'>"
        f"<h3>{esc(gap['title'])} — {esc(gap.get('priority', 'Unrated'))}</h3>"
        f"<p>Status: {esc(gap.get('status', 'unknown'))}</p>"
        f"<p>Decision impact: {esc(gap.get('decision_impact', 'Not supplied'))}</p>"
        f"<p>Evidence needed: {esc(gap.get('required_evidence', 'Not supplied'))}</p>"
        f"<p>Research owner: {esc(gap.get('owner_role', 'Unassigned'))}</p>"
        "</article>"
        for gap in x['active_gaps']
    ) or '<p>No open gaps recorded; this does not establish completeness.</p>'
    return (
        "<section aria-label='Research Intelligence Diagnostic'>"
        "<h2>Research Intelligence Diagnostic</h2>"
        "<p class='ux-disclosure'>Read-only research inventory, not an IT-001 maturity score, "
        "independent human assurance or authorised commercial qualification. "
        "A claim count does not demonstrate corroboration or decision-grade understanding.</p>"
        f"<p>Assessment snapshot: {esc(x['assessed_at'])} · "
        f"Upstream research effective: {esc(x['effective_at'])} · "
        f"Authority: {esc(x['authority'])}</p>"
        f"<div class='ux-grid'>{cards}</div>"
        f"<details><summary>Evidence provenance inventory</summary><ul>{verification}</ul>"
        f"<p>Claims requiring further verification: {esc(x['unverified_claim_count'])}. "
        f"Relationship edges not verified: {esc(x['interpretive_relationship_count'])}. "
        f"Claims without an overlay relationship/framework/programme/candidate reference: "
        f"{esc(x['orphan_claim_count'])}.</p></details>"
        f"<details><summary>Research topics represented (not completeness grades)</summary>"
        f"<ul>{domains}</ul><p>Missing topics cannot be inferred from claim counts alone. "
        "Full domain-by-domain maturity review is still required.</p></details>"
        f"<h2>Prioritised research backlog</h2>{gaps}"
        "<p class='ux-disclosure'>The backlog records evidence requests, not presumed "
        "customer buying intent or qualified sales opportunities.</p>"
        "</section>"
    )
