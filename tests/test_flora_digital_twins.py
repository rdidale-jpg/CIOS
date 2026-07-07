import json
from contextlib import contextmanager

from cios.applications.flora import document_review as review
from cios.applications.flora.digital_twins import bt_twin_page, digital_twins_landing_page, search_bt_twin
from cios.applications.flora.financial_intelligence.rapid_candidates import extract_rapid_financial_candidates
from cios.applications.flora.financial_intelligence.rapid_sources import AcquiredRapidSource, RapidSourceAcquisitionError
from cios.applications.flora.memory.repository import EvidenceRepository, EnterpriseModelRepository, ObservationRepository
from cios.applications.flora.workspace.views import landing_page
from tests.test_rapid_financial_candidate_extraction import BASE, pdf, receipt


def _snap():
    return {
        'evidence': len(EvidenceRepository().list()),
        'observations': len(ObservationRepository().list()),
        'attributes': dict(EnterpriseModelRepository().get('bt-group-plc').attributes),
    }


@contextmanager
def acquired(tmp_path, text=BASE):
    p = pdf(tmp_path, text)
    yield AcquiredRapidSource(p, receipt(p, external_source_call_count=0))
    p.unlink(missing_ok=True)


def test_digital_twins_landing_navigation_and_empty_state(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    assert 'Digital Twins' in landing_page()
    html = digital_twins_landing_page()
    assert 'BT Group' in html
    assert 'Commercial Digital Twin' in html
    assert 'No recent source-backed research.' in html
    assert '/digital-twins/bt-group-plc' in html
    assert 'Vodafone' not in html and 'National Grid' not in html


def test_bt_twin_keeps_trusted_and_candidate_state_separate(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    @contextmanager
    def acq(e, r):
        with acquired(tmp_path) as a:
            yield a
    before = _snap()
    review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-dt-ok', acquisition_boundary=acq, extraction_boundary=extract_rapid_financial_candidates)
    after = _snap()
    html = bt_twin_page()
    trusted = html.split('<h2>What the Twin knows</h2>', 1)[1].split('<h2>New financial findings</h2>', 1)[0]
    findings = html.split('<h2>New financial findings</h2>', 1)[1]
    assert before == after
    assert 'No accepted FY26 financial facts yet' in trusted
    assert 'Revenue' not in trusted
    assert 'Revenue' in findings
    assert 'Operating Profit' in findings
    assert 'Profit Before Tax' in findings
    assert 'Verification pending' in findings
    assert 'This finding has not yet been added to the trusted Commercial Digital Twin.' in findings
    assert 'FY26' in findings and 'GBP' in findings and 'millions' in findings
    assert 'Official document title: FY26 results' in findings
    assert 'Source authority: BT Group plc' in findings
    assert 'Page 1' in findings and 'Group statutory results' in findings
    assert 'Supporting excerpt:' in findings
    assert 'Open official source' in findings and 'target=\'_blank\'' in findings and 'rel=\'noopener noreferrer\'' in findings
    assert 'source_sha256' not in html and str(tmp_path) not in html


def test_search_action_invokes_dual_speed_once_and_default_unchanged(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    calls = []
    def fake_coord(**kwargs):
        calls.append(kwargs)
        return {'run_id': 'fi-new', 'execution_mode': 'dual_speed_financial_intelligence'}
    monkeypatch.setattr('cios.applications.flora.digital_twins.coordinate_dual_speed_financial_intelligence_run', fake_coord)
    assert 'Search for new information' in bt_twin_page()
    run = search_bt_twin()
    assert run['execution_mode'] == 'dual_speed_financial_intelligence'
    assert calls == [{'enterprise_id': 'bt-group-plc', 'reporting_period': 'FY26'}]
    default_run = review.refresh_financial_intelligence(run_id='fi-default')
    assert default_run['execution_mode'] == 'dual_speed_financial_intelligence'


def test_partial_and_unavailable_states_are_honest(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    partial = BASE.replace('Operating profit | 2,897 | 2,700 | statutory | Group\n', '')
    @contextmanager
    def acq(e, r):
        with acquired(tmp_path, partial) as a:
            yield a
    review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-partial', acquisition_boundary=acq, extraction_boundary=extract_rapid_financial_candidates)
    html = bt_twin_page()
    assert 'Partial source-backed financial findings' in html
    assert 'Flora found some usable information' in html
    assert 'Unresolved financial figures: Operating Profit' in html
    assert '>0<' not in html
    p = pdf(tmp_path); rec = receipt(p, validation_result='rejected', failure_code='rapid_source_period_mismatch', failure_stage='validation', safe_failure_message='Period mismatch', external_source_call_count=0)
    @contextmanager
    def fail_acq(e, r):
        raise RapidSourceAcquisitionError('rapid_source_period_mismatch', 'validation', 'Period mismatch', rec)
        yield
    review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-zz-unavailable', acquisition_boundary=fail_acq, extraction_boundary=lambda a: None)
    html = bt_twin_page()
    assert 'No trustworthy new financial information found' in html
    assert 'No fixture or seeded information was substituted' in html
    assert 'trusted Commercial Digital Twin was unchanged' in html
    assert '<article class=\'card\'><h3>' not in html


def test_research_history_uses_standard_runs(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    for i in range(6):
        run = {'run_id': f'fi-h{i}', 'created_at': f'2026-07-06T00:0{i}:00+00:00', 'workflow': 'financial_intelligence', 'enterprise_id': 'bt-group-plc', 'reporting_period': 'FY26', 'rapid_intelligence': {'candidates': [{}] * (3 if i % 2 else 0)}}
        d = tmp_path / 'ai_financial_reports' / 'runs'; d.mkdir(parents=True, exist_ok=True)
        (d / f"fi-h{i}.json").write_text(json.dumps(run))
    html = bt_twin_page()
    assert html.count('Open result') == 5
    assert '/financial-intelligence/fi-h' in html

def test_source_retrieved_zero_candidate_twin_history_is_not_unavailable(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    run = {'run_id':'fi-zero-history','created_at':'2026-07-06T00:00:00+00:00','workflow':'financial_intelligence','enterprise_id':'bt-group-plc','reporting_period':'FY26','rapid_intelligence': {'status':'unavailable','evidence_status':'official_source_retrieved','source_receipt': {'validation_result':'accepted'}, 'candidates': []}}
    d = tmp_path / 'ai_financial_reports' / 'runs'; d.mkdir(parents=True, exist_ok=True)
    (d / 'fi-zero-history.json').write_text(json.dumps(run))
    html = bt_twin_page()
    assert 'Official report retrieved; no safe findings identified' in html
    assert 'No findings to verify' in html
    assert 'Official source unavailable' not in html
