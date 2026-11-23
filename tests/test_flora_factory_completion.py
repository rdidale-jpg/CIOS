from copy import deepcopy

import pytest

from cios.applications.flora.research_intelligence.body_claims import assess_claims, extract_claims
from cios.applications.flora.research_intelligence.operations_preview import research_intent


def extract(body, publisher='Publisher A', digest='a' * 64):
    return extract_claims(
        body.encode(), enterprise='scope-a', url='https://example.org/story',
        digest=digest, published='2026-11-23', publisher=publisher)


def test_body_extracts_named_events_and_preserves_attribution_and_dates():
    result = extract('''<head><p>Company A completed an unrelated rollout.</p></head>
        <body><nav><p>Company A launched a service.</p></nav>
        <p>Company A will deploy the service in the first half of 2027.</p>
        <p>Company A has partnered with North Systems.</p>
        <p>Company A has selected North Systems as its supplier.</p>
        <p>Company A will not deploy the service in 2027.</p></body>''')
    assert [(r['kind'], r['reported_status']) for r in result] == [
        ('rollout', 'planned'), ('partnership', 'announced'), ('supplier selection', 'announced')]
    assert result[0]['source']['locator'] == 'body p2, sentence 1'
    assert result[0]['date_mentions'] == ['first half of 2027']
    assert result[1]['relationship_candidates'] == [{'name': 'North Systems', 'role': 'partner'}]
    assert result[2]['relationship_candidates'] == [{'name': 'North Systems', 'role': 'supplier'}]
    assert all(r['classification'] == 'issuer claim candidate' and not r['publication_eligible'] for r in result)


def test_duplicate_and_conflicting_milestone_keep_all_evidence():
    first, = extract('<body><p>Company A will deploy the service in 2027.</p></body>')
    repeat, = extract('<body><p>Company A will deploy the service in 2027.</p></body>', 'Publisher B', 'b' * 64)
    changed, = extract('<body><p>Company A completed the service in 2028.</p></body>', 'Publisher C', 'c' * 64)
    group, = assess_claims([first, first, repeat])
    assert len(group['claim_ids']) == 2
    assert group['disposition'] == 'possible repeated reporting'
    assert group['source_diversity'] == 'multiple publishers: independence unverified'
    origins = {first['claim_id']: 'shared release', repeat['claim_id']: 'shared release'}
    group, = assess_claims([first, repeat], reviewed_origins=origins)
    assert group['source_diversity'] == 'same reported origin'
    origins[changed['claim_id']] = 'independent reviewed origin'
    group, = assess_claims([first, repeat, changed], reviewed_origins=origins)
    assert group['source_diversity'] == 'distinct reviewed origins'
    assert group['differences'] == ['status', 'date mentions']
    assert not group['publication_eligible']


def test_reviewed_event_mapping_marks_counterparty_disagreement_but_never_crosses_enterprise():
    first, = extract('<body><p>Company A has partnered with North Systems.</p></body>')
    second, = extract('<body><p>Company A has partnered with South Systems.</p></body>', 'Publisher B', 'b' * 64)
    event_map = {r['claim_id']: 'reviewed-single-event' for r in (first, second)}
    result, = assess_claims([first, second], reviewed_events=event_map)
    assert result['differences'] == ['relationship descriptions']
    assert len(assess_claims([first, dict(second, enterprise_id='scope-b')], reviewed_events=event_map)) == 2


def test_operations_intent_is_repeatable_reversible_and_cannot_activate():
    key = ('https://example.org/story', 'a' * 64)
    state = {key: 'current'}
    data = {'enterprise': 'scope-a', 'workspace': 'isolated', 'run_after': '2026-11-23T10:30+00:00',
            'revisions': state, 'withdrawals': [key, key]}
    first = research_intent(**data)
    assert first == research_intent(**deepcopy(data))
    row, = first['lifecycle_changes']
    inverse, = first['rollback_preview']
    assert (row['from'], row['to']) == (inverse['to'], inverse['from'])
    assert state[key] == 'current' and not first['execution_enabled']
    with pytest.raises(ValueError):
        research_intent(**{**data, 'revisions': {}})
    with pytest.raises(ValueError):
        research_intent(**{**data, 'run_after': '2026-11-23T10:30'})
