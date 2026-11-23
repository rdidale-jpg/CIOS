from datetime import date, timedelta
import json
from urllib.error import HTTPError

from cios.applications.flora.research_intelligence.discovery import NEWSROOMS, discover

SUBJECT = 'lloyds-banking-group-plc'
INDEX = NEWSROOMS[SUBJECT][2]
STEM = 'https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds/'
ARTICLE = STEM + 'new-report.html'
MIRROR = STEM + 'new-copy.html'
DENIED = STEM + 'unavailable.html'
CUTOFF = date.today()
TITLE = 'Lloyds announces a technology partnership'


def article(title=TITLE, days=0, *, other_day=None, body=''):
    published = (CUTOFF - timedelta(days=days)).isoformat()
    metadata = json.dumps({'@type': 'NewsArticle', 'datePublished': published})
    second = f'<meta property="article:published_time" content="{other_day}">' if other_day else ''
    return (f'<meta property="og:title" content="{title}">'
            f'<script type="application/ld+json">{metadata}</script>{second}{body}').encode()


def run(pages, *, previous=(), withdrawn=()):
    calls = []

    def fetch(url):
        calls.append(url)
        if url == DENIED:
            raise HTTPError(url, 403, 'Forbidden', {}, None)
        return pages[url], '.html'

    return discover(SUBJECT, fetch, as_of=CUTOFF.isoformat(),
                    previous=previous, withdrawn=withdrawn), calls


def test_independent_links_are_scoped_and_deduplicated():
    pages = {INDEX: (f'<a href="{ARTICLE}"><a href="{ARTICLE}?tracking=1">'
                     f'<a href="{MIRROR}"><a href="{DENIED}">'
                     '<a href="https://not-a-publisher.invalid/article">'
                     f'<a href="{STEM}2026-half-year-results.html">').encode(),
             ARTICLE: article(), MIRROR: article()}
    result, calls = run(pages)
    assert calls == [INDEX, ARTICLE, MIRROR, DENIED]
    assert [row['title'] for row in result['candidates']] == [TITLE]
    candidate = result['candidates'][0]
    assert candidate['published'] == CUTOFF.isoformat()
    assert candidate['evidence_class'] == 'publisher headline candidate'
    assert not candidate['publication_eligible']
    assert candidate['themes'] == ['Partnership']
    assert result['failures'] == [{'url': DENIED, 'reason': 'publisher HTTP response', 'http_status': 403}]


def test_repeated_and_revised_headlines_and_withdrawal():
    pages = {INDEX: f'<a href="{ARTICLE}">'.encode(), ARTICLE: article()}
    first, _ = run(pages)
    previous = first['candidates']
    repeat, _ = run(pages, previous=previous)
    assert repeat['candidates'][0]['status'] == 'unchanged'
    assert repeat['candidates'][0]['candidate_id'] == previous[0]['candidate_id']
    pages[ARTICLE] = article(body='<p>Revised article copy.</p>')
    revised_body, _ = run(pages, previous=previous)
    assert revised_body['candidates'][0]['status'] == 'unchanged'
    assert revised_body['candidates'][0]['document_bytes_changed']
    pages[ARTICLE] = article('Lloyds announces a different technology partnership')
    conflict, _ = run(pages, previous=previous)
    assert conflict['candidates'][0]['status'] == 'conflicting metadata'
    held, calls = run(pages, previous=previous, withdrawn=[ARTICLE])
    assert calls == [INDEX]
    assert held['candidates'] == []
    assert held['failures'] == [{'url': ARTICLE, 'reason': 'withdrawn'}]


def test_conflicting_and_future_dates_do_not_yield_candidates():
    pages = {INDEX: f'<a href="{ARTICLE}"><a href="{MIRROR}">'.encode(),
             ARTICLE: article(days=1, other_day=CUTOFF.isoformat()),
             MIRROR: article(days=-1)}
    result, _ = run(pages)
    assert result['candidates'] == []
    assert result['failures'] == [
        {'url': ARTICLE, 'reason': 'conflicting publication dates'},
        {'url': MIRROR, 'reason': 'headline or publication date unresolved'},
    ]
