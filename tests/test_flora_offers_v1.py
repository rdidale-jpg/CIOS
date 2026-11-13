"""Offers pilot invariants through real revocable authority and protected writes."""
from copy import deepcopy
import json
import sqlite3
from urllib.parse import urlencode

import pytest

from tests.test_flora_security_repair_01b import authority, signed, PASSWORD
from tests.test_flora_sales_pipeline import web
from cios.applications.flora import offers
from cios.applications.flora.commercial_mission import save_employer_context, save_commercial_mission
from cios.applications.flora.security_store import COOKIE, canonical
from cios.applications.flora.security_web import CSRF_COOKIE
from cios.applications.flora.storage import data_path

pytestmark = pytest.mark.real_security_boundary


@pytest.fixture
def actor(authority, tmp_path):
    store = authority[0]
    with store.transaction() as db:
        db.execute('UPDATE memberships SET enterprises=?', (canonical(['BK-ENT-001', 'AV-ENT-001']),))
    _, token, csrf, headers, _ = signed(authority, tmp_path)
    return store, token, csrf, headers


def add_actor(store, tmp_path, user, workspace='synthetic-workspace', roles=None):
    """Explicit synthetic offline authority setup; production never imports it."""
    roles = roles or ['commercial_context.view', 'commercial_context.edit']
    with store.transaction() as db:
        db.execute('INSERT INTO principals(user_id) VALUES (?)', (user,))
        db.execute('INSERT INTO memberships(membership_id,user_id,workspace_id,roles,enterprises) VALUES (?,?,?,?,?)',
            ('membership-' + user, user, workspace, canonical(roles), canonical(['BK-ENT-001', 'AV-ENT-001'])))
    delivery = tmp_path / ('enrollment-' + user)
    store.enroll_offline(user, delivery)
    pre, csrf = store.preauth()
    store.enroll(delivery.read_text().strip(), PASSWORD, pre, csrf)
    pre, csrf = store.preauth()
    token, csrf = store.login(user, PASSWORD, pre, csrf)
    token, csrf = store.select(token, csrf, workspace)
    return {'Cookie': f'{COOKIE}={token}; {CSRF_COOKIE}={csrf}'}


@pytest.fixture
def pilot(actor, tmp_path):
    store, _, _, owner = actor
    seller = add_actor(store, tmp_path, 'pilot-seller')
    reviewer = add_actor(store, tmp_path, 'pilot-reviewer')
    outsider = add_actor(store, tmp_path, 'pilot-outsider')
    foreign = add_actor(store, tmp_path, 'pilot-foreign', 'foreign-workspace', ['cios_owner'])
    save_employer_context(owner, {'organisation': 'Illustrative UK employer', 'capabilities': ['Synthetic declared diagnostic capability']})
    employer = offers.bind_employer(['synthetic-human', 'pilot-seller', 'pilot-reviewer'], ['pilot-reviewer'], 'SYNTHETIC-OWNER-REVIEW', headers=owner)
    for headers in (owner, seller, reviewer):
        offers.select_employer(employer['id'], headers=headers)
    return {'owner': owner, 'seller': seller, 'reviewer': reviewer, 'outsider': outsider, 'foreign': foreign, 'employer': employer, 'store': store}


def draft(pilot, template='service', headers=None, **overrides):
    return offers.save_offer(deepcopy(offers.TEMPLATES[template]) | overrides, headers=headers or pilot['seller'])


def approved(pilot, template='service'):
    r = draft(pilot, template, evidence='SYNTHETIC-PROOF: internal capability review; illustrative only')
    r = offers.transition(r['id'], r['version'], 'submit', headers=pilot['seller'])
    return offers.transition(r['id'], r['version'], 'approve', 'SYNTHETIC-RIGHTS-REVIEW', headers=pilot['reviewer'])


def test_private_version_persistence_and_audit(pilot):
    r = draft(pilot)
    second = offers.save_offer({'entry_play': 'Ask permission for one scoped service discussion.'}, r['id'], r['version'], headers=pilot['seller'])
    assert second['version'] == 2 and second['state'] == 'private_draft'
    records = offers.snapshot(headers=pilot['seller'])['offers']
    assert records[0]['content']['entry_play'] == r['content']['entry_play']
    assert records[0]['version'] == 1 and records[1]['current']
    envelope = json.loads(offers._path().read_text())
    assert len(envelope['offers'][r['id']]) == 2
    assert offers._path().stat().st_mode & 0o777 == 0o600
    assert offers._path().parent.stat().st_mode & 0o777 == 0o700
    with pilot['store'].transaction() as db:
        audit = [json.loads(row[0]) for row in db.execute("SELECT payload FROM audit WHERE event='commercial_offer_mutation'")]
    assert any(a['action'] == 'offer_version_saved' for a in audit)
    assert all('content' not in a for a in audit)


