"""Read-only Lloyds executive perspectives over existing Source and presentation owners."""
from html import escape
import json
from urllib.parse import urlsplit

from . import intelligence_presentation as p, leadership_agenda, visual_streams as v
from .research_intelligence import model, source_import

STAGES = (
    ('Economics', 'LBG-A2030-CIR', 'landscape', 'economics'),
    ('Operations', 'LBG-AR25-MIGRATION', 'inside', 'technology-controls'),
    ('Technology', 'LBG-ENVOY-CONTROLS', 'inside', 'technology'),
    ('Pressure', 'UK-PRA-REPORT27', 'forces', ''),
    ('Strategy', 'LBG-A2030-PLATFORMS', 'forces', 'LBG-A2030-PLATFORMS'),
)
VIEWS = (
    ('anatomy', 'How Lloyds works', (
        ('Branches and customer access', ('LBG-BRAND26-TIMING',),
         'Moving the branch brand changes how customers find service. The announcement establishes a timetable. Branch hand-offs and realised customer outcomes remain open.'),
        ('Platforms and partners', ('LBG-AR25-MIGRATION', 'LBG-ENVOY-GOOGLE', 'LBG-A2030-DATA'),
         'Core and data dependencies sit behind customer delivery. The collaboration identifies a role in Envoy. Contract scope, renewal and estate-wide workshare remain unverified.'),
    )),
    ('swot', 'SWOT', (
        ('Strength · existing AI capability', ('LBG-ENVOY-CONTROLS', 'LBG-ENVOY-GOOGLE'),
         'An existing governed platform makes adoption and measured benefits the relevant questions. Built-in controls do not establish effectiveness.'),
        ('Weakness · migration exposure', ('LBG-AR25-MIGRATION', 'LBG-A2030-PLATFORMS'),
         'Application retirement and core renewal expose dependencies between migrations and live services. The remaining estate and its criticality are unquantified.'),
        ('Opportunity · payments', ('LBG-A2030-WALLET', 'LBG-Q326-CURVE', 'treasury-payments'),
         'Wallet and account-to-account payments could compete for repeat customer use. Acquisition completion provides no evidence of integration progress or customer adoption.'),
        ('Threat · operating disruption', ('UK-PRA-REPORT27', 'LBG-A2030-PLATFORMS'),
         'Migration disruption could affect service delivery while incident reporting requirements change. Evidence of readiness, entity scope and actual exposure remains limited.'),
    )),
    ('swot-more', 'SWOT themes', (
        ('Strength · deposit base', ('LBG-Q326-DEPOSITS', 'LBG-AR25-DEPOSITS'),
         'Group deposit balances provide a substantial funding base. The December 2025 and September 2026 stocks show scale at two dates. They do not identify organic flows, account mix or Retail funding costs.'),
        ('Weakness · benefit measurement', ('LBG-AI26-REPORTED', 'LBG-AI26-EXPECTED'),
         'A reported prior-year AI contribution and a higher management expectation put measurement discipline in focus. Validate net value and control performance before expanding. The figures do not allocate benefits to divisions.'),
        ('Opportunity · data-enabled service', ('LBG-A2030-DATA', 'LBG-ENVOY-CONTROLS'),
         'Existing controls and a stated data priority give the Group a basis to test improvements in customer service. Explore adoption and measurable service outcomes before scaling. The affected business units and realised gains remain unverified.'),
        ('Threat · cost of parallel running', ('LBG-AR25-MIGRATION', 'LBG-A2030-CIR', 'UK-PRA-REPORT27'),
         'Keeping old and new systems running may put pressure on the Group efficiency ambition. Service-led waves offer one response, with a trade-off between migration pace and continuity. No Lloyds-specific overrun or service disruption is established.'),
    )),
    ('risk', 'Risks & pressures', (
        ('Time-bound pressure · incident reporting', ('UK-PRA-REPORT27', 'UK-FCA-REPORT27'),
         'Regulatory implementation gives this pressure a date. Lloyds-specific preparedness, service impact and remediation cost remain unverified.'),
        ('Execution risk · service continuity', ('LBG-AR25-MIGRATION', 'LBG-A2030-CIR'),
         'If parallel running continues longer than planned, costs and customer disruption could delay efficiency gains. Phased migration and service testing could limit the impact.'),
        ('Capability risk · AI controls', ('LBG-ENVOY-CONTROLS',),
         'Controls and monitoring are described by management. Effectiveness, coverage and model assurance results remain open.'),
    )),
    ('competition', 'Competition & AI', (
        ('Payments · policy and strategy', ('LBG-A2030-WALLET', 'treasury-payments'),
         'An account-to-account option could change which provider owns the payment interaction. The policy describes a pilot and establishes neither launch nor adoption.'),
        ('AI · operating scenario', ('LBG-ENVOY-CONTROLS', 'LBG-A2030-DATA'),
         'A future payment assistant could shift discovery toward an intermediary. Adoption would require consent, customer trust and workable protection. No entrant launch is established here.'),
    )),
    ('timeline', 'Strategy timeline', (
        ('2025 reporting · 2026 priorities', ('LBG-AR25-MIGRATION',), ''),
        ('Q3 2026 · transaction and investment context', ('LBG-Q326-CURVE', 'LBG-Q326-INVESTMENT'), ''),
        ('March 2027 · reporting policy', ('UK-PRA-REPORT27',), ''),
        ('2027–2030 · management plans', ('LBG-A2030-PLATFORMS', 'LBG-A2030-INVESTMENT', 'LBG-A2030-CIR'), ''),
    )),
    ('options', 'Strategic options', (
        ('Retire platforms in service-led waves', ('LBG-AR25-MIGRATION', 'UK-PRA-REPORT27', 'LBG-A2030-CIR'),
         'Sequence cutovers around continuity and evidence of recovery. Smaller waves may lengthen dual running and delay savings.'),
        ('Scale AI only after benefit and control tests', ('LBG-ENVOY-CONTROLS', 'LBG-AI26-REPORTED', 'LBG-AI26-EXPECTED'),
         'Validate net value and control performance before expanding deployment. Additional gates can slow learning where risk is already low.'),
    )),
)
def _payments():
    """The one reviewed OGL historical policy extract, subject to live Source checks."""
    path = model.REPO / 'docs/flora-runtime/lloyds-flagship/Payments-Source.json'
    try:
        data = json.loads(path.read_text())
        url = 'https://www.gov.uk/government/publications/national-payments-vision/national-payments-vision'
        if (data['id'] != 'LLF-HMT-PAYMENTS' or data['url'] != url
                or data['retrieval_url'] != url or data['publisher'] != 'HM Treasury'
                or source_import.working_restricted(data) or data.get('restrictions')
                or data['rights']['status'] != 'permitted_ogl_factual_extract'):
            return None
        model.primary_text(data)
        ref = p.Source(data['title'], url, data['publisher'], data['publication_date'],
                       locator=data['excerpts'][0]['locator'])
        return p.Statement('HM Treasury’s 2024 payments policy identified lower-risk billing uses for the first variable recurring payments pilot.',
                           'reported', 'UK payment policy', data['reporting_period'], (ref,),
                           'reviewed_excerpt', 'candidate_intelligence')
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        return None


