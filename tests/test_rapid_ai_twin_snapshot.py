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
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p)); provider=MockProvider()
    snap=create_rapid_ai_twin_snapshot(acquired, provider_boundary=provider, correlation_id='r1', force_reprocess=True)
    assert provider.calls[0][0]=='stage1' and provider.calls[0][1].startswith(b'%PDF')
    assert len(provider.calls)==1
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
    assert 'row-invalid' not in [r['row_id'] for r in rows]
    assert 'Revenue' in build_csv(snap)
    provider2=MockProvider(); snap2=create_rapid_ai_twin_snapshot(acquired, provider_boundary=provider2, correlation_id='r2')
    assert snap2['cache_state']=='hit' and provider2.calls == []
    partial=create_rapid_ai_twin_snapshot(acquired, provider_boundary=Stage2Fail(), correlation_id='r3', force_reprocess=True)
    assert partial['status']=='partial' and partial['financial_tables']
    assert partial['user_status'] == 'Partial AI Twin Snapshot — verification pending'


def test_orchestration_and_bt_twin_rendering_without_canonical_writes(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
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
    assert 'Partial AI Twin Snapshot' in html
    assert 'Download financial tables as CSV' in html and 'View source details' in html
    html_again=digital_twins.bt_twin_page('fi-ai')
    assert html_again == html


def test_partial_snapshot_status_is_honest_in_digital_twin(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p))
    def acq(*a, **k):
        class CM:
            def __enter__(self): return acquired
            def __exit__(self, *exc): return False
        return CM()
    run=review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-ai-partial', acquisition_boundary=acq, extraction_boundary=lambda a: create_rapid_ai_twin_snapshot(a, provider_boundary=Stage2Fail(), force_reprocess=True))
    assert run['rapid_intelligence']['rapid_ai_twin_snapshot']['user_status'] == 'Partial AI Twin Snapshot — verification pending'
    html=digital_twins.bt_twin_page('fi-ai-partial')
    assert 'Partial AI Twin Snapshot' in html
    assert 'AI-built snapshot — verification pending' not in html


def test_provider_preflight_failure_renders_compact_unavailable_state(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p))
    def acq(*a, **k):
        class CM:
            def __enter__(self): return acquired
            def __exit__(self, *exc): return False
        return CM()
    run=review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-ai-preflight', acquisition_boundary=acq)
    snapshot=run['rapid_intelligence']['rapid_ai_twin_snapshot']
    assert snapshot['status'] == 'unavailable'
    assert snapshot['provider_preflight']['status'] == 'failed'
    assert snapshot['provider_preflight']['failed_checks'] == ['credential_present']
    assert snapshot['model_and_cost_record']['ai_call_count'] == 0
    html=digital_twins.bt_twin_page('fi-ai-preflight')
    assert 'AI-built snapshot unavailable' in html
    assert 'Provider boundary unavailable: credential_present' in html
    assert 'No source-backed items available yet' not in html
    assert 'Rapid AI Twin Snapshot available' not in html


def test_bt_click_render_prefers_requested_ai_run_and_ignores_structured_standard(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p)); provider=MockProvider()
    def acq(*a, **k):
        class CM:
            def __enter__(self): return acquired
            def __exit__(self, *exc): return False
        return CM()
    before=review._trusted_state_snapshot('bt-group-plc')
    run=review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-click-ai', acquisition_boundary=acq, extraction_boundary=lambda a: create_rapid_ai_twin_snapshot(a, provider_boundary=provider, force_reprocess=True))
    runs_dir=review._run_dir()
    structured={
        'run_id':'fi-later-structured',
        'created_at':'2026-07-07T00:00:00+00:00',
        'workflow':'financial_intelligence',
        'enterprise_id':'bt-group-plc',
        'execution_mode':'structured_standard_financials',
        'extraction_mode':'structured_standard_financials',
        'rapid_intelligence':{},
    }
    (runs_dir/'fi-later-structured.json').write_text(__import__('json').dumps(structured))
    assert (runs_dir/'fi-click-ai.json').exists()
    assert run['execution_mode'] == 'dual_speed_financial_intelligence'
    assert run['rapid_intelligence']['rapid_ai_twin_snapshot']['status'] == 'partial'
    assert [c[0] for c in provider.calls] == ['stage1']
    html=digital_twins.bt_twin_page('fi-click-ai')
    assert 'Partial AI Twin Snapshot' in html
    assert 'Group results' in html and 'Revenue' in html
    assert 'Management commitment' in html and 'Reduce costs' in html
    assert 'Programme ownership unclear' in html or 'Detailed programme owner' in html
    assert 'View source' in html and 'Page 10' in html
    assert 'No financial tables are available in the rapid snapshot' not in html
    html_again=digital_twins.bt_twin_page('fi-click-ai')
    assert html_again == html
    assert len(provider.calls) == 1
    assert before == review._trusted_state_snapshot('bt-group-plc')


