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
STYLE = """<style>
.llf {margin-block: 1.5rem 2.5rem; color:#12362e}
.llf-header {background:#133a32;color:#f7f3e8;border-radius:1rem;padding:clamp(1rem,3vw,2rem)}
.llf-header h1 {color:inherit;margin:.25rem 0 .65rem}
.llf-header .eyebrow {color:#d2e1d0}
.llf-path {display:flex;gap:.65rem;flex-wrap:wrap;margin:1rem 0}
.llf-path a {padding:.45rem .65rem;border:1px solid #9fb9a7;border-radius:.45rem}
.llf-path a {flex:1 1 7rem;color:#14382d;background:#e8efe2}
.llf details {border:1px solid #b6c8ba;border-radius:.6rem;margin:.6rem 0;padding:.65rem .8rem}
.llf details summary {cursor:pointer;font-weight:650}
.llf dl {display:grid;grid-template-columns:repeat(auto-fit,minmax(12rem,1fr));gap:.6rem}
.llf h3 {margin-bottom:.35rem}
</style>"""


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


def _basis(items):
    items = tuple(items)
    p.note_editorial_sources(s for item in items for s in item.sources)
    rows = []
    for item in items:
        citations = []
        for source in item.sources:
            url = source.url
            if (urlsplit(url).hostname or '').endswith(('lloydsbankinggroup.com', 'lloydsbank.com')):
                url = 'https://www.lloydsbankinggroup.com/'
            citations.append(f'<a href="{escape(url, quote=True)}" rel="noreferrer">{escape(source.title)}</a>')
        state = {'commitment': 'Stated priority or plan', 'target': 'Management target',
                 'expectation': 'Management expectation'}.get(item.measurement_state, 'Attributed disclosure')
        rows.append('<li><strong>' + escape(state) + '</strong> · ' + escape(item.text)
                    + ' <small>' + escape(item.period + ' · ' + item.scope) + '</small> · '
                    + ', '.join(citations) + '</li>')
    return '<details class="llf-basis"><summary>Evidence &amp; scope</summary><ul>' + ''.join(rows) + '</ul></details>'


def _benchmark(data, issues):
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
    return ('<p>FCA complaints received, all products, January–June 2026. Each figure covers one reporting legal entity. '
            'Customer and product denominators differ, so these volumes cannot rank service quality or benchmark Group economics.</p>'
            '<dl>' + ''.join('<div><dt>' + escape(item.scope.split(';')[0]) + '</dt><dd>'
                             + format(item.value, ',') + '</dd></div>' for item in items)
            + '</dl>' + _basis(items))


def render(ctx, data, issues):
    if data.get('enterprise_twin_id') != 'BK-ENT-001' or p.restricted_metadata(data):
        return ''
    facts = _facts(data)
    insight = ctx.reading == 'insight'
    stages = ''.join('<a href="' + escape(v.url(ctx, stream=stream, detail=detail, reading=ctx.reading), quote=True)
                     + '#visual-content">' + escape(label) + '</a>'
                     for label, key, stream, detail in STAGES if key in facts)
    core = tuple(facts[key] for _, key, _, _ in STAGES if key in facts)
    overview = ('Core renewal and application retirement matter to the cost base. Service continuity and control testing '
                'shape the pace at which savings could be realised. These disclosures establish management direction and '
                'sector pressure. They do not establish project-level savings, delivery accountability or a causal outcome.'
                if insight and len(core) == len(STAGES) else
                'Explore Lloyds’ disclosures on efficiency, platform renewal, existing technology controls and regulatory timing.')
    body = (STYLE + '<section class="llf" aria-label="Lloyds flagship overview">'
            '<div class="llf-header"><p class="eyebrow">Lloyds Banking Group · Flagship prototype</p>'
            '<h1>Renew the bank while it runs</h1><p>' + escape(overview) + '</p></div>'
            '<nav class="llf-path" aria-label="Follow the strategic issue">' + stages + '</nav>'
            + (_basis(core) if core else '')
            + '<h2>Explore the enterprise</h2>')
    for key, title, rows in VIEWS:
        body += f'<details id="llf-{key}"' + (' open' if key == 'swot' and insight else '') + '><summary>' + escape(title) + '</summary>'
        count = 0
        for label, dependencies, analysis in rows:
            if not all(ref in facts for ref in dependencies) or (key == 'options' and not insight):
                continue
            count += 1
            body += '<section><h3>' + escape(label) + '</h3>'
            if insight and analysis:
                body += '<p><strong>FLORA Insight</strong> · ' + escape(analysis) + '</p>'
            else:
                body += ''.join(p.render(facts[ref], compact=True) for ref in dependencies)
            body += _basis(facts[ref] for ref in dependencies) + '</section>'
        if not count:
            body += ('<p>Switch to FLORA Insight to compare possible responses.</p>'
                     if key == 'options' and not insight else '<p>Eligible evidence is unavailable for this perspective.</p>')
        body += '</details>'
    body += ('<details id="llf-benchmark"><summary>Peer evidence · service operations</summary>'
             + _benchmark(data, issues) + '</details>')
    if 'treasury-payments' in facts:
        body += '<p><small>Payments policy excerpt contains HM Treasury information licensed under the Open Government Licence v3.0.</small></p>'
    return body + '</section>'
