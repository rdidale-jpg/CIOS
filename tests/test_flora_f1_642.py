"""Real public numbers, isolated authority/storage. Mutations are negative fixtures.

No source or canonical acceptance is granted by these tests. Production security
resolvers are exercised without the legacy header-trust fixture.
"""
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
import json
from pathlib import Path
import shutil

import pytest

from cios.applications.flora.financial_intelligence import candidate_analytics as a
from cios.applications.flora import document_review as review
from cios.applications.flora.research_intelligence import model
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRecord, EnterpriseCanvasAccessRepository
from cios.applications.flora.security_store import canonical
from tests.test_flora_security_repair_01b import authority, signed

pytestmark = pytest.mark.real_security_boundary
SELECTION = 'boe-household-deposit-stocks'


def changed(m, **updates):
    data = m.model_dump(mode='json'); data.update(updates)
    return a.Measurement.model_validate(data)


def recipe(ms, formula='difference', comparison='stock_dates'):
    return a.Derivation(derivation_id='test-recipe', formula=formula, comparison=comparison,
        inputs=tuple(a.InputReference(measurement_id=m.measurement_id, revision=m.revision) for m in ms))


@pytest.fixture
def inputs():
    return list(a._current_inputs(SELECTION).measurements)


@pytest.fixture
def permitted(authority, tmp_path):
    store, token, csrf, headers, _ = signed(authority, tmp_path)
    with store.transaction() as db:
        db.execute('UPDATE memberships SET enterprises=?', (canonical(['BK-IND-002']),))
    acl = EnterpriseCanvasAccessRecord('1.0', 'synthetic-industry-access', 'BK-IND-002', 'synthetic-workspace', 'synthetic-human',
        acl=({'principal_id': 'synthetic-human', 'role': 'owner', 'grant_source': 'synthetic-test-only'},))
    EnterpriseCanvasAccessRepository().save(acl)
    return store, headers, acl


@pytest.fixture
def isolated_source(tmp_path, monkeypatch):
    # Copy the existing source owner's bounded release; never mutate this repo.
    root = tmp_path / 'research'
    rel = Path('enterprise-knowledge/banking/research-model/source-snapshots')
    (root / rel).mkdir(parents=True)
    for name in (a.SOURCE_FILE, 'F1-BOE-LPMZ598.txt'):
        shutil.copyfile(model.REPO / rel / name, root / rel / name)
    monkeypatch.setattr(model, 'REPO', root)
    return root / rel / a.SOURCE_FILE


def test_real_source_and_exact_meaning(inputs):
    assert [m.value.amount for m in inputs] == [Decimal('1884726'), Decimal('1886281')]
    assert [str(m.period.as_at) for m in inputs] == ['2026-05-31', '2026-06-30']
    assert all(m.period.start is None and m.period.end is None for m in inputs)
    assert all(m.value.scale == 'millions' and m.value.currency == 'GBP' for m in inputs)
    assert all(m.source.published is None for m in inputs)
    assert inputs[0].subject_id != 'BK-IND-002'  # Reported subject is not ACL resource.
    result = a.calculate(recipe(inputs, 'percent_change'), inputs)
    assert result['value'].startswith('0.0825053615220461754')
    assert result['semantic_type'] == 'calculated'
    assert a.calculate(recipe(inputs), inputs)['value'] == '1555'


@pytest.mark.parametrize('period', [
    {'kind': 'instant', 'label': 'date'},
    {'kind': 'instant', 'label': 'date', 'as_at': '2026-06-30', 'start': '2026-01-01'},
    {'kind': 'duration', 'label': 'H1', 'start': '2026-01-01', 'end': '2026-06-30'},
    {'kind': 'duration', 'label': 'H1', 'start': '2026-07-01', 'end': '2026-06-30', 'fiscal_year_end': '12-31'},
    {'kind': 'duration', 'label': 'H1', 'start': '2026-01-01', 'end': '2026-06-30', 'fiscal_year_end': '02-30'},
    {'kind': 'duration', 'label': 'H1', 'start': '2026-01-01', 'end': '2026-06-30', 'fiscal_year_end': '12-31', 'as_at': '2026-06-30'},
])
def test_invalid_stock_flow_boundaries_rejected(period):
    with pytest.raises(ValueError): a.FinancialPeriod.model_validate(period)


