"""Persistent commercial vertical slice using real synthetic FLORA sessions."""
from copy import deepcopy
from html import escape
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import threading
from urllib.parse import urlencode

import pytest

from tests.test_flora_security_repair_01b import authority, signed
from cios.applications.flora import sales_pipeline as sales
from cios.applications.flora.banking_portfolio import BANKS
from cios.applications.flora.security_store import COOKIE, canonical
from cios.applications.flora.storage import data_path


@pytest.fixture
def actor(authority, tmp_path):
    store=authority[0]
    with store.transaction() as db:
        db.execute('UPDATE memberships SET enterprises=?', (canonical([BANKS['lloyds'].id,BANKS['barclays'].id]),))
    _,token,csrf,headers,_=signed(authority,tmp_path)
    return store,token,csrf,headers


@pytest.fixture
def web(actor):
    from cios.applications.flora.web.app import FloraWebHandler
    server=ThreadingHTTPServer(('127.0.0.1',0),FloraWebHandler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    def request(path, fields=None, authenticated=True):
        headers=dict(actor[3]) if authenticated else {}
        if fields is not None:
            headers.update({'Origin':'https://flora.test','Content-Type':'application/x-www-form-urlencoded'})
            fields=dict(fields);fields.setdefault('csrf',actor[2])
        conn=HTTPConnection('127.0.0.1',server.server_port)
        try:
            conn.request('GET' if fields is None else 'POST',path,None if fields is None else urlencode(fields),headers)
            response=conn.getresponse()
            request.last_headers=dict(response.getheaders())
            return response.status,response.read().decode(),response.getheader('Location')
        finally:conn.close()
    yield request
    server.shutdown();server.server_close();thread.join(2)


def capture(actor, slug='lloyds'):
    return sales.create_opportunity(slug,BANKS[slug].opportunities[0].id,headers=actor[3])


def complete():
    return {k:{'note':'Synthetic customer-reviewed '+label,'source':'DEMO-MEETING-001 / '+k} for k,(label,_) in sales.CRITERIA.items()}


def update(actor, record, **values):
    return sales.update_opportunity(record['id'],record['version'],values,headers=actor[3])


def test_capture_defaults_provenance_and_persistence(actor):
    r=capture(actor)
    assert r['stage']=='Discovered' and r['demonstration'] is True
    assert r['amount']=='' and r['confidence']=='Unknown'
    assert r['workspace_id']=='synthetic-workspace'
    assert r['provenance']['source_labels']==list(BANKS['lloyds'].analyst_sources)
    assert sales.get_opportunity(r['id'],headers=actor[3])==r
    assert json.loads(data_path('sales_pipeline','opportunities.json').read_text())['records'][r['id']]==r
    # Independent process: proves persistence is not a process-local projection.
    import os, subprocess, sys
    environment=dict(os.environ, SALES_TEST_HEADERS=json.dumps(actor[3]), SALES_TEST_ID=r['id'])
    output=subprocess.check_output([sys.executable,'-c',
        "import json,os; from cios.applications.flora.sales_pipeline import get_opportunity; print(json.dumps(get_opportunity(os.environ['SALES_TEST_ID'],headers=json.loads(os.environ['SALES_TEST_HEADERS']))))"],env=environment,text=True)
    assert json.loads(output)==r



def test_repeated_capture_is_idempotent(actor):
    a=capture(actor);b=capture(actor)
    assert a==b and len(sales.list_opportunities(headers=actor[3]))==1


def test_create_manual_hypothesis_and_edit_activity(actor):
    r=sales.create_opportunity('barclays',values={'title':'Demo service hypothesis','problem':'Unvalidated service friction'},headers=actor[3])
    r=update(actor,r,next_action='Arrange a discovery conversation',activity='Desk research completed',owner='Demo account lead')
    assert r['version']==2 and r['history'][-1]['changes']['activity']=='Desk research completed'
    assert r['history'][-1]['actor']=='synthetic-human'
    assert r['provenance']['kind']=='user_entered_demonstration'


def test_qualification_readiness_does_not_auto_promote(actor):
    r=update(actor,capture(actor),qualification=complete(),evidence_reviewed='yes')
    assert sales.qualification(r)['percent']==100
    assert r['stage']=='Discovered'
    assert sales.maturity(r)=='Evidence-backed potential opportunity'


def test_qualified_requires_complete_supported_inputs_review_and_confirmation(actor):
    r=capture(actor)
    for fields in [{'stage':'Qualified','confirm':'yes'},
                   {'qualification':complete(),'stage':'Qualified','confirm':'yes'},
                   {'qualification':complete(),'evidence_reviewed':'yes','stage':'Qualified'}]:
        with pytest.raises(sales.SalesValidationError):update(actor,r,**fields)
        assert sales.get_opportunity(r['id'],headers=actor[3])==r
    r=update(actor,r,qualification=complete(),evidence_reviewed='yes',stage='Qualified',confirm='yes')
    assert sales.maturity(r)=='Qualified sales opportunity'


def test_active_pursuit_requires_new_confirmation(actor):
    r=update(actor,capture(actor),qualification=complete(),evidence_reviewed='yes',stage='Qualified',confirm='yes')
    with pytest.raises(sales.SalesValidationError):update(actor,r,stage='Pursuit')
    r=update(actor,r,stage='Pursuit',confirm='yes',activity='Synthetic capture review accepted')
    assert sales.maturity(r)=='Active pursuit' and r['demonstration']


def test_cannot_remove_qualification_support_from_active_record(actor):
    r=update(actor,capture(actor),qualification=complete(),evidence_reviewed='yes',stage='Pursuit',confirm='yes')
    with pytest.raises(sales.SalesValidationError):update(actor,r,qualification={},evidence_reviewed='yes')
    assert sales.get_opportunity(r['id'],headers=actor[3])==r


def test_closure_requires_outcome_evidence_and_is_excluded_from_open_totals(actor):
    r=update(actor,capture(actor),value_basis='Estimate',amount='12000',value_reference='Demo assumption: discovery plus delivery')
    with pytest.raises(sales.SalesValidationError):update(actor,r,stage='Lost',confirm='yes')
    r=update(actor,r,stage='Lost',confirm='yes',closure_evidence='DEMO-OUTCOME-001: no budget')
    assert sales.totals([r])=={'amounts':{},'unknown':0,'closed':1}
    assert sales.maturity(r)=='Closed / Lost'
    with pytest.raises(sales.SalesValidationError):update(actor,r,stage='Researching')
    won=update(actor,capture(actor,'barclays'),qualification=complete(),evidence_reviewed='yes',stage='Won',confirm='yes',closure_evidence='DEMO-OUTCOME-002: synthetic customer outcome confirmation')
    assert won['demonstration'] and sales.maturity(won)=='Won — user-confirmed demonstration outcome'
    assert sales.totals([won])['closed']==1



def test_known_and_estimated_amounts_currency_and_unknown_totals(actor):
    a=update(actor,capture(actor),value_basis='Estimate',amount='100.10',value_reference='Demo scope assumption')
    b=update(actor,capture(actor,'barclays'),value_basis='Customer-confirmed amount',amount='200',value_reference='DEMO-CUSTOMER-001: explicit synthetic amount')
    c=deepcopy(a);c.update(currency='USD',amount='50')
    d=deepcopy(a);d.update(amount='',value_basis='Unknown')
    t=sales.totals([a,b,c,d])
    assert t['amounts']=={'GBP · Estimate':'100.10','GBP · Customer-confirmed amount':'200','USD · Estimate':'50'}
    assert t['unknown']==1


def test_money_inputs_reject_fabricated_or_unreferenced_values(actor):
    r=capture(actor)
    for fields in [{'amount':'1'}, {'amount':'100','value_basis':'Estimate'},
                   {'amount':'NaN','value_basis':'Estimate','value_reference':'Demo'},
                   {'amount':'-1','value_basis':'Estimate','value_reference':'Demo'},
                   {'amount':'1.001','value_basis':'Estimate','value_reference':'Demo'}]:
        with pytest.raises(sales.SalesValidationError):update(actor,r,**fields)


def test_pipeline_filters_and_priority(actor):
    a=update(actor,capture(actor),priority='High',confidence='Moderate',confidence_rationale='Demo supporting material assessed',owner='Alice',stage='Researching',amount='100',value_basis='Estimate',value_reference='Demo assumption')
    capture(actor,'barclays')
    for filters in [{'enterprise':a['enterprise']},{'industry':'Banking','stage':'Researching'},
                    {'owner':'Alice'},{'confidence':'Moderate'},{'min_value':'50','currency':'GBP','value_basis':'Estimate'}]:
        assert [r['id'] for r in sales.list_opportunities(headers=actor[3],filters=filters)]==[a['id']]
    assert sales.list_opportunities(headers=actor[3],filters={'industry':'Other'})==[]
    with pytest.raises(sales.SalesValidationError):sales.list_opportunities(headers=actor[3],filters={'min_value':'50'})


def test_stale_update_leaves_record_and_history_unchanged(actor):
    r=capture(actor);new=update(actor,r,title='New title')
    with pytest.raises(sales.SalesValidationError):update(actor,r,title='Stale title')
    assert sales.get_opportunity(r['id'],headers=actor[3])==new


def test_identity_and_source_scope_cannot_be_overridden(actor):
    r=capture(actor)
    for key in ['workspace_id','enterprise_id','demonstration','provenance','created_by']:
        with pytest.raises(sales.SalesValidationError):update(actor,r,**{key:'override'})
    assert sales.get_opportunity(r['id'],headers=actor[3])==r


def test_service_permission_and_workspace_boundaries(actor):
    r=capture(actor)
    with pytest.raises(PermissionError):sales.get_opportunity(r['id'],headers={'X-Flora-User':'synthetic-human'})
    with pytest.raises(PermissionError):sales.create_opportunity('hsbc-uk',BANKS['hsbc-uk'].opportunities[0].id,headers=actor[3])
    with actor[0].transaction() as db:
        db.execute('UPDATE memberships SET workspace_id=?',('other-workspace',))
        db.execute('UPDATE tokens SET workspace_id=?',('other-workspace',))
    assert sales.list_opportunities(headers=actor[3])==[]
    with pytest.raises(PermissionError):sales.get_opportunity(r['id'],headers=actor[3])


def test_revoked_membership_denies_mutation(actor):
    r=capture(actor)
    with actor[0].transaction() as db:db.execute('UPDATE memberships SET active=0,version=version+1')
    with pytest.raises(PermissionError):update(actor,r,title='Rejected')
    stored=json.loads(data_path('sales_pipeline','opportunities.json').read_text())['records'][r['id']]
    assert stored==r


def test_existing_enterprise_acl_is_still_effective(actor):
    from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository,EnterpriseCanvasAccessRecord
    EnterpriseCanvasAccessRepository().save(EnterpriseCanvasAccessRecord('1','canvas-demo',BANKS['lloyds'].id,'synthetic-workspace','other-owner'))
    with pytest.raises(PermissionError):capture(actor)


def test_audit_failure_rolls_back_record_and_history(actor,monkeypatch):
    r=capture(actor)
    old=actor[0].audit
    def audit(db,event,**values):
        if event=='sales_opportunity_mutation':raise OSError('Synthetic audit storage failure')
        return old(db,event,**values)
    monkeypatch.setattr(type(actor[0]),'audit',lambda self,db,event,**values:audit(db,event,**values))
    with pytest.raises(OSError):update(actor,r,title='Must roll back')
    assert sales.get_opportunity(r['id'],headers=actor[3])==r


def test_audit_tracks_workspace_actor_and_record_digest(actor):
    from cios.applications.flora.security_store import digest
    r=update(actor,capture(actor),activity='Synthetic engagement recorded')
    with actor[0].transaction() as db:
        entries=[json.loads(row[0]) for row in db.execute("SELECT payload FROM audit WHERE event='sales_opportunity_mutation' ORDER BY seq")]
    assert len(entries)==2 and entries[-1]['record_digest']==digest(canonical(r))
    assert entries[-1]['workspace_id']=='synthetic-workspace' and entries[-1]['session_ref']


def test_http_discovery_has_distinct_enterprise_landscapes_and_evidence(web):
    for slug in ['lloyds','barclays']:
        status,html,_=web(f'/flora/banking/explorer/{slug}/opportunities',authenticated=False)
        assert status==200 and BANKS[slug].name in html and '<svg' in html
        for o in BANKS[slug].opportunities:assert o.id in html
        status,html,_=web(f'/flora/banking/explorer/{slug}/opportunities/{BANKS[slug].opportunities[0].id}',authenticated=False)
        assert status==200 and 'Unknown' in html and 'Inspect supporting source context' in html


def test_http_capture_edit_qualification_pipeline_journey(web,actor):
    status,_,location=web('/flora/sales/capture',{'enterprise':'lloyds','origin':BANKS['lloyds'].opportunities[0].id})
    assert status==303 and location.endswith('#qualification')
    path=location.split('#')[0]
    status,html,_=web(path)
    assert status==200 and 'Missing information' in html and 'MEDDICC' in html and 'name="csrf"' in html
    assert web.last_headers['Referrer-Policy']=='same-origin'
    record=sales.get_opportunity(path.rsplit('/',1)[1],headers=actor[3])
    status,html,_=web(path+'/save',{'version':record['version'],'stage':'Qualified','confirm':'yes','q_problem':'Unsaved discovery note'})
    assert status==422 and 'all ten supported qualification inputs' in html
    assert 'Unsaved discovery note' in html and 'unsaved form has been restored' in html
    fields={'version':record['version'],'stage':'Qualified','confirm':'yes','evidence_reviewed':'yes','activity':'Synthetic qualification review'}
    for key,value in complete().items():fields['q_'+key]=value['note'];fields['s_'+key]=value['source']
    assert web(path+'/save',fields)[0]==303
    status,html,_=web('/flora/sales/pipeline?stage=Qualified&view=board')
    assert status==200 and 'Qualified sales opportunity' in html and 'Stage board' in html


def test_http_csrf_anonymous_and_scope_override_rejected(web,actor):
    fields={'enterprise':'lloyds','origin':BANKS['lloyds'].opportunities[0].id}
    assert web('/flora/sales/capture',fields,authenticated=False)[0]==403
    assert web('/flora/sales/capture',dict(fields,csrf='wrong'))[0]==403
    assert web('/flora/sales/capture',dict(fields,workspace_id='other'))[0]==422
    assert web('/flora/sales/pipeline',authenticated=False)[0]==403
    assert sales.list_opportunities(headers=actor[3])==[]


def test_display_text_is_escaped_and_missing_values_visible(actor):
    from cios.applications.flora.sales_views import record_page,pipeline_page
    r=update(actor,capture(actor),title='<script>bad</script>')
    html=record_page(r['id'],headers=actor[3])
    assert '<script>' not in html and escape(r['title']) in html
    assert 'Completeness is not win probability' in html and 'Missing information' in html
    assert 'unknown value' in pipeline_page(headers=actor[3])


def test_missing_capability_denies_reads_and_writes(actor):
    r=capture(actor)
    with actor[0].transaction() as db:db.execute('UPDATE memberships SET roles=?',(canonical(['commercial_context.view']),))
    assert len(sales.list_opportunities(headers=actor[3]))==1
    from cios.applications.flora.sales_views import record_page
    assert 'fieldset disabled' in record_page(r['id'],headers=actor[3])
    with pytest.raises(PermissionError):update(actor,r,title='Read-only role')
    with actor[0].transaction() as db:db.execute('UPDATE memberships SET roles=?',(canonical(['package.inspect']),))
    with pytest.raises(PermissionError):sales.list_opportunities(headers=actor[3])
    with pytest.raises(PermissionError):update(actor,r,title='No authority')


def test_unscoped_persisted_record_cannot_be_read_or_updated(actor):
    r=capture(actor)
    path=data_path('sales_pipeline','opportunities.json')
    document=json.loads(path.read_text());document['records'][r['id']].pop('workspace_id')
    path.write_text(json.dumps(document))
    with pytest.raises(PermissionError):sales.get_opportunity(r['id'],headers=actor[3])
    with pytest.raises(PermissionError):update(actor,r,title='No scope')
    assert sales.list_opportunities(headers=actor[3])==[]


def test_notes_without_supporting_references_cannot_qualify(actor):
    for placeholder in ['', 'Unknown', 'TBC', 'Not supplied']:
        q=complete();q['funding']['source']=placeholder
        with pytest.raises(sales.SalesValidationError):update(actor,capture(actor),qualification=q,evidence_reviewed='yes',stage='Qualified',confirm='yes')
