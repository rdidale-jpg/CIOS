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


@pytest.mark.parametrize('bundle', CASES, ids=[r['commission']['industry'] for r in CASES])
def test_commercial_replay_updates_existing_memory(bundle, tmp_path, monkeypatch, verified_flora_test_authority):
    from cios.applications.flora.memory.commercial_views import replay_sections
    from cios.applications.flora.enterprise_canvas.access import (
        EnterpriseCanvasAccessRecord, EnterpriseCanvasAccessRepository,
    )
    from cios.applications.flora.web.app import FloraWebHandler
    from cios.applications.flora.memory.repository import EvidenceRepository
    from cios.applications.flora.research_intelligence.commercial_factory import prepare_commercial

    commission = bundle['commission']
    enterprise = commission['enterprise_id']
    title = commission['legal_name'] + ' · isolated commercial evidence'
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'store'))
    monkeypatch.setenv('FLORA_PILOT_DIR', str(tmp_path / 'store'))
    register = prepare(commission, read_replay(bundle, tmp_path), families())
    sources = json.loads(REPLAY.with_name('commercial-replay.json').read_text())[enterprise]
    result = prepare_commercial(register, commission, sources)
    if live_report := os.getenv('CIOS_FACTORY_LIVE_RESULT'):
        result = next(row for row in json.loads(Path(live_report).read_text())
                      if row['enterprise_id'] == enterprise)
        assert result['commercial_live_records'] >= 4
        assert result['commercial_replay_records'] == 0
    else:
        assert len(result['records']) >= 16
    assert sum(v == 'Partial' for v in result['coverage'].values()) >= (5 if live_report else 6)
    before = replay_sections(enterprise, enterprise)
    actor = 'isolated-commercial-reviewer'
    headers = {'X-Flora-User': actor, 'X-Flora-Enterprises': enterprise,
               'X-Flora-Roles': 'package.review,candidate.promote'}
    monkeypatch.setenv('FLORA_ENVIRONMENT', 'development')
    monkeypatch.setenv('FLORA_FACTORY_ROUTE_REPLAY', '1')
    alias, route = {
        'lloyds-banking-group-plc': ('lloyds', '/enterprises/lloyds?'),
        'bt-group-plc': ('bt-group-plc', '/digital-twins/bt-group-plc/canvas?'),
        'arm-holdings-plc': ('arm', '/industries/technology/experience/enterprise?enterprise=arm&'),
        'easyjet-plc': ('easyjet', '/enterprises/easyjet/preview?'),
    }[enterprise]
    EnterpriseCanvasAccessRepository().save(EnterpriseCanvasAccessRecord(
        '1.0', alias, enterprise, enterprise, actor,
        acl=({'principal_id': actor, 'role': 'owner', 'grant_source': 'test-binding'},),
    ))

    def route_page(perspective, request_headers=headers, reading='facts'):
        handler = object.__new__(FloraWebHandler)
        stream = '' if alias == 'arm' else f'stream={perspective}&'
        handler.path = f'{route}{stream}reading={reading}'
        handler.headers = request_headers
        handler.requestline = f"GET {handler.path} HTTP/1.1"
        handler.storage_status = {'ready': True}
        output = []
        handler._body = lambda *args, **kwargs: output.append(args)
        handler.send_error = lambda code, message: output.append((code, message.encode()))
        handler.do_GET()
        assert len(output) == 1
        return next(item.decode() for item in output[0] if isinstance(item, bytes))

    route_before = route_page('landscape')
    assert 'data-factory-perspective' not in route_before
    archive = blueprint_archive(result)
    package = BlueprintPackageRegistry().receive(archive, 'commercial.zip', actor, enterprise)
    validator = BlueprintPackageValidator()
    assert validator.validate_and_stage(package.package_ref, actor, headers).records_accepted_into_staging == len(result['records'])
    for row in validator.staging_summary(package.import_run_id)['candidates']:
        CandidateReviewService().record_decision(
            row['candidate_record_id'], 'approve', actor, 'Scoped fixture replay', headers)
    plan = DryRunPlanningService().create_plan(package.import_run_id, actor, headers)
    promotion = CanonicalPromotionService()
    approval = promotion.approve_plan(package.import_run_id, plan.plan_id, actor, 'Scoped fixture replay', headers)
    assert promotion.execute_approved_plan(package.import_run_id, approval.approval_id, actor, headers).actual_mutation_count == len(result['records'])
    assert promotion.execute_approved_plan(package.import_run_id, approval.approval_id, actor, headers).final_execution_status == 'repeat_no_change'
    after = replay_sections(enterprise, enterprise)
    assert after in factual_digital_twin_workspace(enterprise, isolated_workspace=enterprise)
    assert after not in factual_digital_twin_workspace(enterprise)
    if commission['industry'] == 'Technology':
        assert '53.6%' in after
    for perspective in ('landscape', 'inside', 'forces'):
        assert '<article' in after.split(f'id="factory-{perspective}"')[1].split('</section>')[0]
    for perspective in ('landscape', 'inside', 'forces'):
        assert f'data-factory-perspective="{perspective}"' in route_page(perspective)
    route_after = route_page('landscape')
    assert 'data-factory-perspective' not in route_page('landscape', {})
    foreign = dict(headers, **{'X-Flora-Enterprises': 'foreign-workspace'})
    assert 'data-factory-perspective' not in route_page('landscape', foreign)
    if commission['industry'] == 'Technology':
        assert '53.6%' in route_page('landscape', reading='insight')
    with monkeypatch.context() as disabled:
        disabled.setenv('FLORA_FACTORY_ROUTE_REPLAY', '0')
        assert 'data-factory-perspective' not in route_page('landscape')
    assert 'No current scoped evidence' in before
    assert '<article' not in replay_sections(enterprise, 'foreign-workspace')
    if output := os.getenv('CIOS_FACTORY_EXAMPLE_OUTPUT'):
        for state, body in [('route-before', route_before), ('route-after', route_after)]:
            (Path(output) / f'{enterprise}-{state}.html').write_text(body)
        for state, body in [('before', before), ('after', after)]:
            (Path(output) / f'{enterprise}-{state}.html').write_text(_page(title, '<h1>'+title+'</h1>'+body))
    repository = EvidenceRepository()
    ev = next(e for e in repository.list() if e.get('use_scope') == 'isolated_commercial_replay')
    assert ev['statement'] in after
    repository.save(dict(ev, status='withdrawn'))
    assert ev['statement'] not in replay_sections(enterprise, enterprise)
    assert ev['statement'] not in route_page(ev['perspective'])


