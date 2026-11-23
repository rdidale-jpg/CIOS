"""Capture or replay the unchanged scale challenge and score frozen paragraph labels."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re
from time import monotonic
from urllib.error import HTTPError

from tools.research.factory_scale import MAX_WORKERS, ROSTER, run_enterprise, scorecard
from tools.research.initial_factory import fetch_disclosure

REFERENCE = Path('docs/research/initial-factory/semantic/reference.json')
LOCATOR = re.compile(r'body p(\d+), sentence \d+(?:, chars \d+–\d+)?')


def acquisition(directory, capture):
    def fetch(url, cap):
        key = sha256(url.encode()).hexdigest()
        record = directory / f'{key}.json'
        if capture:
            try:
                raw, suffix = fetch_disclosure(url, cap)
            except HTTPError as exc:
                result = {'http': exc.code}
            except OSError:
                result = {'transport': True}
            except ValueError:
                result = {'rejected': True}
            else:
                (directory / key).write_bytes(raw)
                result = {'suffix': suffix, 'digest': sha256(raw).hexdigest()}
            record.write_text(json.dumps(result))
        result = json.loads(record.read_text())
        if 'http' in result:
            raise HTTPError(url, result['http'], 'recorded HTTP response', {}, None)
        if 'transport' in result:
            raise OSError('recorded transport failure')
        if 'rejected' in result:
            raise ValueError('recorded acquisition rejection')
        raw = (directory / key).read_bytes()
        if len(raw) > cap or sha256(raw).hexdigest() != result['digest']:
            raise RuntimeError('Capture revision failed integrity check')
        return raw, result['suffix']

    return fetch


def comparison(expected, actual):
    target = actual['target_text'].casefold()
    wanted = expected['target'].casefold()
    return {
        'actor': expected['actor'].casefold() == actual['actor_text'].casefold(),
        'event': expected['kind'] == actual['kind'],
        'status': expected['status'] == actual['reported_status'],
        'target': target == wanted or target.startswith(wanted + ' '),
        'date': expected['dates'] == actual['date_mentions'],
        'value': [expected['value']] == actual.get('value_mentions', []) if expected['value']
                 else not actual.get('value_mentions', []),
        'counterparty': ([expected['counterparty']] if expected['counterparty'] else []) ==
                        [party['name'] for party in actual['relationship_candidates']],
    }


def evaluate(reference, candidates):
    by_revision = {(row['url'], row['document_sha256']): row for row in candidates}
    result = {}
    for cohort, entries in reference.items():
        counts = Counter()
        details = []
        for entry in entries:
            counts['reference_paragraphs'] += 1
            counts['expected_claims'] += len(entry['claims'])
            source = by_revision.get((entry['url'], entry['sha256']))
            if source is None:
                counts['unavailable_paragraphs'] += 1
                continue
            actual = [row for row in source['body_claims']
                      if (locator := LOCATOR.fullmatch(row['source']['locator']))
                      and int(locator[1]) == entry['paragraph']]
            counts['predicted_claims'] += len(actual)
            counts['evaluated_expected_claims'] += len(entry['claims'])
            remaining = list(entry['claims'])
            predictions = []
            for row in actual:
                checks = [comparison(expected, row) for expected in remaining]
                identity = [i for i, check in enumerate(checks)
                            if check['actor'] and check['event'] and check['target']]
                match = max(identity, key=lambda i: sum(checks[i].values()), default=None)
                if match is not None:
                    check = checks[match]
                    remaining.pop(match)
                    counts['matched_event_mentions'] += 1
                    counts.update(field + '_correct' for field, valid in check.items() if valid)
                    if all(check.values()):
                        counts['exact_correct_claims'] += 1
                else:
                    counts['unmatched_predictions'] += 1
                predictions.append({
                    'claim_id': row['claim_id'], 'locator': row['source']['locator'],
                    'actor': row['actor_text'], 'event': row['kind'], 'target': row['target_text'],
                    'reported_status': row['reported_status'],
                    'fields_correct': checks[match] if match is not None else {},
                    'assurance': row['assurance']['factual_state'],
                    'assurance_issues': row['assurance']['issues'],
                })
                link = row['source']
                if (link['url'], link['sha256'], link['publisher'], link['published']) == (
                        source['url'], source['document_sha256'], source['publisher'], source['published']):
                    counts['correct_attributions'] += 1
            details.append({'url': entry['url'], 'sha256': entry['sha256'],
                            'paragraph': entry['paragraph'], 'expected': len(entry['claims']),
                            'predicted': len(actual), 'predictions': predictions,
                            'unmatched_reference': len(remaining)})
        result[cohort] = {'counts': dict(counts), 'paragraphs': details}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--read-live', action='store_true', help='Create a new private capture')
    parser.add_argument('--as-of', type=date.fromisoformat, required=True)
    parser.add_argument('--reference', type=Path, default=REFERENCE)
    args = parser.parse_args()
    if args.read_live:
        args.capture.mkdir(mode=0o700, parents=True, exist_ok=False)
    fetch = acquisition(args.capture, args.read_live)
    roster = json.loads(ROSTER.read_text())
    reports = []
    durations = {}
    for cohort in ('development', 'held_out'):
        started = monotonic()
        selected = [row for row in roster if row['cohort'] == cohort]
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            reports.extend(pool.map(lambda row: run_enterprise(row, as_of=args.as_of.isoformat(),
                                                               fetch=fetch), selected))
        durations[cohort] = round(monotonic() - started, 3)
    candidates = [candidate for report in reports for candidate in report['candidates']]
    result = scorecard(reports)
    result['cohorts'] = {cohort: scorecard([r for r in reports if r['cohort'] == cohort])
                         for cohort in durations}
    result['elapsed_seconds'] = durations
    result['dated_revisions'] = [{'url': row['url'], 'sha256': row['document_sha256']}
                                 for row in candidates]
    result['benchmark'] = evaluate(json.loads(args.reference.read_text()), candidates)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    return reports


if __name__ == '__main__':
    main()
