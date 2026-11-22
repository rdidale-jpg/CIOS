#!/usr/bin/env python3
"""Run a commissioned statutory register wave and produce a Blueprint handoff."""
import argparse
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cios.applications.flora.research_intelligence.initial_factory import (
    IDENTIFIER, REGISTER, RegisterFields, blueprint_archive, prepare,
)
from cios.applications.flora.research_intelligence.source_import import LIMIT
from cios.applications.flora.research_intelligence.commercial_factory import prepare_commercial


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def families():
    contract = ROOT / 'docs/architecture/enterprise-twin-production/factual-contract.md'
    result = re.findall(r'^\| ([^|]+?) \| [MC]\b', contract.read_text(), re.M)
    if len(result) != 31 or len(set(result)) != 31:
        raise ValueError('Unexpected Tier 1 family inventory')
    return result


def model_inventory():
    contract = ROOT / 'docs/architecture/enterprise-twin-production/analytical-models.md'
    models = re.findall(r'^### (.+)$', contract.read_text(), re.M)
    if len(models) != 20 or len(set(models)) != 20:
        raise ValueError('Unexpected analytical model inventory')
    return models


def acquisition(raw, url, observed, directory, *, child=None, replay=False, original_digest=None):
    """Prepare the existing Source proposal; originals are temporary only."""
    fields = RegisterFields({'company-number'})
    fields.feed(raw.decode())
    fields.close()
    digest = sha256(raw).hexdigest()
    path = directory / (digest + '.html')
    path.write_bytes(raw)
    notes = ('Recorded register metadata replay, not an original document' if replay else
             'Original HTTPS Companies House register page, corporate fields only')
    return {'path': path, 'controlled_registration': child, 'metadata': {
        'url': url, 'retrieval_url': url, 'retrieved_at': observed + 'T00:00:00Z',
        'title': 'Companies House public register entry', 'publisher': 'Companies House',
        'reporting_period': observed, 'reviewed_by': 'Commissioned register acquisition',
        'review_notes': notes, 'provenance_verified': True, 'expected_sha256': digest,
        'recorded_replay': replay, 'captured_original_sha256': original_digest,
        'reviewed_quotes': [{'quote': fields.text('company-number'), 'locator': 'company-number'}],
    }}


def acquire_online(commission, directory):
    """An explicit one-pass fetch of exact official public paths. No fallback."""
    number = commission['registration_number']
    children = commission.get('controlled_registrations', [])
    if (len(children) > 4 or len(set(children)) != len(children)
            or not all(IDENTIFIER.fullmatch(key) for key in [number, *children])):
        raise ValueError('Commission allows one company and at most four distinct controlled registrations')
    if commission['as_of'] != date.today().isoformat():
        raise ValueError('A live register observation requires today’s cut-off')
    paths = [(REGISTER + number, None)] + [(REGISTER + child + '/persons-with-significant-control', child)
                                          for child in children]
    opener = build_opener(NoRedirect)
    acquisitions = []
    failed = []
    for url, child in paths:
        try:
            req = Request(url, headers={'Accept': 'text/html', 'User-Agent': 'CIOS bounded register research'})
            with opener.open(req, timeout=12) as response:
                if response.headers.get_content_type() != 'text/html':
                    raise ValueError('Unexpected register media type')
                raw = response.read(LIMIT + 1)
                if len(raw) > LIMIT:
                    raise ValueError('Register response exceeds source budget')
            acquisitions.append(acquisition(raw, url, date.today().isoformat(), directory, child=child))
        except (OSError, ValueError, UnicodeError):
            failed.append(child or number)
    return acquisitions, failed


def read_replay(bundle, directory):
    commission = bundle['commission']
    return [acquisition(row['reviewed_field_anchors'].encode(), row['url'], commission['as_of'],
                        directory, child=row['controlled_registration'], replay=True,
                        original_digest=row['captured_original_sha256']) for row in bundle['captures']]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('commission', type=Path, help='Commission object, or an array of recorded replay bundles')
    parser.add_argument('--acquire-register', action='store_true', help='Use approved public register read for a single commission')
    parser.add_argument('--commercial-replay', type=Path, help='Reviewed commercial Source bindings for isolated replay')
    parser.add_argument('output', type=Path, help='New local output directory')
    args = parser.parse_args()
    inputs = json.loads(args.commission.read_text())
    commercial = json.loads(args.commercial_replay.read_text()) if args.commercial_replay else {}
    args.output.mkdir(parents=True, exist_ok=False)
    results = []
    with TemporaryDirectory() as temp:
        path = Path(temp)
        bundles = [{'commission': inputs}] if args.acquire_register else inputs
        for index, bundle in enumerate(bundles, 1):
            commission = bundle['commission']
            if args.acquire_register:
                sources, failed = acquire_online(commission, path)
            else:
                sources, failed = read_replay(bundle, path), []
            result = prepare(commission, sources, families())
            if commission['enterprise_id'] in commercial:
                result = prepare_commercial(result, commission, commercial[commission['enterprise_id']])
            for model in model_inventory():
                result['models'].setdefault(model, 'Blocked')
            result['acquisition'] = 'original public register' if args.acquire_register else 'recorded register replay'
            result['unavailable_registrations'] = failed
            if result['records']:
                archive = args.output / f'commission-{index}.zip'
                archive.write_bytes(blueprint_archive(result))
                result['blueprint'] = archive.name
            results.append(result)
    (args.output / 'research.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'{len(results)} commissioned subjects. Review research.json and any candidate Blueprints.')


if __name__ == '__main__':
    main()
