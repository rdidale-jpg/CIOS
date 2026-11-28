"""Offline primary-source import proposals; no network, authority or store writes."""
from datetime import date, datetime
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit

PUBLISHERS = {'www.lloydsbankinggroup.com', 'www.lloydsbank.com',
              'www.bankofengland.co.uk', 'www.fca.org.uk', 'www.gov.uk',
              'www.easyjet.com', 'corporate.easyjet.com', 's203.q4cdn.com',
              'www.iata.org', 'www.caa.co.uk', 'www.easa.europa.eu', 'www.eurocontrol.int',
              'bills.parliament.uk', 'www.cert.cyber.gouv.fr', 'www.esma.europa.eu',
              'portail-rse.beta.gouv.fr', 'find-and-update.company-information.service.gov.uk',
              'www.legifrance.gouv.fr'}
LIMIT = 16 * 1024 * 1024


def sha(content):
    return hashlib.sha256(content).hexdigest()


def official_url(value):
    target = urlsplit(value)
    if (target.scheme != 'https' or not (target.hostname in PUBLISHERS or (target.hostname == 'www.nationwide.co.uk' and (re.fullmatch(r'/-/assets/nationwidecouk/documents/about/how-we-are-run/results-and-accounts/[0-9-]+/[0-9]{4}-preliminary-results\.pdf', target.path)
                 or target.path == '/-/assets/nationwidecouk/documents/about/how-we-are-run/results-and-accounts/2025-2026/annual-report-and-accounts-2026.pdf') and not target.query))
            or target.username or target.password or target.port not in (None, 443)
            or target.fragment):
        raise ValueError('Expected an approved official-publisher HTTPS document URL')
    return value


def provenance(metadata, url_validator=official_url):
    url_validator(metadata['url'])
    url_validator(metadata['retrieval_url'])
    retrieved = datetime.fromisoformat(metadata['retrieved_at'].replace('Z', '+00:00'))
    if retrieved.tzinfo is None or retrieved.date() > date.today():
        raise ValueError('Timezone-aware, non-future retrieval date required')
    if not metadata.get('title') or not metadata.get('publisher') or not metadata.get('reporting_period'):
        raise ValueError('Document title, publisher and reporting period required')
    published = metadata.get('publication_date')
    if published and (date.fromisoformat(published) > retrieved.date() or not metadata.get('publication_date_evidence')):
        raise ValueError('Publication date needs evidence and cannot follow retrieval')
    if not metadata.get('reviewed_by') or not metadata.get('review_notes'):
        raise ValueError('Explicit provenance review and limitations required')


class _HTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.hidden = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}: self.hidden += 1
    def handle_endtag(self, tag):
        if tag in {'script', 'style'}: self.hidden = max(0, self.hidden - 1)
    def handle_data(self, text):
        if not self.hidden and text.strip(): self.parts.append(text.strip())


def extract(raw, suffix):
    if len(raw) > LIMIT or not raw:
        raise ValueError('Empty or oversized source file')
    if suffix == '.pdf':
        if not raw.startswith(b'%PDF'): raise ValueError('Invalid PDF signature')
        import fitz
        with fitz.open(stream=raw, filetype='pdf') as document:
            text = '\n'.join(f'[PDF page {i+1}]\n{page.get_text()}' for i, page in enumerate(document))
    elif suffix in {'.html', '.htm', '.txt'}:
        text = raw.decode('utf-8-sig')
        if suffix != '.txt':
            parser = _HTML(); parser.feed(text); text = '\n'.join(parser.parts)
    else:
        raise ValueError('Import accepts PDF, UTF-8 HTML or text only')
    if not text.strip(): raise ValueError('Source has no extractable text; OCR requires explicit review')
    return text