def _facts(data):
    ids = {key for _, key, _, _ in STAGES}
    ids.update(key for _, _, rows in VIEWS for _, keys, _ in rows for key in keys)
    facts = {}
    source_by_id = {row['id']: row for row in data['sources']}
    supplier_spot = {'id': 'technology'}
    if not v.detail_claims(v.Context('lloyds', 'landscape'), supplier_spot, data):
        ids.discard('LBG-ENVOY-GOOGLE')
    for claim in data['claims']:
        key = claim['id']
        if key not in ids:
            continue
        try:
            if (not source_import.working_restricted(claim)
                    and all(not source_import.working_restricted(source_by_id[sid])
                            for sid in claim['source_ids'])
                    and model.primary_claim_supported(data, claim)):
                item = p.claim_view(data, claim)
                if item:
                    facts[key] = item
        except (OSError, ValueError, KeyError, TypeError):
            continue
    payment = _payments()
    if payment and p.eligible(payment):
        facts['treasury-payments'] = payment
    return facts


def _source_rows(items):
    items = tuple(items)
    p.note_editorial_sources(s for item in items for s in item.sources)
    rows = []
    for item in items:
        citations = []
        for source in item.sources:
            url = source.url
            if (urlsplit(url).hostname or '').endswith(('lloydsbankinggroup.com', 'lloydsbank.com')):
                url = 'https://www.lloydsbankinggroup.com/'
            citations.append(f'<a href="{escape(url, quote=True)}" rel="noreferrer">{escape(source.title)}</a>'
                             + (' · ' + escape(source.publisher) if source.publisher else '')
                             + (' · Published ' + escape(source.published) if source.published else '')
                             + (' · ' + escape(source.locator) if source.locator else ''))
        state = {'commitment': 'Stated priority or plan', 'target': 'Management target',
                 'expectation': 'Management expectation'}.get(item.measurement_state, 'Attributed disclosure')
        rows.append('<li><strong>' + escape(state) + '</strong> · ' + escape(item.text)
                    + ' <small>' + escape(item.period + ' · ' + item.scope) + '</small> · '
                    + '; '.join(citations)
                    + '<p class="ltv-note">' + escape(item.verification.replace('_', ' ').capitalize())
                    + ' · ' + escape(item.canonical_status.replace('_', ' ')) + '</p>'
                    + ''.join('<p>' + escape(text) + '</p>' for text in (*item.caveats, *item.material_caveats,
                                                                         *item.counter_evidence))
                    + '</li>')
    return '<ul>' + ''.join(rows) + '</ul>'


