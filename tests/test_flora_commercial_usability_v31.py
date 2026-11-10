"""Issue #554: usability without promoting free-text claims into verified demand."""
from copy import deepcopy
from html import unescape
import pytest
from cios.applications.flora import sales_pipeline as sales
from cios.applications.flora.research_intelligence import model
from cios.applications.flora.research_intelligence.commercial_views import candidate_overview
from cios.applications.flora.research_intelligence.living_map import render_living_map
from cios.applications.flora.research_intelligence.living_map_specs import build_living_map
from cios.applications.flora.research_intelligence.commercial_intelligence import commercial_map
from tests.test_flora_commercial_visual_v3 import projection,store_hash,ORIGIN,CORE
from tests.test_flora_sales_pipeline import actor,web,complete
from tests.test_flora_security_repair_01b import authority


@pytest.mark.parametrize('domain,total',[('banking',9),('aviation',6)])
def test_optional_summary_preserves_ids_mapped_activities_and_source_maturity(domain,total):
    p=projection(domain);s=commercial_map(build_living_map(model.load_assessment(domain)),p)
    h=unescape(render_living_map(s,'commercial'));summary=h.split("class='lm-commercial-summary'",1)[1].split('</details>',1)[0]
    assert not summary.startswith(' open')
    assert summary.count("role='listitem'")==total
    for r in p['candidates']:assert r['url'] in summary and r['title'] in summary
    assert 'focus map' in summary and 'data-lm-from-list' in summary
    assert 'Source-supported context' in summary and 'not additive' in summary
    assert 'activate(a.dataset.lmTarget,!list)' in h


def test_empty_and_unsupported_summary_never_invents_support():
    p=projection();p['candidates']=[]
    s=commercial_map(build_living_map(model.load_assessment()),p)
    assert 'No mapped commercial hypotheses' in render_living_map(s,'commercial')
    p=projection()
    for row in p['candidates']:row['context_supported']=False
    h=render_living_map(commercial_map(s,p),'commercial')
    summary=h.split("class='lm-commercial-summary'",1)[1].split('</details>',1)[0]
    assert 'Current source support missing / unverified' in summary
    assert 'Source-supported context' not in summary


@pytest.mark.parametrize('domain',['banking','aviation'])
def test_executive_summary_and_progressive_investigation_keep_counterevidence_visible(domain):
    p=projection(domain);r=p['candidates'][0];h=unescape(candidate_overview(model.load_assessment(domain),r,p))
    summary=h.split("aria-label='Executive hypothesis summary'",1)[1].split('</section>',1)[0]
    for label in ('Problem','Why now','Potential service','Evidence state','Buyer access','Next action'):assert '<dt>'+label+'</dt>' in summary
    assert '#commercial-counterevidence' in summary
    assert 'Customer budget: Unknown' in summary
    assert "<details class='cv-investigation'>" in h
    counter=h.split("id='commercial-counterevidence'",1)[1].split('</section>',1)[0]
    for p in r['counterevidence']:assert p['id'] in counter
    if r['conflicts']:assert 'Conflicting findings' in summary
    assert h.index('</details><section')<h.index("id='commercial-counterevidence'")


@pytest.mark.parametrize('stage',sales.STAGES)
def test_stage_or_forged_references_cannot_establish_customer_or_pursuit_validation(stage):
    r={'stage':stage,'qualification':complete(),'evidence_reviewed':True,
       'customer_validated':True,'pursuit_qualified':True,'evidence_maturity':'verified'}
    before=deepcopy(r);state=sales.evidence_maturity(r)
    assert state['research']=='Research-qualified · internal review only'
    assert state['customer']=='Customer-validated · not established'
    assert state['pursuit']=='Pursuit-qualified · not established'
    assert 'not independent verification' in state['limitation'] and r==before


