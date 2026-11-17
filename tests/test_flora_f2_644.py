"""F2 real-source/private Main and finite monetary composition assurance."""
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from html.parser import HTMLParser
import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from cios.applications.flora import visual_streams as v, document_review as review
from cios.applications.flora.financial_intelligence import analyst as a, candidate_analytics as f
from cios.applications.flora import intelligence_presentation as p
from cios.applications.flora.security_web import private_read
from cios.applications.flora.public_routes import public_request_target
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository
from cios.applications.flora.security_store import canonical
from tests.test_flora_f1_642 import permitted, authority, inputs, changed
from tests.fixtures.financial_analyst import example, measurement, reference

pytestmark=pytest.mark.real_security_boundary
KEY='boe-household-deposit-stocks'
CTX=v.Context('banking','landscape')


@pytest.fixture
def isolated_source(tmp_path,monkeypatch):
    from cios.applications.flora.research_intelligence import model
    root=tmp_path/'source-owner'
    shutil.copytree(model.REPO/'enterprise-knowledge',root/'enterprise-knowledge')
    monkeypatch.setattr(model,'REPO',root)
    return root/'enterprise-knowledge/banking/research-model/source-snapshots'/f.SOURCE_FILE


class DOM(HTMLParser):
    def __init__(self, text): super().__init__(); self.nodes=[]; self.feed(text)
    def handle_starttag(self, tag, attrs): self.nodes.append((tag,dict(attrs)))


def selected(identity, **extra):
    return {'analysis':[identity], **{k:[value] for k,value in extra.items()}}


def test_real_existing_run_enters_accepted_main_and_detail(permitted):
    _,headers,_=permitted
    identity=f.create_run(KEY,headers=headers)
    html=v.render('/industries/banking',selected(identity),headers)
    dom=DOM(html)
    assert [(tag,x['data-region']) for tag,x in dom.nodes if 'data-region'in x]==[('header','top'),('aside','left'),('main','main')]
    assert sum(tag=='h1' for tag,x in dom.nodes)==1
    assert 'UK household retail-deposit stocks' in html and '0.0825%' in html and '£1.555bn' in html
    assert '£1,884.726bn' in html and '£1,886.281bn' in html
    assert '0–2,000 GBP billions including zero' in a.compose(f.read_analysis(identity,headers=headers))
    assert '/ai-financial-report/'+identity not in html
    assert '<details' not in html.split('<main',1)[1]
    assert '2000000' not in html  # Display conversion, not another source fact.
    assert 'banking-landscape' in html and 'watermark' in html
    assert '1,884,726' in review.run_page(identity,headers=headers)
    from cios.applications.flora.visual_panels import research_inspection
    assert 'Financial analysis</a>' in research_inspection('/industries/banking',{'lens':['inspection']},headers)
    assert 'Financial analysis</a>' not in v.render('/industries/banking',{},headers)


def test_lookup_is_read_only_and_no_scan_or_implicit_creation(permitted,monkeypatch):
    _,headers,_=permitted
    assert f.find_existing_run(KEY,'BK-IND-002',headers=headers) is None
    assert not list(review._run_dir().glob('fi-f1-*'))
    identity=f.create_run(KEY,headers=headers)
    before=review._run_path(identity).read_bytes()
    original=Path.glob
    def no_scan(path,*args,**kwargs):
        if path==review._run_dir(): raise AssertionError('No global financial discovery')
        return original(path,*args,**kwargs)
    monkeypatch.setattr(Path,'glob',no_scan)
    assert f.find_existing_run(KEY,'BK-IND-002',headers=headers)==identity
    assert 'analysis='+identity in a.navigation(CTX,headers)
    assert review._run_path(identity).read_bytes()==before


def test_inspect_only_existing_authority_can_read_without_upload(permitted):
    store,headers,_=permitted;identity=f.create_run(KEY,headers=headers)
    with store.transaction() as db: db.execute('UPDATE memberships SET roles=?',(canonical(['package.inspect']),))
    assert f.find_existing_run(KEY,'BK-IND-002',headers=headers)==identity
    assert '0.0825%' in v.render('/industries/banking',selected(identity),headers)
    with pytest.raises(PermissionError): f.create_run(KEY,headers=headers)


