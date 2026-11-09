"""Experience Repair 01: visible qualifications without accepting pilot scenarios."""
from html.parser import HTMLParser
import pytest
from cios.applications.flora import banking_portfolio as b
from cios.applications.flora.web import app
from cios.applications.flora.twin_inspection.views import twin_inspection_page
from cios.applications.flora.memory.repository import EvidenceRepository, ObservationRepository, EnterpriseModelRepository

HEADERS={'X-Flora-User':'alice','X-Flora-Enterprises':'*','X-Flora-Roles':'blueprint_import_admin','X-Flora-Active-Workspace':'workspace-a'}

class Visible(HTMLParser):
    def __init__(self):super().__init__();self.stack=[];self.parts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);hidden=bool(self.stack and self.stack[-1][1]) or tag in {'script','style','head'} or 'hidden' in a or a.get('aria-hidden')=='true' or 'display:none' in a.get('style','').replace(' ','')
        if tag not in {'br','hr','input','meta','link','img'}:self.stack.append((tag,hidden))
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:self.stack=self.stack[:i];break
    def handle_data(self,data):
        if not self.stack or not self.stack[-1][1]:self.parts.append(data)

def visible(html):
    p=Visible();p.feed(html);return ' '.join(' '.join(p.parts).split())

@pytest.fixture(autouse=True)
def isolate(tmp_path,monkeypatch):
    for key in ('FLORA_DATA_DIR','FLORA_PILOT_DIR'):monkeypatch.setenv(key,str(tmp_path/'data'))
    monkeypatch.setenv('FLORA_ENVIRONMENT','development');monkeypatch.setenv('FLORA_TRUST_PROXY_HEADERS','1')
    from cios.applications.flora.enterprise_intelligence import pipeline
    monkeypatch.setattr(pipeline.run_pipeline,'__defaults__',(tmp_path/'derived',None,None))


def test_barclays_estimate_exposes_formula_assumptions_and_unknown_decision_rights():
    html,status=b.opportunity_page('barclays','COH-BAR-001');text=visible(html)
    assert status==200 and '£60m–£120m' in text
    for claim in ['Illustrative, unverified commercial scenario','external-services sizing','£70m × category 0.95 × scope 1.25','Customer-confirmed budget: Unknown','Qualified commercial pipeline: Not established','Sponsor / buyer / funding / procurement / scope: Unknown','Enterprise economic value: Not calculated','claim-level source/effective/customer-confirmation dates: Unknown']:
        assert claim in text
    assert 'entering buying activity' not in text
    assert b.BANKS['barclays'].opportunities[0].value.midpoint==85


def test_scenario_timing_is_not_a_confirmed_buying_window():
    text=visible(b.opportunity_page('barclays','COH-BAR-001')[0])
    assert 'Scenario timing assumption' in text and '12–36 months' in text
    assert 'Confirmed procurement dates / customer milestones / buying triggers: Unknown' in text


def test_supplier_inference_keeps_basis_default_date_and_missing_evidence():
    text=visible(b.opportunity_page('barclays','COH-BAR-001')[0])
    for claim in ['Accenture','Inferred supplier position','2025-01-01','not a verified contract date','Major-bank transformation services market presence','Contract-specific accepted Evidence: Not supplied','renewal or displacement']:
        assert claim in text


def test_barclays_rollup_is_a_sum_of_scenarios_not_customer_budget():
    text=visible(b.bank_page('barclays')[0])
    assert '£205m' in text and '85 + 80 + 40' in text
    assert 'Illustrative, unverified commercial scenario' in text
    assert 'not customer-confirmed budget or qualified commercial pipeline' in text
    assert '£70m × category 0.95' in text


PAGES=[('landing',lambda:b.banking_landing_page()),('banks',lambda:b.banks_page()),('portfolio',lambda:b.portfolio_page()),('pipeline',lambda:b.pipeline_page()),('heatmap',lambda:b.heatmap_page()),('heatmap-detail',lambda:b.heatmap_detail_page('opportunity-value','Cost transformation','barclays')[0]),('compare',lambda:b.compare_page()),('competitors',lambda:b.competitors_page()[0]),('signals',lambda:b.industry_signal_explorer_page()),('outlook',lambda:b.industry_outlook_page()),('ai-native',lambda:b.ai_native_page()),('timeline',lambda:b.timeline_page()),('evidence',lambda:b.evidence_page('barclays')[0]),('events',lambda:b.enterprise_event_timeline_page('barclays'))]

@pytest.mark.parametrize('name,render',PAGES,ids=[x[0] for x in PAGES])
def test_every_executive_route_has_visible_source_and_assurance_scope(name,render):
    text=visible(render())
    assert 'Curated repository Banking pilot' in text
    assert 'not accepted canonical intelligence' in text
    assert '2026-07-19' in text
    assert 'not calibrated Evidence confidence' in text
    assert 'Scenario timing' in text and 'strategic working scenarios' in text
    assert 'Claim-level accepted Evidence: Not supplied by this pilot' in text