@pytest.mark.parametrize('who', ['owner', 'reviewer', 'outsider', 'foreign'])
def test_private_offers_are_not_visible_to_other_users_even_owner(pilot, who):
    r = draft(pilot)
    assert all(o['id'] != r['id'] for o in offers.snapshot(headers=pilot[who])['offers'])
    with pytest.raises(PermissionError):
        offers.save_offer({'name': 'steal'}, r['id'], 1, headers=pilot[who])


def test_employer_name_and_owner_role_do_not_confer_binding(pilot):
    save_employer_context(pilot['outsider'], {'organisation': 'Illustrative UK employer'})
    with pytest.raises(PermissionError):
        offers.select_employer(pilot['employer']['id'], headers=pilot['outsider'])
    with pytest.raises(PermissionError):
        offers.bind_employer(['pilot-outsider'], ['pilot-outsider'], 'forged', headers=pilot['outsider'])
    with pytest.raises(PermissionError):
        offers.select_employer(pilot['employer']['id'], headers=pilot['foreign'])


def test_binding_rejects_nonmembers_and_requires_reference(pilot):
    for sellers, approvers, ref, error in [(['absent'], ['absent'], 'ref', PermissionError),
            (['pilot-seller'], ['pilot-reviewer'], 'ref', ValueError),
            (['pilot-seller'], ['pilot-seller'], '', ValueError)]:
        with pytest.raises(error):
            offers.bind_employer(sellers, approvers, ref, headers=pilot['owner'])


def test_approval_separate_from_authorship_and_revision(pilot):
    r = draft(pilot)
    with pytest.raises(PermissionError):
        offers.transition(r['id'], 1, 'approve', 'self', headers=pilot['seller'])
    r = offers.transition(r['id'], 1, 'submit', headers=pilot['seller'])
    with pytest.raises(PermissionError):
        offers.transition(r['id'], 2, 'approve', 'owner is not delegated', headers=pilot['owner'])
    assert any(o['id'] == r['id'] for o in offers.snapshot(headers=pilot['reviewer'])['offers'])
    with pytest.raises(ValueError):
        offers.transition(r['id'], 2, 'approve', '', headers=pilot['reviewer'])
    r = offers.transition(r['id'], 2, 'approve', 'SYNTHETIC-REVIEW', headers=pilot['reviewer'])
    assert r['state'] == 'employer_approved' and r['canonical_offer_ref'] is None
    changed = offers.save_offer({'entry_play': 'A revised draft play.'}, r['id'], 3, headers=pilot['reviewer'])
    assert changed['version'] == 4 and changed['state'] == 'private_draft' and changed['review'] is None
    assert offers.snapshot(headers=pilot['seller'])['offers'][-1]['version'] == 3


def test_reviewer_cannot_approve_their_own_offer(pilot):
    r = draft(pilot, headers=pilot['reviewer'])
    r = offers.transition(r['id'], 1, 'submit', headers=pilot['reviewer'])
    with pytest.raises(PermissionError):
        offers.transition(r['id'], 2, 'approve', 'self', headers=pilot['reviewer'])


@pytest.mark.parametrize('field', sorted(set(offers.FIELDS) - offers.VARIATION_FIELDS))
def test_parent_protected_fields_cannot_change(pilot, field):
    parent = approved(pilot)
    with pytest.raises(ValueError):
        offers.save_offer({'name': 'variation', field: 'FORGED OVERRIDE'}, parent_id=parent['id'], parent_version=3, headers=pilot['owner'])
    assert len(offers.snapshot(headers=pilot['owner'])['offers']) == 1


