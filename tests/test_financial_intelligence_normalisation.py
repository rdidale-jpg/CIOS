from cios.applications.flora.financial_intelligence.normalisation import canonicalise_financial_claim, normalise_amount
from cios.applications.flora import document_review
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository
from cios.applications.flora.memory.service import ObservationMemoryService


def base_claim(**kw):
    c = {
        'claim_id': 'c1', 'evidence_id': 'ev1', 'claim_type': 'financial_metric_reported',
        'canonical_enterprise_id': 'bt-group-plc', 'predicate': 'Revenue', 'value': 19.7,
        'reported_amount': 19.7, 'reported_scale': 'billion', 'currency': 'GBP',
        'period': 'FY26', 'state': 'actual', 'business_unit': 'BT Group plc',
        'page_reference': '10', 'source_excerpt': 'Revenue was £19.7bn.',
        'original_statement': 'BT Group plc Revenue 19.7 billion GBP for FY26.',
        'confidence': 95, 'affected_attribute': 'financial_performance.metrics.revenue.FY26.actual',
    }
    c.update(kw)
    return c


def run_for(claims):
    return {'run_id': 'fi-test', 'governed_source': {'source_id': 'bt'}, 'document': {'checksum': 'x', 'document_id': 'doc', 'title': 'BT AR', 'source_url': 'url'}, 'claims': claims, 'candidate_exceptions': []}


def test_bn_and_millions_normalise_to_base_units():
    assert normalise_amount('19.7', 'bn') == 19700000000
    assert normalise_amount('19654', 'm') == 19654000000


def test_scale_is_retained_and_missing_scale_blocks_acceptance():
    ok, reasons = canonicalise_financial_claim(base_claim())
    assert ok['reported_scale'] == 'billions'
    assert ok['normalised_amount'] == 19700000000
    missing, reasons = canonicalise_financial_claim(base_claim(reported_scale=None, unit=None))
    assert 'financial_scale_ambiguous' in reasons
    acceptable, reason = document_review._is_auto_acceptable(missing, run_for([missing]))
    assert acceptable is False
    assert reason == 'financial_scale_ambiguous'


def test_duplicate_financial_metrics_are_reconciled_and_counts_balance(monkeypatch, tmp_path):
    svc = ObservationMemoryService(ObservationRepository(tmp_path / 'obs.jsonl'), EnterpriseModelRepository(tmp_path / 'models'))
    monkeypatch.setattr(document_review, 'ObservationMemoryService', lambda: svc)
    precise = base_claim(claim_id='c2', evidence_id='ev2', value=19654, reported_amount=19654, reported_scale='m', original_statement='BT Group plc Revenue 19654 millions GBP for FY26.', source_excerpt='Revenue was £19,654m.')
    run = document_review._apply_automatic_claims(run_for([base_claim(), precise]))
    counts = run['candidate_lifecycle_counts']
    assert counts['valid_candidates'] == counts['automatically_accepted_candidates'] + counts['deduplicated_candidates'] + counts['candidates_rejected_by_policy']
    assert counts['deduplicated_candidates'] == 1
    assert run['applied_results'][0]['affected_attribute'] == 'financial_performance.metrics.revenue.FY26.group.actual'
    model = EnterpriseModelRepository(tmp_path / 'models').get('bt-group-plc')
    attr = model.attributes['financial_performance.metrics.revenue.FY26.group.actual']
    assert attr.current_value is not None


def test_accounting_bases_remain_distinct(monkeypatch, tmp_path):
    svc = ObservationMemoryService(ObservationRepository(tmp_path / 'obs.jsonl'), EnterpriseModelRepository(tmp_path / 'models'))
    monkeypatch.setattr(document_review, 'ObservationMemoryService', lambda: svc)
    statutory = base_claim(predicate='Operating profit statutory', reported_amount=1, value=1)
    adjusted = base_claim(claim_id='c2', evidence_id='ev2', predicate='Operating profit adjusted', reported_amount=2, value=2)
    run = document_review._apply_automatic_claims(run_for([statutory, adjusted]))
    attrs = EnterpriseModelRepository(tmp_path / 'models').get('bt-group-plc').attributes
    assert 'financial_performance.metrics.operating_profit_statutory.FY26.group.statutory' in attrs
    assert 'financial_performance.metrics.operating_profit_adjusted.FY26.group.adjusted' in attrs
    assert run['deduplicated_count'] == 0


def test_completed_with_exceptions_language_and_reprocess_without_openai(monkeypatch, tmp_path):
    svc = ObservationMemoryService(ObservationRepository(tmp_path / 'obs.jsonl'), EnterpriseModelRepository(tmp_path / 'models'))
    monkeypatch.setattr(document_review, 'ObservationMemoryService', lambda: svc)
    run = document_review._apply_automatic_claims(run_for([base_claim(), base_claim(claim_id='bad', evidence_id='evb', predicate='Adjusted EBITDA', reported_scale=None)]))
    html = document_review._outcome_summary(run)
    assert run['status'] == 'completed_with_exceptions'
    assert 'Financial intelligence was updated. Some extracted facts require attention.' in html
    assert 'Retry</button>' not in html
    assert 'Revenue: £19.7bn' in html
