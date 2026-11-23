from collections import Counter
from datetime import date
import json

from tools.research.factory_scale import MAX_BYTES, ROSTER, run_enterprise, scorecard

INDEX = 'https://publisher.example.org/news'
FIRST = INDEX + '/first'
SECOND = INDEX + '/second'
TODAY = date(2026, 11, 23).isoformat()

ENTRY = {'enterprise_id': 'example', 'industry': 'Technology', 'publisher': 'Example',
         'cohort': 'held_out', 'index': INDEX, 'article_path': r'/news/[a-z-]+'}


def article(title, body):
    return (f'<meta property="og:title" content="{title}">'
            f'<meta property="article:published_time" content="{TODAY}T00:00:00Z">'
            f'<body><p>{body}</p></body>').encode()


def test_fixed_roster_covers_six_industries_and_disjoint_cohorts():
    roster = json.loads(ROSTER.read_text())
    counts = Counter(row['industry'] for row in roster)
    assert len(counts) == 6 and set(counts.values()) == {5}
    assert len({row['enterprise_id'] for row in roster}) == 30
    assert Counter(row['cohort'] for row in roster) == {'development': 6, 'held_out': 24}


def test_scoped_budget_and_anchor_ranking_preserve_attribution():
    links = ('<a href="/news/second">Investor briefing</a>'
             '<a href="/news/first">AI supplier investment</a>'
             '<a href="/news/first?tracking=1">AI supplier investment</a>'
             '<a href="https://external.example.org/news/fake">AI supplier investment</a>'
             '<a href="https://publisher.example.org:444/news/fake">AI supplier investment</a>'
             '<a href="/news/%2e%2e/fake">technology</a>')
    sources = {
        INDEX: links.encode(),
        FIRST: article('Example announces AI investment', 'Example launched a digital service.'),
        SECOND: article('Example supplier initiative', 'Example entered into an agreement with North Systems.'),
    }
    called = []

    def fetch(url, limit):
        assert limit == MAX_BYTES
        called.append(url)
        return sources[url], '.html'

    result = run_enterprise(ENTRY, as_of=TODAY, fetch=fetch)
    assert called == [INDEX, FIRST, SECOND]
    assert result['coverage']['duplicate_links'] == 1
    assert result['claim_states'] == {'attributed_only': 2}
    assert all(not claim['publication_eligible'] for row in result['candidates']
               for claim in row['body_claims'])
    assert scorecard([result])['coverage']['with_body_candidate'] == 1
    called.clear()
    repeated = run_enterprise(ENTRY, as_of=TODAY, fetch=fetch)
    assert scorecard([repeated]) == scorecard([result])
    assert repeated['candidates'] == result['candidates']
    called.clear()
    held = run_enterprise(ENTRY, as_of=TODAY, fetch=fetch, withdrawn=[FIRST])
    assert called == [INDEX, SECOND]
    assert [f['reason'] for f in held['failures']] == ['withdrawn']
    assert scorecard([held])['coverage']['article_reads_attempted'] == 1


def test_no_read_is_preserved_in_coverage_denominator():
    def fail(*_):
        raise OSError('Unavailable during a controlled proof')

    result = run_enterprise(ENTRY, as_of=TODAY, fetch=fail)
    score = scorecard([result])
    assert score['coverage']['enterprises'] == 1
    assert score['coverage']['indexes_parsed'] == 0
    assert score['coverage']['with_body_candidate'] == 0
    assert score['read_status'] == {'transport_error': 1}
