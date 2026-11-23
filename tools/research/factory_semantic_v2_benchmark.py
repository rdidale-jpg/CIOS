"""Score frozen newsroom excerpts and replay the original scale challenge."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

from cios.applications.flora.research_intelligence.body_claims import extract_claims
from cios.applications.flora.research_intelligence.discovery import NewsPage
from tools.research.factory_scale import MAX_BYTES, MAX_WORKERS, ROSTER, run_enterprise, scorecard
from tools.research.factory_semantic_benchmark import acquisition, evaluate


def evaluation_documents(reference, fetch):
    results = []
    for row in (row for split in reference.values() for row in split):
        url = row['url']
        raw, _ = fetch(url, MAX_BYTES)
        revision = sha256(raw).hexdigest()
        if revision != row['sha256']:
            continue
        page = NewsPage(raw)
        published = next(iter(page.structured_dates), '')
        issuer_check = getattr(page, 'issuer_agrees', None)
        context = {'issuer': row['publisher'] if issuer_check(row['publisher'], url) else None} if issuer_check else {}
        claims = extract_claims(raw, enterprise=row['enterprise'], publisher=row['publisher'],
                                url=url, digest=revision, published=published, **context)
        # This direct parser benchmark uses no production admission. The
        # paired scale replay separately exercises the existing assurance gate.
        for claim in claims:
            claim['assurance'] = {'factual_state': 'offline extraction sample', 'issues': []}
        results.append(dict(url=url, document_sha256=revision, published=published,
                            publisher=row['publisher'], body_claims=claims))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('reference', type=Path)
    parser.add_argument('known_reference', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--additional-capture', type=Path)
    args = parser.parse_args()
    fetch = acquisition(args.capture, False)
    reference = json.loads(args.reference.read_text())
    started = monotonic()
    def corpus_fetch(url, cap):
        try:
            return fetch(url, cap)
        except FileNotFoundError:
            if args.additional_capture is None:
                raise
            return acquisition(args.additional_capture, False)(url, cap)

    evaluated = evaluation_documents(reference, corpus_fetch)
    parser_seconds = round(monotonic() - started, 3)

    roster = json.loads(ROSTER.read_text())
    reports = []
    started = monotonic()
    for fold in ('development', 'held_out'):
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            reports.extend(pool.map(
                lambda row: run_enterprise(row, fetch=fetch, as_of='2026-11-23'),
                [row for row in roster if row['cohort'] == fold]))
    replay_seconds = round(monotonic() - started, 3)
    leads = [lead for report in reports for lead in report['candidates']]
    known = json.loads(args.known_reference.read_text())
    replay = scorecard(reports)
    replay['dated_revisions'] = [(lead['url'], lead['document_sha256']) for lead in leads]
    replay['claim_count'] = sum(len(lead['body_claims']) for lead in leads)
    args.output.write_text(json.dumps({
        'unfamiliar': evaluate(reference, evaluated),
        'known': evaluate(known, leads),
        'scale': replay,
        'parser_seconds': parser_seconds,
        'replay_seconds': replay_seconds,
        'external_model_calls': 0,
    }, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