def test_internal_research_readiness_requires_all_inputs_and_boolean_review():
    r={'stage':'Discovered','qualification':complete(),'evidence_reviewed':True}
    assert sales.evidence_maturity(r)['research'].startswith('Research-qualified')
    for key in ('buyer','funding','problem'):
        missing=deepcopy(r);missing['qualification'][key]['source']='Unknown'
        assert sales.evidence_maturity(missing)['research'].startswith('Research hypothesis')
    r['evidence_reviewed']='yes'
    assert sales.evidence_maturity(r)['research'].startswith('Research hypothesis')
    assert sales.evidence_maturity({'stage':'Qualified'})['customer'].endswith('not established')


@pytest.mark.parametrize('forged',['evidence_maturity','customer_validated','pursuit_qualified'])
def test_maturity_cannot_be_posted_or_written_directly_and_denial_keeps_hash(web,actor,forged):
    r=sales.create_opportunity('lloyds',ORIGIN,headers=actor[3]);before=store_hash()
    with pytest.raises(sales.SalesValidationError):sales.update_opportunity(r['id'],r['version'],{forged:'verified'},headers=actor[3])
    assert web('/flora/sales/'+r['id']+'/save',{'version':r['version'],forged:'verified'})[0]==422
    assert store_hash()==before


def test_research_readiness_does_not_advance_stage_or_rewrite_provenance(actor):
    r=sales.create_opportunity('lloyds',ORIGIN,headers=actor[3]);provenance=deepcopy(r['provenance'])
    r=sales.update_opportunity(r['id'],r['version'],{'qualification':complete(),'evidence_reviewed':'yes'},headers=actor[3])
    assert sales.evidence_maturity(r)['research'].startswith('Research-qualified')
    assert r['stage']=='Discovered' and r['provenance']==provenance and r['amount']==''
    assert sales.create_opportunity('lloyds',ORIGIN,headers=actor[3])==r


def test_saved_evidence_status_does_not_use_rejected_unsaved_fields(web,actor):
    r=sales.create_opportunity('lloyds',ORIGIN,headers=actor[3]);before=store_hash()
    fields={'version':r['version'],'stage':'Qualified','confirm':'yes','evidence_reviewed':'yes','q_problem':'Forged input','s_problem':'Unverified label'}
    status,h,_=web('/flora/sales/'+r['id']+'/save',fields)
    assert status==422 and store_hash()==before
    assert 'Research hypothesis · inputs incomplete or unreviewed' in unescape(h)
    assert 'Based on the saved record' in h


def test_pipeline_register_compact_fields_filters_and_empty_state(web,actor):
    assert 'Your pipeline is empty' in web('/flora/sales/pipeline')[1]
    r=sales.create_opportunity('lloyds',ORIGIN,headers=actor[3])
    status,h,_=web('/flora/sales/pipeline');assert status==200
    assert "class='sales-compact'" in h and 'Turn insight into<br>' not in h
    assert 'Pipeline stage: Discovered' in h and '<strong>Value:</strong> Unknown' in h
    assert 'Owner '+r['owner'] in h and 'Next action:' in h and 'Updated ' in h and 'Last activity:' in h and 'Unknown' in h
    assert "class='sales-filters' >" in h
    assert "class='sales-filters' open>" in web('/flora/sales/pipeline?stage=Discovered')[1]
    assert r['id'] in web('/flora/sales/pipeline?view=board')[1]
    assert 'Demonstration commercial workspace' in h and 'Customer validation: not established' in h


def test_public_summary_does_not_lookup_private_records(web,actor,monkeypatch):
    r=sales.create_opportunity('lloyds',ORIGIN,headers=actor[3]);before=store_hash()
    def forbidden(*a,**k):raise AssertionError('Public page attempted private lookup')
    monkeypatch.setattr(sales,'list_opportunities',forbidden);monkeypatch.setattr(sales,'get_opportunity',forbidden)
    for path in ('/industries/banking?lens=commercial','/flora/banking/research/candidates/'+ORIGIN):
        status,h,_=web(path,authenticated=False);assert status==200 and r['id'] not in h
    assert store_hash()==before
