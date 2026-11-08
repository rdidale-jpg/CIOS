"""Increment 01 assurance regressions, using isolated synthetic intelligence only."""
import copy
import json
from types import SimpleNamespace

import pytest

from cios.applications.flora.enterprise_intelligence.models import ReasoningRequestV1
from cios.applications.flora.enterprise_intelligence.provider import StaticJSONProvider
from cios.applications.flora.enterprise_intelligence.retrieval import BoundedTwinRetrievalService
from cios.applications.flora.enterprise_intelligence.runtime import EnterpriseIntelligenceRuntime, deterministic_brief
from cios.applications.flora.enterprise_intelligence.validator import ClaimValidator
from cios.applications.flora.memory.models import Observation
from cios.applications.flora.memory.service import ObservationMemoryService

ENTERPRISE = 'synthetic-integrity-airline'


@pytest.fixture
def memory(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    monkeypatch.setenv('FLORA_PILOT_DIR', str(tmp_path))
    return ObservationMemoryService()


def evidence(eid='EV-FUEL', statement='Synthetic fuel benchmark increased by 15 percent for Q4.', **changes):
    return dict(evidence_id=eid, enterprise_id=ENTERPRISE, organisation=ENTERPRISE,
                summary=statement, cleaned_observation=statement, source_id='SYNTHETIC',
                source_url='https://audit.invalid/source', commercial_condition='enterprise_event_announced',
                affected_attribute='events.fuel', observation_date='2026-11-01',
                extraction_timestamp='2026-11-02T12:00:00Z', publication_date='2026-11-01',
                confidence=80, page_number=1) | changes


def ingest(memory, **changes):
    report = memory.process_evidence(evidence(**changes))
    assert report.factual_claims_accepted == 1
    return report.results[0]


def package(memory):
    request = ReasoningRequestV1.create(ENTERPRISE, ENTERPRISE, 'synthetic-owner', evidence_cut_off='2026-11-08')
    return request, BoundedTwinRetrievalService(memory.models, memory.observations, memory.evidence).retrieve(request)


def brief(memory):
    ingest(memory)
    req, pkg = package(memory)
    return req, pkg, deterministic_brief(req, pkg)


def test_missing_evidence_cannot_support_a_governed_claim(memory):
    _, pkg, payload = brief(memory)
    pkg.selected_observations = tuple(i for i in pkg.selected_observations if i.object_class != 'evidence')
    payload['material_pressures'][0]['supporting_evidence_ids'] = []
    payload['commercial_relevance_assessments'] = []
    payload['recommended_next_moves'] = []
    assert ClaimValidator().validate(payload, pkg)['validation_status']['status'] == 'invalid'


@pytest.mark.parametrize('section,field,statement', [
    ('commercial_relevance_assessments', 'plausible_intervention', 'A funded procurement for Synthetic Seller is confirmed.'),
    ('recommended_next_moves', 'action', 'Pursue the confirmed funded programme.'),
    ('opportunities', 'statement', 'Synthetic Airline intends to buy cloud services.'),
    ('procurements', 'statement', 'Synthetic Airline awarded a contract worth £5m.'),
    ('commercial_relevance_assessments', 'contract_value', '£5m'),
    ('commercial_relevance_assessments', 'buying_intent', 'confirmed'),
    ('commercial_relevance_assessments', 'plausible_intervention', 'A funded procurement is confirmed. Validate ownership next.'),
    ('commercial_relevance_assessments', 'plausible_intervention', 'Validate ownership; a funded procurement is confirmed.'),
    ('commercial_relevance_assessments', 'plausible_intervention', 'Unknown buyer for a confirmed funded procurement.'),
])
def test_pressure_citations_do_not_support_commercial_facts(memory, section, field, statement):
    _, pkg, payload = brief(memory)
    oid = next(i.stable_id for i in pkg.selected_observations if i.object_class == 'observation')
    payload[section] = [{field: statement, 'evidence_basis': [oid], 'lineage': [oid]}]
    assert ClaimValidator().validate(payload, pkg)['validation_status']['status'] == 'invalid'


def test_supported_procurement_and_labelled_conditional_hypothesis_survive(memory):
    ingest(memory)
    text = 'Synthetic Airline has a funded procurement worth £5m.'
    ingest(memory, eid='EV-PROC', statement=text, affected_attribute='events.procurement')
    req, pkg = package(memory)
    payload = deterministic_brief(req, pkg)
    payload['procurements'] = [{'statement': text, 'evidence_basis': ['EV-PROC']}]
    payload['opportunities'] = [{'statement': 'Fuel exposure could support an efficiency hypothesis.',
                                'interpretation_status': 'hypothesis', 'evidence_basis': ['EV-FUEL']}]
    assert ClaimValidator().validate(payload, pkg)['validation_status']['status'] in {'valid', 'valid_with_weakening'}
    assert payload['opportunities'][0]['interpretation_status'] == 'hypothesis'


def test_hypothesis_label_cannot_launder_funded_fact(memory):
    _, pkg, payload = brief(memory)
    payload['opportunities'] = [{'statement': 'A funded procurement is confirmed.',
                                'interpretation_status': 'hypothesis', 'evidence_basis': ['EV-FUEL']}]
    assert ClaimValidator().validate(payload, pkg)['validation_status']['status'] == 'invalid'


def test_negated_source_does_not_support_positive_procurement(memory):
    ingest(memory, statement='Synthetic Airline has no funded procurement.')
    _, pkg = package(memory)
    payload = deterministic_brief(package(memory)[0], pkg)
    payload['procurements'] = [{'statement': 'Synthetic Airline has a funded procurement.', 'evidence_basis': ['EV-FUEL']}]
    assert ClaimValidator().validate(payload, pkg)['validation_status']['status'] == 'invalid'


def test_invalid_provider_output_is_audited_without_replacing_valid_brief(memory, tmp_path):
    req, pkg, payload = brief(memory)
    runtime = EnterpriseIntelligenceRuntime(provider=StaticJSONProvider(copy.deepcopy(payload)))
    good = runtime.generate(req)
    assert good['audit']['status'] == 'Succeeded'
    saved = tmp_path / 'enterprise_intelligence' / 'briefs' / (ENTERPRISE + '.json')
    prior_bytes = saved.read_bytes()
    payload['material_pressures'][0]['supporting_observation_ids'] = ['MISSING']
    bad_req = req.model_copy(update={'request_id': req.request_id + '-rejected'})
    bad = EnterpriseIntelligenceRuntime(provider=StaticJSONProvider(payload)).generate(bad_req)
    assert bad['audit']['status'] != 'Succeeded'
    assert bad['audit']['provider_status'] == 'Succeeded'
    assert bad['audit']['validation_outcome'] == 'invalid'
    assert saved.read_bytes() == prior_bytes
    audit = json.loads((tmp_path / 'enterprise_intelligence' / 'audit' / (bad_req.request_id + '.json')).read_text())
    assert audit['rejected_output']['material_pressures'][0]['supporting_observation_ids'] == ['MISSING']
    from cios.applications.flora.enterprise_intelligence.runtime import latest_result
    assert latest_result(ENTERPRISE)['audit']['status'] != 'Succeeded'


def test_canvas_and_brief_page_do_not_render_legacy_invalid_success(memory, monkeypatch):
    from cios.applications.flora.enterprise_canvas import views as canvas_views
    from cios.applications.flora.enterprise_intelligence import views
    _, _, payload = brief(memory)
    payload['executive_summary']['what_is_happening'] = 'UNSUPPORTED SUCCESS CONTENT'
    payload['validation_status'] = {'status': 'invalid', 'rejected_claims': [{'reason': 'invalid citation'}]}
    result = {'audit': {'status': 'Succeeded', 'validation_outcome': 'invalid'}, 'brief': payload}
    monkeypatch.setattr(canvas_views, 'latest_result', lambda _: result)
    canvas = SimpleNamespace(enterprise_id='MOD')
    assert not canvas_views._has_successful_reasoning(canvas)
    html = canvas_views._reasoning_panel(canvas)
    assert 'UNSUPPORTED SUCCESS CONTENT' not in html
    monkeypatch.setattr(views, 'EnterpriseIntelligenceRuntime', lambda: SimpleNamespace(generate=lambda _: result))
    html, status = views.executive_intelligence_brief_page(ENTERPRISE, {'X-Flora-User': 'alice', 'X-Flora-Enterprises': ENTERPRISE})
    assert status == 200 and 'unavailable' in html.lower()
    assert 'UNSUPPORTED SUCCESS CONTENT' not in html


@pytest.mark.parametrize('changes', [
    {'lifecycle_state': 'retired', 'retired_at': '2026-11-03'},
    {'freshness': 'expired'},
    {'lifecycle_state': 'superseded'},
    {'lifecycle_state': 'rejected'},
])
def test_inactive_observation_and_derived_model_are_not_current_support(memory, changes):
    result = ingest(memory)
    obs = memory.observations.get(result.observation_id)
    for key, value in changes.items():
        setattr(obs, key, value)
    memory.observations._rewrite([obs])
    _, pkg = package(memory)
    assert not pkg.selected_observations
    assert not pkg.selected_entities_and_relationships
    assert memory.observations.get(result.observation_id) is not None


def test_future_model_attribute_is_excluded_from_historical_package(memory):
    ingest(memory)
    ingest(memory, eid='EV-FUTURE', statement='Synthetic future fuel benchmark decreased by 5 percent.',
           affected_attribute='events.future', observation_date='2026-12-01', publication_date='2026-12-01')
    _, pkg = package(memory)
    assert 'future fuel benchmark' not in json.dumps(pkg.to_dict())
    assert 'events.future' in memory.models.get(ENTERPRISE).attributes


@pytest.mark.parametrize('date_field', ['observation_date', 'evidence_publication_date', 'collection_date', 'last_confirmed_date'])
def test_future_observation_dates_do_not_support_historical_reasoning(memory, date_field):
    result = ingest(memory)
    obs = memory.observations.get(result.observation_id)
    setattr(obs, date_field, '2026-12-01')
    memory.observations._rewrite([obs])
    _, pkg = package(memory)
    assert not pkg.selected_observations and not pkg.selected_entities_and_relationships


def test_same_period_numeric_contradiction_is_bidirectional_and_visible(memory):
    first = ingest(memory)
    second = ingest(memory, eid='EV-COUNTER', statement='Synthetic fuel benchmark decreased by 5 percent for Q4.')
    assert second.contradiction
    a, b = (memory.observations.get(r.observation_id) for r in (first, second))
    assert b.observation_id in a.contradicted_by_observation_ids
    assert a.observation_id in b.contradicted_by_observation_ids
    _, pkg = package(memory)
    assert {a.observation_id, b.observation_id} <= {i.stable_id for i in pkg.selected_contradictions}
    assert not any(i.object_class == 'observation' for i in pkg.selected_observations)
    assert all(i.truth_status == 'contradiction' for i in pkg.selected_entities_and_relationships)
    assert pkg.selected_contradictions and 'EV-COUNTER' in pkg.lineage_manifest


def test_different_effective_period_is_change_not_contradiction(memory):
    ingest(memory)
    result = ingest(memory, eid='EV-NEXT', statement='Synthetic fuel benchmark decreased by 5 percent for Q1.',
                    observation_date='2026-11-05', publication_date='2026-11-05')
    assert not result.contradiction
    attr = memory.models.get(ENTERPRISE).attributes['events.fuel']
    assert attr.contradiction_state == 'none' and attr.prior_values


def test_explicit_supersession_resolves_current_support_without_erasing_history(memory):
    first = ingest(memory)
    second = Observation(ENTERPRISE, 'fact', 'Synthetic corrected fuel benchmark decreased by 5 percent.',
                         '2026-11-01', '2026-11-03', 'events.fuel', 80, ('EV-CORRECTION',),
                         supersedes_observation_id=first.observation_id)
    memory.evidence.save(evidence('EV-CORRECTION', second.atomic_statement))
    memory.observations.save(second)
    result = memory.apply_observation(second)
    assert not result.contradiction
    _, pkg = package(memory)
    assert first.observation_id not in {i.stable_id for i in pkg.selected_observations}
    assert memory.observations.get(first.observation_id) is not None


def test_duplicate_replay_does_not_mutate_model_or_confidence_history(memory):
    ingest(memory)
    before = memory.models.get(ENTERPRISE).to_dict()
    result = ingest(memory)
    assert result.action == 'unchanged'
    assert memory.models.get(ENTERPRISE).to_dict() == before
    assert len(memory.observations.list()) == 1


def test_corroboration_merges_lineage_without_inflating_confidence_history(memory):
    ingest(memory)
    ingest(memory, eid='EV-CORR')
    attr = memory.models.get(ENTERPRISE).attributes['events.fuel']
    assert set(attr.evidence_ids) == {'EV-FUEL', 'EV-CORR'}
    assert len(attr.confidence_history) == 1
    before = memory.models.get(ENTERPRISE).to_dict()
    ingest(memory, eid='EV-CORR')
    assert memory.models.get(ENTERPRISE).to_dict() == before


def test_replaying_old_claim_does_not_restore_superseded_value(memory):
    ingest(memory)
    ingest(memory, eid='EV-NEXT', statement='Synthetic fuel benchmark decreased by 5 percent for Q1.',
           observation_date='2026-11-05', publication_date='2026-11-05')
    before = memory.models.get(ENTERPRISE).to_dict()
    ingest(memory)
    assert memory.models.get(ENTERPRISE).to_dict() == before


def test_retired_current_value_cannot_borrow_prior_active_support(memory):
    ingest(memory)
    latest = ingest(memory, eid='EV-NEXT', statement='Synthetic fuel benchmark decreased by 5 percent for Q1.',
                    observation_date='2026-11-05', publication_date='2026-11-05')
    rows = memory.observations.list()
    for row in rows:
        if row.observation_id == latest.observation_id:
            row.lifecycle_state = 'retired'
    memory.observations._rewrite(rows)
    _, pkg = package(memory)
    assert not pkg.selected_entities_and_relationships
    assert 'EV-NEXT' not in {i.stable_id for i in pkg.selected_observations}


@pytest.mark.parametrize('changes', [
    {'observation_date': '2027-11-01', 'publication_date': '2027-11-01'},
    {'scope': 'different-region'},
])
def test_same_quarter_different_year_or_scope_is_not_a_conflict(memory, changes):
    ingest(memory)
    result = ingest(memory, eid='EV-OTHER', statement='Synthetic fuel benchmark decreased by 5 percent for Q4.', **changes)
    assert not result.contradiction


def test_conflict_replay_preserves_both_claims_without_changing_model(memory):
    ingest(memory)
    ingest(memory, eid='EV-COUNTER', statement='Synthetic fuel benchmark decreased by 5 percent for Q4.')
    before = memory.models.get(ENTERPRISE).to_dict()
    ingest(memory, eid='EV-COUNTER', statement='Synthetic fuel benchmark decreased by 5 percent for Q4.')
    assert memory.models.get(ENTERPRISE).to_dict() == before
    assert len(package(memory)[1].selected_contradictions) == 2


def test_raw_missing_schema_is_provider_success_but_intelligence_rejection(memory, tmp_path):
    from cios.applications.flora.enterprise_intelligence.provider import LLMResult
    req, _, _ = brief(memory)
    class MissingSchema:
        def generate_structured(self, **kwargs):
            return LLMResult({'enterprise_id': ENTERPRISE, 'unvalidated': 'raw output'}, 'test', 'test', {}, 0)
    result = EnterpriseIntelligenceRuntime(provider=MissingSchema()).generate(req)
    assert result['audit']['provider_status'] == 'Succeeded'
    assert result['audit']['status'] == 'Rejected'
    assert result['audit']['rejected_output']['unvalidated'] == 'raw output'


def test_validator_exception_is_fail_closed_and_retains_raw_output(memory):
    req, _, payload = brief(memory)
    class BrokenValidator:
        def validate(self, *args):
            raise ValueError('Synthetic validation failure')
    result = EnterpriseIntelligenceRuntime(provider=StaticJSONProvider(payload), validator=BrokenValidator()).generate(req)
    assert result['audit']['status'] == 'Rejected'
    assert result['audit']['provider_status'] == 'Succeeded'
    assert result['audit']['rejected_output']['brief_id'] == payload['brief_id']


def test_missing_commercial_evidence_and_invalid_citation_cannot_be_hidden_in_nested_claim(memory):
    _, pkg, payload = brief(memory)
    payload['commercial_relevance_assessments'][0]['procurement'] = {'buying_intent': True, 'contract_value': 5000000}
    assert ClaimValidator().validate(payload, pkg)['validation_status']['status'] == 'invalid'


def test_unlabelled_opportunity_is_not_inferred_from_pressure(memory):
    _, pkg, payload = brief(memory)
    payload['opportunities'] = [{'statement': 'Synthetic Airline has a cloud migration opportunity.', 'evidence_basis': ['EV-FUEL']}]
    assert ClaimValidator().validate(payload, pkg)['validation_status']['status'] == 'invalid'


def test_nested_invalid_citation_is_rejected_even_with_valid_outer_lineage(memory):
    _, pkg, payload = brief(memory)
    payload['commercial_relevance_assessments'][0]['details'] = [{'statement': 'Inspect evidence.', 'evidence_basis': ['MISSING']}]
    assert ClaimValidator().validate(payload, pkg)['validation_status']['status'] == 'invalid'


def test_source_and_effective_dates_are_preserved_in_transient_context(memory):
    result = ingest(memory, effective_date='2026-10-31', period='Q4', source_date='2026-11-01')
    before = memory.observations.get(result.observation_id).to_dict()
    _, pkg = package(memory)
    dates = pkg.enterprise_context['observation_dates'][result.observation_id]
    assert dates['effective_date'] == '2026-10-31' and dates['effective_period'] == 'Q4'
    assert dates['source_publication_date'] == '2026-11-01'
    assert dates['observed_date'] == '2026-11-01'
    assert memory.observations.get(result.observation_id).to_dict() == before


def test_lower_confidence_replay_does_not_rewrite_observation_or_model(memory):
    ingest(memory)
    ledger = memory.observations.path.read_bytes()
    model = memory.models.get(ENTERPRISE).to_dict()
    ingest(memory, confidence=60)
    assert memory.observations.path.read_bytes() == ledger
    assert memory.models.get(ENTERPRISE).to_dict() == model


def test_evidence_limited_label_cannot_bypass_missing_material_support(memory):
    _, pkg, payload = brief(memory)
    payload['material_pressures'][0].update(interpretation_status='evidence_limited',
                                           supporting_observation_ids=[], supporting_evidence_ids=[])
    assert ClaimValidator().validate(payload, pkg)['validation_status']['status'] == 'invalid'


def test_contested_observation_cannot_be_laundered_through_its_raw_evidence(memory):
    req, pkg, payload = brief(memory)
    obs = next(i for i in pkg.selected_observations if i.object_class == 'observation')
    obs.truth_status = 'contradiction'
    assert ClaimValidator().validate(payload, pkg)['validation_status']['status'] == 'invalid'


def test_counter_evidence_remains_visible_as_conflicted_support(memory):
    ingest(memory)
    ingest(memory, eid='EV-COUNTER', statement='Synthetic fuel benchmark decreased by 5 percent for Q4.')
    _, pkg = package(memory)
    source_items = {i.stable_id: i for i in pkg.selected_observations if i.object_class == 'evidence'}
    assert {'EV-FUEL', 'EV-COUNTER'} <= source_items.keys()
    assert all(i.truth_status == 'contradiction' for i in source_items.values())
