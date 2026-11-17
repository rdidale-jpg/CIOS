"""Ordinary reading, protected internal provenance and genuine session scopes."""
from pathlib import Path
from copy import deepcopy
from dataclasses import replace
import json,shutil
from html.parser import HTMLParser

import pytest

from cios.applications.flora import visual_streams as v,visual_panels as panels,document_review as review
from cios.applications.flora import intelligence_presentation as semantics
from cios.applications.flora.financial_intelligence import candidate_analytics as f,analyst
from cios.applications.flora.public_routes import public_request_target,owner_inspection_request_target
from cios.applications.flora.research_intelligence import model
from cios.applications.flora.security_store import canonical
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository
from tests.test_flora_f1_642 import permitted,authority

pytestmark=pytest.mark.real_security_boundary


@pytest.fixture
def retained(tmp_path,monkeypatch):
    root=tmp_path/'source';shutil.copytree(model.REPO/'enterprise-knowledge',root/'enterprise-knowledge');monkeypatch.setattr(model,'REPO',root)
    return root/'enterprise-knowledge/banking/research-model/source-snapshots/RUD1-Public-Facts.json'


def main(html):return html.split('<main ',1)[1].split('</main>',1)[0]


@pytest.mark.parametrize('path,query',[
    ('/',{}),('/',{'stream':['forces']}),('/industries/banking',{}),('/industries/banking',{'stream':['forces']}),
    ('/industries/banking',{'selected':['nationwide']}),('/industries/banking',{'selected':['starling']}),
    ('/industries/banking',{'agenda':['service-landscape'],'selected':['natwest']}),
    ('/enterprises/lloyds',{}),('/enterprises/lloyds',{'stream':['landscape']}),('/enterprises/lloyds',{'stream':['forces']}),
    ('/enterprises/lloyds',{'detail':['economics']}),('/industries/banking',{'detail':['boe']})])
def test_customer_markup_has_no_research_controls_even_hidden_or_printable(path,query):
    html=v.render(path,query);body=main(html)
    assert '<details'not in body
    for text in ('Sources &amp; reasoning','Sources &amp; basis','Sources & detail','primary_content_sha256','reviewed excerpt','retrieval','canonical acceptance'):
        assert text not in body
    assert body.count('href="https://')<=1
    if 'href="https://'in body:assert 'class="legal-notice"'in body
    assert 'Guest' in html and 'class="account-entry" href="/auth/sign-in"'in html


def test_guest_and_forged_headers_never_lookup_or_serialize_private_finance(permitted,monkeypatch):
    _,headers,_=permitted;identity=f.create_run('nationwide-fy2026',headers=headers)
    original=f.find_existing_run
    def forbidden(*args,**kwargs):raise AssertionError('Guest must not search private runs')
    monkeypatch.setattr(f,'find_existing_run',forbidden)
    for guest in ({},{'X-Flora-User':'synthetic-human','X-Flora-Roles':'cios_owner'}):
        html=v.render('/industries/banking',{'selected':['nationwide']},guest)
        assert identity not in html and '£2.026bn'not in html and 'Prepare financial view'not in html
        assert '100,886'in html and 'Guest'in html
    monkeypatch.setattr(f,'find_existing_run',original)


def test_authorised_selection_immediately_contains_financials_without_analysis_query(permitted):
    _,headers,_=permitted;identity=f.create_run('nationwide-fy2026',headers=headers)
    before=review._run_path(identity).read_bytes()
    html=v.render('/industries/banking',{'selected':['nationwide']},headers);body=main(html)
    for value in ('£6.378bn','£2.026bn','£1.49bn','£127m','2025','2026','Statutory profit before tax'):assert value in body
    assert '<details'not in body and 'Financial analysis</a>'not in body and 'Open analysis detail'not in body
    assert 'Sources &amp; reasoning'not in body
    assert review._run_path(identity).read_bytes()==before
    assert review.load_run(identity)['canonical_update']=={'enterprise_model_updated':False,'observations_created':0}