def test_variation_lineage_and_stale_parent(pilot):
    parent = approved(pilot)
    variation = offers.save_offer({'name': 'Banking focus', 'icp': 'Banking', 'entry_play': 'Ask about one critical banking service.'}, parent_id=parent['id'], parent_version=3, headers=pilot['owner'])
    assert variation['parent'] == {'id': parent['id'], 'version': 3}
    assert variation['content']['capabilities'] == parent['content']['capabilities']
    assert offers.snapshot(headers=pilot['owner'])['offers'][-1]['eligible']
    offers.save_offer({'entry_play': 'New master review needed'}, parent['id'], 3, headers=pilot['reviewer'])
    assert not offers.snapshot(headers=pilot['owner'])['offers'][-1]['eligible']
    with pytest.raises(ValueError):
        offers.save_offer({'name': 'stale'}, variation['id'], 1, headers=pilot['owner'])


@pytest.mark.parametrize('action,state', [('changes', 'changes_requested'), ('reject', 'rejected')])
def test_review_outcomes_are_scoped_and_versioned(pilot, action, state):
    r = draft(pilot)
    offers.transition(r['id'], 1, 'submit', headers=pilot['seller'])
    r = offers.transition(r['id'], 2, action, 'SYNTHETIC-REVIEW', headers=pilot['reviewer'])
    assert r['version'] == 3 and r['state'] == state
    assert not offers.snapshot(headers=pilot['seller'])['offers'][-1]['eligible']


def test_retired_offer_not_reused(pilot):
    r = approved(pilot)
    offers.transition(r['id'], 3, 'retire', headers=pilot['reviewer'])
    with pytest.raises(ValueError):
        offers.discover(selected=r['id'], headers=pilot['seller'])


def test_optimistic_concurrency_and_no_extra_version(pilot):
    r = draft(pilot)
    offers.save_offer({'name': 'Version two'}, r['id'], 1, headers=pilot['seller'])
    with pytest.raises(ValueError):
        offers.save_offer({'name': 'Stale overwrite'}, r['id'], 1, headers=pilot['seller'])
    assert len(offers.snapshot(headers=pilot['seller'])['offers']) == 2


def test_symmetric_discovery_has_identical_assessment_and_deduplication(pilot):
    for template in offers.TEMPLATES:
        draft(pilot, template)
    all_pairs = offers.discover(headers=pilot['seller'])
    assert len(all_pairs) == 9 and len({r['assessment_id'] for r in all_pairs}) == 9
    for match in all_pairs:
        offer_path = offers.discover('offer', match['offer_id'], headers=pilot['seller'])
        account_path = offers.discover('account', match['enterprise_slug'], headers=pilot['seller'])
        a = next(r for r in offer_path if r['assessment_id'] == match['assessment_id'])
        b = next(r for r in account_path if r['assessment_id'] == match['assessment_id'])
        assert a == b == match
        assert not a['pipeline_eligible'] and a['economics'] is None
        assert a['unknowns'] and a['hypothesis_lineage'] and a['what_not_to_claim']
    assert len({r['entry_play'] for r in all_pairs}) == 3


def test_cutoff_filters_observations_and_counters_and_changes_identity(pilot):
    draft(pilot)
    old = offers.discover(evidence_cutoff='2020-01-01', headers=pilot['seller'])
    fresh = offers.discover(headers=pilot['seller'])
    for r in old:
        assert not r['evidence_lineage'] and not r['contradictions']
        assert not r['hypothesis_lineage'][0]['contradictory_evidence']
        assert r['recommended_posture'] == 'research'
    assert {r['assessment_id'] for r in old}.isdisjoint({r['assessment_id'] for r in fresh})


def test_pure_matcher_is_repeatable_and_rejects_policy_override(pilot):
    r = draft(pilot)
    a = offers.accounts()['lloyds']
    seller = {'user_id': 'pilot-seller', 'excluded_accounts': []}
    assert offers.assess_fit(seller, r, a, '2026-11-13') == offers.assess_fit(seller, r, a, '2026-11-13')
    with pytest.raises(ValueError):
        offers.assess_fit(seller, r, a, '2026-11-13', 'weakened-policy')
    excluded = offers.assess_fit(seller | {'excluded_accounts': ['lloyds']}, r, a, '2026-11-13')
    assert excluded['recommended_posture'] == 'deprioritise'