def import_proposal(path, metadata):
    """Validate supplied bytes/attestation and quotations; return an unaccepted proposal.

    A checksum confirms the supplied file, not publisher authorship. Provenance is
    an explicit reviewer attestation. This function cannot qualify a deal.
    """
    provenance(metadata)
    if metadata.get('provenance_verified') is not True:
        raise ValueError('Downloader must attest verified original-source provenance')
    path = Path(path)
    if not path.is_file() or path.stat().st_size > LIMIT:
        raise ValueError('Missing or oversized import')
    raw = path.read_bytes()
    if metadata.get('expected_sha256') != sha(raw):
        raise ValueError('Downloaded file does not match the reviewed checksum')
    text = extract(raw, path.suffix.lower())
    normalise = lambda value: re.sub(r'\s+', ' ', value).strip()
    quotes = metadata.get('reviewed_quotes', [])
    if not quotes: raise ValueError('At least one reviewed quotation and location required')
    for entry in quotes:
        if not entry.get('quote') or not entry.get('locator') or normalise(entry['quote']) not in normalise(text):
            raise ValueError('Reviewed quotation absent from imported content or missing locator')
    return {'metadata': dict(metadata), 'text': text, 'raw': raw,
            'primary_content_sha256': sha(raw), 'text_sha256': sha(text.encode()),
            'status': 'review_ready_not_accepted', 'canonical_mutation': False,
            'automatic_claim_verification': False, 'automatic_qualification': False}


def secondary_url(value):
    """Finite secondary publisher policy; never eligible as an official primary URL."""
    target = urlsplit(value)
    if (target.scheme != 'https' or target.hostname != 'www.theguardian.com'
            or target.username or target.password or target.port not in (None, 443) or target.fragment):
        raise ValueError('Expected a registered secondary-publisher HTTPS URL')
    return value


def secondary_excerpt(source, repo):
    """Read a confined candidate secondary extract without relabelling it primary."""
    from .registry import snapshot_boundary
    provenance(source, secondary_url)
    boundary = snapshot_boundary(source['research_domain'], repo)
    path = (repo / source.get('text_path', '')).resolve()
    if (not path.is_relative_to(boundary) or not path.is_file()
            or path.stat().st_size > LIMIT or source.get('verification') != 'secondary_reviewed'
            or source.get('content_kind') != 'reviewed_web_excerpt'
            or source.get('primary_content_sha256') is not None
            or source.get('retrieval_method') != 'approved_web_research_tool'
            or not source.get('retrieval_reference')):
        raise ValueError('Secondary excerpt needs confined, dated and correctly typed provenance')
    text = path.read_text()
    if sha(text.encode()) != source.get('text_sha256'):
        raise ValueError('Secondary excerpt checksum mismatch')
    if not source.get('excerpts') or any(not e.get('locator') or not e.get('quote') or e['quote'] not in text for e in source['excerpts']):
        raise ValueError('Secondary excerpt requires located retained quotations')
    return text


def routine_factual_use(source, *, url_validator=official_url):
    """Existing Source owner: use eligibility is separate from canonical status.

    Trusted retained Source metadata, never request parameters. This establishes
    only a bounded analytical use, not a licence to redistribute expression.
    Actual source-level restrictions/lifecycle changes isolate that source.
    """
    rights = source.get('rights', {})
    if not isinstance(rights, dict):
        raise PermissionError('Malformed source-use metadata')
    ordinary = rights.get('basis') == 'ordinary_public_factual_analysis'
    # This validates already acquired, retained facts. It does not loosen the
    # separate network/document acquisition policy or fetch an arbitrary URL.
    provenance(source, _factual_url if ordinary and url_validator is official_url else url_validator)
    from ..intelligence_presentation import restricted_metadata
    if (working_restricted(source) or source.get('restrictions')
            or source.get('third_party_material') is not False
            or source.get('retained_form') != 'minimal_facts_and_provenance'
            or source.get('retention') != 'minimal_facts_and_provenance'
            or source.get('purpose') != 'attributed_analytical_working_views'
            or source.get('audience') != 'flora_research_views'):
        raise PermissionError('Source-use exception')
    rights = source.get('rights', {})
    url = urlsplit(source['url'])
    if rights.get('basis') == 'ordinary_public_factual_analysis':
        return _ordinary_factual_method(source)
    if (rights.get('basis') == 'fca_owned_numerical_data_ogl'
            and url.hostname == 'www.fca.org.uk' and url.path == '/data/firm-level-complaints-data-sortable-table'
            and source.get('fact_bindings')
            and all(b.get('kind') == 'service_profile' for b in source['fact_bindings'])
            and rights.get('terms_url') == 'https://www.fca.org.uk/legal'):
        return 'open_numerical_data'
    if (rights.get('basis') == 'isolated_public_financial_facts'
            and source.get('source_category') == 'issuer_results'
            and url.hostname == 'www.nationwide.co.uk'
            and re.fullmatch(r'/-/assets/nationwidecouk/documents/about/how-we-are-run/results-and-accounts/[0-9-]+/[0-9]{4}-preliminary-results\.pdf', url.path)
            and source.get('fact_bindings')
            and all(b.get('kind') == 'financial_measurement' for b in source['fact_bindings'])
            and rights.get('expression_reuse') is False
            and rights.get('contract_restriction_found') is False
            and rights.get('method_review')
            and rights.get('legal_basis_url') == 'https://www.gov.uk/government/publications/report-and-impact-assessment-on-copyright-and-artificial-intelligence/report-on-copyright-and-artificial-intelligence'):
        return 'minimal_factual_analysis'
    raise PermissionError('Source-use exception requires resolution')


