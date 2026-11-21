"""Repository-owned public statement series. Runtime reads no network or private store."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from . import model, source_import
from .registry import snapshot_boundary

PACKAGE = Path('cios/applications/flora/research_intelligence/public_statement_sources')


def _read(relative):
    path = model.REPO / relative
    if (any((model.REPO / Path(*relative.parts[:i])).is_symlink()
            for i in range(1, len(relative.parts) + 1))
            or not path.is_file() or path.stat().st_size > source_import.LIMIT):
        raise ValueError('Public statement package unavailable')
    return json.loads(path.read_text())


def _document_validator(entry):
    origin = entry['origin']
    publisher = urlsplit(origin['origin'])
    if (publisher.scheme != 'https' or publisher.netloc != publisher.hostname
            or publisher.path or publisher.query or publisher.fragment
            or urlsplit(origin['identity_evidence']).scheme != 'https'
            or not urlsplit(origin['identity_evidence']).hostname):
        raise ValueError('Invalid verified publisher binding')

    def validate(value):
        target = urlsplit(value)
        prefix = origin['document_prefix']
        if (target.scheme != 'https' or target.netloc != publisher.netloc
                or target.fragment or target.query
                or not re.fullmatch(r'/[a-zA-Z0-9/_.-]+', target.path)
                or any(part in {'', '.', '..'} for part in target.path[1:].split('/'))
                or not prefix.endswith('/') or not target.path.startswith(prefix)):
            raise ValueError('Document is outside the verified official publisher binding')
        if publisher.hostname == 'www.sec.gov':
            match = re.fullmatch(r'/Archives/edgar/data/([1-9][0-9]*)/([0-9]{18})/([a-zA-Z0-9_.-]+\.htm)', target.path)
            if (not match or match[1] != origin.get('cik')
                    or match[2] != entry['accession']):
                raise ValueError('SEC filing identity mismatch')
        return value

    return validate


def records(subject, *, catalogue=None):
    """Read trusted catalogue entries by subject supplied by an existing view owner.

    The optional catalogue is for offline verification. The live caller always
    reads the repository-owned data. URLs are validators, never fetch targets.
    """
    if catalogue is None:
        catalogue = _read(PACKAGE / 'catalogue.json')
    selected = [entry for entry in catalogue['reports'] if entry['subject'] == list(subject)]
    if len(selected) > 24 or len({e['id'] for e in selected}) != len(selected):
        raise ValueError('Ambiguous or oversized public statement series')
    for entry in selected:
        try:
            filename = entry['file']
            if not re.fullmatch(r'[A-Za-z0-9_-]+\.json', filename):
                raise ValueError('Invalid public statement filename')
            domain = entry.get('legacy_snapshot_domain')
            directory = snapshot_boundary(domain, model.REPO).relative_to(model.REPO) if domain else PACKAGE
            record = _read(directory / filename)
            validate = _document_validator(entry)
            if (record['id'] != entry['id'] or record['publisher'] != entry['publisher']
                    or record['url'] != entry['url'] or record['retrieval_url'] != entry['url']
                    or record['document_identity']['version'] != entry['version']):
                raise ValueError('Public statement document identity mismatch')
            validate(record['url'])
            yield record, validate
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            continue

def presentation_subject(presentation_id):
    """Resolve retained subject metadata from an established presentation identity."""
    catalogue = _read(PACKAGE / 'catalogue.json')
    matches = {tuple(entry['subject']) for entry in catalogue['reports']
               if entry.get('presentation') == presentation_id}
    if len(matches) == 1:
        return matches.pop()
    return None
