import hashlib
from pathlib import Path

from cios.applications.flora.financial_intelligence.rapid_sources import AcquiredRapidSource, RapidSourceReceipt
from cios.applications.flora.financial_intelligence.rapid_ai_twin import create_rapid_ai_twin_snapshot, build_csv
from cios.applications.flora import document_review as review
from cios.applications.flora import digital_twins


def _receipt(path: Path):
    raw = path.read_bytes()
    return RapidSourceReceipt(source_id='bt-fy26', configuration_key='bt-group-plc-fy26', enterprise_id='bt-group-plc', legal_name='BT Group plc', authority='BT Group plc', source_kind='official_results_pdf', document_title='BT Group plc Annual Report 2026', publication_date='2026-06-11', reporting_period='FY26', period_start='2025-04-01', period_end='2026-03-31', scope='Group', requested_url='https://www.bt.com/report.pdf', final_url='https://www.bt.com/report.pdf', artifact_host='www.bt.com', http_status=200, content_type='application/pdf', bytes_downloaded=len(raw), sha256=hashlib.sha256(raw).hexdigest(), retrieved_at='2026-07-06T00:00:00+00:00', request_attempted=True, redirect_chain=(), pdf_magic_valid=True, document_parse_result='parsed', identity_result='matched', period_result='matched', validation_result='accepted', failure_code=None, failure_stage=None, safe_failure_message=None)


def _pdf(tmp_path):
    p=tmp_path/'bt.pdf'; p.write_bytes(b'%PDF-1.4\nBT Group plc FY26\n%%EOF' + b'x'*600); return p


def extraction_payload():
    rows=[
        {'row_id':'row-revenue','reported_label':'Revenue','current_period_display_value':'19,654','comparator_display_value':'20,797','parsed_current_amount':19654,'parsed_comparator_amount':20797,'unit':'GBP','scale':'m','scope':'Group','accounting_basis':'statutory','financial_measurement_state':'actual','source_page':10,'supporting_excerpt':'Revenue 19,654 20,797','confidence':0.96,'ambiguity':'','proposed_canonical_metric_id':'revenue'},
        {'row_id':'row-adjusted-ebitda','reported_label':'Adjusted EBITDA','current_period_display_value':'8,219','comparator_display_value':'8,103','unit':'GBP','scale':'m','scope':'Group','accounting_basis':'adjusted','financial_measurement_state':'actual','source_page':10,'supporting_excerpt':'Adjusted EBITDA 8,219 8,103','confidence':0.94,'ambiguity':'','proposed_canonical_metric_id':'unmapped_reported_metric'},
        {'row_id':'row-consumer','reported_label':'Consumer revenue','current_period_display_value':'9,123','comparator_display_value':'9,200','unit':'GBP','scale':'m','scope':'Consumer segment','accounting_basis':'statutory','financial_measurement_state':'actual','source_page':12,'supporting_excerpt':'Consumer revenue 9,123 9,200','confidence':0.9,'ambiguity':'','proposed_canonical_metric_id':'unmapped_reported_metric'},
        {'row_id':'row-guidance','reported_label':'FY27 free cash flow guidance','current_period_display_value':'c. £1.5bn','comparator_display_value':'n/a','unit':'GBP','scale':'bn','scope':'Group','accounting_basis':'guidance','financial_measurement_state':'guidance','source_page':15,'supporting_excerpt':'FY27 free cash flow guidance c. £1.5bn','confidence':0.88,'ambiguity':'display value retained','proposed_canonical_metric_id':'unmapped_reported_metric'},
        {'row_id':'row-invalid','reported_label':'Invalid','current_period_display_value':'x','source_page':999,'supporting_excerpt':'bad'},
    ]
    return {'document_identity': {'enterprise_name':'BT Group plc','document_title':'BT Group plc Annual Report 2026','reporting_period':'FY26','publication_date':'2026-06-11','document_page_count':200}, 'financial_tables':[{'table_id':'tbl-group','title':'Group results','page':10,'section':'Financial results','scope':'Group','currency':'GBP','scale':'m','accounting_basis':'mixed','column_headings':['Metric','FY26','FY25','Source'],'row_order':[r['row_id'] for r in rows],'rows':rows}], 'reported_facts':[{'fact_id':'fact-cost','category':'cost','statement':'BT reported a cost transformation programme.','source_page':20,'source_section':'Strategy','supporting_excerpt':'cost transformation','confidence':0.9,'reporting_period':'FY26','fact_type':'reported_fact','ambiguity':'','related_table_or_metric_ids':['row-revenue']}], 'management_commitments':[{'commitment':'Reduce costs','owner':'Group Chief Executive','timing':'FY29','quantitative_target':'reported target','current_status':'in progress','source_page':21,'supporting_excerpt':'reduce costs','Unknowns':[]}], 'strategic_priorities':[{'statement':'Simplify BT','source_page':22,'supporting_excerpt':'simplify'}], 'transformation_programmes':[{'programme_name':'Cost transformation','objective':'lower cost base','reported_progress':'in progress','timing':'FY26-FY29','source_citation':{'page':23}}], 'risks_and_pressures':[{'statement':'Revenue pressure','source_page':24,'supporting_excerpt':'revenue declined'}], 'technology_digital_ai':[], 'leadership_and_governance':[], 'customer_market_and_regulation':[], 'unknowns':['Programme ownership unclear'], 'extraction_coverage':{}, 'citation_index':[{'id':'fact-cost','page':20}]}