def test_signal_conviction_is_editorial_not_list_position_confidence():
    text=visible(b.banking_landing_page())
    assert 'Editorial conviction: High' in text and 'list position' in text
    assert 'not an enterprise-specific qualified Material Pressure' in text


def test_account_rank_and_native_horizons_are_scenarios():
    text=visible(b.bank_page('barclays')[0]+b.ai_native_page()+b.timeline_page())
    assert 'Working account priority' in text and 'strategic working scenarios' in text


def test_hash_and_generic_source_labels_do_not_become_evidence():
    text=visible(b.evidence_page('barclays')[0])
    assert 'Annual report 2024' in text
    assert 'view identity only' in text and 'does not prove claim-level provenance' in text
    assert 'canonical Evidence IDs / accepted Observation mappings / source locators: Not supplied' in text


def test_empty_estate_keeps_curated_pilot_without_governed_industry_claim():
    text=visible(app._flora_home_page(HEADERS))
    assert '1 curated Banking pilot' in text and '0 candidate imports' in text and '0 partial releases' in text
    assert '1 governed' not in text and 'One governed industry' not in text
    assert 'Complete Industry Twin acceptance: Not established' in text
    assert '/flora/banking' in app._flora_home_page(HEADERS)


def test_industry_inspection_is_repository_curated_not_owner_accepted():
    html,status=twin_inspection_page('uk-banking',HEADERS,'industry');text=visible(html)
    assert status==200 and 'Curated repository Banking pilot' in text
    assert 'Owner-backed runtime available' not in text and 'not calibrated Evidence confidence' in text


def test_scenario_views_do_not_accept_canonical_intelligence():
    before=(EvidenceRepository().list(),ObservationRepository().list(),EnterpriseModelRepository().get('barclays-plc').to_dict())
    for _,render in PAGES:render()
    b.opportunity_page('barclays','COH-BAR-001')
    assert EvidenceRepository().list()==before[0] and ObservationRepository().list()==before[1]
    model=EnterpriseModelRepository().get('barclays-plc');assert not model.attributes and not model.material_pressures


def test_home_import_counts_use_existing_visibility_identity_and_release_owners(monkeypatch):
    from cios.applications.flora.blueprint_import import BlueprintPackageRegistry,BlueprintPackageValidator
    from cios.applications.flora.blueprint_import.lifecycle import ImportLifecycleService,ImportLifecycle
    from tests.test_flora_factory_presentation_repair import receive
    package=receive()
    text=visible(app._flora_home_page(HEADERS));assert '1 candidate imports' in text and '0 partial releases' in text
    monkeypatch.setattr(ImportLifecycleService,'get',lambda self,run:ImportLifecycle(run,state='promoted',current=True,canonical_writes=1))
    text=visible(app._flora_home_page(HEADERS));assert '0 candidate imports' in text and '1 partial releases' in text
    assert 'Complete Industry Twin acceptance: Not established' in text
    from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository
    assert EnterpriseCanvasAccessRepository().list()==[]
    text=visible(app._flora_home_page({}));assert '0 candidate imports' in text and '0 partial releases' in text


def test_home_counts_do_not_expose_inaccessible_industry_imports(monkeypatch):
    from tests.test_flora_factory_presentation_repair import receive
    from cios.applications.flora import access
    receive()
    monkeypatch.setattr(access,'can_access_enterprise',lambda *a,**kw:False)
    text=visible(app._flora_home_page(HEADERS))
    assert '0 candidate imports' in text and '0 partial releases' in text


@pytest.mark.parametrize('state',['superseded','archived','cancelled','deleted'])
def test_home_excludes_terminal_industry_releases(monkeypatch,state):
    from tests.test_flora_factory_presentation_repair import receive
    from cios.applications.flora.blueprint_import.lifecycle import ImportLifecycleService,ImportLifecycle
    receive()
    monkeypatch.setattr(ImportLifecycleService,'get',lambda self,run:ImportLifecycle(run,state=state,current=False))
    text=visible(app._flora_home_page(HEADERS))
    assert '0 candidate imports' in text and '0 partial releases' in text


def test_unreadable_import_status_is_unavailable_not_a_false_zero(monkeypatch):
    from cios.applications.flora.blueprint_import import BlueprintPackageRegistry
    def corrupt(self):raise ValueError('isolated malformed metadata')
    monkeypatch.setattr(BlueprintPackageRegistry,'list',corrupt)
    text=visible(app._flora_home_page(HEADERS))
    assert 'Industry import status unavailable' in text
    assert '0 candidate imports' not in text

# Domain tests use an explicit fixture identity provider, never HTTP trust.
pytestmark = pytest.mark.usefixtures("verified_flora_test_authority")