@pytest.mark.parametrize('case',['anonymous','forged','revoked-membership','foreign-workspace','foreign-resource','no-capability','missing-acl','acl-principal'])
def test_denial_does_not_emit_private_titles_links_counts_or_charts(permitted,case):
    store,headers,acl=permitted;identity=f.create_run(KEY,headers=headers)
    raw=review.load_run(identity)
    if case=='anonymous': headers={}
    elif case=='forged': headers={'X-Flora-User':'synthetic-human','X-Flora-Roles':'cios_owner'}
    elif case=='foreign-workspace': raw.update(workspace_id='foreign',document={'workspace_id':'foreign','enterprise_id':'BK-IND-002'})
    elif case=='foreign-resource': raw.update(enterprise_id='foreign',document={'workspace_id':'synthetic-workspace','enterprise_id':'foreign'})
    from cios.applications.flora.storage import atomic_write_json
    atomic_write_json(review._run_path(identity),raw)
    with store.transaction() as db:
        if case=='revoked-membership': db.execute('UPDATE memberships SET active=0,version=version+1')
        if case=='no-capability': db.execute('UPDATE memberships SET roles=?',(canonical(['commercial_context.view']),))
    if case=='missing-acl': EnterpriseCanvasAccessRepository().path.unlink()
    if case=='acl-principal': EnterpriseCanvasAccessRepository().save(replace(acl,owner_account='other',acl=({'principal_id':'other'},)))
    assert a.navigation(CTX,headers)==''
    with pytest.raises((PermissionError,FileNotFoundError)):
        v.render('/industries/banking',selected(identity),headers)


@pytest.mark.parametrize('target',[
    '/industries/banking?analysis=../../private','/industries/banking?analysis=fi-x&analysis=fi-y',
    '/industries/banking?analysis=fi-x&workspace=foreign','/industries/banking?analysis=fi-x&stream=forces',
    '/industries/banking?analysis=fi-x&market=FR','/industries/banking?analysis=fi-x&detail=lloyds',
    '/?analysis=fi-x','/enterprises/easyjet?analysis=fi-x','/industries/banking?analysis=fi-x&agenda=funding-economics',
    '/industries/banking?analysis=fi-x&stream=landscape&stream=landscape',
])
def test_private_selector_never_widens_public_grammar(permitted,target):
    _,headers,_=permitted
    assert not public_request_target(target)
    assert a.authorise_request(target,headers=headers) is False


def test_valid_selector_private_guard_context_and_scope_history(permitted):
    _,headers,_=permitted;identity=f.create_run(KEY,headers=headers)
    target='/industries/banking?stream=landscape&selected=lloyds&layer=regulators&analysis='+identity
    assert not public_request_target(target)
    assert a.authorise_request(target,headers=headers)
    assert private_read(SimpleNamespace(path=target,headers=headers,requestline='GET '+target+' HTTP/1.1'))
    html=v.render('/industries/banking',selected(identity,selected='lloyds',layer='regulators'),headers)
    assert 'data-layer="regulators"' in html and 'selected=lloyds' in html
    assert 'UK household retail-deposit stocks' in html
    assert not a.authorise_request('/enterprises/lloyds?analysis='+identity,headers=headers)
    assert a.navigation(v.Context('lloyds','inside'),headers)==''


@pytest.mark.parametrize('mutation',['withdrawn','retracted','revoked','stale','contradictory','superseded','rights','owner-only','source-version','value','formula','payload'])
def test_all_new_surfaces_revalidate_and_never_resurrect_cached_output(permitted,isolated_source,mutation):
    _,headers,_=permitted;identity=f.create_run(KEY,headers=headers)
    raw=review.load_run(identity);old=review._run_path(identity).read_bytes()
    assert a.navigation(CTX,headers)
    package=json.loads(isolated_source.read_text())
    if mutation in {'formula','payload'}:
        raw['analysis']=f.read_analysis(identity,headers=headers)
        if mutation=='formula':raw['analytical_candidate']['derivations'][0]['formula']='eval'
        else: del raw['analytical_candidate']
        from cios.applications.flora.storage import atomic_write_json
        atomic_write_json(review._run_path(identity),raw)
        old=review._run_path(identity).read_bytes()
    else:
        if mutation=='rights': package['source']['rights']['status']='denied'
        elif mutation=='owner-only':package['source']['owner_only']=True
        elif mutation=='source-version':package['source']['text_sha256']='0'*64
        elif mutation=='value':package['claims'][0]['amount']='1'
        else:package['source'][mutation]=True
        isolated_source.write_text(json.dumps(package))
    navigation=a.navigation(CTX,headers)
    assert identity not in navigation and 'Financial analysis</a>' not in navigation
    assert not a.authorise_request('/industries/banking?analysis='+identity,headers=headers)
    with pytest.raises(PermissionError):v.render('/industries/banking',selected(identity),headers)
    external=review.read_run(identity,headers=headers)
    assert external['analysis']=={} and 'analytical_candidate' not in external
    assert '0.0825' not in review.run_page(identity,headers=headers)
    assert review._run_path(identity).read_bytes()==old