def synthesis_payload():
    return {'executive_summary':[{'statement':'Reported revenue changed and cost transformation matters.','supporting_fact_ids':['row-revenue','fact-cost']}], 'what_changed':[{'statement':'Revenue declined versus comparator.','supporting_fact_ids':['row-revenue']}], 'why_it_matters':[], 'financial_trajectory':[], 'enterprise_pressures':[], 'transformation_direction':[], 'management_execution_assessment':[], 'strategic_signals':[{'signal_id':'sig-1','statement':'Cost transformation is commercially material.','supporting_fact_ids':['fact-cost'],'confidence':0.8,'alternative_interpretation':'Routine efficiency wording','commercial_relevance':'productivity','source_lineage':['fact-cost']}], 'hypotheses':[{'hypothesis_id':'hyp-1','proposition':'BT may need automation to deliver cost commitments.','supporting_fact_ids':['fact-cost'],'contradictory_evidence':[],'Unknowns':['investment detail'],'confidence':0.6,'validation_questions':['What initiatives are funded?'],'likely_executive_relevance':['COO'],'what_would_strengthen_it':'named programme benefits','what_would_weaken_it':'commitment withdrawn'}], 'commercial_themes':[{'theme':'productivity and automation','why_it_is_plausible':'cost commitment','supporting_fact_ids':['fact-cost'],'likely_sponsor':'COO','urgency':'medium','confidence':0.6,'Unknowns':[],'what_not_to_claim_yet':'specific opportunity'}], 'likely_executive_stakeholders':['Group Chief Executive'], 'contradictions':['Adjusted and statutory measures differ'], 'unknowns':['Detailed programme owner'], 'questions_to_investigate':['Which programmes deliver savings?'], 'what_not_to_claim':['Do not claim canonical acceptance'], 'recommended_learning_actions':['Validate programme ownership']}

class MockProvider:
    def __init__(self): self.calls=[]
    def extraction(self, acquired, correlation_id):
        self.calls.append(('stage1', acquired.path.read_bytes()))
        from cios.applications.flora.financial_intelligence.rapid_ai_twin import ProviderStageResult
        return ProviderStageResult(extraction_payload(), {'stage':'stage_1_report_extraction','status':'completed','model':'mock','usage':{'input_tokens':10,'output_tokens':20},'estimated_or_actual_cost_usd':0.01})
    def synthesis(self, extraction, citation_index, correlation_id):
        self.calls.append(('stage2', extraction, citation_index))
        from cios.applications.flora.financial_intelligence.rapid_ai_twin import ProviderStageResult
        return ProviderStageResult(synthesis_payload(), {'stage':'stage_2_twin_synthesis','status':'completed','model':'mock','usage':{'input_tokens':5,'output_tokens':15},'estimated_or_actual_cost_usd':0.02})

class Stage2Fail(MockProvider):
    def synthesis(self, extraction, citation_index, correlation_id):
        from cios.applications.flora.financial_intelligence.rapid_ai_twin import ProviderStageResult
        return ProviderStageResult(None, {'stage':'stage_2_twin_synthesis','status':'failed','usage':{}}, 'boom')


