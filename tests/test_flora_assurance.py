"""Controlled reference cases. These results do not estimate field accuracy."""
from dataclasses import asdict, replace
from datetime import date, timedelta
from hashlib import sha256

import pytest

from cios.applications.flora.research_intelligence.assurance import (
    Assertion, BoundEvidence, EvidenceRef, FactScope, assure, bound_revision, publication_preview,
)
from cios.applications.flora.research_intelligence.initial_factory import fingerprint

TODAY = date(2026, 11, 23)
SCOPE = FactScope('enterprise-a', 'enterprise-a', 'service-a', 'status', 'deployment status', '2026-11-23')
CLAIM = Assertion(SCOPE, 'completed', 'status', 'Company A completed the service rollout.')
A = BoundEvidence(EvidenceRef('https://one.example.org/doc', 'a' * 64, 'body p1'),
                  CLAIM, 'Publisher One', 'Origin One', 'direct', TODAY)
B = BoundEvidence(EvidenceRef('https://two.example.org/doc', 'b' * 64, 'body p1'),
                  CLAIM, 'Publisher Two', 'Origin Two', 'direct', TODAY)


def evaluate(rows, *, assertion=CLAIM, active=None):
    if active is None:
        active = {(row.reference.url, row.reference.digest) for row in rows}
    return assure(assertion, rows, current_revisions=active, as_of=TODAY)


CASES = (
    ('no evidence', [], None, 'withheld'),
    ('issuer only', [replace(A, quality='issuer')], None, 'attributed_only'),
    ('syndication', [A, replace(B, origin=A.origin)], None, 'attributed_only'),
    ('same publisher', [A, replace(B, publisher=A.publisher)], None, 'attributed_only'),
    ('independent', [A, B], None, 'verified'),
    ('duplicate', [A, A, A], None, 'attributed_only'),
    ('withdrawal', [A, B], {(A.reference.url, A.reference.digest)}, 'attributed_only'),
    ('changed bytes', [A], {(A.reference.url, 'f' * 64)}, 'withheld'),
    ('future', [replace(A, observed_on=TODAY + timedelta(days=1))], None, 'withheld'),
    ('stale', [replace(A, observed_on=TODAY - timedelta(days=91))], None, 'withheld'),
    ('subsidiary', [replace(A, assertion=replace(CLAIM, scope=replace(SCOPE, entity='subsidiary-a')))],
     None, 'withheld'),
    ('different definition', [A, B, replace(B, assertion=replace(
        CLAIM, value='proposed', scope=replace(SCOPE, definition='separate deployment scope')))],
     None, 'verified'),
    ('different period', [A, B, replace(B, assertion=replace(
        CLAIM, value='proposed', scope=replace(SCOPE, period='2026-10-23')))], None, 'verified'),
    ('contradiction', [A, replace(B, assertion=replace(CLAIM, value='cancelled'))], None, 'conflict'),
    ('same revision disputed', [A, replace(A, assertion=replace(CLAIM, value='proposed'))], None, 'conflict'),
)


@pytest.mark.parametrize('label,rows,active,expected', CASES, ids=[case[0] for case in CASES])
def test_reference_cases(label, rows, active, expected):
    decision = evaluate(rows, active=active)
    assert decision['factual_state'] == expected, label
    assert decision == evaluate(list(reversed(rows)), active=active)
    assert not decision['publication_eligible']


def test_explicit_same_origin_supersession_requires_chronology():
    old = replace(A, observed_on=TODAY - timedelta(days=1), assertion=replace(CLAIM, value='proposed'))
    new = replace(B, publisher=A.publisher, origin=A.origin, replaces=old.reference)
    third = replace(A, reference=EvidenceRef('https://three.example.org/doc', 'c' * 64, 'body p3'),
                    publisher='Publisher Three', origin='Origin Three')
    decision = evaluate([old, new, third])
    assert decision['factual_state'] == 'verified'
    assert any(row['state'] == 'superseded' for row in decision['support'])
    assert evaluate([old, replace(new, observed_on=old.observed_on), third])['factual_state'] == 'conflict'


@pytest.mark.parametrize('assertion', [
    replace(CLAIM, statement='Company A could be buying a new service.'),
    replace(CLAIM, scope=replace(SCOPE, field='relationship'), unit='entity_id', value='Unknown Vendor'),
    replace(CLAIM, scope=replace(SCOPE, period='unknown')),
    replace(CLAIM, scope=replace(SCOPE, field='measurement'), unit='unmapped', value='12'),
    replace(CLAIM, scope=replace(SCOPE, field='measurement'), unit='count', value='1.5'),
])
def test_unresolved_entities_units_and_hypotheses_remain_unsupported(assertion):
    assert evaluate([], assertion=assertion)['factual_state'] == 'unsupported'


def test_exact_revision_hash():
    raw = b'<body><p>Company A completed the service rollout.</p></body>'
    reference = replace(A.reference, digest=sha256(raw).hexdigest())
    assert bound_revision(raw, reference)
    assert not bound_revision(raw + b'changed', reference)


@pytest.mark.parametrize('denial', [
    {}, {'source_use_approved': False}, {'workspace_allowed': False},
    {'execution_approved': False}, {'audience': 'public'}, {'workspace': ''},
    {'approved_scopes': set()}, {'workspace': 'different-scope'},
])
def test_authority_is_separate_from_verified_state(denial):
    decision = evaluate([A, B])
    parameters = {
        'workspace': 'isolated', 'audience': 'isolated_workspace',
        'approved_scopes': {('isolated', 'isolated_workspace', fingerprint(asdict(CLAIM)))},
        'source_use_approved': True, 'workspace_allowed': True, 'execution_approved': True,
    }
    result = publication_preview(decision, **(parameters | denial))
    assert result['eligible_for_isolated_handoff'] is (not denial)
    assert not result['can_publish_live'] and not result['can_mutate_pipeline']


def test_eligible_when_new_independent_support_arrives_and_withheld_when_it_leaves():
    assert evaluate([A])['factual_state'] == 'attributed_only'
    assert evaluate([A, B])['factual_state'] == 'verified'
    assert evaluate([A, B], active={(A.reference.url, A.reference.digest)})['factual_state'] == 'attributed_only'


def test_screening_new_body_uses_exact_revision_and_never_marks_it_verified():
    from cios.applications.flora.research_intelligence.assurance import screen_extracted
    from cios.applications.flora.research_intelligence.body_claims import extract_claims

    raw = b'<body><p>Company A completed the service rollout.</p></body>'
    row, = extract_claims(raw, enterprise='enterprise-a', url=A.reference.url,
                          digest=sha256(raw).hexdigest(), published=TODAY.isoformat(), publisher='Issuer')
    decision = screen_extracted(row, raw, as_of=TODAY)
    assert decision['factual_state'] == 'attributed_only'
    assert decision['binding_required'] and not decision['publication_eligible']
    wrong_bytes = screen_extracted(row, raw + b'changed', as_of=TODAY)
    assert wrong_bytes['factual_state'] == 'withheld'
    assert wrong_bytes['issues'] == ['document_revision_mismatch']


def test_commercial_reading_does_not_infer_a_requirement_or_opportunity():
    from cios.applications.flora.research_intelligence.assurance import commercial_reading

    assert commercial_reading(evaluate([A])) == {'confirmed_development': None, 'buyer_questions': []}
    result = commercial_reading(evaluate([A, B]))
    assert result['confirmed_development'] == CLAIM.statement
    assert len(result['buyer_questions']) == 1
    assert set(result) == {'confirmed_development', 'buyer_questions'}
