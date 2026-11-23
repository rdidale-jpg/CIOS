"""Offline Factory comparison. Imports manual responses and never calls a model."""
import argparse
from collections import Counter
from datetime import date
from hashlib import sha256
import json
import os
from pathlib import Path
import re

from cios.applications.flora.research_intelligence.assurance import screen_extracted
from cios.applications.flora.research_intelligence.body_claims import (
    SENTENCE_BREAK, UNCERTAIN, body_paragraphs, extract_claims,
)
from cios.applications.flora.research_intelligence.discovery import NewsPage, parse_date
from tools.research.factory_scale import MAX_BYTES
from tools.research.factory_semantic_benchmark import LOCATOR, acquisition, comparison

ROOT = Path('docs/research/initial-factory/zero-cost')
KINDS = {'acquisition', 'partnership', 'supply', 'procurement', 'order', 'investment',
         'research collaboration', 'donation', 'capacity expansion', 'migration',
         'announcement', 'portfolio expansion', 'rollout', 'facility opening', 'governance'}
STATUS = {
    'planned': r'\b(?:will|plans? to|intend[sz]? to|agreement to acquire|expects? to)\b',
    'announced': r'\b(?:announc\w+|published|unveiled)\b',
    'in progress': r'\b(?:is|are)\b.{0,70}\b(?:expanding|migrating|bringing|moving|underway)\b',
    'completed': r'\b(?:completed|transitioned|established|closed)\b',
    'committed': r'\bcommitted\b',
    'awarded': r'\bawarded\b',
    'placed': r'\b(?:placed an order|has ordered)\b',
}
CRITICAL = {'acquisition', 'procurement', 'order', 'investment'}
MAX_MANUAL_BYTES = 256 * 1024
MAX_CLAIMS = 6
NON_ACTUAL = re.compile(
    r"\b(?:once|if|unless|subject to)\b|\b(?:will|expect\w*|plan\w*|aim\w*)\b", re.I)


def documents(corpus, captures):
    for row in corpus:
        key = sha256(row['url'].encode()).hexdigest()
        directory = next((c for c in captures if (c / f'{key}.json').is_file()), None)
        if directory is None:
            raise ValueError(f"Missing capture for {row['id']}")
        raw, suffix = acquisition(directory, False)(row['url'], MAX_BYTES)
        if suffix != '.html' or sha256(raw).hexdigest() != row['sha256']:
            raise ValueError(f"Wrong revision for {row['id']}")
        text = dict(body_paragraphs(raw)).get(row['paragraph'])
        if not text or len(text) > 1600:
            raise ValueError(f"Missing or oversized passage for {row['id']}")
        yield row, raw, text


def manual_rows(path, corpus):
    if path.stat().st_size > MAX_MANUAL_BYTES:
        raise ValueError('Manual response exceeds input cap')
    payload = json.loads(path.read_text())
    if not isinstance(payload, list) or len(payload) > len(corpus):
        raise ValueError('Unexpected manual response envelope')
    allowed = {r['id']: r['sha256'] for r in corpus}
    rows = {}
    for row in payload:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str):
            raise ValueError('Malformed manual response row')
        identifier = row['id']
        claims = row.get('claims')
        if (identifier in rows or identifier not in allowed or allowed[identifier] != row.get('sha256')
                or not isinstance(claims, list) or len(claims) > MAX_CLAIMS):
            raise ValueError('Duplicate, unknown, revision-mismatched or oversized response')
        rows[identifier] = claims
    return rows


def candidates(row, text, responses, published):
    """Translate untrusted manual JSON to candidate objects with local provenance."""
    for index, item in enumerate(responses):
        fields = ('actor', 'kind', 'status', 'target', 'quote')
        if not isinstance(item, dict) or any(not isinstance(item.get(key), str) or not item[key].strip() for key in fields):
            raise ValueError('Missing manual candidate field')
        if item['kind'] not in KINDS or item['status'] not in STATUS:
            raise ValueError('Unknown event kind or status')
        party = item.get('counterparty')
        value = item.get('value')
        dates = item.get('dates', [])
        if (not isinstance(dates, list) or any(not isinstance(d, str) or not d for d in dates)
                or any(field is not None and (not isinstance(field, str) or not field)
                       for field in (party, value))):
            raise ValueError('Invalid manual party, date or value')
        quote = item['quote']
        hits = [(i, s.index(quote)) for i, s in enumerate(SENTENCE_BREAK.split(text), 1)
                if quote in s and s.count(quote) == 1]
        locator = None
        if len(hits) == 1 and text.count(quote) == 1:
            n, start = hits[0]
            locator = f"body p{row['paragraph']}, sentence {n}, chars {start}–{start + len(quote)}"
        yield {
            'claim_id': f"{row['id']}-{index + 1}",
            'source': {'url': row['url'], 'sha256': row['sha256'], 'publisher': row['publisher'],
                       'locator': locator or '', 'published': published or ''},
            'excerpt': quote, 'actor_text': item['actor'], 'target_text': item['target'],
            'kind': item['kind'], 'reported_status': item['status'], 'date_mentions': dates,
            'value_mentions': [value] if value else [],
            'relationship_candidates': [{'name': party, 'role': 'unreviewed'}] if party else [],
            'classification': 'issuer claim candidate', 'publication_eligible': False,
        }


