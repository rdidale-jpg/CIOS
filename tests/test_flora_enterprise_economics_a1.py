"""Shipping A1, real owner reads, isolated negative mutations. No admission."""
from copy import deepcopy
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import json

import pytest

from cios.applications.flora import enterprise_economics as economics
from cios.applications.flora import visual_streams as v
from cios.applications.flora import easyjet_capabilities as easyjet
from cios.applications.flora import intelligence_presentation as p
from cios.applications.flora.financial_intelligence import candidate_analytics as financial
from tests.test_flora_f1_642 import authority, permitted

pytestmark = pytest.mark.real_security_boundary
BANK = '/enterprises/lloyds'
AIR = v.EASYJET_ROUTE


def main(path=BANK, detail='', reading='facts', headers=None):
    query = {'stream': ['landscape'], 'reading': [reading]}
    if detail:
        query['detail'] = [detail]
    html = v.render(path, query, headers or {})
    return html[html.index('<main '):html.index('</main>')]


@pytest.mark.parametrize('path,stages,title', [
    (BANK, ('funding', 'lending-income', 'profit-costs'), 'From funding to earnings'),
    (AIR, ('airline-revenue', 'airline-delivery', 'airline-return'), 'From seats to earnings'),
])
@pytest.mark.parametrize('reading', ['facts', 'insight'])
def test_three_connected_stages_share_modes_scope_and_native_urls(path, stages, title, reading):
    for stage in stages:
        html = main(path, stage, reading)
        assert title in html and html.count('data-stage=') == 3
        assert f'data-stage="{stage}"' in html
        assert html.count('aria-current="page"') >= 1
        assert 'econ-explanation" data-semantic-type="insight"' in html
        assert 'econ-explanation" data-semantic-type="assumed"' in html
        assert 'Illustrative' in html and 'not to scale' in html
        assert all(word not in html for word in ('What to investigate', 'No eligible reported measure', 'Research gap'))
        assert 'Source &amp; basis' not in html
        assert html.count('<details') == 0  # Existing Owner inspection retains provenance.
        assert 'reading=insight' not in html


def test_banking_stocks_flows_actuals_and_derived_comparison_keep_definitions():
    # Historical financial component remains at its existing explicit deep link.
    html = main(detail='funding')
    assert '£502.8bn' in html and 'Customer deposits · 30 Sep 2026' in html
    assert '£6.6bn' in html and 'Statutory pretax profit · 9m to 30 Sep 2026' in html
    assert '£6.3bn' in html and '31 December 2025 → 30 September 2026' in html
    assert 'not an organic inflow' in html
    assert 'data-semantic-type="calculated"' in html
    assert all(value not in html for value in ('£11.084bn', '£477.5bn', '3.21%', '.pdf'))
    assert 'Capital absorbs risk; it is not an expense' in main(detail='profit-costs')
    assert 'Lloyds Banking Group plc' in html


def test_aviation_uses_only_currently_released_operating_scale_no_research_financials():
    html = main(AIR)
    assert '356 aircraft' in html and '1,202 routes' in html
    assert 'Winter / summer 2025' in html and '30 September 2025' in html
    assert 'not daily flights' in html and 'not utilisation or profitability' in html
    assert all(value not in html for value in ('10,106', '9,309', '665m', '8.56%', 'AV-REVENUE', 'AV-PROFIT'))
    assert 'Network Planning' in html and 'Fleet Operations' in html
    assert 'Profit &amp; reinvestment' in html and 'econ-airline' in html


@pytest.mark.parametrize('scope,source_id,excluded,retained', [
    ('bank', 'PR-LBG-Q326', ('£502.8bn', '£6.6bn', '£6.3bn'), 'Funding'),
    ('bank', 'PR-LBG-AR25', ('£496.5bn', '£6.3bn'), '£502.8bn'),
    ('air', 'SRC-AV-AR25', ('356 aircraft', '1,202 routes'), 'Revenue'),
])
@pytest.mark.parametrize('field,value', [('withdrawn', True), ('owner_only', True), ('verification', 'unverified')])
@pytest.mark.parametrize('reading', ['facts', 'insight'])
def test_source_lifecycle_removes_every_representation(monkeypatch, scope, source_id, excluded, retained, field, value, reading):
    data = deepcopy(v.current_data(v.resolve(BANK, {'stream': ['landscape']}))) if scope == 'bank' else deepcopy(easyjet._data())
    source = next(row for row in data['sources'] if row['id'] == source_id)
    source[field] = value
    if scope == 'bank':
        monkeypatch.setattr(v, 'current_data', lambda ctx: data)
    else:
        monkeypatch.setattr(easyjet, '_read_assessment', lambda: data)
    html = main(BANK if scope == 'bank' else AIR, reading=reading)
    assert retained in html
    # Includes closed evidence, links, accessible text and print DOM; no cached
    # browser payload, alternate export or hidden numeric attributes exist.
    assert all(text not in html for text in excluded)