def _ordinary_factual_method(source):
    """Accepted method in existing Source metadata, not a publisher licence.

    No discretionary decision per number/issuer. Concrete material exceptions
    must be resolved for the operations requested here. Deep-link permission
    is deliberately outside this homepage-only public method.
    """
    rights = source['rights']
    if not isinstance(source.get('document_identity'), dict):
        raise PermissionError('Document identity unavailable')
    operations = {'read_public', 'independent_facts', 'minimal_numerical_retention', 'public_read_only'}
    if (source.get('source_category') not in {'issuer_results','issuer_announcement','regulatory_filing','official_statistics','third_party'}
            or rights.get('expression_reuse') is not False
            or rights.get('contract_restriction_found') not in (False,None)
            or set(rights.get('operations', operations)) != operations):
        raise PermissionError('Factual method scope unavailable')
    exceptions = rights.get('material_exceptions', [])
    if not isinstance(exceptions, list):
        raise PermissionError('Source-use exceptions unassessed')
    for item in exceptions:
        if (not isinstance(item, dict) or not item.get('issue') or not item.get('operations')
                or not set(item['operations']) <= operations | {'public_deep_link','copy_protected_material','persist_financial_run','bulk_collection','public_export'}):
            raise PermissionError('Invalid source-use exception')
        if operations.intersection(item['operations']):
            # An old unestablished concern is not an applicable restriction.
            # Actual access agreements/restrictions remain fail-closed.
            if (item.get('applicable') is True
                    or item.get('status') in {'restricted','prohibited','revoked','denied'}
                    or item.get('concrete_restriction') is True):
                raise PermissionError('Applicable source-use restriction')
    home = urlsplit(rights.get('attribution_url', ''))
    original = urlsplit(source['url'])
    if (home.scheme != 'https' or home.netloc != original.netloc or home.path not in {'', '/'}
            or home.query or home.fragment or home.username or home.password
            or rights.get('homepage_conditions_met') is False):
        raise PermissionError('Homepage attribution unavailable')
    return 'minimal_factual_analysis'


def _factual_url(value):
    """Public original locator validation, never publisher permission or fetch."""
    import ipaddress
    target=urlsplit(value)
    host=(target.hostname or '').lower()
    if (target.scheme!='https' or not host or '.' not in host
            or host.endswith(('.localhost','.local','.internal','.invalid'))
            or target.username or target.password or target.port not in (None,443)
            or target.fragment or target.query or any(c.isspace() for c in value)
            or '\\' in value):
        raise ValueError('Public factual original HTTPS locator required')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return value
    raise ValueError('IP literals are not publisher identities')