def test_rapid_ai_snapshot_contract_cache_csv_and_partial(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_ROOT', str(tmp_path/'data'))
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p)); provider=MockProvider()
    snap=create_rapid_ai_twin_snapshot(acquired, provider_boundary=provider, correlation_id='r1', force_reprocess=True)
    assert provider.calls[0][0]=='stage1' and provider.calls[0][1].startswith(b'%PDF')
    assert provider.calls[1][0]=='stage2' and 'financial_tables' in provider.calls[1][1] and isinstance(provider.calls[1][2], list)
    rows=snap['financial_tables'][0]['rows']
    assert [r['row_id'] for r in rows] == ['row-revenue','row-adjusted-ebitda','row-consumer','row-guidance']
    assert rows[0]['current_period_display_value'] != rows[0]['comparator_display_value']
    assert {r['accounting_basis'] for r in rows} >= {'statutory','adjusted'}
    assert any(r['scope']=='Consumer segment' for r in rows)
    assert any(r['financial_measurement_state']=='guidance' for r in rows)
    assert all(r['source_page'] for r in rows)
    assert snap['candidate_facts'][0]['source_page'] == 20
    assert snap['commitments'][0]['source_page'] == 21
    assert snap['programmes'][0]['source_citation']['page'] == 23
    assert snap['signals'][0]['supporting_fact_ids'] == ['fact-cost']
    assert snap['hypotheses'][0]['Unknowns'] and snap['hypotheses'][0]['validation_questions']
    assert 'row-invalid' not in [r['row_id'] for r in rows]
    assert 'Revenue' in build_csv(snap)
    provider2=MockProvider(); snap2=create_rapid_ai_twin_snapshot(acquired, provider_boundary=provider2, correlation_id='r2')
    assert snap2['cache_state']=='hit' and provider2.calls == []
    partial=create_rapid_ai_twin_snapshot(acquired, provider_boundary=Stage2Fail(), correlation_id='r3', force_reprocess=True)
    assert partial['status']=='partial' and partial['financial_tables']
    assert partial['user_status'] == 'Partial AI Twin Snapshot'


def test_orchestration_and_bt_twin_rendering_without_canonical_writes(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_ROOT', str(tmp_path/'data'))
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p))
    before=review._trusted_state_snapshot('bt-group-plc')
    def acq(*a, **k):
        class CM:
            def __enter__(self): return acquired
            def __exit__(self, *exc): return False
        return CM()
    run=review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-ai', acquisition_boundary=acq, extraction_boundary=lambda a: create_rapid_ai_twin_snapshot(a, provider_boundary=MockProvider(), force_reprocess=True))
    after=review._trusted_state_snapshot('bt-group-plc')
    assert before == after
    assert run['rapid_intelligence']['rapid_ai_twin_snapshot']['canonical_state']['canonical_writes'] == 0
    html=digital_twins.bt_twin_page('fi-ai')
    assert 'Rapid AI Twin Snapshot' in html and 'Trusted Twin knowledge' in html
    assert 'AI-built snapshot — verification pending' in html
    assert 'Download financial tables as CSV' in html and 'View source' in html
    assert 'Cost transformation is commercially material' in html
    assert 'BT may need automation' in html
    html_again=digital_twins.bt_twin_page('fi-ai')
    assert html_again == html


def test_partial_snapshot_status_is_honest_in_digital_twin(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_ROOT', str(tmp_path/'data'))
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p))
    def acq(*a, **k):
        class CM:
            def __enter__(self): return acquired
            def __exit__(self, *exc): return False
        return CM()
    run=review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-ai-partial', acquisition_boundary=acq, extraction_boundary=lambda a: create_rapid_ai_twin_snapshot(a, provider_boundary=Stage2Fail(), force_reprocess=True))
    assert run['rapid_intelligence']['rapid_ai_twin_snapshot']['user_status'] == 'Partial AI Twin Snapshot'
    html=digital_twins.bt_twin_page('fi-ai-partial')
    assert 'Partial AI Twin Snapshot' in html
    assert 'AI-built snapshot — verification pending' not in html