def test_missing_runtime_credential_blocks_run_before_source_retrieval(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    called = {'source': 0}
    def acq(*a, **k):
        called['source'] += 1
        raise AssertionError('source retrieval must not run')
    # Default production boundary is what is gated before run creation.
    run = review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-no-key')
    assert run['run_created'] is False
    assert run['user_message'] == 'AI research is not configured for this deployment.'
    assert run['provider_readiness']['failed_checks'] == ['credential_present']
    assert not (review._run_dir() / 'fi-no-key.json').exists()
    assert called['source'] == 0


def test_bt_product_hides_support_report_links_when_rendering_ordinary_twin(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    run = {'run_id':'fi-support-hidden','created_at':'2026-07-06T00:00:00+00:00','workflow':'financial_intelligence','enterprise_id':'bt-group-plc','reporting_period':'FY26','execution_mode':'dual_speed_financial_intelligence','rapid_intelligence': {'status':'unavailable','evidence_status':'official_source_unavailable','source_receipt':{}, 'candidates': []}, 'support_reference': 'FI-support-hidden'}
    review._write_json(review._run_dir() / 'fi-support-hidden.json', run)
    html = digital_twins.bt_twin_page('fi-support-hidden')
    assert 'Support reference: FI-support-hidden' in html
    assert 'Download support report' not in html
    assert '/support-report' not in html

class OneCallProvider:
    def __init__(self, raw=None, payload=None, status='completed', finish='stop'):
        self.calls=[]; self.raw=raw; self.payload=payload; self.status=status; self.finish=finish
    def analyse(self, acquired, correlation_id):
        self.calls.append(('one_call', acquired.path.read_bytes()))
        from cios.applications.flora.financial_intelligence.rapid_ai_twin import ProviderStageResult
        call={'stage':'one_call_report_extraction_and_synthesis','status':self.status,'model':'mock','provider_response_id':'resp_123','finish_reason':self.finish,'usage':{'input_tokens':100,'output_tokens':200},'estimated_or_actual_cost_usd':0.03}
        return ProviderStageResult(self.payload, call, None if self.status=='completed' else 'boom', self.raw)

def one_call_payload(rows=12):
    base=extraction_payload();
    rs=[]
    for i in range(rows):
        r=dict(base['financial_tables'][0]['rows'][i % 4]); r['row_id']=f'row-{i}'; r['reported_label']=f'Metric {i}'; r['source_page']=10; rs.append(r)
    base['financial_tables'][0]['rows']=rs
    return base | {'executive_summary':['BT changed commercially.'], 'key_changes':['Revenue moved.'], 'signals':[{'signal_id':'s1','statement':'Signal one','supporting_fact_ids':['row-0']},{'signal_id':'s2','statement':'Signal two','supporting_fact_ids':['row-1']}], 'hypotheses':[{'hypothesis_id':'h1','proposition':'Automation may matter','supporting_fact_ids':['row-0'],'contradictory_evidence':[],'Unknowns':['detail'],'validation_questions':['What is funded?'],'confidence':0.7}], 'commercial_themes':['AI and productivity'], 'unknowns_and_contradictions':['Owner unclear'], 'questions_and_next_actions':['Validate programme owner']}

def test_one_call_valid_markdown_prose_raw_persist_cache_and_render(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p))
    raw='Here is the JSON:\n```json\n' + __import__('json').dumps(one_call_payload()) + '\n```\nThanks'
    provider=OneCallProvider(raw=raw)
    snap=create_rapid_ai_twin_snapshot(acquired, provider_boundary=provider, correlation_id='one', force_reprocess=True)
    assert snap['status']=='ready'
    assert len(provider.calls)==1
    assert snap['provider_receipt']['provider_response_id']=='resp_123'
    assert snap['provider_receipt']['finish_reason']=='stop'
    assert Path(snap['provider_receipt']['raw_response_path']).exists()
    assert len(snap['financial_tables'][0]['rows']) >= 10
    provider2=OneCallProvider(payload=one_call_payload())
    snap2=create_rapid_ai_twin_snapshot(acquired, provider_boundary=provider2, correlation_id='two')
    assert snap2['cache_state']=='hit' and provider2.calls==[]

def test_unstructured_and_empty_provider_states(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p))
    unstructured=create_rapid_ai_twin_snapshot(acquired, provider_boundary=OneCallProvider(raw='BT report says revenue pressure on page 10.'), force_reprocess=True)
    assert unstructured['user_status']=='Partial AI Twin Snapshot — report available'
    assert unstructured['unstructured_ai_report']
    empty=create_rapid_ai_twin_snapshot(acquired, provider_boundary=OneCallProvider(raw='', payload=None), force_reprocess=True)
    assert empty['status']=='unavailable'