def minimal_factual_integrity(source, *, statement_periods=False):
    """Bind actual minimal numerical data to its inspected document/version.

    This hash covers retained facts, never purported original PDF bytes. Legacy
    primary_text validation is unchanged and cannot fall back to this form.
    """
    import json
    from decimal import Decimal
    if (source.get('content_kind') != 'minimal_verified_numerical_facts'
            or source.get('verification') != 'primary_retrieved'
            or source.get('primary_content_sha256') is not None
            or any(k in source for k in ('text_path', 'raw_path', 'text_sha256', 'excerpts'))
            or source.get('retrieval_method') != 'approved_web_research_tool'
            or not source.get('retrieval_reference')):
        raise ValueError('Not a verified minimal factual record')
    identity = source['document_identity']
    if (not isinstance(identity, dict) or identity.get('url') != source['url'] or identity.get('publisher') != source['publisher']
            or identity.get('title') != source['title'] or not identity.get('version')
            or identity.get('published') != source['publication_date']):
        raise ValueError('Factual document identity mismatch')
    bindings = source['fact_bindings']
    if not isinstance(bindings, list) or not bindings:
        raise ValueError('Bounded factual extent required')
    payload = {'document_identity': identity, 'fact_bindings': bindings}
    encoded = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    if sha(encoded) != source.get('facts_sha256'):
        raise ValueError('Retained factual integrity mismatch')
    def valid_period(period):
        retrieval = date.fromisoformat(source['retrieved_at'][:10])
        if statement_periods and period.get('kind') == 'instant':
            return (set(period) == {'kind', 'as_at'}
                    and date.fromisoformat(period['as_at']) <= retrieval)
        return (period.get('kind') == 'duration' and period.get('fiscal_year_end')
                and date.fromisoformat(period['start']) <= date.fromisoformat(period['end']) <= retrieval)

    keys = set()
    for binding in bindings:
        if not isinstance(binding, dict) or not isinstance(binding.get('facts'), dict):
            raise ValueError('Invalid numerical binding')
        facts = binding['facts']; period = facts['period']; value = facts['value']
        if (not isinstance(period, dict) or not isinstance(value, dict)
                or binding['key'] in keys or binding.get('kind') != 'financial_measurement'
                or working_restricted(binding) or working_restricted(facts)
                or binding.get('restrictions') or facts.get('restrictions')
                or not binding.get('locator') or not facts.get('subject_id') or not facts.get('perimeter')
                or not facts.get('definition') or not facts.get('accounting_basis')
                or facts.get('semantic_type') != 'reported' or facts.get('state') not in {'actual','pro_forma'}
                or not Decimal(value['amount']).is_finite()
                or value.get('unit') not in {'currency', 'percentage'}
                or not valid_period(period)):
            raise ValueError('Invalid numerical fact meaning')
        keys.add(binding['key'])
    return bindings


def current_source_records(domain):
    """Read existing research Source metadata, never a new registry or store."""
    import json
    from . import model
    from .registry import snapshot_boundary
    path=snapshot_boundary(domain,model.REPO).parent/'Assessment-Overlay.json'
    relative=path.relative_to(model.REPO)
    if any((model.REPO/Path(*relative.parts[:i])).is_symlink() for i in range(1,len(relative.parts)+1)):
        raise ValueError('Source metadata boundary unavailable')
    if not path.exists():return ()
    if not path.is_file() or path.stat().st_size>LIMIT:raise ValueError('Source metadata unavailable')
    records=json.loads(path.read_text())['sources']
    if not isinstance(records,list) or any(not isinstance(x,dict) for x in records):raise ValueError('Invalid Source metadata')
    return tuple(records)


def document_use_allowed(record, domain='banking', linked_id=None):
    """Honour existing document lifecycle across its factual representations.

    A Source identity/withdrawal binding, not Evidence promotion or permission
    per document. An existing negative cannot be cleared by a second snapshot.
    """
    records=current_source_records(domain)
    if linked_id:
        linked=[s for s in records if s.get('id')==linked_id]
        if len(linked)!=1 or linked[0].get('url')!=record['url']:
            raise ValueError('Existing document Source identity changed or unavailable')
    for source in records:
        if source.get('url')!=record['url']:continue
        if (working_restricted(source) or source.get('restrictions')
                or source.get('verification') in {'unverified','rejected','denied'}):
            raise PermissionError('Existing document Source is restricted')
    return True