def test_existing_internal_inspection_requires_owner_and_preserves_full_provenance(permitted):
    store,headers,_=permitted;identity=f.create_run('nationwide-fy2026',headers=headers)
    q={'selected':['nationwide'],'analysis':[identity],'lens':['inspection']}
    html=panels.research_inspection('/industries/banking',q,headers)
    assert 'Sources, method and limitations'in html and 'https://www.nationwide.co.uk/'in html and 'Reconciled endpoint'in html
    with pytest.raises(PermissionError):panels.research_inspection('/industries/banking',q,{})
    with store.transaction()as db:db.execute('UPDATE memberships SET roles=?',(canonical(['package.inspect']),))
    # Legitimate inspect-only authority keeps own analysis, not Owner inspection.
    assert '£2.026bn'in main(v.render('/industries/banking',{'selected':['nationwide']},headers))
    with pytest.raises(PermissionError):panels.research_inspection('/industries/banking',q,headers)


@pytest.mark.parametrize('mutation',['foreign-workspace','no-resource','no-inspect','revoked','private-source','withdrawn-source'])
def test_no_private_financial_fragments_or_setup_escape_scope(permitted,retained,mutation):
    store,headers,acl=permitted;identity=f.create_run('nationwide-fy2026',headers=headers)
    if mutation=='foreign-workspace':
        raw=review.load_run(identity);raw['workspace_id']='foreign';raw['document']['workspace_id']='foreign'
        from cios.applications.flora.storage import atomic_write_json
        atomic_write_json(review._run_path(identity),raw)
    elif mutation=='no-resource':EnterpriseCanvasAccessRepository().path.unlink()
    elif mutation=='no-inspect':
        with store.transaction()as db:db.execute('UPDATE memberships SET roles=?',(canonical(['commercial_context.view']),))
    elif mutation=='revoked':
        with store.transaction()as db:db.execute('UPDATE memberships SET active=0,version=version+1')
    else:
        p=json.loads(retained.read_text());p['sources'][1]['owner_only'if mutation=='private-source'else'withdrawn']=True;retained.write_text(json.dumps(p))
    body=main(v.render('/industries/banking',{'selected':['nationwide']},headers))
    assert '£2.026bn'not in body and '£6.378bn'not in body and identity not in body
    assert '100,886'in body


def test_nationwide_get_does_not_create_a_run_and_source_withdrawal_preserves_history(permitted,retained):
    _,headers,_=permitted
    html=v.render('/industries/banking',{'selected':['nationwide']},headers)
    assert not list(review._run_dir().glob('fi-*'))
    identity=f.create_run('nationwide-fy2026',headers=headers);before=review._run_path(identity).read_bytes()
    p=json.loads(retained.read_text());p['sources'][1]['withdrawn']=True;retained.write_text(json.dumps(p))
    assert '£2.026bn'not in main(v.render('/industries/banking',{'selected':['nationwide']},headers))
    assert f.read_analysis(identity,headers=headers)=={} and review._run_path(identity).read_bytes()==before


def test_research_url_remains_private_and_query_does_not_expand_public_catalogue():
    for target in ['/industries/banking?lens=inspection&selected=nationwide', '/enterprises/lloyds?lens=inspection&stream=forces']:
        assert owner_inspection_request_target(target) and not public_request_target(target)
    assert not public_request_target('/industries/banking?analysis=fi-f1-'+'a'*32)


def test_research_and_editorial_modes_do_not_leak_between_concurrent_or_failed_renders():
    from concurrent.futures import ThreadPoolExecutor
    fact=panels._facts(v.current_data(v.Context('banking','landscape')),['UK-RATE-NOV26'])[0]
    def core():
        with semantics.editorial_view(): return semantics.render(fact)
    def research():return semantics.render(fact)
    with ThreadPoolExecutor()as pool:
        a,b=pool.submit(core),pool.submit(research)
        assert '<details'not in a.result() and '<details'in b.result()
    with pytest.raises(ValueError):
        with semantics.editorial_view():raise ValueError('isolated render failure')
    assert '<details'in research()


