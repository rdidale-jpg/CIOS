"""Exercise reviewed source facts through the existing isolated authority and web routes."""
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
from cios.applications.flora.memory.repository import EvidenceRepository, EnterpriseModelRepository
from cios.applications.flora.research_intelligence.initial_factory import blueprint_archive
from cios.applications.flora.web.app import FloraWebHandler
from cios.applications.flora.research_intelligence.source_lifecycle import lifecycle_path
from cios.applications.flora.storage import atomic_write_json, data_path
from tools.research.verified_factory_proof import capture
from tests.flora_assurance_fixture import ARM, assess_existing_proof, fixture_handoff

FIXTURE = Path('docs/research/initial-factory/verified/isolated-records.json')
INVESTIGATION = FIXTURE.parent.parent / 'resolution/live-proof.json'
ROUTES = {
    'lloyds-banking-group-plc': ('lloyds', '/enterprises/lloyds?stream=forces'),
    'bt-group-plc': ('bt-group-plc', '/digital-twins/bt-group-plc/canvas?stream=inside'),
    'arm-holdings-plc': ('arm', '/industries/technology/experience/enterprise?enterprise=arm'),
    'easyjet-plc': ('easyjet', '/enterprises/easyjet/preview?stream=inside'),
}


@pytest.mark.parametrize('result', json.loads(FIXTURE.read_text()), ids=ROUTES)
def test_verified_change_route(result, tmp_path, monkeypatch, verified_flora_test_authority):
    enterprise = result['enterprise_id']
    if enterprise == ARM:
        # Use the newly recovered publisher revision in the existing isolated
        # test scope. The committed report itself grants no publication right.
        report = next(row for row in json.loads(INVESTIGATION.read_text())
                      if row['enterprise_id'] == ARM)
        assert report['factual_state'] == 'verified' and report['publication_eligible'] is False
        result = deepcopy(result)
        payload = result['records'][0]['payload']
        assert report['assurance']['assertion']['statement'] == payload['statement']
        original = next(row for row in report['observations'] if row['kind'] == 'notice')['reference']
        prior = payload['document_revisions'][-1]
        assert original['url'] == prior['url']
        prior['sha256'] = original['digest']
        payload['commercial_change']['corroboration']['sha256'] = original['digest']
    evidence, _ = result['records']
    headline = evidence['payload']['commercial_change']['headline']
    alias, route = ROUTES[enterprise]
    for key in ('FLORA_DATA_DIR', 'FLORA_PILOT_DIR'):
        monkeypatch.setenv(key, str(tmp_path / 'isolated'))
    monkeypatch.setenv('FLORA_ENVIRONMENT', 'development')
    monkeypatch.setenv('FLORA_FACTORY_ROUTE_REPLAY', '1')
    source_revisions = [dict(row, lifecycle='current')
                        for row in evidence['payload']['document_revisions']]

    def set_source_revisions():
        atomic_write_json(lifecycle_path(), {'schema_version': '1.0', 'revisions': source_revisions})

    set_source_revisions()
    actor = 'isolated-proof-approver'
    headers = {'X-Flora-User': actor, 'X-Flora-Enterprises': enterprise,
               'X-Flora-Roles': 'package.review,candidate.promote'}
    access = EnterpriseCanvasAccessRepository()
    access.save(EnterpriseCanvasAccessRecord('1.0', alias, enterprise, enterprise, actor,
                acl=({'principal_id': actor, 'role': 'owner', 'grant_source': 'test-binding'},)))

    def render(request_headers):
        handler = object.__new__(FloraWebHandler)
        handler.path = route
        handler.headers = request_headers
        handler.requestline = f'GET {route} HTTP/1.1'
        handler.storage_status = {'ready': True}
        output = []
        handler._body = lambda *args, **kwargs: output.append(args)
        handler.send_error = lambda code, message: output.append((code, message.encode()))
        handler.do_GET()
        return next(item.decode() for item in output[0] if isinstance(item, bytes))

    before = render(headers)
    assert 'data-commercial-change' not in before
    decision = assess_existing_proof(result, {(row['url'], row['sha256']) for row in source_revisions})
    handoff = fixture_handoff(decision, enterprise)
    assert handoff['eligible_for_isolated_handoff'] is (enterprise == ARM)
    assert decision['factual_state'] == ('verified' if enterprise == ARM else 'attributed_only')
    # The three existing issuer-only cards below reproduce the manually
    # reviewed comparison baseline. Only the Arm notice exercises automatic
    # eligibility under the explicitly scoped, test-only handoff.
    blueprint = BlueprintPackageRegistry().receive(blueprint_archive(result), 'scoped.zip', actor, enterprise)
    validator = BlueprintPackageValidator()
    assert validator.validate_and_stage(blueprint.package_ref, actor, headers).records_accepted_into_staging == 2
    for candidate in validator.staging_summary(blueprint.import_run_id)['candidates']:
        CandidateReviewService().record_decision(candidate['candidate_record_id'], 'approve',
                                                actor, (decision['decision_id'] if handoff['eligible_for_isolated_handoff']
                                                        else 'Isolated reviewed factual assertion'), headers)
    plan = DryRunPlanningService().create_plan(blueprint.import_run_id, actor, headers)
    service = CanonicalPromotionService()
    with pytest.raises(PermissionError):
        service.approve_plan(blueprint.import_run_id, plan.plan_id, actor, 'No authority', {})
    approved = service.approve_plan(blueprint.import_run_id, plan.plan_id, actor, 'Isolated proof', headers)
    execute = lambda: service.execute_approved_plan(blueprint.import_run_id, approved.approval_id, actor, headers)
    assert execute().actual_mutation_count == 2
    model = EnterpriseModelRepository().get(enterprise)
    assert execute().final_execution_status == 'repeat_no_change'
    assert EnterpriseModelRepository().get(enterprise) == model
    after = render(headers)
    assert 'data-commercial-change' in after and headline in after
    assert 'data-commercial-change' not in render({})
    other = dict(headers, **{'X-Flora-User': 'unauthorised-member'})
    assert 'data-commercial-change' not in render(other)
    monkeypatch.setenv('FLORA_ENVIRONMENT', 'pilot')
    assert 'data-commercial-change' not in render(headers)
    monkeypatch.setenv('FLORA_ENVIRONMENT', 'development')
    if output := os.getenv('CIOS_VERIFIED_ROUTE_OUTPUT'):
        Path(output).mkdir(parents=True, exist_ok=True)
        for state, markup in [('before', before), ('after', after)]:
            (Path(output) / f'{enterprise}-route-{state}.html').write_text(markup)
    repository = EvidenceRepository()
    row, = repository.list()
    stored_bytes = repository.path.read_bytes()
    source_revisions[-1]['lifecycle'] = 'withdrawn'
    set_source_revisions()
    degraded = assess_existing_proof(result, {(row['url'], row['sha256']) for row in source_revisions
                                               if row['lifecycle'] == 'current'})
    assert not fixture_handoff(degraded, enterprise)['eligible_for_isolated_handoff']
    assert repository.get(row['evidence_id'])['status'] == 'withdrawn'
    assert 'data-commercial-change' not in render(headers)
    assert repository.path.read_bytes() == stored_bytes
    assert EnterpriseModelRepository().get(enterprise) == model
    lifecycle_path().unlink()
    assert 'data-commercial-change' not in render(headers)
    source_revisions[-1]['lifecycle'] = 'current'
    original = source_revisions[-1]['sha256']
    source_revisions[-1]['sha256'] = '0' * 64
    set_source_revisions()
    assert 'data-commercial-change' not in render(headers)
    source_revisions[-1]['sha256'] = original
    set_source_revisions()
    assert 'data-commercial-change' in render(headers)
    repository.save(dict(row, status='withdrawn'))
    assert 'data-commercial-change' not in render(headers)
    assert not data_path('sales_pipeline', 'opportunities.json').exists()