def public_factual_record():
    """One finite case in the existing Source snapshot owner; no writes or URL fetch.

    It never joins the Financial-run selection catalogue. Missing, restricted,
    changed or legally unresolved material yields no public payload.
    """
    import json
    from . import model
    from .registry import snapshot_boundary
    root = snapshot_boundary('banking', model.REPO)
    path = root / 'PFI-Lloyds-Q326.json'
    # No symlinked directory/file can redirect this finite public case to a
    # private store. The configured repository root itself remains the owner.
    relative = path.relative_to(model.REPO)
    if (any((model.REPO / Path(*relative.parts[:i])).is_symlink() for i in range(1, len(relative.parts)+1))
            or not path.is_file() or path.stat().st_size > LIMIT):
        raise ValueError('Public factual source unavailable')
    source = json.loads(path.read_text())
    if (not isinstance(source, dict) or not isinstance(source.get('rights'), dict)
            or source.get('authority') != 'analytical_working_research'
            or source.get('canonical_mutation') is not False):
        raise PermissionError('Public factual authority unavailable')
    if any(not isinstance(source.get(k), str) or not source[k] for k in
           ('url','retrieval_url','retrieved_at','title','publisher','reporting_period','reviewed_by','review_notes')):
        raise ValueError('Factual provenance fields unavailable')
    routine_factual_use(source)
    minimal_factual_integrity(source, statement_periods=True)
    document_use_allowed(source, linked_id='PR-LBG-Q326')
    return source



def public_statement_record(selection):
    """Finite Source selections for statement reads, independent of Financial runs."""
    import json
    from . import model
    from .registry import snapshot_boundary

    entries = {
        'lloyds-q3': ('banking', 'PFI-Lloyds-Q326.json', 'PFI-LBG-Q326',
            'https://www.lloydsbankinggroup.com/assets/pdfs/investors/financial-performance/lloyds-banking-group-plc/2026/q3/2026-lbg-q3-ims.pdf',
            ('research-subject:lloyds-banking-group-plc', 'Lloyds Banking Group plc')),
        'lloyds-h1': ('banking', 'LEI-Lloyds-H126.json', 'LEI-LBG-H126',
            'https://www.lloydsbankinggroup.com/assets/pdfs/investors/financial-performance/lloyds-banking-group-plc/2026/q2/2026-lbg-hy-results.pdf',
            ('research-subject:lloyds-banking-group-plc', 'Lloyds Banking Group plc')),
        'nationwide-annual': ('banking', 'EEI2B-Nationwide-AR26.json', 'EEI2B-NATIONWIDE-AR26',
            'https://www.nationwide.co.uk/-/assets/nationwidecouk/documents/about/how-we-are-run/results-and-accounts/2025-2026/annual-report-and-accounts-2026.pdf',
            ('research-subject:nationwide-building-society-group', 'Nationwide Building Society Group')),
    }
    if selection not in entries:
        raise ValueError('Unavailable financial statement selection')
    domain, filename, record_id, official, subject = entries[selection]
    path = snapshot_boundary(domain, model.REPO) / filename
    relative = path.relative_to(model.REPO)
    if (any((model.REPO / Path(*relative.parts[:i])).is_symlink() for i in range(1, len(relative.parts)+1))
            or not path.is_file() or path.stat().st_size > LIMIT):
        raise ValueError('Financial statement source unavailable')
    record = json.loads(path.read_text())
    if (not isinstance(record, dict) or record.get('id') != record_id
            or record.get('url') != official or record.get('retrieval_url') != official):
        raise ValueError('Financial statement document mismatch')
    expected_publisher = subject[1] if selection in {'lloyds-q3','lloyds-h1'} else 'Nationwide Building Society'
    if record.get('publisher') != expected_publisher:
        raise ValueError('Financial statement issuer mismatch')
    if selection in {'lloyds-q3','lloyds-h1'}:
        # Finite presentation contract, not permission per figure. The renderer
        # names these periods/bases: reject incompatible inputs before display.
        end_month = '09-30' if selection == 'lloyds-q3' else '06-30'
        bases = {'banking_nim':'issuer banking NIM alternative performance measure',
            'average_banking_assets':'issuer period-average banking assets',
            'restructuring':'statutory reconciliation adjustments','volatility':'statutory reconciliation adjustments',
            'profit_before_tax':'statutory','profit_after_tax':'statutory','customer_deposits':'statutory',
            'risk_weighted_assets':'prudential reported','cet1':'prudential reported','cet1_proforma':'prudential pro forma'}
        for binding in record['fact_bindings']:
            f=binding['facts']
            if not isinstance(f,dict) or not isinstance(f.get('value'),dict) or not isinstance(f.get('period'),dict):
                raise ValueError('Malformed financial statement binding')
            year=f['fiscal_year'];metric=f['metric'];value=f['value'];period=f['period']
            basis=bases.get(metric,'underlying') if selection=='lloyds-q3' else 'underlying'
            expected_period=({'kind':'instant','as_at':str(year)+('-09-30' if year==2026 else '-12-31')} if period['kind']=='instant'
                else {'kind':'duration','start':str(year)+'-01-01','end':str(year)+'-'+end_month,'fiscal_year_end':'12-31'})
            perimeter=('banking business; not a legal-bank allocation' if metric in {'banking_nim','average_banking_assets'}
                else 'prudential consolidated Group' if metric in {'risk_weighted_assets','cet1','cet1_proforma'} else 'consolidated Group')
            if selection=='lloyds-h1':
                segment={'retail':'Retail','commercial':'Commercial Banking','retirement':'Insurance, Pensions & Investments','central':'Equity Investments and Central Items'}.get(binding['key'].split('-')[0])
                if segment:perimeter=segment+' reporting segment; consolidated Group internal basis'
            ratio=metric in {'banking_nim','cet1','cet1_proforma'}
            scale='units' if ratio else 'billions' if metric in {'average_banking_assets','risk_weighted_assets'} else 'millions'
            if (year not in {2025,2026} or period!=expected_period or f['accounting_basis']!=basis or f['perimeter']!=perimeter
                    or (f['subject_id'],f['subject_name'])!=subject
                    or value.get('currency')!=(None if ratio else 'GBP')
                    or value['unit']!=('percentage' if ratio else 'currency') or value['scale']!=scale
                    or f['state']!=('pro_forma' if metric=='cet1_proforma' else 'actual')):
                raise ValueError('Financial statement presentation axes mismatch')
    document_use_allowed(record, domain, 'PR-LBG-Q326' if selection=='lloyds-q3' else None)
    return record, subject