@pytest.mark.parametrize('calendar', ['12-31', '03-31', '09-30'])
def test_duration_requires_issuer_calendar_not_bt_fallback(inputs, calendar):
    p = a.FinancialPeriod(kind='duration', label='Explicit source period', start='2025-10-01', end='2026-03-31', fiscal_year_end=calendar)
    m = changed(inputs[0], period=p.model_dump(mode='json'))
    loaded = a.Measurement.model_validate_json(m.model_dump_json())
    assert str(loaded.period.start) == '2025-10-01'
    assert loaded.period.fiscal_year_end == calendar


@pytest.mark.parametrize('field,value', [
    ('subject_id', 'different-legal-bank'), ('subject_name', 'Different bank'),
    ('perimeter', 'subsidiary'), ('metric', 'total_assets'), ('definition', 'Excludes repo'),
    ('accounting_basis', 'adjusted'), ('state', 'target'),
])
def test_incompatible_financial_meaning_rejected(inputs, field, value):
    inputs[1] = changed(inputs[1], **{field: value})
    with pytest.raises(ValueError, match='Incompatible'): a.calculate(recipe(inputs), inputs)


@pytest.mark.parametrize('field,value', [('currency', 'USD'), ('scale', 'billions')])
def test_incompatible_units_rejected(inputs, field, value):
    v = inputs[1].value.model_dump(mode='json'); v[field] = value
    inputs[1] = changed(inputs[1], value=v)
    with pytest.raises(ValueError, match='Incompatible'): a.calculate(recipe(inputs), inputs)


@pytest.mark.parametrize('value', [
    {'amount': '1', 'unit': 'percent', 'currency': 'GBP', 'scale': 'millions'},
    {'amount': '1', 'unit': 'currency', 'currency': 'gbp', 'scale': 'millions'},
    {'amount': '1', 'unit': 'currency', 'currency': None, 'scale': 'millions'},
    {'amount': '1', 'unit': 'currency', 'currency': 'GBP', 'scale': 'm'},
    {'amount': '1.23', 'unit': 'currency', 'currency': 'GBP', 'scale': 'millions'},
    {'amount': 'NaN', 'unit': 'currency', 'currency': 'GBP', 'scale': 'millions'},
    {'amount': 'Infinity', 'unit': 'currency', 'currency': 'GBP', 'scale': 'millions'},
])
def test_missing_or_invalid_numeric_meaning_denied(inputs, value):
    with pytest.raises(ValueError): changed(inputs[0], value=value)


def test_signed_precision_and_base_unit_representation_roundtrip(inputs):
    m = changed(inputs[0], value={'kind':'numeric','amount':'-123.40','unit':'currency','currency':'GBP','scale':'millions'}, precision_dp=2)
    loaded = a.Measurement.model_validate_json(m.model_dump_json())
    assert str(loaded.value.amount) == '-123.40'
    assert loaded.base_amount == Decimal('-123400000.00')
    assert loaded.source == m.source and loaded.period == m.period
    assert loaded.revision == m.revision


@pytest.mark.parametrize('field,value', [('retrieved_at', 'bad'), ('retrieved_at', '2026-06-01'),
    ('retrieved_at', '2099-01-01T00:00:00+00:00'), ('published', '2099-01-01'),
    ('url', 'https://user:secret@www.bankofengland.co.uk/'), ('url', 'http://example.invalid')])
def test_source_chronology_and_url_denied(inputs, field, value):
    source = inputs[0].source.model_dump(mode='json'); source[field] = value
    with pytest.raises(ValueError): changed(inputs[0], source=source)


