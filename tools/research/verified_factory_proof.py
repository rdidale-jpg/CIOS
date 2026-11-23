"""Prepare four reviewed disclosure candidates for the isolated Blueprint proof."""
import argparse
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from cios.applications.flora.research_intelligence.commercial_factory import prepare_commercial
from cios.applications.flora.research_intelligence.discovery import NEWSROOMS, NewsPage, parse_date
from cios.applications.flora.research_intelligence.disclosure_acquisition import normalise
from cios.applications.flora.research_intelligence.initial_factory import blueprint_archive, fingerprint
from cios.applications.flora.research_intelligence.source_import import extract, provenance
from tools.research.initial_factory import families, fetch_disclosure

BASE = Path('docs/research/initial-factory')
VISUAL_FIELDS = ('headline', 'meaning', 'next_question', 'relationship', 'confidence')


def capture(url, anchors, fetch):
    raw, suffix = fetch(url)
    if suffix != '.html':
        raise ValueError('Expected original article HTML')
    body = re.search(rb'<body\b[^>]*>(.*?)</body\s*>', raw, re.I | re.S)
    if not body:
        raise ValueError('Article body unavailable')
    text = normalise(extract(body[1], suffix))
    terms = [normalise(anchor) for anchor in anchors]
    if not terms or not all(terms):
        raise ValueError('Reviewed body anchors missing')
    pivot = re.compile(r'(?<!\w)' + re.escape(terms[0]) + r'(?!\w)')
    if not any(all(term in text[match.start():match.start() + 1500] for term in terms)
               for match in pivot.finditer(text)):
        raise ValueError('Reviewed passage changed or missing')
    return raw


def scoped_origin(url, allowed_host, path_pattern):
    target = urlsplit(url)
    if (target.scheme != 'https' or target.netloc != allowed_host or target.query or target.fragment
            or not re.fullmatch(path_pattern, target.path)):
        raise ValueError('Source outside reviewed HTML origin or path')


def prepare_finding(review, discovery, fetch=fetch_disclosure):
    enterprise = review['enterprise_id']
    if (review['url'], review['published'], enterprise, review['discovery_id']) != (
            discovery['url'], discovery['published'], discovery['enterprise_id'], discovery['candidate_id']):
        raise ValueError('Review does not match the scoped discovery')
    if (review.get('status') in {'restricted', 'withdrawn', 'superseded'}
            or discovery.get('status') == 'conflicting metadata'):
        raise ValueError('Source or evidence remains held for review')
    _, _, index, path_pattern = NEWSROOMS[enterprise]
    host = urlsplit(index).hostname
    def review_url(url):
        scoped_origin(url, host, path_pattern)

    review_url(review['url'])
    raw = capture(review['url'], review['anchors'], fetch)
    page = NewsPage(raw)
    dates = {day for value in [*page.structured_dates, page.properties.get('article:published_time', '')]
             if (day := parse_date(value))}
    if dates != {date.fromisoformat(review['published'])}:
        raise ValueError('Publication date differs from the review')
    provenance({
        'url': review['url'], 'retrieval_url': review['url'],
        'retrieved_at': datetime.now(timezone.utc).isoformat(),
        'title': review['headline'], 'publisher': review['publisher'],
        'reporting_period': review['published'], 'publication_date': review['published'],
        'publication_date_evidence': 'Publisher article date metadata',
        'reviewed_by': 'Checked repository proof binding',
        'review_notes': review['caveat'],
    }, review_url)
    confirmation = review.get('confirmation')
    corroboration = None
    if confirmation:
        if enterprise != 'arm-holdings-plc':
            raise ValueError('No separately scoped counterparty for this proof')
        scoped_origin(confirmation['url'], 'azure.microsoft.com', r'/en-us/blog/azure-cobalt-200-[a-z0-9-]+/')
        supporting = capture(confirmation['url'], confirmation['anchors'], fetch)
        corroboration = {'url': confirmation['url'], 'sha256': sha256(supporting).hexdigest(),
                         'relationship': 'Microsoft confirms its own announcement'}
    digest = sha256(raw).hexdigest()
    claim = {name: review[name] for name in ('key', 'type', 'family', 'statement', 'perspective', 'caveat')}
    claim.update(scope=review['publisher'], period=review['published'], locator='Publisher article body')
    source = {key: review[key] for key in ('enterprise_id', 'url', 'published', 'publisher')}
    # Use homepage-level Source attribution for Lloyds. The review manifest
    # records the exact original HTML separately for isolated reproduction.
    if enterprise == 'lloyds-banking-group-plc':
        source['url'] = 'https://www.lloydsbankinggroup.com/'
    source.update(category='corporate_announcement', scope=claim['scope'],
                  claims=[claim], live_content_sha256=digest)
    source['sha256'] = fingerprint(source)
    base = {'enterprise_id': enterprise, 'records': [], 'coverage': dict.fromkeys(families(), 'Unknown'),
            'models': {}, 'held': {}, 'conflicts': []}
    result = prepare_commercial(base, {'enterprise_id': enterprise, 'as_of': date.today().isoformat()}, [source])
    if len(result['records']) != 2:
        raise ValueError('Existing commercial compiler held the claim')
    evidence = result['records'][0]['payload']
    evidence['commercial_change'] = {key: review[key] for key in VISUAL_FIELDS}
    evidence['commercial_change']['corroboration'] = corroboration
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    reviews = json.loads((BASE / 'verified/lead-review.json').read_text())
    proof = json.loads((BASE / 'discovery/proof.json').read_text())
    discovered = {row['candidate_id']: row for group in proof for row in group['candidates']}
    args.output.mkdir()
    report = []
    for review in reviews:
        enterprise = review['enterprise_id']
        try:
            result = prepare_finding(review, discovered[review['discovery_id']])
        except (OSError, ValueError) as exc:
            report.append({'enterprise_id': enterprise, 'held': str(exc)})
            continue
        (args.output / f'{enterprise}.zip').write_bytes(blueprint_archive(result))
        report.append(result)
    (args.output / 'verified.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