def working_facts():
    """Finite retained research package through the existing snapshot owner.

    No universal release pin, human approval, canonical promotion or URL fetch.
    Integrity remains content-addressed by primary_text for each source. A
    source exception omits only its dependent rows, not unrelated research.
    """
    import json
    from . import model
    from .registry import snapshot_boundary
    root = snapshot_boundary('banking', model.REPO)
    path = root / 'RUD1-Public-Facts.json'
    if path.is_symlink():
        raise PermissionError('Research unavailable')
    data = json.loads(path.read_text())
    from ..intelligence_presentation import restricted_metadata
    if (data.get('authority') != 'analytical_working_research' or data.get('canonical_mutation') is not False
            or working_restricted({k:v for k,v in data.items() if k not in {'sources','service_profiles','financial_selections'}})):
        raise PermissionError('Research authority unavailable')
    from collections import Counter
    records = [s for s in data['sources'] if isinstance(s, dict) and isinstance(s.get('id'), str) and s['id']]
    counts = Counter(s['id'] for s in records)
    sources = {}
    for source in records:
        if counts[source['id']] != 1:
            continue
        try:
            # Ordinary public factual scope cannot be laundered into the
            # existing persisted-run catalogue by relabelling a legacy source.
            # It is served only by the read-only Source entry point below.
            if isinstance(source.get('rights'), dict) and source['rights'].get('basis') == 'ordinary_public_factual_analysis':
                continue
            routine_factual_use(source)
            model.primary_text(source)
            if source['id'] in sources:
                raise ValueError('Duplicate source identity')
            sources[source['id']] = source
        except (PermissionError, ValueError, OSError, KeyError, TypeError):
            continue
    return data, sources