@pytest.mark.parametrize('field,value', [
    ('entity_scope', 'Lloyds Bank plc only'), ('reporting_period', 'Quarter ended 30 September 2026'),
    ('metric_unit', 'USD million'), ('metric_unit', 'GBP billion; average assets'),
    ('kind', 'management_target'), ('metric_value', 999.9), ('owner_only', True), ('withdrawn', True),
])
def test_changed_bank_measure_cannot_inherit_exact_source_meaning(monkeypatch, field, value):
    data = deepcopy(v.current_data(v.resolve(BANK, {'stream': ['landscape']})))
    next(row for row in data['claims'] if row['id'] == 'LBG-Q326-DEPOSITS')[field] = value
    monkeypatch.setattr(v, 'current_data', lambda ctx: data)
    html = main()
    assert '£502.8bn' not in html and '£6.3bn' not in html
    assert '£6.6bn' in html


@pytest.mark.parametrize('field,value', [
    ('entity_scope', 'easyJet airline only'), ('reporting_period', 'FY2026'),
    ('kind', 'hypothesis'), ('metric_value', 999), ('withdrawn', True),
])
def test_changed_aviation_claim_does_not_turn_history_into_current_company_data(monkeypatch, field, value):
    data = deepcopy(easyjet._data())
    next(row for row in data['claims'] if row['id'] == 'AV-FLEET')[field] = value
    monkeypatch.setattr(easyjet, '_read_assessment', lambda: data)
    html = main(AIR)
    assert '356 aircraft' not in html
    assert '1,202 routes' in html


def test_source_recheck_does_not_trust_stale_calculated_agenda(monkeypatch):
    from cios.applications.flora import leadership_agenda
    ctx = v.resolve(BANK, {'stream': ['landscape']})
    data = v.current_data(ctx)
    stale = leadership_agenda.agenda('lloyds', data)
    next(row for row in data['claims'] if row['id'] == 'LBG-AR25-DEPOSITS')['withdrawn'] = True
    html = economics.banking(ctx, data, stale, headers={})
    assert '£6.3bn' not in html and 'Funding perspective' not in html


def test_expired_agenda_review_does_not_recreate_the_released_calculation():
    ctx = v.resolve(BANK, {'stream': ['landscape']})
    html = economics.banking(ctx, v.current_data(ctx), (), headers={})
    assert '£502.8bn' in html and '£6.6bn' in html
    assert '£6.3bn' not in html and 'data-intelligence="funding-base"' not in html


@pytest.mark.parametrize('path', [BANK, AIR])
def test_guest_forged_and_authenticated_public_values_do_not_discover_runs(monkeypatch, permitted, path):
    def forbidden(*args, **kwargs):
        pytest.fail('Public Economics attempted Financial-run access or persistence')
    for name in ('find_existing_run', 'create_run', 'refresh_research', 'read_analysis'):
        monkeypatch.setattr(financial, name, forbidden)
    guest = main(path)
    forged = main(path, headers={'X-Flora-User': 'owner', 'X-Flora-Roles': 'owner', 'X-Flora-Active-Workspace': 'private'})
    authorised = main(path, headers=permitted[1])
    assert guest == forged == authorised
    assert 'fi-private' not in guest


@pytest.mark.parametrize('query', [
    {'workspace': ['private']}, {'run_id': ['fi-private']}, {'export': ['csv']},
    {'stream': ['inside'], 'detail': ['airline-return']},
    {'stream': ['landscape'], 'detail': ['airline-return', 'fleet-operations']},
])
def test_new_stage_routes_keep_finite_scope_and_deny_private_queries(query):
    with pytest.raises(ValueError):
        v.resolve(AIR, query)


