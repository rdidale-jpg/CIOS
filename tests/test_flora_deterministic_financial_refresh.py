import pytest

from cios.applications.flora import document_review as review
from cios.applications.flora.financial_intelligence.provider_guard import provider_call_guard, ProviderCallViolation
from cios.applications.flora.memory.repository import EnterpriseModelRepository, EvidenceRepository, ObservationRepository
from cios.applications.flora.memory.models import EnterpriseModelAttribute


def test_standard_refresh_fails_closed_without_ai_fallback(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    pdf = b'%PDF-1.4\nBT Annual Report narrative only\n'
    local = tmp_path / 'bt.pdf'; local.write_bytes(pdf)

    class Fetch:
        succeeded = True; status_code = 200; media_type = 'application/pdf'; content = pdf; checksum = 'e' * 64
        local_path = str(local); retrieval_date = review.now_iso(); error = ''; final_url = 'https://www.bt.com/report.pdf'; url = final_url; redirect_chain = ()

    monkeypatch.setattr(review, 'fetch_document', lambda url: Fetch())
    monkeypatch.setattr(review, '_bt_annual_report_source', lambda: {'source_id': 'bt-annual-report-2026', 'source_name': 'BT Group plc Annual Report 2026', 'url': 'https://www.bt.com/report.pdf', 'source_type': 'annual_report', 'authority_tier': 'tier_1_company_authoritative', 'publisher': 'BT Group plc'})
    monkeypatch.setattr(review.OpenAIDirectPDFProvider, 'extract_facts', lambda *a, **k: pytest.fail('structured route must not silently fall back to OpenAI'))

    run = review.refresh_financial_intelligence()

    assert run['extraction_mode'] == 'structured_standard_financials'
    assert run['openai_calls_made'] == 0
    assert run['status'] == 'structured_source_unavailable'


def test_provider_guard_blocks_call_before_transmission():
    with provider_call_guard('structured_standard_financials', allowed_calls=0) as guard:
        with pytest.raises(ProviderCallViolation):
            guard.before_provider_call('openai', 'unit.test')
    assert guard.attempted_calls == 1
    assert guard.violations[0]['failure_category'] == 'deterministic_route_provider_violation'


def test_route_level_golden_persists_evidence_and_idempotent(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    pdf_text = b'%PDF-1.4\n(FLORA PDF PAGE 1 Financial highlights) Tj\n(Income statement) Tj\n(Year ended 31 March 2026) Tj\n(GBP millions) Tj\n(Revenue 19,654) Tj\n(Revenue \xc2\xa319.7bn) Tj\n(Adjusted EBITDA 8,230) Tj\n(Capital expenditure 5,127) Tj\n(Cash flow from operating activities 7,000) Tj\n(Normalised free cash flow 1,508) Tj\n'
    pdf = tmp_path / 'bt.pdf'; pdf.write_bytes(pdf_text)

    class Fetch:
        succeeded = True; status_code = 200; media_type = 'application/pdf'; content = pdf_text; checksum = 'f' * 64
        local_path = str(pdf); retrieval_date = review.now_iso(); error = ''; final_url = 'https://www.bt.com/report.pdf'; url = final_url; redirect_chain = ()

    monkeypatch.setattr(review, 'fetch_document', lambda url: Fetch())
    monkeypatch.setattr(review, '_bt_annual_report_source', lambda: {'source_id': 'bt-annual-report-2026', 'source_name': 'BT Group plc Annual Report 2026', 'url': 'https://www.bt.com/report.pdf', 'source_type': 'annual_report', 'authority_tier': 'tier_1_company_authoritative', 'publisher': 'BT Group plc'})
    monkeypatch.setattr(review.OpenAIDirectPDFProvider, 'extract_facts', lambda *a, **k: pytest.fail('structured route must not call OpenAI'))

    first = review.refresh_financial_intelligence(run_id='fi-golden-one')
    before_evidence = len(EvidenceRepository().list())
    second = review.refresh_financial_intelligence(run_id='fi-golden-two')

    model = EnterpriseModelRepository().get('bt-group-plc')
    paths = [p for p in model.attributes if p.startswith('financial_performance.metrics.')]
    active_obs = {oid for p in paths for oid in model.attributes[p].observation_ids}
    assert first['ai_calls_made'] == second['ai_calls_made'] == 0
    assert len(paths) == 0
    assert len(active_obs) == 0
    assert len(EvidenceRepository().list()) == before_evidence
    assert all(EvidenceRepository().get(eid) for attr in model.attributes.values() for eid in attr.evidence_ids)
    assert 'AI calls made: 0' in review.financial_intelligence_run_page('fi-golden-one')
    assert not ObservationRepository().list()

def test_structured_standard_refresh_uses_structured_adapter_and_no_fallback(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    called = {'structured': 0, 'pdf': 0, 'provider': 0, 'packets': 0}

    class Adapter(review.OfficialStructuredFinancialAdapter):
        def extract(self, document, **kwargs):
            called['structured'] += 1
            return super().extract(document, **kwargs)

    monkeypatch.setattr(review, 'OfficialStructuredFinancialAdapter', Adapter)
    monkeypatch.setattr(review.PdfFinancialTableAdapter, 'extract', lambda *a, **k: called.__setitem__('pdf', called['pdf'] + 1) or pytest.fail('structured mode must not use PDF candidate extractor'))
    monkeypatch.setattr(review.OpenAIDirectPDFProvider, 'extract_facts', lambda *a, **k: called.__setitem__('provider', called['provider'] + 1) or pytest.fail('structured mode must not call OpenAI'))
    monkeypatch.setattr(review.SectionAwareOpenAIProvider, 'extract_packets', lambda *a, **k: called.__setitem__('packets', called['packets'] + 1) or pytest.fail('structured mode must not create PDF packets'))

    run = review.refresh_financial_intelligence(run_id='fi-structured-missing')

    assert called == {'structured': 1, 'pdf': 0, 'provider': 0, 'packets': 0}
    assert run['status'] == 'structured_source_unavailable'
    assert run['extraction_mode'] == 'structured_standard_financials'
    assert run['claims'] == []
    assert run['candidate_lifecycle_counts']['packet_candidates_extracted'] == 0
    assert run['ai_calls_made'] == 0
    assert run['pdf_fallback_calls_made'] == 0
    assert run['prohibited_path_counters'] == {'pdf_section_selector_calls': 0, 'pdf_candidate_extractor_calls': 0, 'pdf_packet_calls': 0, 'provider_calls': 0}
    assert 'section_selection_failed' not in str(run)
    assert all('source_page' not in str(c) for c in run['claims'])
    assert any(d['event'] == 'structured_adapter_selected' and d['adapter_class'] == 'Adapter' for d in run['structured_diagnostics'])


def test_structured_missing_source_preserves_existing_trusted_state(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    svc = review.ObservationMemoryService()
    model = svc.models.get('bt-group-plc')
    model.attributes['identity.test_attribute'] = EnterpriseModelAttribute(domain='identity', attribute='test_attribute', current_value='kept', confidence=90, last_observed_date=review.now_iso(), freshness='current', observation_ids=(), evidence_ids=(), provenance_type='test')
    svc.models.save(model)

    before = review._trusted_state_snapshot('bt-group-plc')
    run = review.refresh_financial_intelligence(run_id='fi-preserve')
    after = review._trusted_state_snapshot('bt-group-plc')

    assert run['status'] == 'structured_source_unavailable'
    assert before['active_enterprise_model_attribute_count'] == after['active_enterprise_model_attribute_count']
    assert before['active_observation_count'] == after['active_observation_count']
    assert run['trusted_twin_changed'] is False
    assert run['ephemeral_state_absent_before_run'] is False


def test_structured_missing_source_marks_fresh_ephemeral_absence(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    run = review.refresh_financial_intelligence(run_id='fi-empty')
    assert run['trusted_state_before']['state_existed_before_run'] is False
    assert run['ephemeral_state_absent_before_run'] is True
    assert run['trusted_twin_changed'] is False


def test_malformed_legacy_pdf_candidates_cannot_leak_into_structured_result(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    run = review.refresh_financial_intelligence(run_id='fi-negative-fixture', extraction_mode='structured_standard_financials')
    rendered = str(run) + review.financial_intelligence_run_page('fi-negative-fixture')
    for forbidden in ['adjusted EBITDA — (£m)a', 'adjusted EBITDA — 27.5%', 'FY27 actual', 'source page']:
        assert forbidden not in rendered
    assert 'Reporting period: detected from candidates' not in rendered
