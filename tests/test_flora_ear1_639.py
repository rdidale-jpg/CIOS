"""EAR-1 bounded source-use proof; fixture objects never confer real authority."""
from copy import deepcopy
from dataclasses import fields
from datetime import date
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from tools.research import ear1_proof as q
from cios.applications.flora.blueprint_import import mapping, planning, promotion, review
from cios.applications.flora.memory import repository
from cios.applications.flora.memory.models import Observation
from cios.applications.flora.memory.service import ObservationMemoryService
from cios.applications.flora.research_intelligence.source_import import official_url, provenance
from tests.test_flora_security_repair_01b import authority, signed

BASE = 'e7c58feb84882b0e7a1ea38e7e1c72079402aa86'
pytestmark = pytest.mark.real_security_boundary


def test_two_existing_assertions_have_independent_unaccepted_states():
    report = q.proof(as_of=date(2026, 11, 15))
    assert report['research_qa_passed'] and not report['canonical_admission_proven']
    assert report['canonical_writes'] == report['owner_repository_reads'] == 0
    assert not report['source_permission_granted'] and not report['authority_exercised']
    assert report['receipt_ids'] == [] and report['evidence_decisions_executed'] == 0
    assert not report['model_projection_executed']
    assert [r['assertion_ref'] for r in report['traceability']] == list(q.CLAIMS)
    for row in report['traceability']:
        assert row['states'] == dict(researched=True, source_verified=True,
             use_permitted='UNRESOLVED', technically_admitted=False,
             real_identity_mapped='UNVERIFIED', evidence_accepted='UNVERIFIED',
             observation_established='UNVERIFIED', model_reflected='UNVERIFIED',
             newly_visible_in_flora=False)
        assert row['source_type_financial_contract_compatible']


@pytest.mark.parametrize('mutate', [
    lambda p: p['document'].update(url=q.URL.replace('investors.natwestgroup.com', 'www.fca.org.uk')),
    lambda p: p['document'].update(retrieval_url='https://mirror.test/natwest.pdf'),
    lambda p: p['document'].update(url=q.URL+'?redirect=https://elsewhere.test'),
    lambda p: p['document'].update(url=q.URL+'#page=5'),
    lambda p: p['document'].update(url=q.URL.replace('https://', 'http://')),
    lambda p: p['document'].update(host='natwestgroup.com'),
    lambda p: p['document'].update(path='/other-report.pdf'),
    lambda p: p['document'].update(issuer='National Westminster Bank PLC'),
    lambda p: p['document'].update(reporting_scope='UK legal bank'),
    lambda p: p['document'].update(registration='guessed-entity'),
    lambda p: p['document'].update(source_type='annual_report'),
    lambda p: p['document'].update(title='A different report'),
    lambda p: p['document'].update(publication_date='2026-11-15'),
    lambda p: p['document'].update(reporting_date='2026-10-30'),
    lambda p: p['document'].update(page_count=42),
    lambda p: p['document'].update(original_bytes_sha256='0'*64),
    lambda p: p['document'].update(original_bytes_retained=True),
    lambda p: p['assertion_refs'].append('THIRD-CLAIM'),
    lambda p: p.update(assertion_refs=p['assertion_refs'][:1]),
    lambda p: p['allowed_proposal_fields'].append('full PDF redistribution'),
    lambda p: p.update(status='accepted'),
    lambda p: p['audiences'][0].update(owner_choice='Accept'),
    lambda p: p['audiences'][0].update(recorded=True),
    lambda p: p['audiences'][1].update(executed=True),
    lambda p: p['audiences'][1].update(permission='permitted'),
    lambda p: p['audiences'][1].update(audience='unrestricted_public_export'),
    lambda p: p['rights'].update(licence_granted=True),
    lambda p: p['rights'].update(rights_receipt_id='forged-receipt'),
    lambda p: p['rights'].update(decision_expires_at='2026-12-15'),
    lambda p: p['real_owner_state'].update(canonical_enterprise_id='natwest'),
    lambda p: p['real_owner_state'].update(canonical_evidence_ids=['forged-evidence']),
    lambda p: p['real_owner_state'].update(existing_presence='absent'),
    lambda p: p['real_owner_state'].update(authorised_read_service_available=True),
    lambda p: p['preserved_reference_sha256'].update({'../outside.json': '0'*64}),
])
def test_edited_review_json_cannot_grant_rights_identity_or_admission(mutate):
    proposal = q.load_proposal()
    mutate(proposal)
    with pytest.raises(ValueError):
        q.proof(proposal)


