"""FIG-1 design assurance with explicit examples; no production admission."""
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

import pytest

from tools.research import fig1_demo as demo, fig1_quality as quality
from cios.applications.flora import intelligence_presentation as p
from tests.test_flora_security_repair_01b import authority, signed

pytestmark = pytest.mark.real_security_boundary
BASE = 'e7c58feb84882b0e7a1ea38e7e1c72079402aa86'


def test_five_banks_all_dimensions_actual_owner_audit_without_acceptance():
    report = quality.validate()
    assert report == {'design_qa_passed': True, 'bank_exemplars': 5, 'dimension_assessments': 50,
        'actual_gate_owners_assessed': 17, 'current_issuer_policy_denials': ['NW', 'HS', 'SA', 'NB', 'ST'],
        'new_rights_grants': 0, 'canonical_promotions': 0, 'runtime_changes': 0,
        'research_completeness_claim': False, 'proof_scope': 'fixed synthetic examples, not a live financial analyst'}


def test_nine_fixed_cases_are_reproducible_and_never_canonical():
    result = demo.demonstration()
    assert result == demo.demonstration()
    assert result == json.loads((demo.PACK/'Demo-Output.json').read_text())
    assert result['reported_stock']['as_at'] == '2026-09-30'
    assert result['reported_flow']['start'] == '2026-01-01'
    assert result['reported_flow']['end'] == '2026-09-30'
    assert result['compatible_calculation']['value'] == '5'
    assert result['compatible_calculation']['canonical_status'] == 'derived_view_not_canonical'
    assert Decimal(result['estimate']['value']) == Decimal('0.14')
    assert result['estimate']['assumptions'] and result['estimate']['caveats']
    assert all(result['conflict'][key] for key in ('primary_omitted', 'alternative_omitted'))
    assert result['conflict']['historical_positions_preserved_in_this_fixture'] == ['100', '101']
    assert result['superseded_omitted'] and result['revoked_source_omitted']
    assert result['typed_candidate_json_roundtrip']
    assert result['canonical_writes'] == result['new_source_permissions'] == result['paid_calls'] == 0
    assert result['owner_repository_reads'] == 0 and result['receipt_ids'] == []
    assert not result['canonical_acceptance_executed']


def test_six_existing_information_types_remain_distinct_in_example_rendering():
    rows = demo.fixtures()
    assert {r.semantic_type for r in rows.values()} == {'reported', 'calculated', 'estimated', 'assumed', 'insight', 'hypothesis'}
    assert all(r.canonical_status != 'accepted' for r in rows.values())
    for row in rows.values():
        html = p.render(row)
        assert 'data-semantic-type="'+row.semantic_type+'"' in html
        assert 'example.invalid' in html


@pytest.mark.parametrize('changes', [dict(scope='Example subsidiary'), dict(period='Other nine months'),
    dict(unit='USD billion'), dict(basis='Underlying instead of statutory'), dict(measurement_state='target')])
def test_existing_difference_rejects_incompatible_financial_inputs(changes):
    rows = demo.fixtures()
    with pytest.raises(ValueError, match='Incompatible'):
        p.difference(rows['flow'], replace(rows['costs'], **changes), text='Invalid comparison')


def test_stock_is_not_automatically_a_compatible_flow_or_a_cash_flow():
    rows = demo.fixtures()
    with pytest.raises(ValueError): p.difference(rows['flow'], rows['stock'], text='Not cash flow')
    assert 'point-in-time' in rows['stock'].period


@pytest.mark.parametrize('changes', [dict(method=''), dict(caveats=())])
def test_estimate_needs_visible_method_and_limits(changes):
    estimate = replace(demo.fixtures()['estimated'], **changes)
    assert not p.eligible(estimate) and p.render(estimate) == ''


@pytest.mark.parametrize('changes', [dict(assumption_owner=''), dict(assumption_version=''), dict(caveats=())])
def test_working_assumption_needs_owner_version_and_caveats(changes):
    assert not p.eligible(replace(demo.fixtures()['assumption'], **changes))


