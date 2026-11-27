"""Official filings through the shared Source, EEI-2A and Economics path."""
import json
import shutil

from cios.applications.flora import enterprise_economics as economics
from cios.applications.flora.financial_intelligence import candidate_analytics as f
from cios.applications.flora.financial_intelligence import public_statements as p
from cios.applications.flora.research_intelligence import source_import as source
from cios.applications.flora.research_intelligence import statement_sources as s
from cios.applications.flora.research_intelligence import technology_experience as tech

EQ = ('research-subject:equinix-inc-group', 'Equinix, Inc.')
NW = ('research-subject:nationwide-building-society-group', 'Nationwide Building Society Group')


def package(tmp_path, monkeypatch):
    target = tmp_path / s.PACKAGE
    shutil.copytree(s.model.REPO / s.PACKAGE, target)
    statement = s.model.REPO / 'enterprise-knowledge/banking/research-model/source-snapshots/EEI2B-Nationwide-AR26.json'
    prior = tmp_path / statement.relative_to(s.model.REPO)
    prior.parent.mkdir(parents=True)
    shutil.copyfile(statement, prior)
    monkeypatch.setattr(s.model, 'REPO', tmp_path)
    return target


def write(path, obj):
    path.write_text(json.dumps(obj))


def test_real_new_issuer_and_successive_report_without_python_change(tmp_path, monkeypatch):
    path = package(tmp_path, monkeypatch) / 'catalogue.json'
    nationwide, latest, prior = json.loads(path.read_text())['reports']
    write(path, {'reports': [nationwide]})
    assert len(p.statement_series(NW)) == 44
    assert not economics.presented_statement_series('technology:equinix')
    write(path, {'reports': [nationwide, prior]})
    before = economics.presented_statement_series('technology:equinix')
    assert len(before) == 30 and max(line.fiscal_year for line in before) == 2024
    write(path, {'reports': [nationwide, prior, latest]})
    current = economics.presented_statement_series('technology:equinix')
    assert len(current) == 45 and len(p.statement_history(EQ)) == 60
    assert {line.statement for line in current} == {'income', 'balance', 'cash_flow', 'segment'}
    assert {line.fiscal_year for line in current} == {2023, 2024, 2025}
    assert {line.source.source_id for line in p.statement_history(EQ)} == {latest['id'], prior['id']}
    _, result = next(p.annual_growth(current, ('revenue',)))
    assert result['value'].startswith('5.3612254')
    assert [row['measurement_id'] for row in result['inputs']] == [
        'eqix-2025-revenue-2024', 'eqix-2025-revenue-2025']


def test_withdrawal_exception_and_origin_mismatch_isolate_affected_report(tmp_path, monkeypatch):
    target = package(tmp_path, monkeypatch)
    path = target / 'EEI3-EQUINIX-10K-2025.json'
    report = json.loads(path.read_text())
    for change in ({'withdrawn': True}, {'restrictions': ['material use restriction']},
                   {'rights': {**report['rights'], 'material_exceptions': [{
                       'issue': 'facts_reuse_exception', 'operations': ['independent_facts'], 'status': 'unresolved'}]}}):
        write(path, {**report, **change})
        lines = p.statement_series(EQ)
        assert len(lines) == 30 and max(line.fiscal_year for line in lines) == 2024
        assert len(p.statement_series(NW)) == 44
    write(path, report)
    catalogue = json.loads((target / 'catalogue.json').read_text())
    catalogue['reports'][1]['accession'] = '000110123926000099'
    assert max(line.fiscal_year for line in p.statement_series(EQ, catalogue=catalogue)) == 2024


def test_correction_retains_predecessor_while_suppressing_withdrawn_revision(tmp_path, monkeypatch):
    target = package(tmp_path, monkeypatch)
    catalogue = json.loads((target / 'catalogue.json').read_text())
    latest, prior = [target / entry['file'] for entry in catalogue['reports'][1:]]
    old = json.loads(prior.read_text())
    new = json.loads(latest.read_text())
    original = next(b for b in old['fact_bindings'] if b['key'] == 'eqix-2024-revenue-2024')
    corrected = next(b for b in new['fact_bindings'] if b['key'] == 'eqix-2025-revenue-2024')
    original['facts']['revision_state'] = 'superseded'
    corrected['facts']['revision_state'] = 'restated'
    corrected['facts']['supersedes'] = f.stable_hash(original)
    corrected['facts']['value']['amount'] = '8749'
    corrected['facts']['original_display'] = '8,749'
    for path, record in ((prior, old), (latest, new)):
        payload = {key: record[key] for key in ('document_identity', 'fact_bindings')}
        record['facts_sha256'] = source.sha(json.dumps(
            payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())
        write(path, record)
    visible = {line.measurement_id: line for line, _ in p.statements(p.statement_series(EQ))}
    assert original['key'] not in visible
    assert visible[corrected['key']].original_display == '8,749'
    assert len(p.statement_history(EQ)) == 60
    write(latest, {**new, 'withdrawn': True})
    assert original['key'] not in {line.measurement_id for line in p.statement_series(EQ)}


def test_existing_equinix_route_uses_public_only(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Public statements cannot read or create private runs')
    for name in ('read_analysis', 'find_existing_run', 'create_run'):
        monkeypatch.setattr(f, name, forbidden)
    url = tech.BASE + '/enterprise'
    facts = tech.render(url, {'detail': 'financials'})
    insight = tech.render(url, {'detail': 'financial-insight'})
    assert all(label in facts for label in ('Financial statements', 'Cash flow statement', '40,141', 'Segment reporting'))
    assert '+5.36' in insight and 'investing used cash' in insight
    assert 'Source &amp; basis' in facts
    assert all(row.source.url == 'https://www.sec.gov/' for row in p.statement_series(
        ('research-subject:lloyds-banking-group-plc', 'Lloyds Banking Group plc')))
    assert f.public_factual_projection() == {}