@pytest.mark.parametrize('field,value', [
    ('reported_value', '453.4'), ('reported_value', '-454.3'),
    ('currency', 'USD'), ('unit', 'million'), ('measurement_state', 'target'),
    ('subject_name', 'National Westminster Bank PLC'), ('period_end', '2026-03-31'),
    ('accounting_basis', 'organic deposit flow'), ('canonical_target_id', 'fixture:guessed'),
    ('canonical_evidence_id', 'fixture:approved'), ('source_verified', False),
    ('proposed_attribute', 'financial_performance.metrics.revenue.FY26.actual'),
])
def test_assertion_scope_sign_currency_basis_and_authority_cannot_drift(field, value):
    rows = q.selected_research()
    rows[0][field] = value
    with pytest.raises(ValueError):
        q.validate_proposal(q.load_proposal(), rows)


def test_proof_never_reads_owner_repositories_constructs_memory_or_writes(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Forbidden owner operation in read-only proof')
    for cls in (repository.EvidenceRepository, repository.ObservationRepository,
                repository.EnterpriseModelRepository):
        monkeypatch.setattr(cls, '__init__', forbidden)
    for cls, method in ((review.CandidateReviewService, 'record_decision'),
                        (mapping.ImportMappingService, 'record_mapping'),
                        (planning.DryRunPlanningService, 'create_plan'),
                        (promotion.CanonicalPromotionService, 'approve_plan'),
                        (promotion.CanonicalPromotionService, 'execute_approved_plan'),
                        (ObservationMemoryService, 'process_evidence'),
                        (ObservationMemoryService, 'apply_observation')):
        monkeypatch.setattr(cls, method, forbidden)
    monkeypatch.setattr(Observation, '__post_init__', forbidden)
    monkeypatch.setattr(Path, 'write_text', forbidden)
    monkeypatch.setattr(Path, 'write_bytes', forbidden)
    assert q.proof()['canonical_writes'] == 0


def test_standalone_cli_has_no_pythonpath_or_working_directory_dependency(tmp_path):
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    result = subprocess.run([sys.executable, str(q.ROOT/'tools/research/ear1_proof.py')],
                            cwd=tmp_path, env=env, capture_output=True, text=True, check=True)
    report = json.loads(result.stdout)
    assert len(report['traceability']) == 2 and report['canonical_writes'] == 0


@pytest.mark.parametrize('key,base', list(zip(q.CLAIMS, ['454300000000', '453400000000'])))
def test_real_financial_owner_reports_deposit_and_stock_date_gaps(key, base):
    row = next(r for r in q.selected_research() if r['id'] == key)
    probe = q.contract_probe(row)
    assert probe['base_unit_representation_only'] == base
    assert probe['metric_resolution_reason'] == 'unsupported_metric'
    assert probe['financial_owner_rejection_reasons'] == ['unsupported_metric']
    assert not probe['canonical_financial_fact_created'] and not probe['table_row_recognised']
    assert probe['unqualified_period_normaliser']['canonical_period_id'] == 'FY26'
    assert probe['unqualified_period_normaliser']['period_end'] == '2026-03-31'
    assert not probe['as_at_period_safe'] and not probe['numeric_model_fallback_supported']
    assert not probe['observation_has_persistent_numeric_field']
    assert 'canonical_enterprise_id' in probe['factual_binding_result']


def test_transient_fixture_numeric_field_does_not_survive_owned_serialization():
    # Pure example object, not accepted NatWest memory or a write to a repository.
    obs = Observation('fixture:group', 'financial_metric_reported',
                      'Example Group reported a deposit stock.', '2026-09-30',
                      '2026-11-15T12:00:00Z', 'financial_performance.metrics.example',
                      50, ('fixture:evidence-not-real',))
    obs.normalised_amount = 1
    assert 'normalised_amount' not in {f.name for f in fields(obs)}
    restored = Observation.from_dict(obs.to_dict())
    assert not hasattr(restored, 'normalised_amount')
    assert restored.supporting_evidence_ids == ('fixture:evidence-not-real',)


def test_constructor_does_not_invent_supporting_evidence():
    with pytest.raises(ValueError, match='accepted Evidence ID'):
        Observation('fixture:group', 'financial_metric_reported', 'Example Group reported deposits.',
                    '2026-09-30', '2026-11-15', 'financial_performance.metrics.example', 50)


@pytest.mark.parametrize('later,revoked', [(False, False), (True, False), (False, True), (True, True)])
def test_expiry_and_revocation_never_unlock_a_deferred_proposal(later, revoked):
    proposal = q.load_proposal()
    proposal['rights']['revoked'] = revoked
    result = q.proof(proposal, as_of=date(2026, 12, 16) if later else date(2026, 11, 15))
    assert result['unselected_proposal_review_current'] is not later
    assert result['source_use_revoked'] is revoked
    assert not result['source_permission_granted'] and not result['canonical_admission_proven']
    assert all(not r['states']['technically_admitted'] for r in result['traceability'])


class ReadOnlyExampleEvidence:
    """No save method, no real canonical IDs or production I/O."""
    def __init__(self, rows): self.rows = deepcopy(rows)
    def list(self): return deepcopy(self.rows)
    def get(self, key): return next((deepcopy(r) for r in self.rows if r['evidence_id'] == key), None)


def reconciliation_case(monkeypatch, rows=None, **payload_changes):
    scope = {'access_owner': 'fixture:group', 'workspace_id': 'fixture:workspace',
             'enterprise_id': 'fixture:group'}
    package = SimpleNamespace(identity=SimpleNamespace(enterprise_id='fixture:group'))
    payload = {'enterprise_id': 'fixture:group', 'statement': 'Example assertion',
               'status': 'accepted'} | payload_changes
    candidate = {'original_source_id': 'fixture:source-cell', 'payload': payload}
    monkeypatch.setattr(repository, 'EvidenceRepository', lambda: ReadOnlyExampleEvidence(rows or []))
    return candidate, package, scope


def test_existing_reconciler_returns_proposal_not_receipt_for_new_fixture(monkeypatch):
    c, package, scope = reconciliation_case(monkeypatch)
    out = mapping.evidence_reconciliation(c, package, scope=scope)
    assert out['kind'] == 'new' and out['disposition'] == 'propose_create'
    assert out['canonical_id'] == 'fixture:source-cell'
    assert not any(k in out for k in ('approval_id', 'execution_receipt_id', 'accepted'))


@pytest.mark.parametrize('state', ['revoked', 'withdrawn', 'retracted', 'expired', 'rejected', 'candidate'])
def test_existing_reconciler_does_not_reuse_noncurrent_fixture_target(state, monkeypatch):
    c, package, scope = reconciliation_case(monkeypatch)
    row = dict(c['payload'], evidence_id='fixture:evidence',
               source_external_id=c['original_source_id'], governed_source_scope=scope,
               lifecycle_state=state)
    c, package, scope = reconciliation_case(monkeypatch, [row])
    out = mapping.evidence_reconciliation(c, package, scope=scope)
    assert out['disposition'] == 'unresolved' and out['kind'] == 'unresolved identity'


def test_existing_reconciler_stops_multiple_canonical_targets(monkeypatch):
    c, package, scope = reconciliation_case(monkeypatch)
    rows = [dict(c['payload'], evidence_id=key, source_external_id=c['original_source_id'],
                 governed_source_scope=scope) for key in ('fixture:one', 'fixture:two')]
    c, package, scope = reconciliation_case(monkeypatch, rows)
    out = mapping.evidence_reconciliation(c, package, scope=scope)
    assert out['disposition'] == 'unresolved' and out['canonical_id'] == ''


@pytest.mark.parametrize('field,value', [('enterprise_id', 'fixture:other'),
                                        ('workspace_id', 'fixture:foreign-workspace')])
def test_existing_reconciler_rejects_cross_owner_or_tenant_target(field, value, monkeypatch):
    c, package, scope = reconciliation_case(monkeypatch)
    target_scope = dict(scope)
    target_scope[field] = value
    row = dict(c['payload'], evidence_id='fixture:evidence', governed_source_scope=target_scope)
    if field == 'enterprise_id': row['enterprise_id'] = value
    c, package, scope = reconciliation_case(monkeypatch, [row])
    with pytest.raises(review.BlueprintReviewError, match='crosses Enterprise'):
        mapping.evidence_reconciliation(c, package, scope=scope,
                                        canonical_id='fixture:evidence', disposition='map_existing')


def test_existing_reconciler_requires_contradiction_resolution(monkeypatch):
    c, package, scope = reconciliation_case(monkeypatch, contradiction_state='open')
    out = mapping.evidence_reconciliation(c, package, scope=scope)
    assert out['kind'] == 'contradictory' and out['disposition'] == 'conflict'


@pytest.mark.parametrize('metadata', [{'freshness': 'stale'}, {'withdrawn': True},
                                      {'retracted': True}, {'core_contradiction': True}])
def test_current_mapping_lifecycle_helper_is_not_complete_source_revocation_policy(metadata):
    # An observed implementation gap, not desirable future admission behaviour.
    # EAR never treats this helper alone as use/admission/acceptance authority.
    assert mapping.evidence_is_current({'lifecycle_state': 'accepted', **metadata})
    assert not q.proof()['canonical_admission_proven']


@pytest.mark.parametrize('decision,expected', [(None, 'unresolved'), ('defer', 'defer'),
                                             ('reject', 'reject'), ('quarantine', 'quarantine')])
def test_stateless_existing_plan_effect_is_not_a_persisted_approval(decision, expected):
    candidate = {'candidate_record_id': 'fixture:candidate', 'candidate_object_class': 'evidence',
                 'original_source_id': 'fixture:source-cell', 'import_run_id': 'fixture:run',
                 'validation_status': 'accepted', 'payload': {}}
    dec = {'decision': decision} if decision else None
    # _effect is stateless. create_plan would write plans+ledger and is forbidden here.
    effect = planning.DryRunPlanningService._effect(None, candidate, dec, None)
    assert effect.effect_type == expected and effect.expected_mutation_count == 0
    assert effect.actual_mutation_count == 0 and not effect.canonical_id


@pytest.mark.parametrize('cls,method,args', [
    (review.CandidateReviewService, 'record_decision', ('fixture:candidate', 'approve', 'pretend-owner', 'reason', {})),
    (mapping.ImportMappingService, 'record_mapping', ({}, 'map_existing', 'pretend-owner', {})),
    (planning.DryRunPlanningService, 'create_plan', ('fixture:run', 'pretend-owner', {})),
    (promotion.CanonicalPromotionService, 'approve_plan', ('fixture:run', 'fixture:plan', 'pretend-owner', 'reason', {})),
    (promotion.CanonicalPromotionService, 'execute_approved_plan', ('fixture:run', 'fixture:approval', 'pretend-owner', {})),
])
def test_real_write_boundaries_deny_before_uninitialised_service_body(cls, method, args):
    # No dependency constructor, repositories or fixture approval bypass.
    obj = object.__new__(cls)
    with pytest.raises(PermissionError):
        getattr(obj, method)(*args)


def test_actual_scoped_session_cannot_review_foreign_enterprise_or_workspace(authority, tmp_path):
    from cios.applications.flora.access import require_resource_scope
    store, token, csrf, headers, old = signed(authority, tmp_path)
    for enterprise, workspace in [('fixture:NatWest-Group-not-authorised', 'synthetic-workspace'),
                                  ('synthetic-enterprise', 'fixture:other-workspace')]:
        with pytest.raises(PermissionError):
            require_resource_scope(headers, 'package.review', enterprise, workspace)
    store.logout(token, csrf)
    assert not review.can_review_blueprint_candidate(headers, 'synthetic-enterprise', 'synthetic-workspace')


def test_enabled_or_semantically_compatible_metadata_never_bypasses_publisher_policy():
    with pytest.raises(ValueError, match='approved official-publisher'):
        official_url(q.URL)
    metadata = dict(url=q.URL, retrieval_url=q.URL, retrieved_at='2026-11-15T12:00:00Z',
                    title='NatWest Q3', publisher='NatWest Group plc', reporting_period='2026-09-30',
                    reviewed_by='fixture:reviewer-not-authority', review_notes='Research only',
                    enabled=True, source_permitted=True, provenance_verified=True)
    with pytest.raises(ValueError, match='approved official-publisher'):
        provenance(metadata)


def test_runtime_architecture_history_source_permissions_and_comparator_unchanged():
    protected = ['cios', 'architecture', 'enterprise-knowledge', 'tools/research/history_integrity.py',
                 'tools/ci/flora_ci.py', 'tools/ci/baselines', 'docs/flora-runtime/bie2',
                 'docs/flora-runtime/bie3', 'docs/flora-runtime/eai1-628', 'docs/flora-runtime/eai2']
    subprocess.run(['git', 'diff', '--exit-code', BASE, '--', *protected], cwd=q.ROOT,
                   capture_output=True, check=True)
    from tools.research.history_integrity import approved_history
    assert len(approved_history(q.ROOT)) == 173


def test_proof_output_is_reproducible_without_network_and_contains_no_owner_receipts():
    assert q.proof(as_of=date(2026, 11, 15)) == q.proof(as_of=date(2026, 11, 15))
    text = json.dumps(q.proof())
    assert 'fixture:' not in text
    for forbidden in ('£0.9', 'procurement budget confirmed', 'accepted Evidence created'):
        assert forbidden not in text
