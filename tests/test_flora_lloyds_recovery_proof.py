"""Lloyds recovery: existing owners, explicit temporary authority, no runtime adapter.

The retained commercial replay has claim-binding checksums, not original source
bytes. Passing these tests proves service integration, NOT factual re-verification,
source-use permission, production canonical import or public Gold eligibility.
"""
from copy import deepcopy
import json
import os
from pathlib import Path

import pytest

from cios.applications.flora.blueprint_import import (
    BlueprintPackageRegistry, BlueprintPackageValidator, CandidateReviewService,
    DryRunPlanningService,
)
from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService
from cios.applications.flora.enterprise_canvas.access import (
    EnterpriseCanvasAccessRecord, EnterpriseCanvasAccessRepository,
)
from cios.applications.flora.memory.commercial_views import replay_sections, route_replay
from cios.applications.flora.memory.repository import EvidenceRepository, EnterpriseModelRepository
from cios.applications.flora.research_intelligence.commercial_factory import prepare_commercial
from cios.applications.flora.research_intelligence.initial_factory import blueprint_archive, fingerprint, prepare
from tools.research.initial_factory import families, read_replay

BASE = Path('docs/research/initial-factory')
ENTERPRISE = 'lloyds-banking-group-plc'
CASES = {'division': {'commercial_unit', 'condon'}, 'ai': {'envoy', 'envoy_google'}}


def retained_case(case):
    bundle = next(row for row in json.loads((BASE / 'register-replay.json').read_text())
                  if row['commission']['enterprise_id'] == ENTERPRISE)
    sources = json.loads((BASE / 'commercial-replay.json').read_text())[ENTERPRISE]
    selected = [deepcopy(row) for row in sources
                if {c['key'] for c in row['claims']} & CASES[case]]
    assert len(selected) == 1
    assert {c['key'] for c in selected[0]['claims']} == CASES[case]
    held = next(row for row in sources if row.get('hold'))
    return bundle, selected, held


def compile_case(case, directory):
    bundle, selected, held = retained_case(case)
    commission = bundle['commission']
    identity = prepare(commission, read_replay(bundle, directory), families())
    # Include the actual existing held financial record. It must stay held even
    # when unrelated divisional/operating disclosures compile successfully.
    return prepare_commercial(identity, commission, [*selected, held])