def test_provider_envelope_json_and_truncation_preserve_largest_subset(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p))
    payload=one_call_payload(rows=3)
    payload['financial_tables'][0]['rows'].append({'row_id':'bad-page','reported_label':'Bad page','source_page':999,'supporting_excerpt':'bad'})
    raw={'id':'resp_nested','status':'incomplete','output':[{'content':[{'text':'Leading prose before JSON\\n' + __import__('json').dumps(payload)}]}]}
    provider=OneCallProvider(raw=raw, finish='max_output_tokens')
    snap=create_rapid_ai_twin_snapshot(acquired, provider_boundary=provider, correlation_id='truncated', force_reprocess=True)
    assert snap['status']=='partial'
    assert snap['validation']['truncated'] is True
    assert len(snap['financial_tables'][0]['rows']) == 3
    assert 'bad-page' not in [r['row_id'] for r in snap['financial_tables'][0]['rows']]
    assert snap['user_status'] == 'Partial AI Twin Snapshot — verification pending'
    assert snap['provider_receipt']['raw_response_length'] > 0

def test_empty_sections_hidden_and_non_empty_never_unavailable(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p))
    payload=one_call_payload(rows=2)
    payload.pop('management_commitments', None)
    payload.pop('transformation_programmes', None)
    snap=create_rapid_ai_twin_snapshot(acquired, provider_boundary=OneCallProvider(payload=payload), correlation_id='hidden', force_reprocess=True)
    assert snap['status'] != 'unavailable'
    run={'run_id':'hidden','rapid_intelligence':{'rapid_ai_twin_snapshot':snap}}
    html=digital_twins._rapid_snapshot_section(run)
    assert 'Financial tables' in html
    assert 'Management commitments' not in html
    assert 'Transformation programmes' not in html

def test_bt_one_call_real_provider_payload_uses_json_mode_and_pdf(monkeypatch, tmp_path):
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p))
    captured=[]
    class Count:
        def count(self, **kwargs):
            captured.append(('count', kwargs))
            return {'input_tokens': 123}
    class Responses:
        input_tokens=Count()
        def create(self, **kwargs):
            captured.append(('create', kwargs))
            class Usage:
                def model_dump(self): return {'input_tokens':123,'output_tokens':45}
            class Resp:
                id='resp_json_mode'; status='completed'; usage=Usage(); output_text=__import__('json').dumps(one_call_payload(rows=1))
                def model_dump(self, mode='json'):
                    return {'id':self.id,'status':self.status,'usage':self.usage.model_dump(),'output_text':self.output_text}
            return Resp()
    class Client:
        def __init__(self, **kwargs): self.responses=Responses()
    monkeypatch.setitem(__import__('sys').modules, 'openai', type('OpenAIModule', (), {'OpenAI': Client}))
    from cios.applications.flora.financial_intelligence.rapid_ai_twin import RapidAITwinProvider
    from cios.applications.flora.financial_intelligence.openai_provider import OpenAIDirectPDFProvider
    provider=RapidAITwinProvider(OpenAIDirectPDFProvider(model='gpt-test'))
    snap=create_rapid_ai_twin_snapshot(acquired, provider_boundary=provider, correlation_id='json-mode', force_reprocess=True)
    creates=[x for x in captured if x[0]=='create']
    assert len(creates)==1
    create_payload=creates[0][1]
    assert create_payload['text']['format'] == {'type':'json_object'}
    assert 'foundation_fact_set' not in __import__('json').dumps(create_payload)
    assert 'json_schema' not in __import__('json').dumps(create_payload['text'])
    content=create_payload['input'][0]['content']
    assert content[0]['type']=='input_file' and content[0]['file_url']=='https://www.bt.com/report.pdf'
    assert 'Return exactly one JSON object' in content[1]['text']
    assert snap['provider_receipt']['provider_response_id']=='resp_json_mode'
    assert snap['model_and_cost_record']['input_tokens'] == 123


def test_provider_request_rejection_not_cached_and_safe_code(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    p=_pdf(tmp_path); acquired=AcquiredRapidSource(p,_receipt(p))
    class RejectingProvider:
        def __init__(self): self.calls=0
        def analyse(self, acquired, correlation_id):
            self.calls+=1
            from cios.applications.flora.financial_intelligence.rapid_ai_twin import ProviderStageResult
            call={'stage':'one_call_report_extraction_and_synthesis','status':'provider_request_invalid','http_status':400,'provider_error_code':'invalid_json_schema','model':'mock','usage':{},'elapsed_ms':37}
            return ProviderStageResult(None, call, 'invalid_json_schema', None)
    provider=RejectingProvider()
    snap=create_rapid_ai_twin_snapshot(acquired, provider_boundary=provider, correlation_id='reject', force_reprocess=True)
    assert snap['status']=='unavailable'
    assert snap['validation']['safe_failure_code']=='provider_rejected_request'
    assert 'output format was invalid' in snap['user_explanation']
    assert snap['snapshot_truthfulness']['snapshot_record_persisted'] is False
    provider2=RejectingProvider()
    create_rapid_ai_twin_snapshot(acquired, provider_boundary=provider2, correlation_id='reject2')
    assert provider2.calls == 1
