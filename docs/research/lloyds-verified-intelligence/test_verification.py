"""Finite review QA and real-service denials; no fabricated positive source bytes."""
from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from review import BASE, ROOT, build, original, fingerprint


def test_all_notes_and_crosswalk_entries_have_specific_review_and_unchanged_identity():
    expected = build()
    for filename, value in expected.items():
        assert json.loads((HERE / filename).read_text()) == value
    notes = expected['Note-Disposition.json']['notes']
    old = {r['id']: r for r in original('Recovery.json')['records']}
    assert len(notes) == len(old) == 49
    assert {r['recovery_id'] for r in notes} == set(old)
    refs = {r['review_ref'] for r in expected['Source-Inspection.json']['sources']}
    for row in notes:
        assert row['original_record_sha256'] == fingerprint(old[row['recovery_id']])
        assert row['entity_scope'] == old[row['recovery_id']]['entity']
        assert row['original_period'] == old[row['recovery_id']]['period']
        assert row['review_delta'] and set(row['reviewed_source_refs']) <= refs
        assert not any(row[k] for k in ('source_bytes_verified', 'new_source_permission',
                                       'canonical_acceptance', 'production_admission'))
    rows = expected['Crosswalk-Review.json']['entries']
    crosswalk = original('Entity-Crosswalk.json')['entries']
    assert len(rows) == len(crosswalk) == 34
    assert [r['crosswalk_entry'] for r in rows] == list(range(1, 35))
    for new, prior in zip(rows, crosswalk):
        assert new['original_record_sha256'] == fingerprint(prior)
        assert not new['canonical_id_resolved'] and not new['workspace_id_resolved']


def test_partial_and_date_qualified_claims_are_not_upgraded_to_unqualified_verified_facts():
    rows = {r['recovery_id']: r for r in build()['Note-Disposition.json']['notes']}
    assert rows['REC-TIER-F18']['disposition'] == 'partial_chart_identity_unverified'
    assert rows['REC-TIER-F08A']['disposition'] == 'historical_label_not_current_confirmed'
    assert rows['REC-TIER-F23B']['disposition'] == 'official_decision_publication_separated'
    assert rows['REC-TIER-F26D']['reviewed_source_refs'] == ['INVESTORS']
    assert rows['REC-R2-OBS-MS-ADOPTION']['reviewed_source_refs'] == ['MS-ISSUER', 'MS-SUPPLIER']
    sources = {r['review_ref']: r for r in build()['Source-Inspection.json']['sources']}
    assert sources['BOE-NOV']['publication_date'] == '2026-11-05'
    assert sources['LBG-TERMS']['publication_date'] is None
    assert sources['LBG-TERMS']['stated_terms_last_changed_on'] == '2010-06-01'
    assert sources['ENVOY-PDF']['publication_date'] == '2026-04-28'
    assert sources['ENVOY-HTML']['publication_date'] == '2026-05-01'
    assert all(r['original_bytes_sha256'] is None and not r['publisher_byte_archive_created']
               and not r['source_use_authority_changed'] for r in sources.values())


@pytest.mark.parametrize('journey', json.loads((HERE / 'Journey-Status.json').read_text())['journeys'],
                         ids=['transaction-banking', 'envoy'])
def test_existing_acquisition_stops_on_source_hold_or_missing_original_bytes(journey, tmp_path, monkeypatch):
    from tools.research.verified_factory_proof import prepare_finding
    source = next(s for s in build()['Source-Inspection.json']['sources']
                  if s['review_ref'] == journey['primary_review_ref'])
    enterprise = 'lloyds-banking-group-plc'
    review = {'enterprise_id': enterprise, 'url': source['original_url'],
              'published': source['publication_date'], 'discovery_id': journey['id'],
              'status': 'restricted', 'anchors': ['Transaction Banking'] if journey['id'] == 'transaction-banking' else ['Envoy']}
    discovery = {'enterprise_id': enterprise, 'url': source['original_url'],
                 'published': source['publication_date'], 'candidate_id': journey['id']}
    for key in ('FLORA_DATA_DIR', 'FLORA_PILOT_DIR'):
        monkeypatch.setenv(key, str(tmp_path / 'no-store'))

    def never_fetch(_):
        pytest.fail('Existing Source hold must be applied before acquisition')

    with pytest.raises(ValueError, match='held for review'):
        prepare_finding(review, discovery, never_fetch)

    attempts = []
    def unavailable_original(url):
        # Negative service input representing the separately observed proxy
        # denial. This is NOT a fresh HTTP test or a positive source capture.
        attempts.append(url)
        raise OSError('Original publisher bytes unavailable; no hash substitution')

    review.pop('status')
    with pytest.raises(OSError, match='Original publisher bytes unavailable'):
        prepare_finding(review, discovery, unavailable_original)
    assert attempts == [source['original_url']]
    assert not (tmp_path / 'no-store').exists()
    assert journey['original_bytes_sha256'] is None
    assert journey['state'] == 'blocked_before_acquisition_and_staging'
    assert not journey['candidate_evidence_created'] and not journey['production_activation']


@pytest.mark.parametrize('event,period,statement', [
    ('transaction-banking', '2026-11-18', 'Lloyds announced a Transaction Banking appointment.'),
    ('envoy', '2026-05-01', 'Lloyds announced an internal AI platform.'),
])
def test_existing_assurance_does_not_treat_approval_flags_as_missing_evidence(event, period, statement):
    from cios.applications.flora.research_intelligence.assurance import (
        Assertion, EvidenceRef, FactScope, assure, bound_revision, publication_preview,
    )
    scope = FactScope('lloyds-banking-group-plc', 'Lloyds Banking Group plc', event,
                      'publisher_notice', 'Dated issuer announcement', period)
    assertion = Assertion(scope, 'announced', 'status', statement)
    assert not bound_revision(b'', EvidenceRef('https://www.lloydsbankinggroup.com/', '', 'Publisher body'))
    decision = assure(assertion, [], current_revisions=set(), as_of=date(2026, 11, 26))
    assert decision['factual_state'] == 'withheld' and not decision['publication_eligible']
    for flags in (False, True):
        preview = publication_preview(decision, workspace='isolated-test-only', audience='isolated_workspace',
            approved_scopes={('isolated-test-only', 'isolated_workspace', fingerprint(decision['assertion']))},
            source_use_approved=flags, workspace_allowed=flags, execution_approved=flags)
        assert not any(preview.values())


def test_held_financial_projection_and_owner_decisions_remain_inactive():
    from cios.applications.flora.financial_intelligence.candidate_analytics import public_factual_projection
    assert public_factual_projection() == {}
    status = json.loads((HERE / 'Journey-Status.json').read_text())
    assert not status['section_2_output_active'] and not status['section_5_pdf_links_active']
    assert status['production_mutations'] == status['pipeline_mutations'] == status['new_financial_runs'] == 0
    assert status['source_permission_changes'] == 0