def test_actual_future_date_rejected_but_target_retains_state(inputs):
    p = {'kind': 'instant', 'label': 'Future target', 'as_at': '2099-12-31'}
    with pytest.raises(ValueError): changed(inputs[0], period=p)
    target = changed(inputs[0], state='target', period=p)
    assert target.state == 'target'


@pytest.mark.parametrize('case', ['reversed', 'same-date', 'flow-as-stock', 'flow-period-mismatch'])
def test_temporal_comparisons_fail_closed(inputs, case):
    comparison = 'stock_dates'
    if case == 'reversed': inputs.reverse()
    elif case == 'same-date': inputs[1] = changed(inputs[1], period=inputs[0].period.model_dump(mode='json'))
    else:
        inputs[0] = changed(inputs[0], period={'kind':'duration','label':'H1','start':'2026-01-01','end':'2026-06-30','fiscal_year_end':'12-31'})
        if case == 'flow-period-mismatch': comparison = 'same_period'
    with pytest.raises(ValueError): a.calculate(recipe(inputs, comparison=comparison), inputs)


def test_same_period_reported_conflict_is_not_a_financial_difference(inputs):
    inputs[1] = changed(inputs[1], period=inputs[0].period.model_dump(mode='json'))
    with pytest.raises(ValueError, match='Conflicting'): a.calculate(recipe(inputs, comparison='same_period'), inputs)


@pytest.mark.parametrize('kind', ['estimated', 'assumed'])
def test_assumption_arithmetic_retains_weaker_semantics(inputs, kind):
    inputs[1] = changed(inputs[1], semantic_type=kind, assumption_owner='synthetic-scenario-owner', assumption_version='fixture-v1')
    result = a.calculate(recipe(inputs), inputs)
    assert result['semantic_type'] == 'estimated'
    assert result['dependency_types'] == ['reported', kind]
    assert result['assumptions'] == [{'owner':'synthetic-scenario-owner','version':'fixture-v1'}]
    assert result['canonical_status'] == 'derived_view_not_canonical'


def test_assumptions_need_explicit_owner_version(inputs):
    with pytest.raises(ValueError): changed(inputs[0], semantic_type='assumed')


def test_stale_input_revision_duplicate_and_zero_denominator_rejected(inputs):
    spec = recipe(inputs)
    mutated = [inputs[0], changed(inputs[1], original_display='A changed source display')]
    with pytest.raises(ValueError, match='revision'): a.calculate(spec, mutated)
    with pytest.raises(ValueError, match='Duplicate'): a.calculate(spec, [*inputs, inputs[0]])
    inputs[0] = changed(inputs[0], value={'kind':'numeric','amount':'0','unit':'currency','currency':'GBP','scale':'millions'})
    with pytest.raises(ValueError, match='denominator'): a.calculate(recipe(inputs, 'percent_change'), inputs)


def test_actual_run_repository_reload_idempotency_and_no_canonical_mutation(permitted):
    store, headers, _ = permitted
    identity = a.create_run(SELECTION, headers=headers)
    raw = review.load_run(identity)
    path = review._run_path(identity)
    before = path.read_bytes()
    assert a.create_run(SELECTION, headers=headers) == identity
    assert path.read_bytes() == before
    assert raw['claims'] == []
    assert raw['canonical_update'] == {'enterprise_model_updated':False,'observations_created':0}
    assert len(raw['analytical_candidate']['measurements']) == 2
    assert raw['analytical_candidate']['measurements'][0]['value']['amount'] == '1884726'
    projection = a.read_analysis(identity, headers=headers)
    assert [r['value'] for r in projection['results']][0] == '1555'
    exposed = review.read_run(identity, headers=headers)
    assert 'analytical_candidate' not in exposed and exposed['analysis'] == projection
    assert '0.0825%' in review.financial_intelligence_run_page(identity, headers=headers)
    assert '1,555 GBP millions' in a.render_run(identity, headers=headers)
    root = store.path.parent.parent
    assert not (root/'memory').exists()
    assert not (root/'sales_pipeline').exists()
    assert not (root/'commercial_context').exists()