def reviewed_change(ctx, data):
    """Reuse the existing public flagship timeline disclosure and its Source checks."""
    if data.get('enterprise_twin_id') != 'BK-ENT-001' or p.restricted_metadata(data):
        return ''
    item = _facts(data).get('LBG-Q326-CURVE')
    if item is None or not p.eligible(item):
        return ''
    publication = next((source.published for source in item.sources if source.published), '')
    return ('<p><strong>Curve acquisition reported complete</strong></p>'
            + ('<p class="change-period">Published ' + escape(publication) + ' · ' + escape(item.period) + '</p>'
               if publication else '<p class="change-period">' + escape(item.period) + '</p>')
            + '<p>Integration scope and external procurement remain unproven.</p>'
            + '<a href="' + escape(v.url(ctx, detail='flagship', reading=ctx.reading), quote=True)
            + '#llf-timeline">Explore the timeline</a>')


def _benchmark(data, issues, inspect):
    service = next((issue for issue in issues if issue.key == 'service-recovery'), None)
    peers = [leadership_agenda.bank_service_issue(key, data) for key in ('natwest', 'hsbc-uk')]
    units = {'complaints received; all-product total', 'complaints received; FCA Open table total'}
    items = [next((f for f in row.facts if f.unit in units and p.eligible(f)
                   and f.value is not None and f.sources[0].url ==
                   'https://www.fca.org.uk/data/firm-level-complaints-data-sortable-table'), None)
             for row in (service, *peers) if row]
    items = [item for item in items if item is not None and item.period == '1 January–30 June 2026']
    if len(items) < 2 or not service or items[0] not in service.facts:
        return '<p>Eligible matched-period Lloyds and peer activity figures are unavailable.</p>'
    largest = max(item.value for item in items)
    bars = ''.join('<div><dt>' + escape(item.scope.split(';')[0]) + '</dt><dd>'
                   + format(item.value, ',') + '<meter min="0" max="' + str(largest or 1)
                   + '" value="' + str(item.value) + '" aria-label="Complaints received"></meter></dd></div>'
                   for item in items)
    return ('<p>Complaints received · January–June 2026 · all products</p>'
            '<p class="ltv-note">Counts cover distinct legal entities. Customer and product denominators differ, '
            'so the bars show activity volume only and cannot rank service quality.</p>'
            '<dl class="llf-bars">' + bars + '</dl>' + inspect('Peer evidence', items))


