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
              'www.iata.org', 'www.caa.co.uk', 'www.easa.europa.eu', 'www.eurocontrol.int'}
LIMIT = 16 * 1024 * 1024


def sha(content):
    return hashlib.sha256(content).hexdigest()


def official_url(value):
    target = urlsplit(value)
    if (target.scheme != 'https' or target.hostname not in PUBLISHERS
            or target.username or target.password or target.port not in (None, 443)
            or target.fragment):
        raise ValueError('Expected an approved official-publisher HTTPS document URL')
    return value


def provenance(metadata):
    official_url(metadata['url'])
    official_url(metadata['retrieval_url'])
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