def test_head_only_or_conflicting_passage_cannot_be_used_as_evidence():
    url = 'https://example.invalid/'
    for raw in (b'<head>service launched in Scotland</head><body>Publisher menu</body>',
                b'<body>Service cancelled in Scotland</body>'):
        with pytest.raises(ValueError, match='passage'):
            capture(url, ['service launched', 'Scotland'], lambda _: (raw, '.html'))


def test_unresolved_discovery_revisions_and_withdrawn_sources_are_held_before_fetch():
    from tools.research.verified_factory_proof import BASE, prepare_finding

    review = json.loads((BASE / 'verified/lead-review.json').read_text())[2]
    groups = json.loads((BASE / 'discovery/proof.json').read_text())
    discovery = next(row for group in groups for row in group['candidates']
                     if row['candidate_id'] == review['discovery_id'])

    def never_fetch(_):
        pytest.fail('Held source must not be fetched')

    with pytest.raises(ValueError, match='held'):
        prepare_finding(dict(review, status='withdrawn'), discovery, never_fetch)
    with pytest.raises(ValueError, match='held'):
        prepare_finding(review, dict(discovery, status='conflicting metadata'), never_fetch)


def test_missing_counterparty_corroboration_holds_the_arm_claim():
    from tools.research.verified_factory_proof import BASE, prepare_finding

    review = json.loads((BASE / 'verified/lead-review.json').read_text())[2]
    groups = json.loads((BASE / 'discovery/proof.json').read_text())
    discovery = next(row for group in groups for row in group['candidates']
                     if row['candidate_id'] == review['discovery_id'])

    def fetch(url):
        if url == review['url']:
            return (('<meta property="article:published_time" content="' + review['published'] + '">'
                     '<body>' + ' '.join(review['anchors']) + '</body>').encode(), '.html')
        return b'<body>Microsoft withdrew Cobalt availability.</body>', '.html'

    with pytest.raises(ValueError, match='passage changed'):
        prepare_finding(review, discovery, fetch)