def bound_facts(source, key, kind):
    """Exact located factual axes, not substring support or a new approval.

    The retained source record owns these transcribed cells and their axes.
    Ordinary derived/display rows must match them, rather than self-admitting.
    """
    from ..intelligence_presentation import restricted_metadata
    bindings = [b for b in source['fact_bindings'] if b['key'] == key and b['kind'] == kind]
    if len(bindings) != 1 or working_restricted(bindings[0]):
        raise ValueError('Ambiguous or restricted source fact')
    binding = bindings[0]
    indices = binding.get('excerpt_indices', [])
    if (not indices or any(type(i) is not int or i < 0 or i >= len(source['excerpts']) for i in indices)
            or len(indices) != len(set(indices))):
        raise ValueError('Invalid factual-cell locations')
    entries = [source['excerpts'][i] for i in indices]
    facts = binding['facts']
    if kind == 'financial_measurement':
        from decimal import Decimal
        if len(entries) != 1 or Decimal(entries[0]['quote'].replace(',', '')) != abs(Decimal(facts['value']['amount'])):
            raise ValueError('Financial cell differs from located factual value')
    else:
        if (len(entries) != 3 or [e['quote'].replace(',', '').removesuffix('%') for e in entries]
                != [str(facts[k]) for k in ('received','closed','upheld')]
                or any(facts['name'] not in e['locator'] or facts['period'] not in e['locator'] for e in entries)):
            raise ValueError('Service cells differ from located entity/period values')
    return facts


def working_restricted(record):
    from ..intelligence_presentation import restricted_metadata
    return restricted_metadata(record) or any(record.get(key) is True for key in
        ('revoked', 'denied', 'contradictory', 'stale', 'superseded'))


def public_enterprise_role():
    """Finite government-attributed role fact through the current Source owner.

    Existing open-government factual use only; no issuer permission, registry,
    canonical identity creation, private lookup, or Financial-run authority.
    """
    import json
    from . import model
    from .registry import snapshot_boundary
    root=snapshot_boundary('banking',model.REPO)
    path=root/'CEO1-GOV-ROLE.json'
    relative=path.relative_to(model.REPO)
    if (any((model.REPO/Path(*relative.parts[:i])).is_symlink() for i in range(1,len(relative.parts)+1))
            or not path.resolve().is_relative_to(root.resolve())):return ()
    try:
        package=json.loads(path.read_text());source=package['source'];facts=package['facts']
        expected='https://www.gov.uk/government/news/seven-new-towns-proposed-to-kickstart-housebuilding-push'
        if (working_restricted(package) or package.get('authority')!='analytical_working_research'
                or package.get('canonical_mutation') is not False or working_restricted(source)
                or source.get('id')!='CEO1-GOV-ROLE' or source.get('url')!=expected or source.get('retrieval_url')!=expected
                or source.get('publication_date')!='2026-03-22' or source.get('restrictions')
                or source.get('rights',{}).get('material_exceptions') or working_restricted(source.get('rights',{}))
                or source.get('rights',{}).get('status')!='permitted_ogl_factual_extract'
                or source['rights'].get('terms_url')!='https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/'
                or len(facts)!=1):return ()
        provenance(source);content=model.primary_text(source)
        fact=facts[0]
        if (working_restricted(fact) or fact.get('id')!='CEO1-ROLE-NUNN-20260322'
                or fact.get('subject_id')!='BK-ENT-001' or fact.get('legal_name')!='Lloyds Banking Group plc'
                or fact.get('name')!='Charlie Nunn' or fact.get('role')!='Group Chief Executive'
                or fact.get('semantic_type')!='reported' or fact.get('period')!='22 March 2026'
                or fact.get('current_mandate_verified') is not False or fact.get('source_id')!=source['id']
                or fact.get('statement')!='The government identified Charlie Nunn as Lloyds Banking Group Chief Executive on 22 March 2026.'
                or 'Charlie Nunn, Group Chief Executive at Lloyds Banking Group, said:' not in content):return ()
        return source,fact
    except (OSError,ValueError,KeyError,TypeError):return ()
