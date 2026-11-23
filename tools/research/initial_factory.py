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
from cios.applications.flora.research_intelligence.discovery import NEWSROOMS, discover
from cios.applications.flora.research_intelligence.disclosure_acquisition import acquire_disclosures


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


def fetch_disclosure(url, max_bytes=LIMIT):
    with build_opener(NoRedirect).open(Request(url, headers={
        'Accept': 'text/html, application/pdf', 'User-Agent': 'CIOS commissioned factual research'
    }), timeout=12) as response:
        kind = response.headers.get_content_type()
        if kind not in {'text/html', 'application/pdf'}:
            raise ValueError('Unexpected disclosure media type')
        raw = response.read(max_bytes + 1)
        return raw, '.pdf' if kind == 'application/pdf' else '.html'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('commission', type=Path, help='Commission object, or an array of recorded replay bundles')
    parser.add_argument('--acquire-register', action='store_true', help='Use approved public register read for a single commission')
    parser.add_argument('--commercial-replay', type=Path, help='Reviewed commercial Source bindings for isolated replay')
    parser.add_argument('--acquire-commercial', action='store_true', help='Check the reviewed disclosure bindings against originals')
    parser.add_argument('--discover', action='store_true', help='Read bounded official newsroom indices into a review report')
    parser.add_argument('--extract-body', action='store_true', help='Include candidate body events and conflict signals in discovery')
    parser.add_argument('--withdrawn-discovery', type=Path, help='JSON list of explicit Source exclusions for this commission')
    parser.add_argument('--previous-discovery', type=Path, help='An earlier report for revision comparison')
    parser.add_argument('output', type=Path, help='New local output directory')
    args = parser.parse_args()
    inputs = json.loads(args.commission.read_text())
    if args.extract_body and not args.discover:
        parser.error('--extract-body requires --discover')
    if args.discover:
        if args.acquire_register or args.acquire_commercial or args.commercial_replay:
            parser.error('Discovery is a separate candidate-only run')
        if (not isinstance(inputs, list) or not 1 <= len(inputs) <= 4
                or not all(isinstance(key, str) and key in NEWSROOMS for key in inputs)
                or len(set(inputs)) != len(inputs)):
            parser.error('Commission one to four distinct newsroom enterprise identifiers')
        previous = json.loads(args.previous_discovery.read_text()) if args.previous_discovery else []
        withdrawn = json.loads(args.withdrawn_discovery.read_text()) if args.withdrawn_discovery else []
        if not isinstance(withdrawn, list) or not all(isinstance(url, str) for url in withdrawn):
            parser.error('Expected a JSON array of withdrawn Source URLs')
        records = [row for result in previous for row in result['candidates']]
        results = [
            discover(enterprise, fetch_disclosure, as_of=date.today().isoformat(),
                     previous=records, withdrawn=withdrawn, include_body=args.extract_body)
            for enterprise in inputs
        ]
        if args.extract_body:
            from cios.applications.flora.research_intelligence.body_claims import assess_claims
            for result in results:
                historical = [row for row in records if row['enterprise_id'] == result['enterprise_id']
                              and row['url'] not in withdrawn]
                result['body_assessment'] = assess_claims(
                    claim for row in [*historical, *result['candidates']]
                    for claim in row.get('body_claims', ()))
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'discovery.json').write_text(json.dumps(results, indent=2) + '\n')
        return
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
                disclosures = commercial[commission['enterprise_id']]
                if args.acquire_commercial:
                    disclosures = acquire_disclosures(disclosures, fetch_disclosure)
                result = prepare_commercial(result, commission, disclosures)
                result['commercial_live_records'] = sum(
                    bool(row['payload'].get('live_content_sha256')) for row in result['records'])
                result['commercial_replay_records'] = sum(
                    row['payload'].get('use_scope') == 'isolated_commercial_replay'
                    and row['payload'].get('recorded_replay') is True for row in result['records'])
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