@pytest.mark.parametrize('operation', ['read', 'render', 'create', 'review', 'promote'])
def test_absent_or_forged_authentication_confers_no_authority(permitted, operation):
    _, headers, _ = permitted; identity = a.create_run(SELECTION, headers=headers)
    forged = {'X-Flora-User':'synthetic-human','X-Flora-Roles':'cios_owner','X-Flora-Active-Workspace':'synthetic-workspace'}
    with pytest.raises(PermissionError):
        if operation == 'read': a.read_analysis(identity, headers=forged)
        elif operation == 'render': a.render_run(identity, headers=forged)
        elif operation == 'create': a.create_run(SELECTION, headers=forged)
        elif operation == 'review': review.update_reviews(identity, {}, headers=forged)
        else: review.apply_accepted(identity, headers=forged)


@pytest.mark.parametrize('denial', ['foreign-workspace', 'foreign-resource', 'missing-acl', 'acl-principal', 'revoked-membership', 'no-capability'])
def test_actual_resource_and_tenant_denials(permitted, denial):
    store, headers, acl = permitted; identity = a.create_run(SELECTION, headers=headers)
    raw = review.load_run(identity)
    if denial == 'foreign-workspace': raw.update(workspace_id='another-workspace', document={'workspace_id':'another-workspace','enterprise_id':'BK-IND-002'})
    if denial == 'foreign-resource': raw.update(enterprise_id='other-bank', document={'workspace_id':'synthetic-workspace','enterprise_id':'other-bank'})
    from cios.applications.flora.storage import atomic_write_json
    atomic_write_json(review._run_path(identity), raw)
    if denial == 'missing-acl': EnterpriseCanvasAccessRepository().path.unlink()
    if denial == 'acl-principal': EnterpriseCanvasAccessRepository().save(replace(acl, owner_account='other-human', acl=({'principal_id':'other-human'},)))
    with store.transaction() as db:
        if denial == 'revoked-membership': db.execute('UPDATE memberships SET active=0,version=version+1')
        if denial == 'no-capability': db.execute('UPDATE memberships SET roles=?', (canonical(['commercial_context.view']),))
    with pytest.raises(PermissionError): a.read_analysis(identity, headers=headers)


@pytest.mark.parametrize('mutation', ['withdrawn', 'retracted', 'revoked', 'stale', 'contradiction', 'superseded', 'rights-denied', 'owner-only', 'wrong-subject', 'changed-number', 'changed-source', 'expired-review'])
def test_source_use_changes_remove_all_dependent_output_and_keep_history(permitted, isolated_source, mutation):
    _, headers, _ = permitted
    identity = a.create_run(SELECTION, headers=headers)
    before = review._run_path(identity).read_bytes()
    assert a.read_analysis(identity, headers=headers)['title']
    package = json.loads(isolated_source.read_text())
    if mutation in {'withdrawn','retracted','owner-only'}: package['source'][mutation.replace('-','_')] = True
    elif mutation == 'rights-denied': package['source']['rights']['status'] = 'denied'
    elif mutation in {'revoked','stale','contradiction','superseded'}: package['source']['status'] = mutation
    elif mutation == 'wrong-subject': package['subject_identity'] = 'different-bank'
    elif mutation == 'changed-number': package['claims'][0]['amount'] = '999'
    elif mutation == 'changed-source': package['source']['url'] = 'https://www.sec.gov/example'
    else: package['review_until'] = '2026-01-01'
    isolated_source.write_text(json.dumps(package))
    assert a.read_analysis(identity, headers=headers) == {}
    exposed = review.read_run(identity, headers=headers)
    assert exposed['analysis'] == {} and 'analytical_candidate' not in exposed
    assert not any(s in json.dumps(exposed) for s in ('1884726','1886281','0.0825','bankofengland.co.uk'))
    html = a.render_run(identity, headers=headers)
    assert 'unavailable' in html and 'deposit' not in html and '1555' not in html and 'href' not in html
    assert review._run_path(identity).read_bytes() == before


