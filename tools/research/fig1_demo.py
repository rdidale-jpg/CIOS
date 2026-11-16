"""FIG-1 fixed synthetic contract demonstration, not a financial engine.

No real bank inputs, network, acquisition, source permission, owner repository,
canonical write, provider call or application route. Existing pure financial and
presentation contracts are exercised; proposed behaviour is labelled separately.
"""
from dataclasses import asdict, replace
from decimal import Decimal
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cios.applications.flora import intelligence_presentation as p
from cios.applications.flora.financial_intelligence.schema import NumericFactValue
from cios.applications.flora.financial_intelligence.normalisation import (
    normalise_amount, normalise_reporting_period, resolve_metric, rounding_compatible,
)
from cios.applications.flora.memory.models import Observation
from cios.applications.flora.memory.service import _financial_model_value
from cios.applications.flora.blueprint_import.mapping import evidence_is_current
from cios.applications.flora.research_intelligence.source_import import official_url

PACK = ROOT / 'docs/flora-runtime/fig1'
FIXTURE_SCOPE = 'Fictional Example Banking Group; synthetic fixture only'
FLOW_PERIOD = '1 January–30 September 2026 (fictional 9M flow)'
FIXTURE_SOURCE = p.Source('Synthetic worked example; no official-source claim',
                         'https://example.invalid/fig1-fixture', 'Fictional fixture',
                         '2026-10-30', 'As explicitly stated per synthetic measure',
                         locator='Fixed FIG-1 fixture, not a real bank report')


def fixtures():
    """Small fixed worked example using the existing Statement contract."""
    def reported(text, value, period, basis):
        return p.Statement(text, 'reported', FIXTURE_SCOPE, period, (FIXTURE_SOURCE,),
                           'reported_source', 'synthetic_candidate_not_canonical',
                           measurement_state='actual', basis=basis,
                           value=Decimal(value), unit='GBP billion',
                           caveats=('Fictional example; not actual bank economics or an accepted record.',))
    stock = reported('Example Group customer deposits were GBP 100 billion at 30 September 2026.',
                     '100', '30 September 2026 (point-in-time stock)', 'Group total deposit stock')
    income = reported('Example Group income was GBP 12 billion during the stated nine months.',
                      '12', FLOW_PERIOD, 'Fictional statutory Group period basis')
    costs = reported('Example Group operating costs were GBP 7 billion during the stated nine months.',
                     '7', FLOW_PERIOD, 'Fictional statutory Group period basis')
    calc = p.difference(income, costs, text='Illustrative income less operating costs was GBP 5 billion, before credit charges and other items.')
    assumption = p.Statement('The example assumes 40% of operating costs are addressable and a 5% change in that share.',
        'assumed', FIXTURE_SCOPE, FLOW_PERIOD, (FIXTURE_SOURCE,), 'fixture_assumption',
        'synthetic_working_assumption_not_canonical', assumption_owner='Example analyst, not a real bank executive',
        assumption_version='fig1-fixture-v1', caveats=('Neither fraction is reported company evidence or a delivery commitment.',))
    amount = costs.value * Decimal('0.40') * Decimal('0.05')
    estimate = p.Statement('Illustrative gross scenario cost reduction is GBP 0.14 billion; this is not a forecast or buyer budget.',
        'estimated', FIXTURE_SCOPE, FLOW_PERIOD, (FIXTURE_SOURCE,), 'synthetic_scenario',
        'derived_view_not_canonical', value=amount, unit='GBP billion',
        method='7 × 0.40 × 0.05 = 0.14 GBP billion; fixed example arithmetic',
        dependencies=(costs.text, assumption.text), dependency_types=('reported', 'assumed'),
        caveats=('Fictional baseline and explicit working assumptions; gross before implementation costs, timing, feasibility and double counting.',
                 'Not net benefit, cash release, procurement funding, customer intent or an opportunity value.'))
    insight = p.Statement('In this fictional example, the scenario result depends on cost addressability rather than the deposit-stock size.',
        'insight', FIXTURE_SCOPE, FLOW_PERIOD, (FIXTURE_SOURCE,), 'example_interpretation',
        'derived_view_not_canonical', reasoning='The fixed cost scenario uses the cost flow and two assumptions, with no deposit-stock input.',
        dependencies=(costs.text, assumption.text), counter_evidence=('The addressable share or implementation feasibility may not exist.',))
    hypothesis = p.Statement('The fictional addressable-cost scenario may be achievable.', 'hypothesis',
        FIXTURE_SCOPE, FLOW_PERIOD, (FIXTURE_SOURCE,), 'example_hypothesis', 'derived_view_not_canonical',
        reasoning='A conditional interpretation of the illustrative scenario only.', dependencies=(estimate.text,),
        counter_evidence=('Execution costs and operational constraints could remove the gross effect.',),
        falsifier='The example assumption fails if the addressable share is unsupported or implementation costs exceed the gross effect.')
    return dict(stock=stock, flow=income, costs=costs, calculated=calc, assumption=assumption,
                estimated=estimate, insight=insight, hypothesis=hypothesis)


