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
    provenance(source, url_validator)
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
    if (source.get('source_category') != 'issuer_results'
            or rights.get('policy_reference') != 'https://github.com/rdidale-jpg/CIOS/pull/698/commits/9a7181fbcc43c23188c3f4ce7b7b1dea9d41977e'
            or rights.get('expression_reuse') is not False
            or rights.get('contract_restriction_found') is not False
            or not rights.get('method_review')
            or set(rights.get('operations', [])) != operations):
        raise PermissionError('Factual method scope unavailable')
    exceptions = rights.get('material_exceptions')
    if not isinstance(exceptions, list):
        raise PermissionError('Source-use exceptions unassessed')
    for item in exceptions:
        if (not isinstance(item, dict) or not item.get('issue') or not item.get('operations')
                or not set(item['operations']) <= operations | {'public_deep_link','copy_protected_material','persist_financial_run','bulk_collection','public_export'}):
            raise PermissionError('Invalid source-use exception')
        if operations.intersection(item['operations']):
            if (item.get('status') != 'resolved_for_factual_method' or not item.get('basis')
                    or not item.get('resolved_by') or not item.get('source_version')
                    or item['source_version'] != source.get('document_identity', {}).get('version')
                    or date.fromisoformat(item.get('resolved_on', '')) > date.today()):
                raise PermissionError('Material source-use exception unresolved')
    home = urlsplit(rights.get('attribution_url', ''))
    original = urlsplit(source['url'])
    if (home.scheme != 'https' or home.netloc != original.netloc or home.path not in {'', '/'}
            or home.query or home.fragment or home.username or home.password
            or rights.get('homepage_conditions_met') is not True):
        raise PermissionError('Homepage attribution unavailable')
    return 'minimal_factual_analysis'


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
    if not isinstance(bindings, list) or not 1 <= len(bindings) <= 48:
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
                or facts.get('semantic_type') != 'reported' or facts.get('state') != 'actual'
                or not Decimal(value['amount']).is_finite()
                or value.get('unit') not in {'currency', 'percentage'}
                or not valid_period(period)):
            raise ValueError('Invalid numerical fact meaning')
        keys.add(binding['key'])
    return bindings


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
    # Known material issue cannot disappear by deleting its metadata. Resolution
    # belongs to the Source/legal owner, not the viewer or a category flag.
    issues = source.get('rights', {}).get('material_exceptions', [])
    if not isinstance(issues, list):
        raise PermissionError('Invalid factual source-use scope')
    matching = [i for i in issues if isinstance(i, dict) and i.get('issue') == 'lloyds_section_2']
    if (len(matching) != 1 or matching[0].get('status') != 'resolved_for_factual_method'
            or set(matching[0].get('operations', [])) != {'independent_facts','minimal_numerical_retention','public_read_only'}):
        raise PermissionError('Lloyds factual output remains inactive')
    routine_factual_use(source)
    minimal_factual_integrity(source)
    return source



def public_statement_record(selection):
    """Finite Source selections for statement reads, independent of Financial runs."""
    import json
    from . import model
    from .registry import snapshot_boundary

    entries = {
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