def test_clean_financial_stock_view_preserves_both_dates_and_kind():
    bundle=f._current_inputs('boe-household-deposit-stocks')
    projection=f.current_projection(f._run_record('boe-household-deposit-stocks',bundle,'test-only-no-write'))
    html=analyst.compose_editorial(projection)
    assert '31 May 2026'in html and '30 Jun 2026'in html
    assert 'Published balances'in html and 'member value'not in html
    assert '£1,884.726bn'in html and '£1,886.281bn'in html
    assert '£1.555bn'in html and '0.0825%'in html


@pytest.mark.parametrize('key,qualifier',[
    ('economic','Preliminary estimate; subject to revision.'),
    ('environmental','First reporting is in 2028.'),
    ('legal','Parliamentary approval was not established'),
    ('LBG-ENVOY-CONTROLS','independent effectiveness is not established here')])
def test_material_force_qualifications_remain_in_editorial_copy(key,qualifier):
    fact=panels._facts(v.current_data(v.Context('banking','landscape')),['UK-RATE-NOV26'])[0]
    with semantics.editorial_view():
        html=semantics.render(semantics.editorial_force(fact,key))
    assert qualifier in html and '<details'not in html


def test_estimate_dependencies_remain_visible_without_research_controls():
    fact=panels._facts(v.current_data(v.Context('banking','landscape')),['UK-RATE-NOV26'])[0]
    insight=replace(fact,semantic_type='insight',reasoning='Test interpretation',
        dependencies=('Test input',),dependency_types=('assumed',),counter_evidence=('Test contrary evidence',))
    with semantics.editorial_view():html=semantics.render(insight)
    assert 'FLORA Insight'in html and 'Based on estimates or working assumptions.'in html
    assert '<details'not in html


def test_generic_bridge_preserves_scale_and_weaker_semantics():
    from tests.fixtures.financial_analyst import example,reference
    from decimal import Decimal
    projection=example('mutual-bridge')
    rows=[]
    for i,raw in enumerate(projection['measurements']):
        m=f.Measurement.model_validate(raw)
        value=m.value.model_copy(update={'amount':m.value.amount/Decimal(1000),'scale':'billions'})
        update={'value':value}
        if i==1:update.update(semantic_type='assumed',assumption_owner='test-only',assumption_version='v1')
        rows.append(m.model_copy(update=update))
    spec=f.Reconciliation(derivation_id='test-only-scaled',opening=reference(rows[0]),
        adjustments=tuple(map(reference,rows[1:-1])),endpoint=reference(rows[-1]),
        opening_basis='underlying',adjustment_basis='disclosed_bridge',endpoint_basis='statutory')
    projection['measurements']=[m.model_dump(mode='json')for m in rows]
    projection['results']=[f.reconcile(spec,rows)]
    html=analyst.compose_editorial(projection)
    assert '£0.3bn'in html and '£0.08bn'in html and '£0.2bn'in html
    assert 'data-semantic-type="estimated"'in html and '>Estimated</span>'in html
    assert 'Member rewards and integration'not in html and '<details'not in html


@pytest.mark.parametrize('key,tokens',[
    ('cyber',('43%','69%')),('provider',('Four named',)),('service',('118,861','66.12%'))])
@pytest.mark.parametrize('mutation',['rights','private','withdrawn','source_host'])
def test_ordinary_editorial_does_not_bypass_existing_eai_source_restrictions(key,tokens,mutation,tmp_path,monkeypatch):
    from tests.test_flora_eai2_integration import changed_release,KEYS
    changed_release(key,mutation,tmp_path,monkeypatch)
    scope,agenda_key=KEYS[key]
    body=main(v.render(v.SCOPES[scope]['route'],{'agenda':[agenda_key]}))
    assert all(token not in body for token in tokens)
    assert '<details'not in body
