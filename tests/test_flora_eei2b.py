"""Annual statement integration on the real, bounded Nationwide source."""
import json
import shutil

import pytest

from cios.applications.flora import visual_streams
from cios.applications.flora.financial_intelligence import candidate_analytics as f
from cios.applications.flora.financial_intelligence import public_statements as p
from cios.applications.flora.research_intelligence import model, source_import as s

SELECTION = 'nationwide-annual'
PATH = 'enterprise-knowledge/banking/research-model/source-snapshots/EEI2B-Nationwide-AR26.json'


def test_verified_full_statements_and_lineage():
    lines = p.annual_details(SELECTION)
    assert len(lines) == 44
    assert {line.statement for line in lines} == {'income', 'balance', 'cash_flow'}
    assert {line.fiscal_year for line in lines} == {2025, 2026}
    index = {line.measurement_id: line for line in lines}
    assert str(index['nw-operating_cash-2026'].value.amount) == '3904'
    assert index['nw-operating_cash-2025'].original_display == '(7,914)'
    assert index['nw-cet1_ratio-2026'].original_display == '19.1%'
    _, result = p.balance_changes(lines, ('cash_central',))[0]
    assert result['value'] == '8928'
    assert result['inputs'] == [
        {'measurement_id': key, 'revision': index[key].revision}
        for key in ('nw-cash_central-2025', 'nw-cash_central-2026')
    ]
    prior, current = (index['nw-total_income-2025'], index['nw-total_income-2026'])
    assert (prior.period.end-prior.period.start).days == 360
    assert current.period.start.isoformat() == '2025-04-01'
    spec = f.Derivation(derivation_id='incompatible', formula='percent_change', comparison='duration_dates',
                        inputs=tuple(f.InputReference(measurement_id=line.measurement_id, revision=line.revision)
                                     for line in (prior, current)))
    with pytest.raises(ValueError):
        p.compare(lines, spec)


def test_route_render_and_withdrawal_fall_back_to_legacy(monkeypatch, tmp_path):
    query = {'selected': ['nationwide']}
    def forbidden(*args, **kwargs):
        raise AssertionError('Private Financial access')
    monkeypatch.setattr(f, 'read_analysis', forbidden)
    monkeypatch.setattr(f, 'find_existing_run', forbidden)
    facts = visual_streams.render('/industries/banking', query)
    assert all(fragment in facts for fragment in ('Cash flow statement', '3,904', '38,411', '361 days'))
    assert '<details' not in facts.split('<main ', 1)[1].split('</main>', 1)[0]
    insight = visual_streams.render('/industries/banking', {**query, 'reading': ['insight']})
    assert '+8,928' in insight and 'each contributed cash' in insight
    shutil.copytree(model.REPO / 'enterprise-knowledge', tmp_path / 'enterprise-knowledge')
    monkeypatch.setattr(model, 'REPO', tmp_path)
    path = tmp_path / PATH
    record = json.loads(path.read_text())
    record['withdrawn'] = True
    path.write_text(json.dumps(record))
    assert p.annual_details(SELECTION) == ()
    for mode in ('facts', 'insight'):
        html = visual_streams.render('/industries/banking', {**query, 'reading': [mode]})
        assert all(fragment not in html for fragment in ('3,904', '38,411', '+8,928', 'each contributed cash'))
        assert '£2.026bn' in html or '2,026' in html
    assert f.public_factual_projection() == {}


def test_exact_source_selector_and_origin_boundaries():
    record, _ = s.public_statement_record(SELECTION)
    assert s.official_url(record['url']) == record['url']
    for candidate in ('https://www.nationwide.co.uk/annual-report-and-accounts-2026.pdf', record['url']+'?other=1',
                      'https://www.bt.com/report','https://investor.equinix.com/report'):
        with pytest.raises(ValueError):
            s.official_url(candidate)
    for selection in ('easyjet','bt','equinix','/tmp/report',record['url']):
        assert p.annual_details(selection) == ()
