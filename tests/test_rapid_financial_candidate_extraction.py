import hashlib, json
from pathlib import Path

import pytest

from cios.applications.flora.financial_intelligence.rapid_candidates import extract_rapid_financial_candidates
from cios.applications.flora.financial_intelligence.rapid_sources import AcquiredRapidSource, RapidSourceReceipt

BASE = """BT Group plc Results for the full year to 31 March 2026 FY26
synthetic source-family test fixture
Group statutory results
GBP m
Metric | FY26 | FY25 | Basis | Scope
Revenue | 19,654 | 20,800 | statutory | Group
Operating profit | 2,897 | 2,700 | statutory | Group
Profit before tax | 1,436 | 1,200 | statutory | Group
Adjusted operating profit | 3,100 | 3,000 | adjusted | Group
Segment revenue | 999 | 888 | statutory | Consumer segment
"""

def pdf(tmp_path: Path, text=BASE) -> Path:
    p=tmp_path/(hashlib.sha1(text.encode()).hexdigest()+'.pdf')
    import fitz
    doc=fitz.open(); page=doc.new_page(); page.insert_text((72,72), text, fontsize=10, fontname='courier'); doc.save(str(p)); doc.close()
    assert p.read_bytes().startswith(b'%PDF')
    return p

def receipt(path: Path, **overrides):
    raw=path.read_bytes(); data=dict(source_id='bt-fy26-results-release', configuration_key='bt-group-plc-fy26-results-release', enterprise_id='bt-group-plc', legal_name='BT Group plc', authority='BT Group plc', source_kind='official_results_pdf', document_title='FY26 results', publication_date='2026-05-22', reporting_period='FY26', period_start='2025-04-01', period_end='2026-03-31', scope='BT Group consolidated / Group', requested_url='https://www.bt.com/fy26.pdf', final_url='https://www.bt.com/fy26.pdf', artifact_host='www.bt.com', http_status=200, content_type='application/pdf', bytes_downloaded=len(raw), sha256=hashlib.sha256(raw).hexdigest(), retrieved_at='2026-07-06T00:00:00+00:00', request_attempted=True, redirect_chain=(), pdf_magic_valid=True, document_parse_result='parsed', identity_result='matched', period_result='matched', validation_result='accepted', failure_code=None, failure_stage=None, safe_failure_message=None)
    data.update(overrides); return RapidSourceReceipt(**data)

def run(tmp_path, text=BASE, **rkw):
    p=pdf(tmp_path,text); return extract_rapid_financial_candidates(AcquiredRapidSource(p, receipt(p, **rkw)))

def by_metric(result): return {c.proposed_canonical_metric_id:c for c in result.candidates}

def test_rejected_source_receipt_produces_zero_candidates(tmp_path):
    p=pdf(tmp_path); r=receipt(p, validation_result='rejected')
    result=extract_rapid_financial_candidates(AcquiredRapidSource(p,r))
    assert result.extraction_status=='failed_precondition'
    assert result.candidate_count==0
    assert result.exceptions[0].category=='source precondition failed'

def test_extracts_three_core_statutory_group_candidates_with_lineage(tmp_path):
    result=run(tmp_path); facts=by_metric(result)
    assert result.extraction_status=='completed'
    assert result.ai_call_count==0 and result.provider_cost==0 and result.canonical_write_count==0
    assert facts['revenue'].reported_amount.as_tuple() and str(facts['revenue'].reported_amount)=='19654'
    assert facts['operating_profit'].reported_amount == facts['operating_profit'].reported_amount.__class__('2897')
    assert facts['profit_before_tax'].reported_amount == facts['profit_before_tax'].reported_amount.__class__('1436')
    for metric,c in facts.items():
        loc=json.loads(c.source_locator)
        assert c.currency=='GBP' and c.reported_scale=='millions'
        assert c.raw_period_text=='FY26' and c.period_start=='2025-04-01' and c.period_end=='2026-03-31'
        assert c.scope_text=='BT Group consolidated / Group'
        assert c.accounting_basis_text=='statutory' and c.measurement_state_text=='actual'
        assert loc['page']==1 and loc['row']==c.raw_metric_label and loc['column']=='FY26'
        assert loc['scale_context']=='GBP m' and loc['source_sha256']==c.source_hash
        assert c.original_displayed_value in {'19,654','2,897','1,436'}
        assert c.supporting_excerpt
    assert any(e.category=='adjusted value rejected' for e in result.exceptions)
    assert any(e.category=='segment value rejected' for e in result.exceptions)

