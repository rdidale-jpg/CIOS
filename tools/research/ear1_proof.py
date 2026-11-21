"""Issue639 offline contract observations, never an admission/approval engine.

This CLI only reads a fixed unselected decision proposal and existing BIE-3
research. No network, owner repository lookup, staging, planning write,
Observation construction, projection or canonical persistence is performed.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cios.applications.flora.blueprint_import.atomicity import validate_atomic_statement
from cios.applications.flora.financial_intelligence.adapters import _recognised_row
from cios.applications.flora.financial_intelligence.normalisation import (
    canonicalise_financial_claim, normalise_amount, normalise_reporting_period,
    resolve_metric,
)
from cios.applications.flora.financial_intelligence.schema import NumericFactValue
from cios.applications.flora.memory.models import Observation
from cios.applications.flora.memory.service import (
    FactualClaim, _financial_model_value, validate_factual_claim,
)
from cios.applications.flora.memory.source_contracts import contract_for
from cios.applications.flora.research_intelligence.source_import import official_url

PACK = ROOT / 'docs/flora-runtime/ear1'
SOURCE = 'BIE3-NW-Q3'
URL = ('https://investors.natwestgroup.com/~/media/Files/R/RBS-IR-V2/'
       'results-center/30102026/nwg-q3-2026-results.pdf')
CLAIMS = ('BIE3-NW-DEPOSITS-TOTAL', 'BIE3-NW-DEPOSITS-EX-CENTRAL')
FIELDS = ['reported amount', 'GBP', 'billion', 'Group legal scope', 'as-at date',
          'separate total/ex-central definition', 'original citation and attribution']
REFERENCES = {'docs/flora-runtime/bie3/Claim-Proposals.json',
              'docs/flora-runtime/bie3/Source-Review.json',
              'docs/flora-runtime/bie3/reviewed-cells/BIE3-NW-Q3.txt'}


def load_proposal():
    return json.loads((PACK / 'NatWest-Use-Proposal.json').read_text())


def selected_research():
    """Reference immutable existing research; do not mint replacement claims."""
    rows = json.loads((ROOT / 'docs/flora-runtime/bie3/Claim-Proposals.json').read_text())
    return [deepcopy(next(row for row in rows if row['id'] == key)) for key in CLAIMS]


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def validate_proposal(proposal, claims=None):
    """Check this fixed, UNSELECTED review artefact, not future permission.

    Intentionally rejects an 'approved' edited JSON file: real owner decisions
    must occur in the existing authorised owners, not in this CLI.
    """
    doc = proposal['document']
    parsed = urlsplit(doc['url'])
    _require(doc['url'] == doc['retrieval_url'] == URL, 'Exact original document required')
    _require(doc['host'] == parsed.hostname and doc['path'] == parsed.path,
             'Host/path scope mismatch')
    _require(doc['issuer'] == 'NatWest Group plc' and doc['registration'] == 'SC045551'
             and doc['reporting_scope'] == 'NatWest Group plc and its subsidiaries',
             'Reporting Group identity mismatch')
    _require(doc['source_type'] == 'investor_results' and doc['page_count'] == 43
             and doc['title'] == 'NatWest Group Q3 2026 Interim Management Statement'
             and doc['publication_date'] == '2026-10-30'
             and doc['reporting_date'] == '2026-09-30', 'Version/period/type mismatch')
    _require(doc['original_bytes_sha256'] is None and not doc['original_bytes_retained'],
             'No original-byte archive/hash is available')
    _require(tuple(proposal['assertion_refs']) == CLAIMS, 'Exactly the two selected assertion refs required')
    _require(proposal['allowed_proposal_fields'] == FIELDS, 'Only the exact proposed numerical fields/use')
    _require(proposal['status'] == 'unselected_owner_decision_proposal_not_import_package',
             'Review proposal is not an acceptance package')
    _require({a['audience'] for a in proposal['audiences']} ==
             {'internal_authorised_owner_review', 'seller_read_only_display'}
             and len(proposal['audiences']) == 2, 'Exact two proposed audiences required')
    for audience in proposal['audiences']:
        _require(audience['owner_choice'] is None and audience['recommendation'] == 'Defer'
                 and not audience['recorded'] and not audience['executed']
                 and audience['permission'] == 'UNRESOLVED', 'No owner decision/permission executed')
    rights = proposal['rights']
    _require(rights['terms_url'] == 'https://www.natwestgroup.com/hygiene/legal-information.html'
             and rights['rights_receipt_id'] is None and rights['owner_decision_id'] is None
             and not rights['licence_granted'] and rights['decision_expires_at'] is None,
             'No licence or source-use receipt exists')
    # This is an editorial proposal review date, never an approved rights expiry.
    date.fromisoformat(rights['proposed_review_until'])
    owner = proposal['real_owner_state']
    _require(owner['existing_presence'] == 'UNVERIFIED'
             and not owner['authorised_read_service_available'], 'Real owner state is unverified')
    for key, value in owner.items():
        if key.endswith('_id'):
            _require(value is None, 'No real canonical/source/review/receipt ID available')
        elif key.endswith('_ids'):
            _require(value == [], 'No canonical IDs or decision receipts available')
    _require(set(proposal['preserved_reference_sha256']) == REFERENCES, 'Exact historical references required')
    for relative, digest in proposal['preserved_reference_sha256'].items():
        path = (ROOT / relative).resolve()
        _require(path.is_relative_to((ROOT / 'docs/flora-runtime/bie3').resolve()) and path.is_file(),
                 'Preserved research path mismatch')
        _require(hashlib.sha256(path.read_bytes()).hexdigest() == digest,
                 'Original BIE-3 research changed')
    rows = selected_research() if claims is None else claims
    expected = selected_research()
    _require(len(rows) == 2, 'Two-claim maximum')
    for row, original in zip(rows, expected):
        _require(row == original, 'Selected assertion identity/value/scope/period/basis changed')
        _require(row['source_ids'] == [SOURCE] and validate_atomic_statement(row['statement']).atomic,
                 'One original source and atomic financial assertion required')
    return rows


def contract_probe(row):
    """Use pure existing-owner checks; IDs remain blank, never guessed."""
    claim = FactualClaim('', row['claim_type'], row['statement'], row['proposed_model_domain'],
                         row['proposed_attribute'], row['reported_value'], row['unit'],
                         row['currency'], row['reporting_period'], row['measurement_state'],
                         '', row['source_locator'], 50, row['id'])
    try:
        validate_factual_claim(claim)
    except ValueError as exc:
        binding = str(exc)
    else:
        raise ValueError('Unbound claim unexpectedly accepted by existing owner')
    label = ('Customer deposits' if row['id'] == CLAIMS[0]
             else 'Customer deposits excluding central items')
    numeric = NumericFactValue(amount=Decimal(row['reported_value']), scale=row['unit'],
                               currency=row['currency'])
    # Deliberately no Evidence/source/Enterprise ID, including in this pure
    # numeric compatibility input. It is not an accepted financial fact.
    candidate = dict(claim_type=row['claim_type'], predicate=label,
                     reported_amount=row['reported_value'], reported_scale=row['unit'],
                     currency=row['currency'], period=row['reporting_period'],
                     period_start=None, period_end=row['period_end'],
                     state='actual', accounting_basis='other_explicitly_reported_basis',
                     source_excerpt=row['statement'], affected_attribute=row['proposed_attribute'])
    normalised, reasons = canonicalise_financial_claim(candidate)
    _require('unsupported_metric' in reasons and normalised['canonical_financial_fact'] is None,
             'Existing financial metric owner changed; reassess the compatibility finding')
    period = normalise_reporting_period(row['reporting_period'])
    return {
        'factual_binding_result': binding,
        'numeric_representation': numeric.model_dump(mode='json'),
        'base_unit_representation_only': format(normalise_amount(row['reported_value'], row['unit']).normalize(), 'f'),
        'metric_resolution_reason': resolve_metric(label)[1],
        'financial_owner_rejection_reasons': reasons,
        'canonical_financial_fact_created': False,
        'table_row_recognised': _recognised_row(label)[0] is not None,
        'unqualified_period_normaliser': asdict(period) if period else None,
        'as_at_period_safe': False,
        'numeric_model_fallback_supported': _financial_model_value(row['statement']) != row['statement'],
        'observation_has_persistent_numeric_field': 'normalised_amount' in Observation.__dataclass_fields__,
        'probe_extent': 'Pure contract observations only; no Observation or Model constructed, saved or projected',
    }


def proof(proposal=None, *, as_of=None):
    proposal = load_proposal() if proposal is None else deepcopy(proposal)
    rows = validate_proposal(proposal)
    try:
        official_url(proposal['document']['url'])
    except ValueError as exc:
        technical = str(exc)
    else:
        raise ValueError('Publisher policy changed; this proof cannot authorise a new admission')
    current = (as_of or date.today()) <= date.fromisoformat(proposal['rights']['proposed_review_until'])
    contract = contract_for(proposal['document']['source_type'])
    traced = []
    for row in rows:
        traced.append({
            'assertion_ref': row['id'], 'source_ref': SOURCE,
            'proposed_attribute_not_canonical': row['proposed_attribute'],
            'states': {'researched': True, 'source_verified': True,
                       'use_permitted': 'UNRESOLVED', 'technically_admitted': False,
                       'real_identity_mapped': 'UNVERIFIED', 'evidence_accepted': 'UNVERIFIED',
                       'observation_established': 'UNVERIFIED', 'model_reflected': 'UNVERIFIED',
                       'newly_visible_in_flora': False},
            'source_type_financial_contract_compatible':
                row['claim_type'] in contract.permitted_claim_types and contract.foundation_eligible,
            'compatibility_not_acceptance': contract_probe(row),
        })
    return {'research_qa_passed': True, 'canonical_admission_proven': False,
            'technical_denial': technical, 'unselected_proposal_review_current': current,
            'source_use_revoked': bool(proposal['rights']['revoked']),
            'source_permission_granted': False, 'authority_exercised': False,
            'owner_repository_reads': 0, 'canonical_writes': 0,
            'evidence_decisions_executed': 0, 'model_projection_executed': False,
            'receipt_ids': [], 'traceability': traced,
            'stop': 'Exact-use decision, existing-owner technical/metric/as-at/persistence support, real scoped identities and individual authority/receipts required'}


if __name__ == '__main__':
    print(json.dumps(proof(), indent=2))
