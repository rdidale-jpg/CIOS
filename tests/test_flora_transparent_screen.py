from __future__ import annotations

import json
from html.parser import HTMLParser

from cios.applications.flora.flora_transparent import REQUIRED_STAGES, page, start_bt_digital_twin, flora_payload
from cios.applications.flora.web.app import FloraWebHandler

class FormParser(HTMLParser):
    def __init__(self): super().__init__(); self.forms=[]
    def handle_starttag(self, tag, attrs):
        if tag=='form': self.forms.append(dict(attrs))

def test_flora_one_screen_header_and_button(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    html=page(); p=FormParser(); p.feed(html)
    assert 'Product' in html and 'Flora' in html
    assert 'Deployed revision' in html and 'Application version' in html
    assert [f for f in p.forms if f.get('method')=='post' and f.get('action')=='/flora/bt-digital-twin']
    assert 'Executive Brief' not in html and 'Download support report' not in html

class NoStartThread:
    created=[]
    def __init__(self, target=None, args=(), kwargs=None, daemon=None): self.target=target; self.args=args; NoStartThread.created.append(self)
    def start(self): return None

def test_one_click_creates_one_ai_rapid_twin_run_and_initial_events(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    import cios.applications.flora.document_review as review
    monkeypatch.setattr(review.threading,'Thread',NoStartThread); NoStartThread.created=[]
    run=start_bt_digital_twin()
    files=list((tmp_path/'ai_financial_reports'/'runs').glob('fi-*.json'))
    assert len(files)==1 and len(NoStartThread.created)==1
    persisted=json.loads(files[0].read_text())
    assert persisted['execution_mode']=='dual_speed_financial_intelligence'
    assert 'structured_standard_financials' not in persisted['execution_mode']
    stages=[e['stage'] for e in persisted['flora_event_journal']]
    assert stages[:3]==['button_received','run_created','strategy_selected']

def test_completed_run_synthesizes_required_transcript_and_twin(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    d=tmp_path/'ai_financial_reports'/'runs'; d.mkdir(parents=True)
    run={'run_id':'fi-done','created_at':'2026-07-07T00:00:00+00:00','deployed_revision':'rev','status':'completed','terminal':True,'workflow':'financial_intelligence','enterprise_id':'bt-group-plc','reporting_period':'FY26','execution_mode':'dual_speed_financial_intelligence','rapid_intelligence':{'status':'ready','source_receipt':{'document_title':'BT Annual Report 2026','sha256':'abc','byte_count':123},'provider_receipt':{'response_received':True,'provider_response_id':'resp_1','provider_status':'completed','model':'gpt-test','input_tokens':10,'output_tokens':20,'response_text_length':100,'structured_payload_present':True},'snapshot_truthfulness':{'financial_row_count':1,'analysis_section_count':1,'rendered_section_count':2},'financial_tables':[{'rows':[{'reported_label':'Revenue','current_period_display_value':'£20bn','comparator_display_value':'£19bn','unit':'GBP','scale':'bn','accounting_basis':'reported','source_page':10,'supporting_excerpt':'Revenue was £20bn.'}]}],'report_analysis':{'executive_summary':['BT summary']},'signals':[{'summary':'Signal','source_page':11,'supporting_excerpt':'Signal excerpt'}],'hypotheses':[{'summary':'Hypothesis'}],'unknowns':['Unknown']}}
    (d/'fi-done.json').write_text(json.dumps(run))
    payload=flora_payload(); stages={e['stage'] for e in payload['events']}
    assert all(stage in stages for stage,_,_ in REQUIRED_STAGES)
    html=page()
    assert 'BT Digital Twin created — verification pending' in html
    assert 'Instructions sent to AI' in html and 'Enterprise identity: BT Group plc' in html
    assert 'Financial tables' in html and 'Revenue' in html
    assert 'Executive view' in html or 'Twin summary' in html
    assert 'Trusted Twin changed: no' in html and 'Canonical writes: 0' in html