def test_arithmetic_does_not_erase_assumed_dependencies_or_make_reported_truth():
    result = demo.demonstration()['assumption_taint_current_contract']
    assert result['semantic_type'] == 'calculated'  # existing operation label, not desired automatic certainty
    assert result['dependency_types'] == ['reported', 'assumed']
    assert 'never Reported' in result['proposed_display_requirement']
    estimated = demo.fixtures()['estimated']
    assert estimated.semantic_type == 'estimated' and 'assumed' in estimated.dependency_types


@pytest.mark.parametrize('metadata', [{'rights': {'status': 'revoked'}}, {'rights': {'status': 'denied'}},
    {'rights': {'status': 'unknown'}}, {'withdrawn': True}, {'retracted': True},
    {'core_contradiction': True}, {'owner_only': True}, {'freshness': 'stale'}, {'freshness': 'superseded'}])
def test_existing_source_metadata_denial_is_applied_before_fixture_output(metadata):
    assert p.restricted_metadata(metadata)
    rendered = '' if p.restricted_metadata(metadata) else p.render(demo.fixtures()['stock'])
    assert rendered == ''


def test_a_nondenial_helper_result_is_not_source_permission():
    assert not p.restricted_metadata({})
    assert quality.validate()['new_rights_grants'] == 0
    # The actual caller must resolve source permission; the renderer cannot do so.


def test_current_numeric_temporal_and_lifecycle_contract_limits_are_honest():
    result = demo.current_contract_limits()
    assert result['deposit_metric_result'] == 'unsupported_metric'
    assert result['stock_date_misnormalised_currently']['period_end'] == '2026-03-31'
    assert not result['dynamic_numeric_field_survives_observation_reload']
    assert result['existing_provenance_dictionary_can_retain_typed_payload']
    assert not result['typed_payload_projection_currently_implemented']
    assert not result['deposit_numeric_prose_fallback_supported']
    assert all(result['mapping_helper_gap'].values())  # observed gaps, not desired future policy


def test_proof_does_not_use_canonical_repositories_services_network_or_providers(monkeypatch):
    from cios.applications.flora.memory import repository, service
    from cios.applications.flora.blueprint_import.review import CandidateReviewService
    from cios.applications.flora.blueprint_import.mapping import ImportMappingService
    from cios.applications.flora.blueprint_import.planning import DryRunPlanningService
    from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService
    def forbidden(*args, **kwargs): raise AssertionError('Forbidden owner/network operation in FIG-1 demo')
    for cls in (repository.EvidenceRepository, repository.ObservationRepository, repository.EnterpriseModelRepository):
        monkeypatch.setattr(cls, '__init__', forbidden)
    for cls, name in [(CandidateReviewService, 'record_decision'), (ImportMappingService, 'record_mapping'),
                      (DryRunPlanningService, 'create_plan'), (CanonicalPromotionService, 'approve_plan'),
                      (CanonicalPromotionService, 'execute_approved_plan'),
                      (service.ObservationMemoryService, 'process_evidence'),
                      (service.ObservationMemoryService, 'apply_observation')]:
        monkeypatch.setattr(cls, name, forbidden)
    monkeypatch.setattr(socket, 'create_connection', forbidden)
    assert demo.demonstration()['canonical_writes'] == 0
    assert quality.validate()['new_rights_grants'] == 0