def render(ctx, data, issues, *, inspection=False):
    if data.get('enterprise_twin_id') != 'BK-ENT-001' or p.restricted_metadata(data):
        return ''
    facts = _facts(data)
    # One executive composition; reading parameters are retained only as old URLs.
    insight = True
    overview = ('Core renewal and application retirement matter to the cost base. Service continuity and control testing '
                'shape the pace at which savings could be realised. These disclosures establish management direction and '
                'sector pressure. They do not establish project-level savings, delivery accountability or a causal outcome.'
                if insight and all(key in facts for _, key, _, _ in STAGES) else
                'Explore Lloyds’ disclosures on efficiency, platform renewal, existing technology controls and regulatory timing.')
    from .lloyds_twin_visual import INTERACTIONS, opening, choices

    packets = []

    def inspect(title, items, *, content=None):
        if inspection:
            packets.append(f'<section><h2>{escape(title)}</h2>'
                           + (content if content is not None else _source_rows(items)) + '</section>')
        else:
            p.note_editorial_sources(source for item in items for source in item.sources)
        return ''

    body = ('<section class="llf" aria-label="Lloyds flagship overview">'
            + opening(ctx, facts, STAGES, inspect, overview)
            + '<section aria-labelledby="ltv-perspectives"><h2 id="ltv-perspectives">Perspectives</h2>')
    perspectives = []
    for key, title, rows in VIEWS:
        if key == 'swot-more':
            continue
        if key == 'swot':
            rows = (*rows, *next(rows for k, _, rows in VIEWS if k == 'swot-more'))
        cards = []
        for index, (label, dependencies, analysis) in enumerate(rows):
            if not all(ref in facts for ref in dependencies) or (key == 'options' and not insight):
                continue
            items = tuple(facts[ref] for ref in dependencies)
            detail = ''.join(p.render(item, compact=True) for item in items)
            if analysis:
                detail += '<p data-semantic-type="insight"><strong>FLORA Insight</strong> · ' + escape(analysis) + '</p>'
            cards.append((f'{key}-{index}', label, detail + inspect(label, items)))
        if key == 'swot':
            quadrants = []
            for quadrant in ('Strength', 'Weakness', 'Opportunity', 'Threat'):
                themes = [(ident, text.split(' · ', 1)[1], detail) for ident, text, detail in cards
                          if text.startswith(quadrant + ' · ')]
                if themes:
                    quadrants.append(('quadrant-' + quadrant.lower(), quadrant,
                                      choices(quadrant + ' themes', themes, 'themes')))
            content = ('<p class="ltv-note">Opportunities describe market or strategic choices for Lloyds.</p>'
                       + choices('SWOT quadrants', quadrants, 'swot'))
        else:
            content = choices('Findings', cards, key)
        if not cards:
            content = ('<p>Switch to FLORA Insight to compare possible responses.</p>'
                       if key == 'options' and not insight else '<p>Eligible evidence is unavailable for this perspective.</p>')
        if key == 'competition':
            controls = facts.get('LBG-ENVOY-CONTROLS')
            known = ('<div class="ltv-band"><strong>Company-disclosed development</strong>'
                     + p.render(controls, compact=True) + inspect('Envoy controls', (controls,)) + '</div>'
                     if controls else '')
            content = (known + content
                       + '<p class="ltv-note">The policy pilot and a future payment assistant have different evidence. '
                         'A named AI-native entrant launch is unverified.</p>')
        perspectives.append((key, title, content))
    perspectives.append(('benchmark', 'Peer evidence · service operations', _benchmark(data, issues, inspect)))
    body += choices('Perspectives', perspectives, 'perspectives') + '</section>'
    if inspection:
        if 'treasury-payments' in facts:
            packets.append('<p>Payments policy excerpt contains HM Treasury information licensed under the Open Government Licence v3.0.</p>')
        href = escape(v.url(ctx), quote=True)
        return ('<h1>Lloyds flagship research inspection</h1>'
                f'<p><a href="{href}">Return to the executive view</a></p>' + ''.join(packets))
    return body + INTERACTIONS + '</section>'
