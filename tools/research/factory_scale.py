"""Run the fixed offline research challenge through existing Factory discovery."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date
import json
from pathlib import Path
from time import monotonic
from urllib.error import HTTPError

from cios.applications.flora.research_intelligence.body_claims import assess_claims
from cios.applications.flora.research_intelligence.discovery import DiscoveryScope, discover
from cios.applications.flora.research_intelligence.source_lifecycle import parse_revisions
from tools.research.initial_factory import fetch_disclosure

ROSTER = Path('docs/research/initial-factory/scale/roster.json')
MAX_BYTES = 2 * 1024 * 1024
MAX_ARTICLES = 4
MAX_WORKERS = 6


def run_enterprise(entry, *, as_of, fetch=fetch_disclosure, withdrawn=()):
    reads = []
    start = monotonic()

    def bounded(url):
        read = {'url': url}
        reads.append(read)
        try:
            raw, suffix = fetch(url, MAX_BYTES)
            read['bytes'] = len(raw)
            if suffix != '.html' or len(raw) > MAX_BYTES:
                raise ValueError('Exceeds configured HTML or byte boundary')
            read['status'] = 'html_read'
            return raw, suffix
        except HTTPError as exc:
            read.update(status='http_error', http_status=exc.code)
            raise
        except OSError:
            read['status'] = 'transport_error'
            raise
        except ValueError:
            read['status'] = 'media_or_budget'
            raise

    scope = DiscoveryScope(entry['industry'], entry['publisher'], entry['index'], entry['article_path'])
    report = discover(entry['enterprise_id'], bounded, as_of=as_of, include_body=True,
                      scope=scope, max_articles=MAX_ARTICLES, withdrawn=withdrawn)
    claims = [claim for candidate in report['candidates'] for claim in candidate['body_claims']]
    report.update(industry=entry['industry'], publisher=entry['publisher'], cohort=entry['cohort'],
                  reads=reads, seconds=round(monotonic() - start, 3),
                  claim_states=dict(Counter(claim['assurance']['factual_state'] for claim in claims)),
                  event_assessment=assess_claims(claims))
    return report


def scorecard(reports):
    badges = Counter()
    states = Counter()
    themes = Counter()
    sources = Counter()
    failures = Counter()
    for report in reports:
        candidates = report['candidates']
        badges['enterprises'] += 1
        badges['indexes_parsed'] += report['coverage']['index_read']
        badges['with_dated_candidate'] += bool(candidates)
        badges['with_body_candidate'] += bool(report['claim_states'])
        badges['dated_candidates'] += len(candidates)
        badges['article_reads_attempted'] += sum(row['url'] != report['index']
                                                 for row in report['reads'])
        for field in ('scoped_links', 'duplicate_links', 'duplicate_headlines', 'stale', 'no_topic'):
            badges[field] += report['coverage'][field]
        badges['event_groups_with_differences'] += sum(bool(row['differences']) for row in report['event_assessment'])
        states.update(report['claim_states'])
        for candidate in candidates:
            themes.update(candidate['themes'])
        for row in report['reads']:
            badges['requests'] += 1
            badges['returned_bytes'] += row.get('bytes', 0)
            sources[row['status']] += 1
        for row in report['failures']:
            failures[str(row.get('http_status', row['reason']))] += 1
    return {'coverage': dict(badges), 'read_status': dict(sources), 'claim_states': dict(states),
            'theme_hits': dict(themes), 'source_failures': dict(failures), 'paid_search_calls': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--cohort', choices=('development', 'held_out', 'all'), default='all')
    parser.add_argument('--as-of', default=date.today().isoformat())
    parser.add_argument('--source-state', type=Path, help='Optional current Source owner snapshot')
    args = parser.parse_args()
    as_of = date.fromisoformat(args.as_of).isoformat()
    roster = json.loads(ROSTER.read_text())
    selected = [row for row in roster if args.cohort in ('all', row['cohort'])]
    withdrawn = set()
    if args.source_state:
        states = parse_revisions(json.loads(args.source_state.read_text()))
        withdrawn = {url for url, _ in states} - {url for (url, _), state in states.items()
                                                 if state == 'current'}
    started = monotonic()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        reports = list(executor.map(lambda entry: run_enterprise(entry, as_of=as_of,
                                                                withdrawn=withdrawn), selected))
    result = scorecard(reports)
    result['wall_seconds'] = round(monotonic() - started, 3)
    args.output.mkdir(parents=True, exist_ok=False)
    # Full results stay in the operator's local review directory.
    (args.output / 'research.json').write_text(json.dumps(reports, indent=2) + '\n')
    (args.output / 'scorecard.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
