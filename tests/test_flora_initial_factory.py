"""Explicit non-production authority for the commissioning replay."""
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
from cios.applications.flora.memory.repository import EnterpriseModelRepository
from cios.applications.flora.memory.views import factual_digital_twin_workspace
from cios.applications.flora.research_intelligence.initial_factory import blueprint_archive, prepare
from cios.applications.flora.workspace.views import _page
from tools.research.initial_factory import families, read_replay

REPLAY = Path('docs/research/initial-factory/register-replay.json')
CASES = json.loads(REPLAY.read_text())


@pytest.mark.parametrize('bundle', CASES, ids=[r['commission']['industry'] for r in CASES])
def test_four_industry_blueprint_replay(bundle, tmp_path, monkeypatch, verified_flora_test_authority):
    commission = bundle['commission']
    enterprise = commission['enterprise_id']
    title = commission['legal_name'] + ' · isolated factual workspace'
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'store'))
    monkeypatch.setenv('FLORA_PILOT_DIR', str(tmp_path / 'store'))
    raw = read_replay(bundle, tmp_path)
    held = deepcopy(raw[0])
    held['metadata']['withdrawn'] = True
    held['metadata']['expected_sha256'] = 'different-withdrawn-version'
    result = prepare(commission, [*raw, raw[0], held], families())
    assert len(result['records']) == 8
    assert set(result['held']) == {'unavailable, restricted or mismatched acquisition', 'repeated register assertion'}
    edge, = result['relationship_candidates']
    assert edge['object_registration'] == commission['registration_number']
    assert edge['subject_registration'] == commission['controlled_registrations'][0]
    assert len(result['coverage']) == 31
    assert sum(level == 'Partial' for level in result['coverage'].values()) == 2
    archive = blueprint_archive(result)
    assert archive == blueprint_archive(prepare(commission, [held, raw[0], *raw], families()))
    name = 'isolated-reviewer'
    headers = {'X-Flora-User': name, 'X-Flora-Enterprises': enterprise,
               'X-Flora-Roles': 'package.review,candidate.promote'}
    before = _page(title, factual_digital_twin_workspace(enterprise, title=title))
    package = BlueprintPackageRegistry().receive(archive, 'review.zip', name, enterprise)
    validator = BlueprintPackageValidator()
    validation = validator.validate_and_stage(package.package_ref, name, headers)
    assert validation.records_accepted_into_staging == 8
    review = CandidateReviewService()
    for row in validator.staging_summary(package.import_run_id)['candidates']:
        review.record_decision(row['candidate_record_id'], 'approve', name,
                               'Isolated test fixture for inspected register records', headers)
    plan = DryRunPlanningService().create_plan(package.import_run_id, name, headers)
    assert plan.expected_canonical_mutation_count == 8
    service = CanonicalPromotionService()
    approval = service.approve_plan(package.import_run_id, plan.plan_id, name, 'Isolated replay', headers)
    outcome = service.execute_approved_plan(package.import_run_id, approval.approval_id, name, headers)
    assert outcome.actual_mutation_count == 8
    assert service.execute_approved_plan(package.import_run_id, approval.approval_id, name, headers).final_execution_status == 'repeat_no_change'
    assert len(EnterpriseModelRepository().get(enterprise).attributes) == 4
    after = _page(title, factual_digital_twin_workspace(enterprise, title=title))
    assert 'identity.register_classification' in after and 'identity.register_classification' not in before
    assert not (tmp_path / 'store' / 'pipeline').exists()
    if output := os.getenv('CIOS_FACTORY_EXAMPLE_OUTPUT'):
        for state, page in [('before', before), ('after', after)]:
            (Path(output) / f'{enterprise}-{state}.html').write_text(page)


def test_same_period_conflicts_quarantined_and_wrong_identity_held(tmp_path):
    from tools.research.initial_factory import acquisition
    bundle = CASES[1]
    commission = bundle['commission']
    raw = read_replay(bundle, tmp_path)
    document = bundle['captures'][0]
    conflicting = acquisition(document['reviewed_field_anchors'].replace('>Active<', '>Dissolved<').encode(),
                              document['url'], commission['as_of'], tmp_path)
    wrong = deepcopy(raw[0])
    wrong['metadata']['url'] = CASES[2]['captures'][0]['url']
    result = prepare(commission, [*raw, conflicting, wrong], families())
    assert result['conflicts'] == [{'attribute': 'identity.register_status', 'observed': commission['as_of']}]
    assert 'unavailable, restricted or mismatched acquisition' in result['held']
    assert len(result['records']) == 6


def test_withdrawn_version_cannot_be_reintroduced_as_independent_copy(tmp_path):
    bundle = CASES[0]
    overview, control = read_replay(bundle, tmp_path)
    withdrawn = deepcopy(control)
    withdrawn['metadata']['withdrawn'] = True
    report = prepare(bundle['commission'], [overview, control, withdrawn], families())
    assert len(report['records']) == 6
    assert report['relationship_candidates'] == []
    assert report['held']['unavailable, restricted or mismatched acquisition'] == 2