def test_mission_exclusion_and_version_are_inputs(pilot):
    draft(pilot)
    before = offers.discover(headers=pilot['seller'])
    save_commercial_mission(pilot['seller'], {'executive_role': 'Seller', 'commercial_objective': 'Validate', 'excluded_accounts': ['lloyds'], 'version': 2})
    after = offers.discover(headers=pilot['seller'])
    assert next(r for r in after if r['enterprise_slug'] == 'lloyds')['recommended_posture'] == 'deprioritise'
    assert {r['assessment_id'] for r in before}.isdisjoint({r['assessment_id'] for r in after})


def test_account_permission_boundary_filters_private_assessment(pilot):
    draft(pilot)
    with pilot['store'].transaction() as db:
        db.execute('UPDATE memberships SET enterprises=?,version=version+1 WHERE user_id=?', (canonical(['AV-ENT-001']), 'pilot-seller'))
    matches = offers.discover(headers=pilot['seller'])
    assert {r['enterprise_slug'] for r in matches} == {'easyjet', 'equinix'}


def test_studio_default_off_explicit_scope_and_grounded_private_composition(pilot):
    a = approved(pilot, 'service'); b = approved(pilot, 'consulting')
    components = [(a['id'], 3), (b['id'], 3)]
    assert not offers.snapshot(headers=pilot['seller'])['studio_enabled']
    with pytest.raises(PermissionError):
        offers.compose(components, 'lloyds', headers=pilot['seller'])
    offers.studio_toggle(True, headers=pilot['seller'])
    assert not offers.snapshot(headers=pilot['reviewer'])['studio_enabled']
    r = offers.compose(components, 'lloyds', headers=pilot['seller'])
    assert r['kind'] == 'composite' and r['state'] == 'private_draft'
    assert r['components'] == [{'id': a['id'], 'version': 3}, {'id': b['id'], 'version': 3}]
    assert 'simpler option' in r['content']['next_test']
    assert not any(o['id'] == r['id'] for o in offers.snapshot(headers=pilot['reviewer'])['offers'])
    offers.studio_toggle(False, headers=pilot['seller'])
    with pytest.raises(PermissionError):
        offers.compose(components, 'lloyds', headers=pilot['seller'])


def test_studio_rejects_unapproved_unreferenced_or_duplicate_components(pilot):
    a = draft(pilot); b = approved(pilot, 'ai')
    offers.studio_toggle(True, headers=pilot['seller'])
    for parts in ([(a['id'], 1), (b['id'], 3)], [(b['id'], 3), (b['id'], 3)]):
        with pytest.raises(ValueError):
            offers.compose(parts, 'lloyds', headers=pilot['seller'])


def test_composite_cannot_publish_with_stale_components(pilot):
    a = approved(pilot); b = approved(pilot, 'ai')
    offers.studio_toggle(True, headers=pilot['seller'])
    r = offers.compose([(a['id'], 3), (b['id'], 3)], 'lloyds', headers=pilot['seller'])
    offers.transition(r['id'], 1, 'submit', headers=pilot['seller'])
    offers.transition(a['id'], 3, 'retire', headers=pilot['reviewer'])
    with pytest.raises(ValueError):
        offers.transition(r['id'], 2, 'approve', 'SYNTHETIC', headers=pilot['reviewer'])


def test_no_pipeline_or_canonical_mutations_from_offer_workflows(pilot):
    before = {str(p): p.read_bytes() for p in data_path().rglob('*') if p.is_file() and 'security' not in p.parts and 'commercial_context' not in p.parts}
    draft(pilot); offers.discover(headers=pilot['seller'])
    offers.studio_toggle(True, headers=pilot['seller'])
    after = {str(p): p.read_bytes() for p in data_path().rglob('*') if p.is_file() and 'security' not in p.parts and 'commercial_context' not in p.parts}
    assert before == after
    assert not data_path('sales_pipeline', 'opportunities.json').exists()


def test_binding_revocation_invalidates_selected_context(pilot):
    draft(pilot)
    offers.revoke_employer(pilot['employer']['id'], headers=pilot['owner'])
    assert not offers.snapshot(headers=pilot['seller'])['selected']
    with pytest.raises(PermissionError):
        offers.discover(headers=pilot['seller'])


def test_membership_revocation_denies_service(pilot):
    draft(pilot)
    with pilot['store'].transaction() as db:
        db.execute('UPDATE memberships SET active=0,version=version+1 WHERE user_id=?', ('pilot-seller',))
    with pytest.raises(PermissionError):
        offers.snapshot(headers=pilot['seller'])
    with pytest.raises(PermissionError):
        draft(pilot)


