"""Read-only deterministic assurance of bounded, scope-resolved assertions.

The caller supplies Source-owner bindings and already resolved factual scopes.
This module cannot grant Source reuse, approve a Blueprint, or publish.
"""
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import re
from urllib.parse import urlsplit

from ..blueprint_import.atomicity import validate_atomic_statement
from .initial_factory import fingerprint

STATUS = frozenset({'proposed', 'contracted', 'completed', 'available', 'announced', 'cancelled'})
DIRECT_FIELDS = frozenset({'registry_status', 'publisher_notice'})
QUALITIES = frozenset({'issuer', 'report', 'direct', 'official'})


@dataclass(frozen=True)
class FactScope:
    enterprise: str
    entity: str
    event: str
    field: str
    definition: str
    period: str


@dataclass(frozen=True)
class Assertion:
    scope: FactScope
    value: str
    unit: str
    statement: str


@dataclass(frozen=True)
class EvidenceRef:
    url: str
    digest: str
    locator: str


@dataclass(frozen=True)
class BoundEvidence:
    """Source-owner fixture input, independent of the extracted claim."""
    reference: EvidenceRef
    assertion: Assertion
    publisher: str
    origin: str
    quality: str
    observed_on: date
    replaces: EvidenceRef | None = None


def locator_is_bound(ref):
    target = urlsplit(ref.url)
    return (target.scheme == 'https' and bool(target.hostname) and not target.username
            and not target.password and not target.fragment
            and re.fullmatch(r'[a-f0-9]{64}', ref.digest) is not None
            and bool(ref.locator.strip()))


def bound_revision(raw, ref):
    """Verify exact bytes supplied by the existing bounded acquisition path."""
    return locator_is_bound(ref) and sha256(raw).hexdigest() == ref.digest


def valid_assertion(assertion):
    if not all(asdict(assertion.scope).values()) or not validate_atomic_statement(assertion.statement).atomic:
        return False
    try:
        labels = assertion.scope.period.split('/')
        period = [date.fromisoformat(value) for value in labels]
    except ValueError:
        return False
    if len(period) not in {1, 2} or period != sorted(period) or [day.isoformat() for day in period] != labels:
        return False
    if assertion.scope.field == 'status':
        return assertion.unit == 'status' and assertion.value in STATUS
    if assertion.scope.field == 'registry_status':
        return assertion.unit == 'status' and assertion.value in {'Active', 'Dissolved'}
    if assertion.scope.field == 'publisher_notice':
        return assertion.unit == 'status' and assertion.value == 'announced'
    if assertion.scope.field == 'relationship':
        return assertion.unit == 'entity_id' and bool(re.fullmatch(r'[a-z0-9][a-z0-9-]{2,100}', assertion.value))
    if assertion.scope.field != 'measurement' or assertion.unit not in {'count', 'percent', 'GBP', 'USD'}:
        return False
    try:
        amount = Decimal(assertion.value)
    except InvalidOperation:
        return False
    return amount.is_finite() and (assertion.unit != 'count'
                                   or (amount >= 0 and amount == amount.to_integral_value()))


def _usable(item, current_revisions, as_of):
    return (locator_is_bound(item.reference)
            and (item.reference.url, item.reference.digest) in current_revisions
            and item.quality in QUALITIES and bool(item.origin and item.publisher)
            and as_of - timedelta(days=90) <= item.observed_on <= as_of
            and valid_assertion(item.assertion)
            and (item.assertion.scope.field != 'status' or item.assertion.value != 'completed'
                 or date.fromisoformat(item.assertion.scope.period.split('/')[-1]) <= item.observed_on))


def _replaced(older, newer):
    return (newer.replaces == older.reference
            and newer.publisher == older.publisher and newer.origin == older.origin
            and newer.observed_on > older.observed_on
            and newer.assertion.unit == older.assertion.unit
            and newer.quality in {'direct', 'official'})


