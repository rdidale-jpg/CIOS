from experiments.document_understanding.schema import ExtractionRun, FoundationFact
from cios.applications.flora.live import ai_review
from cios.applications.flora.live.ai_review import apply_accepted, create_upload_run, update_reviews
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository


def fact(**overrides):
    base = dict(
        fact_id='f1', canonical_enterprise_id='bt-group-plc', claim_type='financial_metric_reported',
        subject_type='enterprise', subject_name='BT Group plc', predicate='reported revenue', object_type='financial_metric',
        value_number=20.4, scale='billion', currency='GBP', period_label='FY26', state='actual',
        source_document_id='doc', source_page_start=12, source_page_end=12, source_excerpt='Revenue was £20.4bn in FY26.',
        extraction_confidence=.91, explicit_in_source=True, extractor_provider='openai', extractor_model='gpt-5.5', extractor_version='test',
    )
    base.update(overrides)
    return FoundationFact(**base)


def test_ai_financial_report_review_applies_accepted_claim(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    def fake_extract(self, document, schema=None, page_ranges=None):
        return ExtractionRun(run_id='x', route='openai-direct', provider='openai', model='gpt-5.5', status='completed', started_at=ai_review.now_iso(), completed_at=ai_review.now_iso(), latency_seconds=0, facts=[fact()])

    monkeypatch.setattr(ai_review.OpenAIDirectPDFProvider, 'extract_facts', fake_extract)
    pdf = tmp_path / 'bt.pdf'
    pdf.write_bytes(b'%PDF-1.4\nBT Annual Report fixture')

    run = create_upload_run(pdf)
    assert run['provider'] == 'openai'
    assert run['model'] == 'gpt-5.5'
    assert run['claims'][0]['page_reference'] == '12'

    update_reviews(run['run_id'], {f"action_{run['claims'][0]['claim_id']}": ['accept']})
    applied = apply_accepted(run['run_id'])

    assert applied['applied_results']
    assert ObservationRepository().list()
    model = EnterpriseModelRepository().get('bt-group-plc')
    assert 'financial_performance.metrics.reported_revenue.FY26.actual' in model.attributes


def test_review_page_exposes_accept_amend_reject(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    def fake_extract(self, document, schema=None, page_ranges=None):
        return ExtractionRun(run_id='x', route='openai-direct', provider='openai', model='gpt-5.5', status='completed', started_at=ai_review.now_iso(), completed_at=ai_review.now_iso(), latency_seconds=0, facts=[fact()])
    monkeypatch.setattr(ai_review.OpenAIDirectPDFProvider, 'extract_facts', fake_extract)
    pdf = tmp_path / 'bt.pdf'; pdf.write_bytes(b'%PDF-1.4')
    run = create_upload_run(pdf)
    html = ai_review.run_page(run['run_id'])
    assert 'Accept' in html and 'Amend' in html and 'Reject' in html
    assert 'Enterprise Memory' in html
