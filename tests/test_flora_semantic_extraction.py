from datetime import date
from hashlib import sha256

from cios.applications.flora.research_intelligence.assurance import screen_extracted
from cios.applications.flora.research_intelligence.body_claims import assess_claims, extract_claims


def extract(paragraph):
    raw = f'<body><p>{paragraph}</p></body>'.encode()
    claims = extract_claims(
        raw, enterprise='issuer', url='https://example.org/news/one',
        digest=sha256(raw).hexdigest(), published='2026-11-02', publisher='Example issuer')
    return raw, claims


def test_nested_completed_acquisition_and_distinct_planned_donation():
    raw, claims = extract(
        'EXAMPLETOWN — Horizon SE (NYSE: HZN) today announced it has completed the acquisition of '
        'North Labs, a laboratory equipment manufacturer. In parallel, Horizon SE announced plans '
        'to donate £2 million to North University, supporting education.')
    purchase, donation = claims
    assert purchase['actor_text'] == 'Horizon SE'
    assert purchase['target_text'] == 'North Labs'
    assert purchase['kind'] == 'acquisition'
    assert purchase['reported_status'] == 'completed'
    assert donation['kind'] == 'donation'
    assert donation['reported_status'] == 'planned'
    assert donation['value_mentions'] == ['£2 million']
    assert donation['relationship_candidates'] == [{'name': 'North University', 'role': 'recipient'}]
    assert purchase['claim_id'] != donation['claim_id']
    assert all(not row['publication_eligible'] for row in claims)
    assert extract(raw.decode().removeprefix('<body><p>').removesuffix('</p></body>'))[1] == claims


def test_dateline_not_actor_and_lifecycle_keeps_hold_authority():
    raw, (claim,) = extract(
        'Exmouth, England — Nov. 2, 2026 — Valley Devices, an Atlas company, announces a '
        'major expansion of its portfolio, bringing a number of products into its range.')
    assert claim['actor_text'] == 'Valley Devices'
    assert claim['date_mentions'] == ['nov. 2, 2026']
    assert claim['source']['locator'].startswith('body p1, sentence 1, chars ')
    assert claim['excerpt'].startswith('Valley Devices')
    assessment = screen_extracted(claim, raw, as_of=date(2026, 11, 23))
    assert assessment['factual_state'] == 'attributed_only'
    assert assessment['binding_required'] and not assessment['publication_eligible']
    assert screen_extracted(claim, raw + b' ', as_of=date(2026, 11, 23))['factual_state'] == 'withheld'


def test_negated_or_hedged_progress_does_not_generate_a_fact():
    _, claims = extract(
        'Horizon SE has not completed the acquisition of North Labs. '
        'Horizon SE may announce an acquisition of North Labs. '
        'North Labs is expected to become a division of Horizon SE.')
    assert claims == []


def test_semicolon_requires_two_explicit_subjects_and_preserves_distinct_spans():
    raw, (first, second) = extract(
        'Horizon SE has completed the acquisition of North Labs; '
        'East Systems announced plans to donate £2 million to West University.')
    assert [first['actor_text'], second['actor_text']] == ['Horizon SE', 'East Systems']
    assert len({row['source']['locator'] for row in (first, second)}) == 2
    tampered = dict(second, excerpt=first['excerpt'])
    assert screen_extracted(tampered, raw, as_of=date(2026, 11, 23))['issues'] == [
        'source_span_mismatch']


def test_approximate_annual_value_does_not_become_a_completed_investment():
    _, (row,) = extract(
        'Horizon SE has committed to expand its research collaboration with North University, '
        'focusing on projects worth approximately £2 million annually across several areas.')
    assert row['target_text'] == 'North University'
    assert row['reported_status'] == 'committed'
    assert row['value_mentions'] == ['approximately £2 million annually']


def test_differing_candidate_amounts_retain_both_revisions_for_review():
    _, (first,) = extract('Horizon SE plans to donate £2 million to North University.')
    _, (second,) = extract('Horizon SE plans to donate £3 million to North University.')
    group, = assess_claims([first, second])
    assert group['differences'] == ['reported values']
    assert len(group['claim_ids']) == 2
    assert not group['publication_eligible']


def test_scale_route_repeats_candidate_then_excludes_withdrawn_source():
    from tools.research.factory_scale import run_enterprise

    index = 'https://issuer.example.org/news'
    url = index + '/acquisition'
    entry = {'enterprise_id': 'issuer', 'industry': 'Technology', 'publisher': 'Horizon SE',
             'cohort': 'held_out', 'index': index, 'article_path': r'/news/[a-z-]+'}
    documents = {
        index: b'<a href="/news/acquisition">AI acquisition</a>',
        url: (b'<meta property="og:title" content="Horizon AI acquisition">'
              b'<meta property="article:published_time" content="2026-11-02">'
              b'<body><p>Horizon SE has completed the acquisition of North Labs.</p></body>'),
    }
    visited = []

    def fetch(source, _):
        visited.append(source)
        return documents[source], '.html'

    args = {'as_of': '2026-11-23', 'fetch': fetch}
    first = run_enterprise(entry, **args)
    repeated = run_enterprise(entry, **args)
    assert first['candidates'] == repeated['candidates']
    assert first['claim_states'] == {'attributed_only': 1}
    claim, = first['candidates'][0]['body_claims']
    assert claim['kind'] == 'acquisition' and not claim['publication_eligible']
    visited.clear()
    withdrawn = run_enterprise(entry, **args, withdrawn=[url])
    assert visited == [index]
    assert withdrawn['candidates'] == []
    assert withdrawn['failures'] == [{'url': url, 'reason': 'withdrawn'}]