def test_original_economics_and_financial_routes_remain_separate():
    legacy = v.resolve(BANK, {'detail': ['economics']})
    assert legacy.stream == 'inside'  # Historic unqualified URL remains unchanged.
    landscape = main(detail='economics')
    assert 'From funding to earnings' in landscape
    assert 'stream=inside&amp;detail=economics' in landscape
    for stage in economics.AIRLINE_STAGES:
        ctx = v.resolve(AIR, {'stream': ['landscape'], 'detail': [stage], 'reading': ['insight']})
        for stream in ('inside', 'forces'):
            target = urlsplit(v.stream_url(ctx, stream))
            resolved = v.resolve(target.path, parse_qs(target.query))
            assert resolved.scope == 'easyjet' and resolved.reading == 'insight' and not resolved.detail


def test_unauthenticated_requests_never_probe_private_canonical_models(monkeypatch):
    from cios.applications.flora.enterprise_canvas import service
    def forbidden(*args, **kwargs):
        pytest.fail('Unauthenticated canonical-model probe')
    monkeypatch.setattr(service, 'can_view_enterprise_canvas', forbidden)
    assert economics._qualified_pressure_link({}, 'Lloyds Banking Group plc') == ''
    assert economics._qualified_pressure_link({'X-Flora-User': 'owner'}, 'Lloyds Banking Group plc') == ''


def test_qualified_pressure_link_requires_binding_acl_and_current_requalification(monkeypatch, permitted):
    from cios.applications.flora.live import source_registry
    from cios.applications.flora.enterprise_canvas import service
    from cios.applications.flora.memory.repository import EnterpriseModelRepository
    from cios.applications.flora.blueprint_import import material_pressure
    state = {'access': False, 'qualification': 'REJECTED'}
    monkeypatch.setattr(source_registry, 'canonical_enterprise_id', lambda company: 'isolated-bound-enterprise')
    monkeypatch.setattr(source_registry, 'configured_enterprise_aliases', lambda: {'isolated': 'isolated-bound-enterprise'})
    monkeypatch.setattr(service, 'can_view_enterprise_canvas', lambda headers, identity: state['access'])
    monkeypatch.setattr(EnterpriseModelRepository, 'get', lambda self, identity: object())
    monkeypatch.setattr(material_pressure, 'model_pressure_assessments', lambda model: [{'qualification': state['qualification']}])
    headers = permitted[1]
    assert economics._qualified_pressure_link(headers, 'Lloyds Banking Group plc') == ''
    state['access'] = True
    assert economics._qualified_pressure_link(headers, 'Lloyds Banking Group plc') == ''
    state['qualification'] = 'QUALIFIED'
    assert '/digital-twins/isolated-bound-enterprise/canvas#material-pressures' in economics._qualified_pressure_link(headers, 'Lloyds Banking Group plc')
    state['access'] = False
    assert economics._qualified_pressure_link(headers, 'Lloyds Banking Group plc') == ''


def test_shipping_restrictions_and_all_artwork_are_unchanged():
    import subprocess
    from hashlib import sha256
    root = Path(__file__).resolve().parents[1]
    base = '03719d7573f087c65d9622719273aa4b89caf7d3'
    case = 'enterprise-knowledge/banking/research-model/source-snapshots/PFI-Lloyds-Q326.json'
    # Ordinary factual activation evolves only this Source record; the three
    # original measured values/definitions and all historical research survive.
    from tests.flora_lloyds_research_contract import preserved_research_cut
    preserved_research_cut()
    assert len(financial.public_factual_projection()['facts']) == 3
    for directory in ('visual_stream_assets', 'easyjet_art'):
        for path in subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', base, 'cios/applications/flora/' + directory], cwd=root, text=True).splitlines():
            if Path(path).suffix.lower() in {'.png','.jpg','.jpeg','.webp','.avif','.svg'}:
                assert (root / path).read_bytes() == subprocess.check_output(['git', 'show', base + ':' + path], cwd=root)


def test_renderer_evolution_is_explicit_and_unknown_cut_is_rejected():
    from tools.research.enterprise_economics_compatibility import validate, predecessor
    root = Path(__file__).resolve().parents[1]
    assert validate(root)['comparator_changed'] is False
    path = 'cios/applications/flora/visual_streams.py'
    unknown = (root / path).read_bytes() + b'\n# unknown cut\n'
    assert predecessor(root, path, unknown) == unknown