@pytest.mark.parametrize('case', CASES)
def test_recovered_facts_through_existing_model_and_projection(
        case, tmp_path, monkeypatch, verified_flora_test_authority):
    for key in ('FLORA_DATA_DIR', 'FLORA_PILOT_DIR'):
        monkeypatch.setenv(key, str(tmp_path / 'isolated'))
    monkeypatch.setenv('FLORA_ENVIRONMENT', 'development')
    monkeypatch.setenv('FLORA_FACTORY_ROUTE_REPLAY', '1')
    result = compile_case(case, tmp_path)
    assert result['held']['commercial disclosure held or provenance invalid'] == 1
    assert len(result['records']) == 12  # 4 register + 2 commercial assertions, E/O pairs
    assert blueprint_archive(result) == blueprint_archive(compile_case(case, tmp_path))
    commercial = [r['payload'] for r in result['records']
                  if r['record_class'] == 'evidence' and r['payload'].get('use_scope')]
    assert len(commercial) == 2
    assert all(r['recorded_replay'] and not r['live_content_sha256'] for r in commercial)
    assert all(r['reporting_scope'] == 'Lloyds Banking Group plc' for r in commercial)
    statements = [r['statement'] for r in commercial]
    assert not any('structural hedge' in str(r) for r in result['records'])
    actor = 'isolated-recovery-reviewer'
    headers = {'X-Flora-User': actor, 'X-Flora-Enterprises': ENTERPRISE,
               'X-Flora-Roles': 'package.review,candidate.promote'}
    EnterpriseCanvasAccessRepository().save(EnterpriseCanvasAccessRecord(
        '1.0', 'lloyds', ENTERPRISE, ENTERPRISE, actor,
        acl=({'principal_id': actor, 'role': 'owner', 'grant_source': 'explicit-test-binding'},)))
    shell = '<main><h1>Isolated existing-owner proof; not public Gold</h1></main>'
    streams = sorted({row['perspective'] for row in commercial})
    project = lambda h=headers: '\n'.join(route_replay(
        shell, '/enterprises/lloyds', {'stream': [stream]}, h) for stream in streams)
    before = project()
    assert all(s not in before for s in statements)
    registry = BlueprintPackageRegistry()
    package = registry.receive(blueprint_archive(result), case + '.zip', actor, ENTERPRISE)
    validator = BlueprintPackageValidator()
    assert validator.validate_and_stage(package.package_ref, actor, headers).records_accepted_into_staging == 12
    for candidate in validator.staging_summary(package.import_run_id)['candidates']:
        CandidateReviewService().record_decision(candidate['candidate_record_id'], 'approve', actor,
            'Temporary test authority ONLY; retained replay, no source/publication acceptance', headers)
    plan = DryRunPlanningService().create_plan(package.import_run_id, actor, headers)
    promotion = CanonicalPromotionService()
    for denied in ({}, dict(headers, **{'X-Flora-Enterprises': 'other-workspace'})):
        with pytest.raises(PermissionError):
            promotion.approve_plan(package.import_run_id, plan.plan_id, actor, 'Denied', denied)
    approval = promotion.approve_plan(package.import_run_id, plan.plan_id, actor,
                                     'Isolated service integration proof, not production authority', headers)
    execute = lambda: promotion.execute_approved_plan(package.import_run_id, approval.approval_id, actor, headers)
    assert execute().actual_mutation_count == 12
    model = EnterpriseModelRepository().get(ENTERPRISE)
    assert len(model.attributes) == 6
    assert execute().final_execution_status == 'repeat_no_change'
    assert EnterpriseModelRepository().get(ENTERPRISE) == model
    after = project()
    assert all(s in after for s in statements)
    assert all(s not in project({}) for s in statements)
    assert all(s not in project(dict(headers, **{'X-Flora-User': 'other-actor'})) for s in statements)
    assert all(s not in project(dict(headers, **{'X-Flora-Enterprises': 'other-workspace'})) for s in statements)
    assert all(s not in replay_sections('other-enterprise', ENTERPRISE, perspective='inside') for s in statements)
    monkeypatch.setenv('FLORA_ENVIRONMENT', 'pilot')
    assert all(s not in project() for s in statements)
    monkeypatch.setenv('FLORA_ENVIRONMENT', 'development')
    repository = EvidenceRepository()
    rows = [r for r in repository.list() if r.get('use_scope') == 'isolated_commercial_replay']
    assert len(rows) == 2
    # An explicit Evidence withdrawal is the existing available mechanism for
    # this legacy replay. No invented document-byte digest/lifecycle receipt.
    for row in rows:
        repository.save(dict(row, status='withdrawn'))
    assert all(s not in project() for s in statements)
    assert EnterpriseModelRepository().get(ENTERPRISE) == model  # history retained
    # A changed assertion cannot reuse the old supporting Observation as though
    # nothing changed; the read-time exact-statement check fails closed.
    for row in rows:
        repository.save(dict(row, status='current', statement='Deliberately mismatched test correction.'))
    assert all(s not in project() for s in statements)
    assert EnterpriseModelRepository().get(ENTERPRISE) == model
    assert not any(p.exists() for p in (
        tmp_path / 'isolated' / 'financial_intelligence',
        tmp_path / 'isolated' / 'sales_pipeline', tmp_path / 'isolated' / 'pipeline'))
    assert {p.name for p in (tmp_path / 'isolated').iterdir()} <= {
        'memory', 'blueprint_import', 'enterprise_canvas'}
    if output := os.getenv('CIOS_LLOYDS_RECOVERY_OUTPUT'):
        target = Path(output)
        target.mkdir(parents=True, exist_ok=True)
        report = {'case': case, 'authority': 'temporary verified_flora_test_authority only',
                  'factual_assurance': 'retained attributed replay; no new original-source verification',
                  'publication_eligible': False, 'production_activation': False,
                  'candidate_streams': streams,
                  'register_assertions': 4, 'recovered_assertions': 2,
                  'isolated_service_mutations': 12, 'derived_model_attributes': 6,
                  'repeat': 'repeat_no_change', 'candidate_statements': statements,
                  'withdrawal': 'Evidence withdrawal removes both dependent presentation statements',
                  'correction': 'mismatched evidence/Observation suppressed; model history unchanged',
                  'source_lifecycle_limit': 'legacy replay has no original-byte document revision binding',
                  'denials': ['guest', 'other actor', 'other workspace', 'other enterprise', 'pilot runtime'],
                  'financial_record': 'held before staging; no new Financial run',
                  'source_bindings': [{'publisher': r['publisher'], 'period': r['period'],
                    'source_url': r['source_url'], 'source_locator': r['source_locator'],
                    'binding_sha256_not_document_bytes': r['source_content_sha256']} for r in commercial]}
        (target / (case + '.json')).write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')