@pytest.mark.parametrize('mutate', [
    lambda p: p['Banking-Exemplars'].pop(),
    lambda p: p['Banking-Exemplars'][0].update(subject='National Westminster Bank PLC'),
    lambda p: p['Banking-Exemplars'][0].update(real_canonical_ids=['guessed']),
    lambda p: p['Banking-Exemplars'][0].update(rights_status='permitted'),
    lambda p: p['Banking-Exemplars'][0].update(public_runtime_integration=True),
    lambda p: p['Banking-Exemplars'][0]['metrics'][1].update(unit='GBP million'),
    lambda p: p['Banking-Exemplars'][0]['metrics'][1].update(temporal_scope='9M2026'),
    lambda p: p['Banking-Exemplars'][0]['metrics'][1].update(measurement_state='target'),
    lambda p: p['Banking-Exemplars'][0]['metrics'][1].update(reported_value='453.4'),
    lambda p: p['Banking-Exemplars'][1]['metrics'][1].update(reported_value='701'),
    lambda p: p['Banking-Exemplars'][1]['metrics'][0].update(temporal_scope='Q32026'),
    lambda p: p['Banking-Exemplars'][2]['metrics'][5].update(temporal_scope='9M to2026-09-30'),
    lambda p: p['Banking-Exemplars'][3]['metrics'][6].update(reported_value='0'),
    lambda p: p['Banking-Exemplars'][4]['metrics'][5].update(basis='Active UK bank customers'),
    lambda p: p['Banking-Exemplars'][4]['metrics'][7].update(basis='Recognised annual revenue'),
    lambda p: p['Source-Ledger'][0].update(url='https://mirror.invalid/natwest.pdf'),
    lambda p: p['Source-Ledger'][0].update(original_bytes_sha256='0'*64),
    lambda p: p['Source-Ledger'][0].update(canonical_acceptance='accepted'),
    lambda p: p['Analysis-Specification']['coverage'][0]['dimensions'].pop('G'),
    lambda p: p['Analysis-Specification']['coverage'][0]['dimensions']['G'].update(status='complete'),
    lambda p: p['Gate-Audit'][0].update(symbol='invented_owner'),
    lambda p: p['Gate-Audit'][0].update(authority_change_executed=True),
])
def test_research_design_integrity_rejects_fabrication_or_scope_changes(mutate):
    pack = quality.load(); mutate(pack)
    with pytest.raises((ValueError, KeyError)): quality.validate(pack)


@pytest.mark.parametrize('script', ['fig1_demo.py', 'fig1_quality.py'])
def test_offline_scripts_are_portable_without_inherited_pythonpath(script, tmp_path):
    env = dict(os.environ); env.pop('PYTHONPATH', None)
    result = subprocess.run([sys.executable, str(demo.ROOT/'tools/research'/script)],
                            cwd=tmp_path, env=env, capture_output=True, text=True, check=True)
    assert json.loads(result.stdout)


def test_public_source_status_does_not_grant_private_scope(authority, tmp_path):
    from cios.applications.flora.access import require_resource_scope
    store, token, csrf, headers, _ = signed(authority, tmp_path)
    for enterprise, workspace in [('other-enterprise', 'synthetic-workspace'),
                                  ('synthetic-enterprise', 'other-workspace')]:
        with pytest.raises(PermissionError):
            require_resource_scope(headers, 'package.review', enterprise, workspace)
    store.logout(token, csrf)
    with pytest.raises(PermissionError):
        require_resource_scope(headers, 'package.review', 'synthetic-enterprise', 'synthetic-workspace')


def test_runtime_canonical_source_history_and_accepted_architecture_are_unchanged():
    # This assertion describes the accepted design-only FIG-1 cut. Later
    # owner-commissioned implementations must not be mistaken for FIG-1 edits.
    reviewed_design = '741e01c40dcc354213bf7f424c4cedf7af0c541b'
    subprocess.run(['git', 'diff', '--exit-code', BASE, reviewed_design, '--', 'cios', 'architecture', 'enterprise-knowledge',
                    'tools/research/history_integrity.py', 'tools/ci/flora_ci.py', 'tools/ci/flora-baseline-v1.json',
                    'docs/flora-runtime/bie2', 'docs/flora-runtime/bie3', 'docs/flora-runtime/eai1-628'],
                   cwd=demo.ROOT, capture_output=True, check=True)
    assert not (demo.ROOT/'tools/research/ear1_proof.py').exists()  # no EAR-1 branch integration
    from tools.research.history_integrity import approved_history
    assert len(approved_history(demo.ROOT)) == 175  # 173 preserved + exact two F1 candidates.