def test_write_and_audit_failure_roll_back(pilot, monkeypatch):
    before = offers._path().read_bytes()
    original = offers.SecurityStore.audit
    def fail(self, db, event, **values):
        if event == 'commercial_offer_mutation':
            raise sqlite3.OperationalError('synthetic audit failure')
        return original(self, db, event, **values)
    monkeypatch.setattr(offers.SecurityStore, 'audit', fail)
    with pytest.raises(sqlite3.OperationalError):
        draft(pilot)
    assert offers._path().read_bytes() == before


def test_real_http_authentication_csrf_origin_and_form_validation(pilot, web):
    assert web('/flora/offers', authenticated=False)[0] == 403
    assert web('/flora/offers')[0] == 200
    before = offers._path().read_bytes()
    assert web('/flora/offers/studio-toggle', {'enabled': 'yes', 'csrf': 'forged'})[0] == 403
    assert offers._path().read_bytes() == before
    assert web('/flora/offers/studio-toggle', {'enabled': 'yes', 'extra_permission': 'approve'})[0] == 403
    assert web('/flora/offers/studio-toggle', {'enabled': 'yes'})[0] == 303
    assert offers.snapshot(headers=pilot['owner'])['studio_enabled']


@pytest.mark.parametrize('path', ['/flora/offers/secret', '/flora/offers/discover?mode=offer&mode=account',
    '/flora/offers?workspace=foreign', '/flora/offers?offer=a&offer=b', '/flora/offers%2fcompany'])
def test_http_rejects_unrecognised_routes_and_selectors(pilot, web, path):
    assert web(path)[0] in {403, 404}


def test_forged_headers_confer_no_offer_access(pilot):
    headers = {'X-Flora-User': 'pilot-seller', 'X-Flora-Active-Workspace': 'synthetic-workspace', 'X-Flora-Roles': 'cios_owner'}
    with pytest.raises(PermissionError):
        offers.snapshot(headers=headers)


def test_offer_text_is_escaped_in_browser(pilot, web):
    r = draft(pilot, headers=pilot['owner'], name='<script>alert(1)</script>')
    status, html, _ = web('/flora/offers/edit?' + urlencode({'offer': r['id']}))
    assert status == 200 and '&lt;script&gt;' in html and '<script>alert(1)</script>' not in html


def test_source_adapter_preserves_existing_status_and_no_invented_observations():
    accounts = offers.accounts()
    assert set(accounts) == {'lloyds', 'easyjet', 'equinix'}
    assert all(not a['observation_lineage'] for a in accounts.values())
    assert all(a['lineage'] and a['limitations'] for a in accounts.values())
    assert accounts['equinix']['id'].startswith('presentation:')


def test_offer_relevance_is_context_sensitive_without_opaque_score(pilot):
    service = draft(pilot, 'service'); ai = draft(pilot, 'ai')
    service_results = offers.discover(selected=service['id'], headers=pilot['seller'])
    ai_results = offers.discover(selected=ai['id'], headers=pilot['seller'])
    assert next(r for r in service_results if r['enterprise_slug'] == 'easyjet')['recommended_posture'] == 'validate'
    assert next(r for r in ai_results if r['enterprise_slug'] == 'easyjet')['recommended_posture'] == 'research'
    assert all('score' not in r and 'win_probability' not in r for r in service_results + ai_results)


def test_expired_recent_auth_cannot_approve_or_change_employer(pilot):
    import time
    from cios.applications.flora.security_store import cookie_token, digest
    r = draft(pilot); offers.transition(r['id'], 1, 'submit', headers=pilot['seller'])
    token = cookie_token(pilot['reviewer'])
    with pilot['store'].transaction() as db:
        db.execute('UPDATE tokens SET created=? WHERE hash=?', (time.time() - 901, digest(token)))
    with pytest.raises(PermissionError):
        offers.transition(r['id'], 2, 'approve', 'stale login', headers=pilot['reviewer'])
    assert offers.snapshot(headers=pilot['reviewer'])['selected']


def test_approval_does_not_override_component_or_account_access(pilot):
    a = approved(pilot); b = approved(pilot, 'ai')
    offers.studio_toggle(True, headers=pilot['seller'])
    with pilot['store'].transaction() as db:
        db.execute('UPDATE memberships SET enterprises=?,version=version+1 WHERE user_id=?', (canonical(['AV-ENT-001']), 'pilot-seller'))
    with pytest.raises(PermissionError):
        offers.compose([(a['id'], 3), (b['id'], 3)], 'lloyds', headers=pilot['seller'])