def hybrid_gate(claim, raw, published):
    quote = claim['excerpt']
    if not claim['source']['locator']:
        return 'unbound_quote'
    if not published:
        return 'publication_date_unresolved'
    status = claim['reported_status']
    if UNCERTAIN.search(quote) or (status in {'completed', 'awarded', 'placed'}
                                  and NON_ACTUAL.search(quote)):
        return 'status_uncertain_or_negated'
    decision = screen_extracted(claim, raw, as_of=date.fromisoformat(published))
    if decision['factual_state'] != 'attributed_only':
        return 'assurance_withheld'
    values = [claim['actor_text'], claim['target_text'], *claim['date_mentions'],
              *claim['value_mentions'], *(p['name'] for p in claim['relationship_candidates'])]
    anchored = all(re.search(r'(?<!\w)' + re.escape(v.casefold()) + r'(?!\w)', quote.casefold())
                   for v in values)
    if not anchored or not re.search(STATUS[status], quote, re.I):
        return 'field_support_unresolved'
    return None


def grade(found, reference):
    expected = list(reference['claims'])
    tally = Counter(expected=len(expected), predicted=len(found))
    for claim in found:
        matches = [comparison(row, claim) for row in expected]
        match = next((i for i, fields in enumerate(matches) if all(fields.values())), None)
        if match is not None:
            expected.pop(match)
            tally['correct'] += 1
            tally['commercial_relevance_points'] += reference['commercial_relevance']
        else:
            tally['false_positive'] += 1
            if claim['kind'] in CRITICAL or claim.get('value_mentions'):
                tally['critical_review_flags'] += 1
        if any(fields['actor'] and fields['event'] and fields['target'] for fields in matches):
            tally['event_matches'] += 1
            if any(fields['actor'] and fields['event'] and fields['target'] and fields['status'] for fields in matches):
                tally['status_correct'] += 1
        tally['bound_attribution'] += bool(claim['source']['locator'])
    tally['missed'] = len(expected)
    return tally


def score(corpus, captures, reference, manual, withdrawn):
    if set(reference) != {r['id'] for r in corpus}:
        raise ValueError('Reference coverage must match the frozen corpus')
    report = {'documents': [], 'arms': {}}
    active_corpus = [row for row in corpus if row['url'] not in withdrawn]
    report['documents'].extend(
        {key: row[key] for key in ('id', 'split', 'category')} | {'disposition': 'withdrawn'}
        for row in corpus if row['url'] in withdrawn)
    for row, raw, text in documents(active_corpus, captures):
        item = {key: row[key] for key in ('id', 'split', 'category')}
        report['documents'].append(item)
        page = NewsPage(raw)
        meta = [page.properties.get(key, '') for key in
                ('article:published_time', 'datePublished', 'publish-date')]
        dates = {d for v in meta + page.structured_dates if (d := parse_date(v))}
        published = next(iter(dates)).isoformat() if len(dates) == 1 else None
        baseline = extract_claims(raw, enterprise=row['id'], url=row['url'],
                                  digest=row['sha256'], published=published or '',
                                  publisher=row['publisher'])
        baseline = [claim for claim in baseline if int(LOCATOR.fullmatch(
            claim['source']['locator'])[1]) == row['paragraph']]
        label = reference[row['id']]
        item['deterministic'] = dict(grade(baseline, label))
        item['baseline_kinds'] = [claim['kind'] for claim in baseline]
        if row['id'] in manual:
            raw_claims = list(candidates(row, text, manual[row['id']], published))
            actions = [(claim, hybrid_gate(claim, raw, published)) for claim in raw_claims]
            item['semantic'] = dict(grade(raw_claims, label))
            item['hybrid'] = dict(grade([c for c, reason in actions if reason is None], label))
            item['hybrid_exclusions'] = dict(Counter(reason for _, reason in actions if reason))
    for arm in ('deterministic', 'semantic', 'hybrid'):
        report['arms'][arm] = {}
        for split in ('development', 'evaluation'):
            rows = [r for r in report['documents'] if r['split'] == split and arm in r]
            counts = sum((Counter(r[arm]) for r in rows), Counter())
            report['arms'][arm][split] = {'evaluated_documents': len(rows), **dict(counts),
                'precision': counts['correct'] / counts['predicted'] if counts['predicted'] else None,
                'recall': counts['correct'] / counts['expected'] if counts['expected'] else None}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('packet', 'score'))
    parser.add_argument('output', type=Path)
    parser.add_argument('--capture', type=Path, action='append', required=True)
    parser.add_argument('--responses', type=Path)
    parser.add_argument('--withdrawn', type=Path, help='Local JSON list of withdrawn URLs')
    parser.add_argument('--split', choices=('development', 'evaluation'))
    args = parser.parse_args()
    corpus = json.loads((ROOT / 'corpus.json').read_text())
    withdrawn = set(json.loads(args.withdrawn.read_text())) if args.withdrawn else set()
    if args.mode == 'packet':
        if not args.split or args.responses:
            parser.error('Packet requires a split and never imports responses')
        selected = [r for r in corpus if r['split'] == args.split and r['url'] not in withdrawn]
        data = [dict(id=r['id'], sha256=r['sha256'], publisher=r['publisher'], passage=text)
                for r, _, text in documents(selected, args.capture)]
    else:
        reference = json.loads((ROOT / 'reference.json').read_text())
        manual = manual_rows(args.responses, corpus) if args.responses else {}
        data = score(corpus, args.capture, reference, manual, withdrawn)
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as file:
        file.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
