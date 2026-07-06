import json
from contextlib import contextmanager

import pytest

from cios.applications.flora import document_review as review
from cios.applications.flora.financial_intelligence.rapid_candidates import extract_rapid_financial_candidates
from cios.applications.flora.financial_intelligence.rapid_sources import AcquiredRapidSource, RapidSourceAcquisitionError
from cios.applications.flora.memory.repository import EvidenceRepository, EnterpriseModelRepository, ObservationRepository
from tests.test_rapid_financial_candidate_extraction import BASE, pdf, receipt


def _repo_snapshot():
    model = EnterpriseModelRepository().get('bt-group-plc')
    return {
        'evidence': len(EvidenceRepository().list()),
        'observations': len(ObservationRepository().list()),
        'attributes': dict(model.attributes),
    }


def test_dual_speed_mode_persists_combined_standard_run_and_preserves_rapid_result(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    before = _repo_snapshot()
    @contextmanager
    def acq(e, r):
        with acquired(tmp_path) as a:
            yield a
    run = review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-dual-speed', acquisition_boundary=acq, extraction_boundary=extract_rapid_financial_candidates)
    after = _repo_snapshot()
    assert (tmp_path / 'ai_financial_reports' / 'runs' / 'fi-dual-speed.json').exists()
    assert run['execution_mode'] == 'dual_speed_financial_intelligence'
    assert run['overall_status'] == 'completed'
    assert run['completion_class'] == 'unverified'
    assert run['rapid_intelligence']['status'] == 'ready'
    assert run['rapid_intelligence']['evidence_status'] == 'official_source_retrieved'
    assert run['rapid_intelligence']['candidate_count'] == 3
    assert run['verification']['status'] == 'unavailable'
    assert run['canonical_update']['status'] == 'not_applicable'
    assert run['canonical_update']['enterprise_model_updated'] is False
    assert run['cost_summary']['ai_call_count'] == 0
    assert run['cost_summary']['estimated_provider_cost_usd'] == 0
    assert before == after


def test_dual_speed_progress_and_result_render_from_standard_run_only(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    @contextmanager
    def acq(e, r):
        with acquired(tmp_path) as a:
            yield a
    review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-dual-render', acquisition_boundary=acq, extraction_boundary=extract_rapid_financial_candidates)
    status = review.financial_intelligence_progress_status('fi-dual-render')
    html, code = review.financial_intelligence_run_response('fi-dual-render')
    assert status['terminal'] is True
    assert status['final_result_url'] == '/financial-intelligence/fi-dual-render'
    assert code == 200
    assert 'Official-source candidate facts' in html
    assert 'Verification summary' in html
    assert 'Status: Unavailable' in html
    assert 'Canonical update summary' in html
    assert 'Status: No canonical update required' in html
    assert 'These figures were extracted from an approved official document' in html

def test_dual_speed_fixture_is_not_default(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    created = {}

    def fake_background(enterprise_id, run_id, extraction_mode='structured_standard_financials'):
        created['mode'] = extraction_mode

    monkeypatch.setattr(review.threading, 'Thread', lambda target, args, daemon: type('T', (), {'start': lambda self: target(*args)})())
    monkeypatch.setattr(review, '_background_refresh', fake_background)
    run = review.create_financial_intelligence_progress_run('bt-group-plc')
    assert run['extraction_mode'] == 'structured_standard_financials'
    assert created['mode'] == 'structured_standard_financials'


def test_unsupported_mode_still_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    with pytest.raises(ValueError):
        review.refresh_financial_intelligence(run_id='fi-bad-mode', extraction_mode='unsupported_mode')
def _snap():
    from cios.applications.flora.memory.repository import EvidenceRepository, EnterpriseModelRepository, ObservationRepository
    model = EnterpriseModelRepository().get('bt-group-plc')
    return {'e': len(EvidenceRepository().list()), 'o': len(ObservationRepository().list()), 'a': dict(model.attributes)}

@contextmanager
def acquired(tmp_path, text=BASE):
    p = pdf(tmp_path, text)
    yield AcquiredRapidSource(p, receipt(p, external_source_call_count=0))
    p.unlink(missing_ok=True)

def test_slice_2c_success_persists_source_candidates_and_renders(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    calls = {'acq':0, 'ext':0}
    @contextmanager
    def acq(e, r):
        calls['acq'] += 1
        with acquired(tmp_path) as a:
            yield a
    def ext(a):
        calls['ext'] += 1
        return extract_rapid_financial_candidates(a)
    before = _snap()
    run = review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-2c-ok', acquisition_boundary=acq, extraction_boundary=ext)
    after = _snap()
    lane = run['rapid_intelligence']
    saved = json.loads((tmp_path/'ai_financial_reports'/'runs'/'fi-2c-ok.json').read_text())
    assert calls == {'acq':1, 'ext':1}
    assert lane['status'] == 'ready'
    assert lane['evidence_status'] == 'official_source_retrieved'
    assert lane['extraction_status'] == 'completed'
    assert lane['candidate_count'] == 3
    assert lane['ai_call_count'] == lane['canonical_write_count'] == 0
    assert all(c['verification_status'] == 'candidate_unverified' for c in lane['candidates'])
    assert all(json.loads(c['source_locator'])['source_sha256'] == lane['source_receipt']['sha256'] for c in lane['candidates'])
    assert str(tmp_path) not in json.dumps(saved)
    assert '%PDF' not in json.dumps(saved)
    assert lane['source_temporary_file_removed'] is True
    assert before == after
    html, code = review.financial_intelligence_run_response('fi-2c-ok')
    assert code == 200
    assert 'Official-source candidate facts' in html
    assert 'These figures were extracted from an approved official document' in html
    assert 'Page 1' in html
    assert 'Verification pending' in html
    assert 'Canonical memory has not been updated' in html

def test_slice_2c_acquisition_failure_does_not_extract(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    p = pdf(tmp_path); r = receipt(p, validation_result='rejected', failure_code='rapid_source_period_mismatch', failure_stage='validation', safe_failure_message='Rapid source reporting-period marker was not found.', external_source_call_count=0)
    @contextmanager
    def acq(e, rp):
        raise RapidSourceAcquisitionError('rapid_source_period_mismatch', 'validation', 'Rapid source reporting-period marker was not found.', r)
        yield
    def ext(a):
        pytest.fail('extraction must not run after acquisition failure')
    run = review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-2c-fail', acquisition_boundary=acq, extraction_boundary=ext)
    lane = run['rapid_intelligence']
    assert lane['status'] == 'unavailable'
    assert lane['candidate_count'] == 0
    assert lane['extraction_status'] == 'not_run'
    assert lane['exceptions'][0]['exception_type'] == 'rapid_source_period_mismatch'
    html, _ = review.financial_intelligence_run_response('fi-2c-fail')
    assert 'Official source unavailable' in html
    assert 'No financial findings were created. No fixture or seeded information was substituted' in html

def test_slice_2c_partial_and_zero_extraction_are_honest(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    partial = BASE.replace('Operating profit | 2,897 | 2,700 | statutory | Group\n','')
    @contextmanager
    def acq(e, r):
        with acquired(tmp_path, partial) as a: yield a
    run = review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-2c-partial', acquisition_boundary=acq, extraction_boundary=extract_rapid_financial_candidates)
    assert run['rapid_intelligence']['status'] == 'partial'
    assert run['rapid_intelligence']['candidate_count'] == 2
    assert run['rapid_intelligence']['exception_count'] >= 1
    zero = BASE.replace('GBP m\n','')
    @contextmanager
    def acq2(e, r):
        with acquired(tmp_path, zero) as a: yield a
    run2 = review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-2c-zero', acquisition_boundary=acq2, extraction_boundary=extract_rapid_financial_candidates)
    assert run2['rapid_intelligence']['status'] == 'unavailable'
    assert run2['rapid_intelligence']['candidate_count'] == 0
    assert run2['rapid_intelligence']['source_receipt']['validation_result'] == 'accepted'


def test_default_structured_mode_does_not_invoke_rapid_acquisition(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    monkeypatch.setattr(review, 'acquire_rapid_financial_source', lambda *a, **k: pytest.fail('default mode must not acquire rapid source'))
    run = review.refresh_financial_intelligence(run_id='fi-default', extraction_mode='structured_standard_financials')
    assert run['extraction_mode'] == 'structured_standard_financials'

def test_official_source_zero_candidate_result_uses_honest_wording(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    @contextmanager
    def acq(e, r):
        with acquired(tmp_path, BASE.replace('GBP m\n','')) as a:
            yield a
    review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-zero-candidates', acquisition_boundary=acq, extraction_boundary=extract_rapid_financial_candidates)
    html, code = review.financial_intelligence_run_response('fi-zero-candidates')
    assert code == 200
    assert 'Official BT report retrieved — no safe financial findings identified' in html
    assert 'Flora reached and validated the approved BT FY26 report, but it could not identify the required financial figures safely.' in html
    assert 'No fixture or seeded information was substituted, and the trusted Commercial Digital Twin was unchanged.' in html
    assert 'Revenue' in html and 'Operating profit' in html and 'Profit before tax' in html
    assert 'Official-source candidate facts' not in html
    assert 'These figures were extracted' not in html
    assert '<table><thead><tr><th>Metric</th>' not in html
    assert 'operating_profit' not in html
    assert 'official_source_retrieved' not in html
    assert 'no_trustworthy_evidence' not in html
    assert 'not_applicable' not in html
    assert 'candidate_unverified' not in html
    assert 'Support reference: FI-zero-candidates' in html