def current_contract_limits():
    period = normalise_reporting_period('30 September 2026')
    text = 'Example Group reported customer deposits of GBP 100 billion at 30 September 2026.'
    # Transient format fixture only. Its Evidence string/lifecycle is not real
    # ownership, an acceptance receipt or a persisted canonical object.
    obj = Observation('fixture:example-group-not-real', 'financial_metric_reported', text,
                      '2026-09-30', '2026-11-16', 'financial_performance.metrics.example-deposit',
                      50, ('fixture:evidence-not-accepted',), lifecycle_state='candidate',
                      human_provenance={'fixture_only': True,
                          'example_financial_payload': {'kind': 'numeric', 'amount': '100',
                                                       'scale': 'billion', 'currency': 'GBP'}})
    obj.normalised_amount = 100000000000
    clone = Observation.from_dict(json.loads(json.dumps(obj.to_dict())))
    typed_metadata = NumericFactValue.model_validate(clone.human_provenance['example_financial_payload'])
    return {
        'deposit_metric_result': resolve_metric('Customer deposits')[1],
        'stock_date_misnormalised_currently': asdict(period),
        'dynamic_numeric_field_survives_observation_reload': hasattr(clone, 'normalised_amount'),
        'existing_provenance_dictionary_can_retain_typed_payload': typed_metadata.amount == Decimal('100'),
        'typed_payload_projection_currently_implemented': False,
        'deposit_numeric_prose_fallback_supported': _financial_model_value(text) != text,
        'mapping_helper_gap': {key: evidence_is_current({'lifecycle_state': 'accepted', **value})
            for key, value in [('stale', {'freshness': 'stale'}), ('withdrawn', {'withdrawn': True}),
                               ('retracted', {'retracted': True}), ('core_contradiction', {'core_contradiction': True})]},
        'extent': 'Observed format/serialization limits, not a successful canonical financial projection',
    }


def demonstration():
    f = fixtures()
    rendered = {key: p.render(value) for key, value in f.items()}
    for key, item in f.items():
        if not p.eligible(item):
            raise ValueError('Fixed synthetic example unexpectedly ineligible: ' + key)
    # Candidate numeric JSON persistence is supported without any Observation,
    # Evidence, Model or application repository write.
    number = NumericFactValue(amount=Decimal('100.125'), scale='billion', currency='GBP')
    with tempfile.TemporaryDirectory(prefix='fig1-synthetic-json-') as scratch:
        path = Path(scratch) / 'example-candidate-value.json'
        path.write_text(number.model_dump_json())
        restored = NumericFactValue.model_validate_json(path.read_text())
    conflict = replace(f['stock'], core_contradiction=True)
    superseded = replace(f['stock'], freshness='superseded')
    conflicting_alternative = replace(f['stock'], text='Conflicting fictional deposit value is GBP 101 billion.',
                                      value=Decimal('101'), core_contradiction=True)
    revoked_metadata = {'rights': {'status': 'revoked'}}
    # Demonstrate the EXISTING caller/presentation boundary with a fixed fixture,
    # not a substitute source-use evaluator or permission grant.
    revoked_html = '' if p.restricted_metadata(revoked_metadata) else p.render(f['stock'])
    incompatible = {}
    for key, changed in [('subsidiary', replace(f['costs'], scope='Fictional subsidiary, not Group')),
                         ('period', replace(f['costs'], period='Different fictional flow period')),
                         ('currency', replace(f['costs'], unit='USD billion')),
                         ('basis', replace(f['costs'], basis='Different adjusted definition')),
                         ('stock_vs_flow', f['stock'])]:
        try:
            p.difference(f['flow'], changed, text='Incompatible example must not render')
        except ValueError:
            incompatible[key] = 'rejected_by_existing_difference'
        else:
            raise ValueError('Existing comparison accepted incompatible fixture: ' + key)
    assumed_cost = replace(f['costs'], semantic_type='assumed', value=Decimal('6.5'),
                           assumption_owner='Example analyst', assumption_version='v1',
                           caveats=('Assumed cost input, not reported.',))
    dependent = p.difference(f['flow'], assumed_cost, text='A calculation dependent on an assumed input')
    return {
        'classification': 'SYNTHETIC NON-PRODUCTION ARCHITECTURE DEMONSTRATION; no real bank facts',
        'canonical_writes': 0, 'canonical_acceptance_executed': False,
        'new_source_permissions': 0, 'owner_repository_reads': 0, 'paid_calls': 0, 'receipt_ids': [],
        'reported_stock': {'as_at': '2026-09-30', 'value': '100', 'scale': 'billion', 'currency': 'GBP'},
        'reported_flow': {'start': '2026-01-01', 'end': '2026-09-30', 'value': '12', 'scale': 'billion', 'currency': 'GBP'},
        'compatible_calculation': {'value': str(f['calculated'].value), 'semantic_type': f['calculated'].semantic_type,
                                   'canonical_status': f['calculated'].canonical_status, 'method': f['calculated'].method},
        'estimate': {'value': str(f['estimated'].value), 'semantic_type': f['estimated'].semantic_type,
                     'method': f['estimated'].method, 'assumptions': f['assumption'].text,
                     'caveats': list(f['estimated'].caveats), 'canonical_status': f['estimated'].canonical_status},
        'conflict': {'primary_omitted': p.render(conflict) == '',
                     'alternative_omitted': p.render(conflicting_alternative) == '',
                     'historical_positions_preserved_in_this_fixture': ['100', '101']},
        'superseded_omitted': p.render(superseded) == '', 'revoked_source_omitted': revoked_html == '',
        'group_subsidiary_and_comparison_checks': incompatible,
        'typed_candidate_json_roundtrip': restored == number,
        'normalised_candidate_value': format(normalise_amount(restored.amount, restored.scale), 'f'),
        'current_contract_limits': current_contract_limits(),
        'assumption_taint_current_contract': {'semantic_type': dependent.semantic_type,
            'dependency_types': list(dependent.dependency_types),
            'proposed_display_requirement': 'Estimated or explicitly assumption-dependent calculation; never Reported or accepted truth'},
        'rendered_examples': rendered,
        'limits': 'No live eligibility, source permission, original source receipt, authenticated owner action, durable numeric Model creation or production UI demonstrated',
    }


if __name__ == '__main__':
    print(json.dumps(demonstration(), indent=2))