def test_composition_requires_explicit_account_and_keeps_candidate_lineage(pilot):
    a = approved(pilot); b = approved(pilot, 'ai')
    offers.studio_toggle(True, headers=pilot['seller'])
    with pytest.raises(ValueError):
        offers.compose([(a['id'], 3), (b['id'], 3)], headers=pilot['seller'])
    r = offers.compose([(a['id'], 3), (b['id'], 3)], 'lloyds', headers=pilot['seller'])
    assert r['target_context']['enterprise_id'] == 'BK-ENT-001'
    assert r['classification'] == 'derived_private_composite_candidate'
    assert 'residual need is not established' in r['composition_review']['value_thesis']


def test_match_and_studio_make_no_network_or_paid_calls(pilot, monkeypatch):
    import socket
    def denied(*args, **kwargs):
        raise AssertionError('Unexpected network call')
    a = approved(pilot); b = approved(pilot, 'ai')
    monkeypatch.setattr(socket, 'create_connection', denied)
    offers.discover(headers=pilot['seller'])
    offers.studio_toggle(True, headers=pilot['seller'])
    offers.compose([(a['id'], 3), (b['id'], 3)], 'lloyds', headers=pilot['seller'])


def test_selected_employer_isolated_when_same_user_changes_workspace(pilot):
    store = pilot['store']
    from cios.applications.flora.security_store import cookie_token
    with store.transaction() as db:
        db.execute('INSERT INTO memberships(membership_id,user_id,workspace_id,roles,enterprises) VALUES (?,?,?,?,?)',
            ('second-seller-membership', 'pilot-seller', 'second-workspace', canonical(['commercial_context.view', 'commercial_context.edit']), canonical(['BK-ENT-001'])))
    from cios.applications.flora.access import cookie_value
    token, csrf = store.select(cookie_token(pilot['seller']), cookie_value(pilot['seller'], CSRF_COOKIE), 'second-workspace')
    headers = {'Cookie': f'{COOKIE}={token}; {CSRF_COOKIE}={csrf}'}
    assert not offers.snapshot(headers=headers)['selected']
    assert not offers.snapshot(headers=headers)['studio_enabled']
    with pytest.raises(PermissionError):
        offers.select_employer(pilot['employer']['id'], headers=headers)


def test_concurrent_edit_cannot_overwrite_a_newer_version(pilot):
    from concurrent.futures import ThreadPoolExecutor
    r = draft(pilot)
    def edit(name):
        try:
            return offers.save_offer({'name': name}, r['id'], 1, headers=pilot['seller'])['version']
        except ValueError:
            return 'stale'
    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(edit, ['first revision', 'second revision']))
    assert sorted(outcomes, key=str) == [2, 'stale']
    assert len(offers.snapshot(headers=pilot['seller'])['offers']) == 2


def test_composite_edit_preserves_target_and_component_lineage(pilot):
    a = approved(pilot); b = approved(pilot, 'ai')
    offers.studio_toggle(True, headers=pilot['seller'])
    r = offers.compose([(a['id'], 3), (b['id'], 3)], 'lloyds', headers=pilot['seller'])
    revised = offers.save_offer({'name': 'Revised candidate'}, r['id'], 1, headers=pilot['seller'])
    assert revised['target_context'] == r['target_context']
    assert revised['components'] == r['components']
    assert revised['composition_review'] == r['composition_review']
    matches = offers.discover(selected=r['id'], headers=pilot['seller'])
    assert next(r for r in matches if r['enterprise_slug'] == 'easyjet')['recommended_posture'] == 'deprioritise'


def test_approved_components_without_proof_references_cannot_compose(pilot):
    a = draft(pilot)
    offers.transition(a['id'], 1, 'submit', headers=pilot['seller'])
    offers.transition(a['id'], 2, 'approve', 'SYNTHETIC-review', headers=pilot['reviewer'])
    b = approved(pilot, 'ai')
    offers.studio_toggle(True, headers=pilot['seller'])
    with pytest.raises(ValueError):
        offers.compose([(a['id'], 3), (b['id'], 3)], 'lloyds', headers=pilot['seller'])