def test_commercial_digest_rejects_tampering_and_withdrawal_isolates_repeats(tmp_path):
    from cios.applications.flora.research_intelligence.commercial_factory import prepare_commercial

    bundle = CASES[0]
    commission = bundle['commission']
    base = prepare(commission, read_replay(bundle, tmp_path), families())
    sources = json.loads(REPLAY.with_name('commercial-replay.json').read_text())[commission['enterprise_id']]
    tampered = deepcopy(sources[1])
    tampered['claims'][0]['statement'] = 'An unreviewed assertion.'
    withdrawn = dict(sources[0], withdrawn=True)
    result = prepare_commercial(base, commission, [*sources, withdrawn, tampered])
    statements = [row['payload'].get('statement', '') for row in result['records']]
    assert not any('Envoy' in text or 'unreviewed' in text for text in statements)
    assert any('Natasha Condon' in text for text in statements)
    assert result['held']['commercial disclosure held or provenance invalid'] >= 7


def test_disclosure_acquisition_does_not_replay_changed_or_denied_sources():
    from urllib.error import HTTPError

    from cios.applications.flora.research_intelligence.disclosure_acquisition import acquire_disclosures
    from cios.applications.flora.research_intelligence.initial_factory import fingerprint

    sources = json.loads(REPLAY.with_name('commercial-replay.json').read_text())
    source = sources['arm-holdings-plc'][0]
    held = dict(source, status='withdrawn')
    calls = []

    def fetch(url):
        calls.append(url)
        return b'<p>Licensing and other revenue of USD 773 million.</p>', '.html'

    live, untouched = acquire_disclosures([source, held], fetch)
    assert len(calls) == 1
    assert len(live['claims']) == 1
    assert len(live['live_content_sha256']) == 64
    assert live['sha256'] == fingerprint({k: v for k, v in live.items() if k not in {'sha256', 'status'}})
    assert untouched == held

    def denied(url):
        raise HTTPError(url, 403, 'Access denied', None, None)

    def unavailable(url):
        raise TimeoutError()

    assert acquire_disclosures([source], denied)[0]['status'] == 'restricted'
    assert acquire_disclosures([source], unavailable) == [source]
    changed = acquire_disclosures([source], lambda url: (b'<p>Different disclosure</p>', '.html'))
    assert changed[0]['status'] == 'restricted'
    assert changed[0]['claims'] == []
