import pytest

from cios.applications.flora import document_review as review
from cios.applications.flora.financial_intelligence.provider_guard import provider_call_guard, ProviderCallViolation
from cios.applications.flora.memory.repository import EnterpriseModelRepository, EvidenceRepository, ObservationRepository


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
    assert run['status'] == 'section_selection_failed'


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
    assert len(paths) == 5
    assert len(active_obs) == 5
    assert len(EvidenceRepository().list()) == before_evidence
    assert all(EvidenceRepository().get(eid) for attr in model.attributes.values() for eid in attr.evidence_ids)
    assert 'AI calls made: 0' in review.financial_intelligence_run_page('fi-golden-one')
    assert ObservationRepository().list()