def test_prior_period_not_selected_and_display_text_retained(tmp_path):
    facts=by_metric(run(tmp_path))
    assert facts['revenue'].raw_value_text=='19,654'
    assert facts['revenue'].reported_amount.__class__('20800') != facts['revenue'].reported_amount

def test_candidate_ids_are_deterministic_and_no_duplicates(tmp_path):
    p=pdf(tmp_path); acquired=AcquiredRapidSource(p, receipt(p))
    a=extract_rapid_financial_candidates(acquired); b=extract_rapid_financial_candidates(acquired)
    assert [c.candidate_id for c in a.candidates] == [c.candidate_id for c in b.candidates]
    assert len({c.candidate_id for c in a.candidates}) == 3

def test_table_scale_marker_variants_are_controlled_and_propagated(tmp_path):
    for marker in ('£m', 'GBP m', 'GBP millions'):
        result = run(tmp_path, BASE.replace('GBP m', marker))
        assert result.extraction_status == 'completed'
        assert {c.reported_scale for c in result.candidates} == {'millions'}
        assert {json.loads(c.source_locator)['scale_context'] for c in result.candidates} == {marker}

def test_missing_scale_creates_partial_with_exception(tmp_path):
    result=run(tmp_path, BASE.replace('GBP m\n',''))
    assert result.extraction_status=='failed_extraction'
    assert result.candidate_count==0
    assert {e.category for e in result.exceptions} >= {'scale missing'}

def test_contradictory_table_scale_creates_exception(tmp_path):
    profile = json.loads(Path('config/flora/rapid_extraction/bt-group-plc-fy26.json').read_text())
    profile['permitted_scale_markers'] = {**profile['permitted_scale_markers'], 'GBP bn': 'billions'}
    p = pdf(tmp_path, BASE.replace('GBP m', 'GBP m and GBP bn'))
    result = extract_rapid_financial_candidates(AcquiredRapidSource(p, receipt(p)), profile=profile)
    assert result.candidate_count == 0
    assert any(e.category == 'scale contradictory' for e in result.exceptions)

def test_ambiguous_period_creates_exception(tmp_path):
    result=run(tmp_path, BASE.replace('Metric | FY26 | FY25 | Basis | Scope','Metric | Current | FY25 | Basis | Scope'))
    assert result.candidate_count==0
    assert any(e.category=='period column not identified' for e in result.exceptions)

def test_duplicate_revenue_rows_create_exception_and_partial(tmp_path):
    text=BASE.replace('Operating profit | 2,897 | 2,700 | statutory | Group', 'Revenue | 21,000 | 20,000 | statutory | Group\nOperating profit | 2,897 | 2,700 | statutory | Group')
    result=run(tmp_path, text)
    assert result.extraction_status=='partial'
    assert any(e.category=='multiple metric rows matched' and e.metric_identity=='revenue' for e in result.exceptions)

def test_negative_fixtures_fail_safely(tmp_path):
    cases=[
        (BASE.replace('Revenue | 19,654','Revenue | not-a-number'), 'amount ambiguous'),
        (BASE.replace('Revenue | 19,654 | 20,800 | statutory | Group\n',''), 'metric label not found'),
        (BASE.replace('synthetic source-family test fixture','x').replace('Group statutory results','No matching section'), 'supporting excerpt unavailable'),
    ]
    for text,cat in cases:
        result=run(tmp_path,text)
        assert any(e.category==cat for e in result.exceptions)

def test_source_receipt_sha_mismatch_fails_precondition(tmp_path):
    p=pdf(tmp_path); r=receipt(p, sha256='0'*64)
    result=extract_rapid_financial_candidates(AcquiredRapidSource(p,r))
    assert result.extraction_status=='failed_precondition'
    assert result.candidate_count==0

