from datetime import date
from hashlib import sha256

import pytest

from cios.applications.flora.research_intelligence.investigation import MAX_BYTES, MAX_ATTEMPTS, investigate

ISSUER = 'https://newsroom.arm.com/news/arm-microsoft-azure-cobalt-200'
INDEX = 'https://azure.microsoft.com/en-us/blog/'
ORIGINAL = INDEX + 'azure-cobalt-200-now-available/'
ANOTHER = INDEX + 'cobalt-200-engineering/'
TODAY = date(2026, 11, 23)
CANDIDATE = {
    'candidate_id': 'isolated-cobalt', 'enterprise_id': 'arm-holdings-plc', 'url': ISSUER,
    'published': '2026-11-17', 'publication_eligible': False,
}
HTML = (b'<meta property="article:published_time" content="2026-11-17T11:00:00Z">'
        b'<body><p>Today at Microsoft Ignite 2026, we are announcing general availability '
        b'of Azure Cobalt 200-based virtual machines.</p></body>')


def run(original=HTML, *, other=None, active=None, withdrawn=()):
    sources = {ORIGINAL: original}
    links = [ORIGINAL, ORIGINAL + '?track=1',
             'https://unapproved.example.org/en-us/blog/cobalt-200-now-available/',
             INDEX + 'other-topic/']
    if other:
        links.extend([ANOTHER, INDEX + 'zz-cobalt-200-over-budget/'])
        sources[ANOTHER] = other
    sources[INDEX] = ''.join(f'<a href="{url}">Reference</a>' for url in links).encode()
    called = []

    def fetch(url, budget):
        assert budget == MAX_BYTES
        called.append(url)
        return sources[url], '.html'

    report = investigate(CANDIDATE, fetch, as_of=TODAY, current_revisions=active,
                         withdrawn=withdrawn)
    assert len(called) == report['attempts'] <= MAX_ATTEMPTS
    assert not report['publication_eligible']
    return report, called


def test_index_discovers_original_and_improves_narrow_notice():
    report, called = run()
    assert called == [INDEX, ORIGINAL]
    assert report['starting_state'] == 'withheld'
    assert report['factual_state'] == 'verified'
    assert report['assurance']['support'][0]['source']['digest'] == sha256(HTML).hexdigest()
    assert report['commercial_reading']['buyer_questions']
    assert 'Microsoft' in report['source_relationship']
    assert report == run()[0]


@pytest.mark.parametrize('raw', [
    HTML.replace(b'announcing general availability', b'discussing possibilities'),
    HTML.replace(b'2026-11-17', b'2026-11-16'),
    HTML.replace(b'<body><p>', b'<head><p>').replace(b'</body>', b'</head>'),
    HTML.replace(b'we are announcing', b'A third party said we are announcing'),
])
def test_weak_distant_undated_or_repeated_claim_is_not_verified(raw):
    report, _ = run(raw)
    assert report['factual_state'] == 'withheld'
    assert not report['commercial_reading']['confirmed_development']


def test_conflict_suppresses_all_verified_output_and_keeps_competing_reference():
    counter = HTML.replace(
        b'Today at Microsoft Ignite 2026, we are announcing general availability of Azure Cobalt 200-based virtual machines.',
        b'Azure Cobalt 200-based virtual machines are not generally available.')
    report, called = run(other=counter)
    assert len(called) == 3
    assert report['factual_state'] == 'conflict'
    assert report['assurance']['factual_state'] != 'verified'
    assert [row['kind'] for row in report['observations']] == ['notice', 'counterclaim']
    assert report['commercial_reading']['confirmed_development'] is None


def test_missing_or_withdrawn_revision_requires_new_eligible_evidence():
    assert run(active=set())[0]['factual_state'] == 'withheld'
    assert run(active={(ORIGINAL, '0' * 64)})[0]['factual_state'] == 'withheld'
    report, called = run(withdrawn=(ORIGINAL,))
    assert called == [INDEX] and report['factual_state'] == 'withheld'
    assert run(active={(ORIGINAL, sha256(HTML).hexdigest())})[0]['factual_state'] == 'verified'
    assert run(withdrawn=(ISSUER,))[1] == []


def test_scope_rejects_cross_origin_candidate_before_fetch():
    with pytest.raises(ValueError, match='scoped discovery candidate'):
        investigate(dict(CANDIDATE, url=ORIGINAL), lambda *_: pytest.fail('Unexpected fetch'), as_of=TODAY)


def test_later_withdrawal_is_a_material_update_and_never_confirms_current_availability():
    update = (b'<meta property="article:published_time" content="2026-11-18T10:00:00Z">'
              b'<body><p>Azure Cobalt 200 virtual machines have been withdrawn.</p></body>')
    report, _ = run(other=update)
    assert report['factual_state'] == 'withheld'
    assert report['material_updates'] == ['later_update']
    assert report['assurance']['factual_state'] == 'withheld'
    assert not report['commercial_reading']['confirmed_development']