@pytest.mark.parametrize('case',['bank-income','mutual-bridge','technology','aviation','technology-scenario'])
def test_finite_generic_components_render_synthetic_monetary_examples(case):
    data=example(case);html=a.compose(data)
    assert 'Synthetic' in html and 'contract example only' in html
    assert 'Financial measurements' not in html or 'no real issuer' in html
    assert 'Measurements and chart data' in html and 'including zero' in html
    assert ('Estimated' in html and 'Working assumption'in html) if case=='technology-scenario' else 'Reported' in html
    assert len([x for x in DOM(html).nodes if x[0]=='h1'])==1
    if case=='mutual-bridge':assert 'Reconciled endpoint' in html and data['results'][0]['value']=='200'


@pytest.mark.parametrize('bad',['duplicate','wrong-sign','endpoint','entity','period','currency','basis','source-version','revision'])
def test_mutual_bridge_does_not_weaken_financial_compatibility(bad):
    ms=[measurement('mutual','opening','300',basis='underlying'),measurement('mutual','adjustment','-100',basis='bridge'),measurement('mutual','endpoint','200',basis='statutory')]
    if bad=='wrong-sign':ms[1]=changed(ms[1],value={'kind':'numeric','amount':'100','currency':'GBP','unit':'currency','scale':'millions'})
    if bad=='endpoint':ms[-1]=changed(ms[-1],value={'kind':'numeric','amount':'201','currency':'GBP','unit':'currency','scale':'millions'})
    if bad=='entity':ms[1]=changed(ms[1],subject_id='other')
    if bad=='period':ms[1]=changed(ms[1],period={'kind':'duration','label':'other','start':'2025-01-01','end':'2025-06-30','fiscal_year_end':'12-31'})
    if bad=='currency':ms[1]=changed(ms[1],value={'kind':'numeric','amount':'-100','currency':'USD','unit':'currency','scale':'millions'})
    if bad=='basis':ms[1]=changed(ms[1],accounting_basis='statutory')
    if bad=='source-version':
        source=ms[1].source.model_dump(mode='json');source['source_revision']='f'*64;ms[1]=changed(ms[1],source=source)
    opening,adjustment,endpoint=map(reference,ms)
    if bad=='revision':adjustment=f.InputReference(measurement_id=ms[1].measurement_id,revision='f'*64)
    recipe=f.Reconciliation(derivation_id='synthetic-bridge',opening=opening,adjustments=(adjustment,adjustment)if bad=='duplicate'else(adjustment,),endpoint=endpoint,opening_basis='underlying',adjustment_basis='bridge',endpoint_basis='statutory')
    with pytest.raises(ValueError):f.reconcile(recipe,ms)


def test_bridge_and_arithmetic_keep_assumptions_weaker_than_reported():
    ms=[measurement('mutual','opening','300',basis='underlying'),measurement('mutual','adjustment','-100',basis='bridge',kind='assumed'),measurement('mutual','endpoint','200',basis='statutory')]
    recipe=f.Reconciliation(derivation_id='synthetic-bridge',opening=reference(ms[0]),adjustments=(reference(ms[1]),),endpoint=reference(ms[-1]),opening_basis='underlying',adjustment_basis='bridge',endpoint_basis='statutory')
    result=f.reconcile(recipe,ms)
    assert result['semantic_type']=='estimated' and result['dependency_types']==['reported','assumed','reported']
    data=example('technology-scenario');data['results'][0]['semantic_type']='calculated'
    with pytest.raises(ValueError):a.compose(data)


def test_chart_refuses_cross_entity_currency_basis_stock_flow_and_unsupported_counts(inputs):
    for other in [changed(inputs[1],subject_id='bank'),changed(inputs[1],accounting_basis='adjusted'),
            changed(inputs[1],value={'kind':'numeric','amount':'10','currency':'USD','scale':'millions','unit':'currency'})]:
        with pytest.raises(ValueError):a.chart([inputs[0],other],0)
    with pytest.raises(ValueError):changed(inputs[0],value={'kind':'numeric','amount':'10','currency':None,'scale':'units','unit':'passengers'})


@pytest.mark.parametrize('kind',['reported','calculated','estimated','assumed','insight','hypothesis'])
def test_existing_six_semantics_are_finite_and_unsupported_slots_omitted(kind):
    data=example('bank-income');m=f.Measurement.model_validate(data['measurements'][0])
    source=p.Source('Synthetic source',m.source.url)
    statement=p.Statement('Synthetic commercial statement',kind,m.perimeter,m.period.label,(source,),
        'reviewed_excerpt'if kind=='reported'else'derived_from_inputs','candidate_intelligence',
        method='Synthetic method',reasoning='Synthetic explicitly stated reasoning',
        dependencies=()if kind=='reported'else('Synthetic input',),dependency_types=('reported',),
        caveats=('Synthetic limitation',),counter_evidence=('Synthetic counter-evidence',),
        falsifier='Synthetic disconfirming condition',assumption_owner='synthetic-owner',assumption_version='1')
    html=a.compose(data,statements=(statement,))
    assert 'Synthetic commercial statement' in html and 'data-semantic-type="'+kind+'"' in html
    assert 'Synthetic commercial statement' not in a.compose(data,statements=(replace(statement,text='What should we investigate next?'),))