def layout_pdf(tmp_path: Path) -> Path:
    p=tmp_path/'synthetic-bt-results-layout-regression-fixture.pdf'
    import fitz
    doc=fitz.open(); page=doc.new_page(width=595, height=842)
    page.insert_text((72,72),'synthetic BT-results-layout regression fixture',fontsize=10)
    page.insert_text((72,92),'Group statutory results',fontsize=10)
    page.insert_text((72,112),'GBP m',fontsize=10)
    # Deliberately insert comparator column before FY26 and keep labels/values in separate positioned blocks.
    page.insert_text((300,132),'FY25',fontsize=10)
    page.insert_text((380,132),'FY26',fontsize=10)
    labels=[('Revenue',152),('Operating profit',172),('Profit before tax',192),('Adjusted operating profit',212),('Segment revenue',232)]
    for txt,y in labels: page.insert_text((72,y),txt,fontsize=10)
    fy25=['20,800','2,700','1,200','3,000','888']; fy26=['19,654','2,897','1,436','3,100','999']
    for v,(_,y) in zip(fy25,labels): page.insert_text((300,y),v,fontsize=10)
    for v,(_,y) in zip(fy26,labels): page.insert_text((380,y),v,fontsize=10)
    doc.save(str(p)); doc.close(); return p

def test_structural_bt_layout_fixture_reproduces_old_matcher_failure_and_new_extractor_reconstructs_rows(tmp_path):
    p=layout_pdf(tmp_path); res=extract_rapid_financial_candidates(AcquiredRapidSource(p, receipt(p)))
    facts=by_metric(res)
    assert res.diagnostics['old_line_row_count']==0
    assert res.diagnostics['geometric_row_count']>=3
    assert res.extraction_status=='completed' and res.candidate_count==3
    assert facts['revenue'].raw_value_text=='19,654'
    assert facts['operating_profit'].raw_value_text=='2,897'
    assert facts['profit_before_tax'].raw_value_text=='1,436'
    for c in facts.values():
        loc=json.loads(c.source_locator)
        assert loc['page']==1 and loc['column']=='fy26'
        assert loc['table']=='Group statutory results'
        assert loc['scale_context']=='GBP m'
        assert c.currency=='GBP' and c.reported_scale=='millions'
        assert c.scope_text=='BT Group consolidated / Group'
        assert c.accounting_basis_text=='statutory' and c.measurement_state_text=='actual'
        assert c.verification_status=='candidate_unverified'
        assert len(c.supporting_excerpt) < 300
    assert any(e.category=='adjusted value rejected' for e in res.exceptions)
    assert any(e.category=='segment value rejected' for e in res.exceptions)
    assert 'document_text' not in res.diagnostics and 'words' not in json.dumps(res.diagnostics).lower()

def split_label_layout_pdf(tmp_path: Path) -> Path:
    p=tmp_path/'synthetic-bt-split-label-regression-fixture.pdf'
    import fitz
    doc=fitz.open(); page=doc.new_page(width=595, height=842)
    page.insert_text((72,72),'synthetic BT-results-layout regression fixture',fontsize=10)
    page.insert_text((72,92),'Group statutory results',fontsize=10)
    page.insert_text((72,112),'GBP m',fontsize=10)
    page.insert_text((300,132),'FY25',fontsize=10); page.insert_text((380,132),'FY26',fontsize=10)
    page.insert_text((72,152),'Revenue',fontsize=10)
    page.insert_text((72,172),'Operating',fontsize=10); page.insert_text((132,172),'profit',fontsize=10)
    page.insert_text((72,192),'Profit before tax',fontsize=10)
    for v,y in [('20,800',152),('2,700',172),('1,200',192)]: page.insert_text((300,y),v,fontsize=10)
    for v,y in [('19,654',152),('2,897',172),('1,436',192)]: page.insert_text((380,y),v,fontsize=10)
    doc.save(str(p)); doc.close(); return p

def test_split_operating_profit_label_is_reconstructed_across_spans(tmp_path):
    p=split_label_layout_pdf(tmp_path)
    res=extract_rapid_financial_candidates(AcquiredRapidSource(p, receipt(p)))
    facts=by_metric(res)
    assert res.extraction_status=='completed'
    assert facts['operating_profit'].raw_metric_label == 'Operating profit'
    assert facts['operating_profit'].raw_value_text == '2,897'
    assert res.diagnostics['candidate_count'] == 3
    assert res.diagnostics['extraction_status'] == 'completed'
    assert res.diagnostics['metric_aliases_attempted']
