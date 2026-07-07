from __future__ import annotations

from html.parser import HTMLParser

from cios.applications.flora import document_review as review
from cios.applications.flora import digital_twins


class FormParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.forms=[]; self._form=None; self._button=False
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='form':
            self._form={'method': attrs.get('method','get').lower(), 'action': attrs.get('action',''), 'labels': []}
        elif tag=='button' and self._form is not None:
            self._button=True
    def handle_data(self, data):
        if self._button and self._form is not None:
            t=data.strip()
            if t: self._form['labels'].append(t)
    def handle_endtag(self, tag):
        if tag=='button': self._button=False
        elif tag=='form' and self._form is not None:
            self.forms.append(self._form); self._form=None


def forms(html: str):
    p=FormParser(); p.feed(html); return p.forms


class NoStartThread:
    created=[]
    def __init__(self, target=None, args=(), kwargs=None, daemon=None):
        self.target=target; self.args=args; self.kwargs=kwargs or {}; self.daemon=daemon; NoStartThread.created.append(self)
    def start(self):
        return None


def test_rendered_bt_twin_search_form_uses_authoritative_ai_route(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    monkeypatch.setattr(digital_twins, 'provider_runtime_readiness', lambda: {'status':'passed'})
    rendered=forms(digital_twins.bt_twin_page())
    search=[f for f in rendered if 'Search for new information' in f['labels']]
    assert len(search)==1
    assert search[0]['method']=='post'
    assert search[0]['action']=='/digital-twins/bt-group-plc/search'
    assert 'structured_standard_financials' not in digital_twins.bt_twin_page()


def test_rendered_financial_intelligence_refresh_and_reprocess_use_same_ai_route(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    monkeypatch.setattr(review, '_bt_annual_report_source', lambda: {'source_id':'bt-annual-report-2026','source_name':'BT Group plc Annual Report 2026','url':'https://www.bt.com/report.pdf'})
    rendered=forms(review.financial_intelligence_page())
    starts=[f for f in rendered if f['labels'] and f['labels'][0] in {'Refresh Financial Intelligence','Reprocess Financial Intelligence'}]
    assert {f['labels'][0] for f in starts} == {'Refresh Financial Intelligence','Reprocess Financial Intelligence'}
    assert all(f['method']=='post' and f['action']=='/digital-twins/bt-group-plc/search' for f in starts)
    assert '/financial-intelligence/bt-group-plc/refresh' not in review.financial_intelligence_page()


def test_policy_forces_missing_and_structured_ordinary_bt_fy26_to_ai():
    missing=review.resolve_financial_intelligence_execution_policy(enterprise_id='bt-group-plc', reporting_period='FY26', product_surface='legacy_refresh', requested_execution_strategy='', ordinary_research=True)
    structured=review.resolve_financial_intelligence_execution_policy(enterprise_id='bt-group-plc', reporting_period='FY26', product_surface='financial_intelligence', requested_execution_strategy='structured_standard_financials', ordinary_research=True)
    assert missing['execution_strategy']=='dual_speed_financial_intelligence'
    assert structured['execution_strategy']=='dual_speed_financial_intelligence'


def test_only_restricted_verification_can_select_structured_mode():
    allowed=review.resolve_financial_intelligence_execution_policy(enterprise_id='bt-group-plc', reporting_period='FY26', product_surface='restricted_structured_verification', requested_execution_strategy='structured_standard_financials', ordinary_research=False, explicit_verification=True)
    rejected=review.resolve_financial_intelligence_execution_policy(enterprise_id='bt-group-plc', reporting_period='FY26', product_surface='restricted_structured_verification', requested_execution_strategy='structured_standard_financials', ordinary_research=True, explicit_verification=False)
    assert allowed['execution_strategy']=='structured_standard_financials'
    assert rejected['execution_strategy']=='dual_speed_financial_intelligence'


def test_one_rendered_bt_search_submission_creates_one_ai_run(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    monkeypatch.setattr(digital_twins, 'provider_runtime_readiness', lambda: {'status':'passed'})
    monkeypatch.setattr(review.threading, 'Thread', NoStartThread)
    monkeypatch.setattr(digital_twins, 'create_financial_intelligence_progress_run', review.create_financial_intelligence_progress_run)
    NoStartThread.created=[]
    rendered=forms(digital_twins.bt_twin_page())
    assert [f for f in rendered if f['action']=='/digital-twins/bt-group-plc/search']
    run=digital_twins.search_bt_twin()
    run_files=list((tmp_path/'ai_financial_reports'/'runs').glob('fi-*.json'))
    assert len(run_files)==1
    assert len(NoStartThread.created)==1
    persisted=review.load_run(run['run_id'])
    assert persisted['execution_mode']=='dual_speed_financial_intelligence'
    assert persisted['extraction_mode']=='dual_speed_financial_intelligence'
    assert 'structured_standard_financials' not in persisted.get('execution_mode','')


def test_read_only_bt_routes_do_not_create_runs(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    html=digital_twins.bt_twin_page()
    assert 'BT Group' in html
    assert not (tmp_path/'ai_financial_reports'/'runs').exists()
    # Existing-result navigation and support-report link rendering are read-only helpers.
    run={'run_id':'fi-ai','created_at':'2026-07-07T00:00:00+00:00','workflow':'financial_intelligence','enterprise_id':'bt-group-plc','reporting_period':'FY26','execution_mode':'dual_speed_financial_intelligence','rapid_intelligence':{'candidates':[{}]}}
    d=tmp_path/'ai_financial_reports'/'runs'; d.mkdir(parents=True, exist_ok=True); (d/'fi-ai.json').write_text(__import__('json').dumps(run))
    before=len(list(d.glob('fi-*.json')))
    assert 'View full research result' in digital_twins.bt_twin_page('fi-ai') or 'Open result' in digital_twins.bt_twin_page('fi-ai')
    assert len(list(d.glob('fi-*.json')))==before


def test_historical_structured_runs_are_labelled_and_not_reused(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    d=tmp_path/'ai_financial_reports'/'runs'; d.mkdir(parents=True, exist_ok=True)
    (d/'fi-old.json').write_text('{"run_id":"fi-old","created_at":"2026-07-06T00:00:00+00:00","workflow":"financial_intelligence","enterprise_id":"bt-group-plc","reporting_period":"FY26","extraction_mode":"structured_standard_financials","status":"structured_source_unavailable","claims":[],"applied_results":[],"exceptions":[]}')
    monkeypatch.setattr(review.threading, 'Thread', NoStartThread); NoStartThread.created=[]
    run=review.create_financial_intelligence_progress_run('bt-group-plc', extraction_mode='', product_surface='legacy_refresh', ordinary_research=True)
    assert run['run_id']!='fi-old'
    assert run['execution_mode']=='dual_speed_financial_intelligence'


def test_result_page_displays_revision_strategy_and_run_truth(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    run={'run_id':'fi-visible','created_at':'2026-07-07T00:00:00+00:00','workflow':'financial_intelligence','enterprise_id':'bt-group-plc','reporting_period':'FY26','execution_mode':'dual_speed_financial_intelligence','deployed_revision':'rev-test','overall_status':'completed','completion_class':'unverified','result_url':'/financial-intelligence/fi-visible','support_reference':'FI-visible','rapid_intelligence':{'evidence_status':'official_source_unavailable','exceptions':[{'failure_stage':'validation','user_message':'source unavailable'}]},'verification':{},'canonical_update':{},'cost_summary':{'ai_call_count':1,'cache_reused':False}}
    d=tmp_path/'ai_financial_reports'/'runs'; d.mkdir(parents=True, exist_ok=True); (d/'fi-visible.json').write_text(__import__('json').dumps(run))
    html,status=review.financial_intelligence_run_response('fi-visible', show_support_control=False)
    assert status==200
    assert 'Execution strategy: AI Rapid Twin' in html
    assert 'Deployed revision: rev-test' in html
    assert 'Run ID: fi-visible' in html
    assert 'Provider call attempted: yes' in html