def test_duration_basis_scope_and_assumption_versions_are_visible():
    data=example('mutual-bridge');html=a.compose(data)
    assert '01 Jan 2026 – 30 Jun 2026' in html
    assert 'Synthetic mutual-bridge · underlying' in html
    assert 'Synthetic mutual-bridge · disclosed bridge' in html
    assert 'Synthetic mutual-bridge · statutory' in html
    scenario=a.compose(example('technology-scenario'))
    assert 'synthetic-scenario-owner · version fixture-v1' in scenario
    assert 'weaker Estimated basis' in scenario


def test_tiny_axis_values_remain_nonzero_and_unknown_subject_rows_do_not_merge(inputs):
    small=[]
    for m,value in zip(inputs,('0.0001','0.0002')):
        small.append(changed(m,value={'kind':'numeric','amount':value,'currency':'GBP','scale':'units','unit':'currency'},precision_dp=4))
    html=a.chart(small,0)
    assert '0–0 GBP' not in html and '0.0002' in html
    with pytest.raises(ValueError):a.chart([inputs[0],changed(inputs[1],subject_name='Wrong issuer name')],0)
    conflict=changed(inputs[1],period=inputs[0].period.model_dump(mode='json'))
    with pytest.raises(ValueError,match='Conflicting'):a.chart([inputs[0],conflict],0)


def test_weaker_narrative_dependencies_cannot_be_calculated_or_reported():
    data=example('technology-scenario');m=f.Measurement.model_validate(data['measurements'][0])
    statement=p.Statement('Unsupported stronger scenario claim','calculated',m.perimeter,m.period.label,
        (p.Source('Synthetic source',m.source.url),),'derived_from_inputs','derived_view_not_canonical',
        method='Synthetic method',dependencies=('Assumed input',),dependency_types=('assumed',),caveats=('Synthetic caveat',))
    assert 'Unsupported stronger scenario claim' not in a.compose(data,statements=(statement,))


@pytest.mark.parametrize('path',[
    'cios/applications/flora/security_web.py','cios/applications/flora/visual_streams.py'])
@pytest.mark.parametrize('mutation',['prior-call','guard-path','guard-position'])
def test_owner_compatibility_rejects_unreviewed_guard_or_previous_code_changes(tmp_path,path,mutation):
    import subprocess
    from tests.flora_f2_owner_contract import assert_owner_compatible, BASE
    root=Path(__file__).resolve().parents[1]
    original=subprocess.check_output(['git','show',BASE+':'+path],cwd=root)
    current=(root/path).read_text()
    if mutation=='prior-call':
        current=current.replace('verified_context(handler.headers)','verified_context({})') if 'security_web'in path else current.replace('return panels(resolve(path,query),headers)','return panels(resolve(path,{}),headers)')
    elif mutation=='guard-path':
        current=current.replace("{'/industries/banking','/enterprises/lloyds'}", "{'/industries/banking','/enterprises/lloyds','/macro'}") if 'security_web'in path else current.replace("if 'analysis'in query:","if query:")
    else:
        current=current.replace("    path=parsed.path\n", "    path=parsed.path\n    unused=True\n") if 'security_web'in path else current.replace(' from .visual_panels import render as panels\n',' from .visual_panels import render as panels\n unused=True\n')
    assert current!=(root/path).read_text()
    target=tmp_path/path;target.parent.mkdir(parents=True);target.write_text(current)
    # The helper's historical-source command needs this checkout's Git data;
    # mutation is tested in a separate worktree-shaped filesystem only.
    (tmp_path/'.git').write_text('gitdir: '+subprocess.check_output(['git','rev-parse','--absolute-git-dir'],cwd=root,text=True).strip()+'\n')
    with pytest.raises(AssertionError):assert_owner_compatible(tmp_path,path,original)


def test_distinct_consolidation_perimeters_remain_identifiable():
    data=example('bank-income');other=deepcopy(data['measurements'][0])
    other.update(measurement_id='synthetic-segment-income',perimeter='Fictional segment boundary')
    data['measurements'].append(other)
    html=a.compose(data)
    assert 'Synthetic bank-income · statutory · Fictional segment boundary' in html
    assert 'Synthetic bank-income · statutory · Fictional bank-income entity; no real issuer' in html