@pytest.mark.parametrize('selection', ['lloyds-deposit-stocks','natwest','hsbc','santander','ons','sec','../../private'])
def test_unadmitted_source_selections_fail_closed(permitted, selection):
    _, headers, _ = permitted
    with pytest.raises(PermissionError): a.create_run(selection, headers=headers)


@pytest.mark.parametrize('operation', ['review', 'promote'])
def test_analytical_runs_cannot_enter_canonical_operations(permitted, operation):
    _, headers, _ = permitted; identity = a.create_run(SELECTION, headers=headers)
    before = review._run_path(identity).read_bytes()
    with pytest.raises(ValueError):
        if operation == 'review': review.update_reviews(identity, {}, headers=headers)
        else: review.apply_accepted(identity, headers=headers)
    assert review._run_path(identity).read_bytes() == before


def test_legacy_global_latest_summaries_cannot_disclose_private_candidate(permitted):
    _, headers, _ = permitted
    identity = a.create_run(SELECTION, headers=headers)
    raw = review.load_run(identity)
    for html in (review.financial_intelligence_page(), review.financial_intelligence_admin_health_page(), review._outcome_summary(raw)):
        assert not any(s in html for s in ('1884726','1,884,726','1886281','retail-deposit stocks',identity))
    assert review._legacy_run_paths() == []
    assert review._active_refresh_run() is None


def test_missing_payload_cannot_restore_forged_cached_analysis(permitted):
    _, headers, _ = permitted; identity = a.create_run(SELECTION, headers=headers)
    raw = review.load_run(identity)
    raw['analysis'] = a.read_analysis(identity, headers=headers)
    del raw['analytical_candidate']
    from cios.applications.flora.storage import atomic_write_json
    atomic_write_json(review._run_path(identity), raw)
    assert review.read_run(identity, headers=headers)['analysis'] == {}
    assert a.read_analysis(identity, headers=headers) == {}
    assert '1,884,726' not in review.run_page(identity, headers=headers)
    for operation in (lambda: review.update_reviews(identity, {}, headers=headers), lambda: review.apply_accepted(identity, headers=headers)):
        with pytest.raises(ValueError): operation()


def test_source_excerpt_digest_and_original_publisher_boundaries(permitted, isolated_source):
    _, headers, _ = permitted; identity = a.create_run(SELECTION, headers=headers)
    path = isolated_source.with_name('F1-BOE-LPMZ598.txt')
    path.write_text(path.read_text().replace('1884726','1884727'))
    assert a.read_analysis(identity, headers=headers) == {}


def test_write_failure_rolls_back_candidate_with_existing_journal(permitted, monkeypatch):
    from cios.applications.flora import storage
    store, headers, _ = permitted
    original = storage.atomic_write_json
    def fail_after_write(path, data):
        original(path, data)
        if data.get('workflow') == a.WORKFLOW: raise OSError('synthetic post-write failure')
    monkeypatch.setattr(storage, 'atomic_write_json', fail_after_write)
    with pytest.raises(OSError): a.create_run(SELECTION, headers=headers)
    assert not list(review._run_dir().glob('fi-f1-*.json'))


def test_completed_candidate_progress_is_terminal_not_canonical(permitted):
    _, headers, _ = permitted; identity = a.create_run(SELECTION, headers=headers)
    status = review.financial_intelligence_progress_status(identity, headers=headers)
    assert status['terminal'] is True and status['progress_percent'] == 100
    assert status['facts_valid'] == 0  # No accepted/reviewable canonical claims.
    assert status['final_result_url'] == '/ai-financial-report/' + identity
    html = review.financial_intelligence_progress_page(identity, headers=headers)
    assert '1,884,726' in html and 'Failed' not in html and 'unavailable' not in html


