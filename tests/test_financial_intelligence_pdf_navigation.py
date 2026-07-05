import json, sys, types
from pathlib import Path

from cios.applications.flora.financial_intelligence.pdf_document_adapter import load_canonical_pdf_document, QUALITY_CORRUPT
from cios.applications.flora.financial_intelligence.section_packets import select_candidate_pages, SectionAwareOpenAIProvider, build_page_packets
from cios.applications.flora.financial_intelligence.schema import ExperimentDocument
from cios.applications.flora.live.documents import DocumentPage
from cios.applications.flora import document_review


def _doc(tmp_path, page_count=222):
    pdf = tmp_path / 'report.pdf'; pdf.write_bytes(b'%PDF-1.4\nfixture')
    return ExperimentDocument(document_id='DOC', enterprise_id='bt-group-plc', title='BT Annual Report', source_url='https://example.com/report.pdf', retrieval_timestamp=document_review.now_iso(), checksum='a'*64, media_type='application/pdf', page_count=page_count, local_path=str(pdf))


def test_corrupt_embedded_text_fails_quality_gate(tmp_path):
    doc = _doc(tmp_path)
    canonical = load_canonical_pdf_document(doc, [DocumentPage(1, '\x00\x01@@@@@@@')])
    assert canonical.quality_state == QUALITY_CORRUPT
    assert canonical.quality_metrics['total_characters'] < 200


def test_stronger_parser_selected_when_it_produces_better_text(monkeypatch, tmp_path):
    doc = _doc(tmp_path, 2)
    class Page:
        def extract_text(self):
            return 'Financial highlights Revenue £20bn. Adjusted EBITDA £8bn. Operating profit £3bn. This sentence is readable.'
    class Reader:
        def __init__(self, *_): self.pages=[Page(), Page()]
    mod=types.ModuleType('pypdf'); mod.PdfReader=Reader
    monkeypatch.setitem(sys.modules, 'pypdf', mod)
    canonical = load_canonical_pdf_document(doc, [DocumentPage(1, '\x00bad')])
    assert canonical.selected_parser == 'pypdf'
    assert canonical.quality_state in {'text_extraction_usable','text_extraction_partial'}


def test_corrupt_text_cannot_enter_keyword_selection(tmp_path):
    doc = _doc(tmp_path)
    canonical = load_canonical_pdf_document(doc, [DocumentPage(1, 'revenue net debt ebitda \x00\x01')])
    assert canonical.quality_state == QUALITY_CORRUPT
    assert select_candidate_pages(canonical.pages) == []


def test_visual_navigation_invoked_and_preserves_page_numbers(monkeypatch, tmp_path):
    doc = _doc(tmp_path, 120)
    class Base:
        model='gpt-test'; max_output_tokens=100; max_retries=0; timeout_seconds=1
    
    class Counter:
        def count(self, **_): return {'input_tokens': 10}
    class Responses:
        input_tokens = Counter()
        def create(self, **_): raise RuntimeError('stop before paid call')
    class Client:
        responses = Responses()
    monkeypatch.setitem(sys.modules, 'openai', types.SimpleNamespace(OpenAI=lambda **_: Client()))
    extraction, plan = SectionAwareOpenAIProvider(Base()).extract_packets(doc, [DocumentPage(1, '\x00')], correlation_id='corr')
    assert plan['visual_navigation']['visual_fallback_used'] is True
    assert plan['candidate_pages']
    assert all(p['page_number'] >= 1 for p in plan['candidate_pages'])


def test_bt_golden_fixture_produces_non_empty_financial_plan_and_domains(tmp_path):
    doc = _doc(tmp_path, 222)
    canonical = load_canonical_pdf_document(doc, [DocumentPage(1, '\x00')])
    from cios.applications.flora.financial_intelligence.section_packets import visual_navigation_plan
    plan = visual_navigation_plan(doc, canonical)
    domains = {r['section_type'] for r in plan['selected_ranges']}
    assert plan['selected_ranges']
    assert len(domains) >= 3


def test_page_packets_remain_bounded():
    candidates = [type('C', (), {'page_number': i, 'text': 'Revenue £1bn', 'score': 10, 'matched_terms': (), 'matched_headings': (), 'reason': 'x'}) for i in range(1, 20)]
    packets = build_page_packets(candidates, max_packets=4)
    assert 1 <= len(packets) <= 4


def test_terminal_failed_progress_never_displays_working(monkeypatch):
    monkeypatch.setattr(document_review, 'load_run', lambda run_id: {'run_id': run_id, 'created_at': document_review.now_iso(), 'status': 'provider_response_invalid', 'claims': [], 'applied_results': [], 'exceptions': []})
    html = document_review.financial_intelligence_progress_page('fi-x')
    assert 'Working' not in html
    assert 'Failed' in html or 'Needs attention' in html


def test_missing_historic_progress_run_never_crashes(monkeypatch):
    monkeypatch.setattr(document_review, 'load_run', lambda run_id: (_ for _ in ()).throw(FileNotFoundError(run_id)))
    html = document_review.financial_intelligence_progress_page('fi-old')
    assert 'This previous refresh result is no longer available.' in html
    assert 'Start new refresh' in html


def test_zero_packets_cannot_complete_status(tmp_path):
    doc = _doc(tmp_path, 10)
    from cios.applications.flora.financial_intelligence.schema import ExtractionRun
    run = {'run_id':'fi-zero','created_at':document_review.now_iso(),'status':'validating','document':doc.model_dump(),'claims':[],'applied_results':[],'provider_diagnostics':[],'exceptions':[]}
    marked = document_review._mark_failure(run, 'failed', 'zero packets/facts/Observations cannot produce completed status')
    assert marked['status'] != 'completed'

def test_missing_progress_status_returns_terminal_safe_404_payload(monkeypatch):
    monkeypatch.setattr(document_review, 'load_run', lambda run_id: (_ for _ in ()).throw(FileNotFoundError('/var/data/flora/ai_financial_reports/runs/'+run_id+'.json')))
    status = document_review.financial_intelligence_progress_status('fi-old')
    assert status['status'] == 'not_found'
    assert status['terminal'] is True
    assert status['requested_run_id'] == 'fi-old'
    assert 'Please start a new run' in status['message']
    assert '/var/data' not in str(status)
    assert status['final_result_url'] is None


def test_missing_progress_page_terminal_browser_script_does_not_redirect_none(monkeypatch):
    monkeypatch.setattr(document_review, 'load_run', lambda run_id: {'run_id': run_id, 'created_at': document_review.now_iso(), 'status': 'queued', 'claims': [], 'applied_results': [], 'exceptions': []})
    html = document_review.financial_intelligence_progress_page('fi-old')
    assert 'if(s.final_result_url)' in html
    assert 'This financial intelligence run is no longer available' in html
