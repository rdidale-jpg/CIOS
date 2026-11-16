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
    if (target.scheme != 'https' or not (target.hostname in PUBLISHERS or (target.hostname == 'www.nationwide.co.uk' and re.fullmatch(r'/-/assets/nationwidecouk/documents/about/how-we-are-run/results-and-accounts/[0-9-]+/[0-9]{4}-preliminary-results\.pdf', target.path) and not target.query))
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


def routine_factual_use(source):
    """Existing Source owner: use eligibility is separate from canonical status.

    Trusted retained Source metadata, never request parameters. This establishes
    only a bounded analytical use, not a licence to redistribute expression.
    Actual source-level restrictions/lifecycle changes isolate that source.
    """
    official_url(source['url'])
    provenance(source)
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