def test_seller_cannot_modify_or_withdraw_employer_approved_master(pilot):
    r = approved(pilot)
    with pytest.raises(PermissionError):
        offers.save_offer({'name': 'Corporate override'}, r['id'], 3, headers=pilot['seller'])
    with pytest.raises(PermissionError):
        offers.transition(r['id'], 3, 'retire', headers=pilot['seller'])
    assert offers.snapshot(headers=pilot['seller'])['offers'][-1]['state'] == 'employer_approved'


def test_delegated_reviewer_can_draft_master_revision_but_not_self_approve(pilot):
    r = approved(pilot)
    from cios.applications.flora.offers_views import render
    html = render('/flora/offers/edit', {'offer': [r['id']]}, pilot['reviewer'])
    assert 'Withdraw employer-approved version' in html and 'Save new private version' in html
    revision = offers.save_offer({'entry_play': 'Revised master play'}, r['id'], 3, headers=pilot['reviewer'])
    offers.transition(r['id'], revision['version'], 'submit', headers=pilot['reviewer'])
    with pytest.raises(PermissionError):
        offers.transition(r['id'], 5, 'approve', 'self', headers=pilot['reviewer'])


def test_grandparent_withdrawal_invalidates_nested_variations(pilot):
    master = approved(pilot)
    child = offers.save_offer({'name': 'First variation'}, parent_id=master['id'], parent_version=3, headers=pilot['seller'])
    offers.transition(child['id'], 1, 'submit', headers=pilot['seller'])
    offers.transition(child['id'], 2, 'approve', 'SYNTHETIC', headers=pilot['reviewer'])
    grandchild = offers.save_offer({'name': 'Nested variation'}, parent_id=child['id'], parent_version=3, headers=pilot['owner'])
    offers.transition(master['id'], 3, 'retire', headers=pilot['reviewer'])
    record = next(r for r in offers.snapshot(headers=pilot['owner'])['offers'] if r['id'] == grandchild['id'])
    assert not record['eligible']


def test_changed_upstream_source_snapshot_requires_policy_reconciliation(monkeypatch):
    from cios.applications.flora.research_intelligence import model
    original = model.load_assessment
    def changed(domain):
        value = deepcopy(original(domain))
        value['sources'][0]['limitation'] = 'A changed source state requires new review'
        # Select a guaranteed referenced source, not an unused metadata row.
        for source in value['sources']:
            source['limitation'] = 'Changed after reviewed cutoff'
        return value
    monkeypatch.setattr(model, 'load_assessment', changed)
    with pytest.raises(ValueError, match='snapshot changed'):
        offers.accounts()


def test_fresh_owner_can_declare_company_in_browser_without_imported_twin(actor, web):
    from cios.applications.flora.commercial_mission import resolve_employer_context
    assert resolve_employer_context(actor[3]) is None
    status, html, _ = web('/flora/offers/company')
    assert status == 200 and 'Save declared company context' in html
    assert web('/flora/offers/profile', {'organisation': 'Synthetic fresh employer', 'expected_version': 0})[0] == 303
    profile = resolve_employer_context(actor[3])
    assert profile.organisation == 'Synthetic fresh employer' and profile.version == 1
    assert not offers.snapshot(headers=actor[3])['employers']
    assert not offers.snapshot(headers=actor[3])['selected']
    assert web('/flora/offers/profile', {'organisation': 'stale override', 'expected_version': 0})[0] == 403
    assert resolve_employer_context(actor[3]).organisation == 'Synthetic fresh employer'


def test_declare_employer_preserves_existing_profile_and_does_not_grant_authority(pilot):
    from cios.applications.flora.commercial_mission import resolve_employer_context
    before = resolve_employer_context(pilot['owner'])
    result = offers.declare_employer(before.organisation, before.version, headers=pilot['owner'])
    assert result.capabilities == before.capabilities and result.context_id == before.context_id
    assert result.version == before.version + 1
    changed = offers.declare_employer('Synthetic second employer', result.version, headers=pilot['owner'])
    assert not changed.capabilities and not changed.partners and not changed.credentials
    assert changed.context_id == before.context_id
    assert offers.snapshot(headers=pilot['owner'])['selected']['organisation'] == 'Illustrative UK employer'
    with pytest.raises(PermissionError):
        offers.declare_employer('Impersonation', headers=pilot['seller'])