@pytest.mark.parametrize('industry', ['Banking', 'Technology', 'Aviation'])
def test_same_existing_run_owner_persists_duration_and_assumptions_across_industries(permitted, inputs, monkeypatch, industry):
    # Source adapter is an explicit synthetic fixture here, never the real-data
    # proof. Authority/Financial persistence still use their actual services.
    original = a._current_inputs(SELECTION)
    period = {'kind':'duration','label':'Synthetic H1','start':'2026-01-01','end':'2026-06-30','fiscal_year_end':'12-31'}
    values = []
    for i, amount in enumerate(('100.00','105.00')):
        source = inputs[i].source.model_dump(mode='json')
        source.update(owner='synthetic-test-only', record_id='synthetic-'+str(i),
            source_id='synthetic-source', url='https://example.invalid/fixture',
            title='Synthetic financial fixture', publisher='Synthetic fixture', use_reference='Test fixture only; no source permission claim')
        values.append(changed(inputs[i], measurement_id='synthetic-'+str(i),
            subject_id='synthetic-'+industry, subject_name='Synthetic '+industry+' company', perimeter='Synthetic Group',
            period=period, source=source, semantic_type='assumed', assumption_owner='synthetic-scenario-owner', assumption_version='1',
            value={'kind':'numeric','amount':amount,'unit':'currency','currency':'GBP','scale':'millions'}, precision_dp=2,
            original_display='Synthetic £'+amount+'m', caveats=['Synthetic scenario only, not an actual company result']))
    bundle = a.InputBundle(original.resource_id, 'Synthetic '+industry+' flow test', tuple(values), original.source)
    monkeypatch.setattr(a, '_current_inputs', lambda _: bundle)
    _, headers, _ = permitted
    identity = a.create_run('synthetic-test-only', headers=headers)
    payload = review.load_run(identity)['analytical_candidate']
    loaded = [a.Measurement.model_validate(m) for m in payload['measurements']]
    assert str(loaded[0].value.amount) == '100.00' and loaded[0].period.kind == 'duration'
    result = a.read_analysis(identity, headers=headers)
    assert result['results'][0]['value'] == '5.00'
    assert all(r['semantic_type'] == 'estimated' for r in result['results'])


def test_all_173_prior_research_files_and_comparator_remain_exactly_preserved():
    import inspect
    import subprocess
    import types
    from tools.research import history_integrity as history
    root = Path(__file__).resolve().parents[1]
    baseline = '9f3dcc5b0577eb0408bc0185f0847de19a5c1f66'
    source = subprocess.check_output(['git','show',baseline+':tools/research/history_integrity.py'], cwd=root).decode()
    old = types.ModuleType('f1_baseline_history'); exec(compile(source,'baseline_history','exec'),old.__dict__)
    before = old.approved_history(root); after = history.approved_history(root)
    assert len(before) == 173 and len(after) == 178
    assert {key:after[key] for key in before} == before
    assert set(after)-set(before) == set(history.F1_CANDIDATE_ADDITIONS) | set(history.RUD1_ADDITIONS)
    old_comparator = source.split('def compare_history(',1)[1].split('\n\ndef verify_history',1)[0].strip()
    assert inspect.getsource(history.compare_history).split('def compare_history(',1)[1].strip() == old_comparator
    for path in history.F1_CANDIDATE_ADDITIONS:
        changed_history = deepcopy(after); changed_history[path] += b'unapproved'
        with pytest.raises(AssertionError): history.compare_history(after, changed_history)
    for path in ('tools/ci/flora-baseline-v1.json','tools/ci/flora_ci.py'):
        assert (root/path).read_bytes() == subprocess.check_output(['git','show',baseline+':'+path], cwd=root)