def assure(assertion, evidence, *, current_revisions, as_of):
    """Evaluate one exact field. Evidence outside its scope stays separate."""
    scoped = {}
    for item in evidence:
        if item.assertion.scope == assertion.scope:
            scoped.setdefault(item.reference, set()).add(item)
    ambiguous = {ref for ref, items in scoped.items() if len(items) > 1}
    entries = [item for items in scoped.values() for item in items]
    usable = [item for item in entries if item.reference not in ambiguous
              and _usable(item, current_revisions, as_of)]
    superseded = {old.reference for old in usable for new in usable if _replaced(old, new)}
    surviving = [item for item in usable if item.reference not in superseded]
    values = {(item.assertion.value, item.assertion.unit) for item in surviving}
    matching = [item for item in surviving
                if item.assertion == assertion]
    direct = [item for item in matching if item.quality in {'direct', 'official'}]
    independent = any(a.origin != b.origin and a.publisher != b.publisher
                      for i, a in enumerate(direct) for b in direct[i + 1:])
    official = (assertion.scope.field in DIRECT_FIELDS
                and any(item.quality == 'official' for item in matching))

    if not valid_assertion(assertion):
        state = 'unsupported'
    elif ambiguous or len(values) > 1:
        state = 'conflict'
    elif independent or official:
        state = 'verified'
    elif matching:
        state = 'attributed_only'
    else:
        state = 'withheld'

    def audit(item):
        state = ('ambiguous' if item.reference in ambiguous else
                 'superseded' if item.reference in superseded else
                 'current' if item in surviving else 'excluded')
        return {'source': asdict(item.reference), 'state': state, 'origin': item.origin,
                'publisher': item.publisher, 'observed_on': item.observed_on.isoformat(),
                'quality': item.quality, 'value': item.assertion.value, 'unit': item.assertion.unit,
                'statement': item.assertion.statement,
                'replaces': asdict(item.replaces) if item.replaces else None}

    result = {
        'assertion': asdict(assertion), 'as_of': as_of.isoformat(), 'factual_state': state,
        'support': sorted((audit(item) for item in entries), key=fingerprint),
        'publication_eligible': False,
    }
    return {'decision_id': fingerprint(result), **result}


def publication_preview(decision, *, workspace, audience, approved_scopes,
                        source_use_approved, workspace_allowed, execution_approved):
    """Gate an isolated proposal. Existing Source/Blueprint services own approval."""
    approved = (
        decision['factual_state'] == 'verified' and bool(workspace)
        and audience == 'isolated_workspace'
        and (workspace, audience, fingerprint(decision['assertion'])) in approved_scopes
        and source_use_approved is True and workspace_allowed is True
        and execution_approved is True
    )
    return {'eligible_for_isolated_handoff': approved, 'can_publish_live': False,
            'can_mutate_pipeline': False}


def screen_extracted(candidate, raw, *, as_of):
    """Screen a newly extracted newsroom excerpt in its acquisition context."""
    source = candidate['source']
    ref = EvidenceRef(source['url'], source['sha256'], source['locator'])
    published = date.fromisoformat(source['published'])
    issues = []
    if not bound_revision(raw, ref):
        issues.append('document_revision_mismatch')
    if published > as_of or published < as_of - timedelta(days=90):
        issues.append('outside_review_window')
    if not validate_atomic_statement(candidate['excerpt']).atomic:
        issues.append('non_atomic_or_speculative')
    result = {
        'claim_id': candidate['claim_id'], 'source': asdict(ref),
        'factual_state': 'withheld' if issues else 'attributed_only',
        'issues': issues, 'binding_required': True, 'publication_eligible': False,
    }
    return {'decision_id': fingerprint(result), **result}


def commercial_reading(decision):
    """Keep a verified development apart from buyer-engagement questions."""
    if decision['factual_state'] != 'verified':
        return {'confirmed_development': None, 'buyer_questions': []}
    assertion = decision['assertion']
    field = assertion['scope']['field']
    questions = []
    if field == 'publisher_notice':
        questions.append('What is in scope, and which date or eligibility criteria would the buyer confirm?')
    elif field == 'status':
        questions.append('Who owns the next milestone, and what would confirm acceptance?')
    elif field == 'relationship':
        questions.append('Which party owns delivery and which relationship terms are confirmed?')
    return {'confirmed_development': assertion['statement'], 'buyer_questions': questions}