@pytest.mark.parametrize('case', CASES)
@pytest.mark.parametrize('mutation', ['entity', 'scope', 'date', 'checksum', 'withdrawal'])
def test_bad_source_bindings_never_become_candidates(case, mutation):
    bundle, sources, _ = retained_case(case)
    source = deepcopy(sources[0])
    if mutation == 'entity':
        source['enterprise_id'] = 'lloyds-bank-plc'  # subsidiary is not the Group
    elif mutation == 'scope':
        source['claims'][0]['scope'] = 'Lloyds Bank plc'
    elif mutation == 'date':
        source['published'] = '2027-01-01'
    elif mutation == 'withdrawal':
        source['withdrawn'] = True
    if mutation != 'checksum':
        source['sha256'] = fingerprint({k: v for k, v in source.items()
                                       if k not in {'sha256', 'withdrawn', 'status'}})
    else:
        source['sha256'] = '0' * 64
    base = {'enterprise_id': ENTERPRISE, 'records': [], 'coverage': dict.fromkeys(families(), 'Unknown'),
            'models': {}, 'held': {}, 'conflicts': []}
    result = prepare_commercial(base, bundle['commission'], [source])
    assert len(result['records']) == (2 if mutation == 'scope' else 0)
    if mutation == 'scope':
        assert all(r['payload'].get('statement') != source['claims'][0]['statement'] for r in result['records'])


@pytest.mark.parametrize('corruption', [None, 'head', 'runtime', 'withdrawal', 'touch', 'screenshot'])
def test_current_browser_evidence_checker_rejects_invalid_bindings(tmp_path, corruption):
    """Checker unit inputs; NOT a claim that this test ran a real browser."""
    import importlib.util
    import subprocess
    from hashlib import sha256
    path = Path('docs/research/lloyds-intelligence-recovery/check_canvas_browser.py')
    spec = importlib.util.spec_from_file_location('recovery_canvas_check', path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    # Reuse the historical metadata shape, explicitly rebind this unit input to
    # HEAD and one test byte-string. Actual hosted evidence is produced by the
    # unchanged browser runner, not by this unit fixture.
    proof = json.loads(Path('docs/product/flora-experience/main-canvas/Browser-after.json').read_text())
    proof['sha'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    (tmp_path / 'unit-only.jpg').write_bytes(b'checker-unit-input-not-a-browser-capture')
    proof['screenshots'] = {'unit-only.jpg': sha256((tmp_path / 'unit-only.jpg').read_bytes()).hexdigest()}
    if corruption == 'head': proof['sha'] = '0' * 40
    elif corruption == 'runtime': proof['runtime_hashes'][next(iter(proof['runtime_hashes']))] = '0' * 64
    elif corruption == 'withdrawal': proof['withdrawal_history_reload_print_accessibility'] = False
    elif corruption == 'touch': proof['devices'][0]['physical_hits'] = False
    elif corruption == 'screenshot': proof['screenshots']['unit-only.jpg'] = '0' * 64
    (tmp_path / 'Browser-after.json').write_text(json.dumps(proof))
    if corruption is None:
        assert checker.check(tmp_path)['passed']
    else:
        with pytest.raises(AssertionError): checker.check(tmp_path)
