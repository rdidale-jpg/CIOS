"""BIE-3 admission/model-boundary negatives and selected legal-bank views."""
from copy import deepcopy
from dataclasses import replace
from datetime import date
from pathlib import Path
import hashlib,inspect,json,os,subprocess,sys,types
import pytest
from cios.applications.flora import leadership_agenda as a,visual_streams as v,intelligence_presentation as p
from cios.applications.flora.research_intelligence import registry,model
from cios.applications.flora.memory.models import Observation
from tools.research import bie3_quality as q,history_integrity as h
from tests.test_flora_eai2_integration import changed_release
from tests.test_flora_sales_pipeline import actor,web
from tests.test_flora_security_repair_01b import authority,signed

ROOT=q.ROOT;BASE='c295e056cbae0f1adebc1070eb272d79b650a45f'

def test_standalone_research_cli_works_without_pythonpath_from_another_directory(tmp_path):
    env=dict(os.environ);env.pop('PYTHONPATH',None)
    result=subprocess.run([sys.executable,str(ROOT/'tools/research/bie3_quality.py')],cwd=tmp_path,env=env,
                          capture_output=True,text=True,check=True)
    assert json.loads(result.stdout)['new_canonical_imports']==0

def test_exact_four_state_inventory_and_unbound_existing_contracts():
    pack=q.load();assert q.validate(pack)=={'reviewed_sources':10,'source_verified_research_proposals':24,'new_permitted_runtime_claims':7,'reused_public_received_claims':2,'differentiated_commercial_cases':3,'new_canonical_approvals':0,'new_canonical_imports':0,'real_canonical_receipt_status':'UNVERIFIED'}
    report=q.admission_report(pack);assert len(report['rows'])==31
    assert all(r['canonical_owner_accepted']=='UNVERIFIED'for r in report['rows'])
    assert sum(r['visible_runtime']for r in report['rows'])==7
    assert all('canonical_enterprise_id'in r['factual_binding_result']for r in report['rows']if r['claim_id'].startswith(('BIE3-NW-','BIE3-HS-','BIE3-SA-')))
    assert sum(not r['source_type_foundation_compatible']for r in report['rows']if 'source_type_foundation_compatible'in r)==4
    assert report==json.loads((q.PACK/'Acceptance-Inventory.json').read_text())
    assert q.compatibility(pack)==json.loads((q.PACK/'Owner-Mapping-Compatibility.json').read_text())

def test_compatibility_probes_never_construct_observations_or_write_canonical_state(monkeypatch):
    def deny(*args,**kwargs):raise AssertionError('Forbidden canonical operation in review QA')
    from cios.applications.flora.blueprint_import.review import CandidateReviewService
    from cios.applications.flora.blueprint_import.mapping import ImportMappingService
    from cios.applications.flora import storage
    monkeypatch.setattr(Observation,'__post_init__',deny)
    monkeypatch.setattr(CandidateReviewService,'record_decision',deny)
    monkeypatch.setattr(ImportMappingService,'record_mapping',deny)
    monkeypatch.setattr(storage,'atomic_write_json',deny)
    assert q.validate(q.load())['new_canonical_imports']==0

@pytest.mark.parametrize('mutation',['source_url','source_archive','future_publication','canonical_id','evidence_id','owner_accept','visible_research','wrong_actor','wrong_currency','wrong_period','wrong_unit','wrong_sign','wrong_metric_basis','conflate_deposits','duplicate_subject','planned_effective_date','tsb_nine_months','tsb_bank_join','speculation','wrong_basis','wrong_measurement_state','wrong_financial_cell_value'])
def test_research_contract_rejects_bad_entity_period_basis_rights_authority_and_financial_joins(mutation):
    pack=q.load();claims=pack['Claim-Proposals'];by={c['id']:c for c in claims}
    if mutation=='source_url':pack['Source-Review'][0]['url']='https://www.fca.org.uk/data/pretend-natwest-issuer-report'
    elif mutation=='source_archive':pack['Source-Review'][0]['original_bytes_sha256']='0'*64
    elif mutation=='future_publication':pack['Source-Review'][0]['publication_date']='2027-01-01'
    elif mutation=='canonical_id':claims[0]['canonical_target_id']='guessed-target'
    elif mutation=='evidence_id':claims[0]['canonical_evidence_id']='forged-accepted'
    elif mutation=='owner_accept':claims[0]['owner_decision']['selected']='accept'
    elif mutation=='visible_research':claims[0]['states']['visible_runtime']=True
    elif mutation=='wrong_actor':claims[0]['actor_ref']='actor:natwest'
    elif mutation=='wrong_currency':by['BIE3-HS-REV']['currency']='GBP'
    elif mutation=='wrong_period':by['BIE3-HS-REV']['reporting_period']='Quarter ended30 September2026'
    elif mutation=='wrong_unit':by['BIE3-HS-REV']['unit']='billion'
    elif mutation=='wrong_sign':by['BIE3-HS-ECL']['reported_value']=701
    elif mutation=='wrong_metric_basis':by['BIE3-NW-CAL-OPEN']['proposed_attribute']='financial_performance.metrics.group.cal_headline.2025.actual'
    elif mutation=='conflate_deposits':by['BIE3-NW-DEPOSITS-TOTAL']['reported_value']='453.4'
    elif mutation=='duplicate_subject':claims[1]['proposed_attribute']=claims[0]['proposed_attribute']
    elif mutation=='planned_effective_date':by['BIE3-SA-PARTVII']['effective_date']='2027-01-01'
    elif mutation=='tsb_nine_months':by['BIE3-SA-TSB-PBT']['period_start']='2026-01-01'
    elif mutation=='tsb_bank_join':by['BIE3-SA-TSB-PBT']['actor_ref']='actor:tsb'
    elif mutation=='speculation':claims[0]['statement']='NatWest Group may need a new supplier.'
    elif mutation=='wrong_basis':by['BIE3-HS-REV']['accounting_basis']='Constant currency HSBC Holdings Group'
    elif mutation=='wrong_measurement_state':by['BIE3-HS-REV']['measurement_state']='target'
    elif mutation=='wrong_financial_cell_value':by['BIE3-NW-PBT']['reported_value']=6544
    with pytest.raises((AssertionError,ValueError)):q.validate(pack)

def test_collection_or_semantic_labels_do_not_grant_issuer_admission():
    pack=q.load()
    for s in pack['Source-Review']:
        s['enabled']=True;s['technical_publisher_admitted']=True;s['rights_review']='permitted'
    rows=q.admission_report(pack)['rows'][:24]
    assert all(not r['technical_host_admitted']and not r['source_permitted']and not r['visible_runtime']for r in rows)

@pytest.mark.parametrize('selected,values',[('natwest',[92548,101586,55.31]),('hsbc-uk',[79323,76912,59.09]),('santander-uk',[61365,60615,48.06])])
@pytest.mark.parametrize('stream',['landscape','forces'])
def test_selected_bank_uses_same_existing_concern_and_exact_legal_entity(selected,values,stream):
    data=model.load_assessment();before=deepcopy(data);rows=a.agenda('banking',data,selected=selected)
    assert data==before and len(rows)==len({r.key for r in rows})==4
    row=next(r for r in rows if r.key=='service-landscape')
    assert row.title==a.BANK_SERVICE[selected][0]+': complaint activity and resolution'
    assert [float(f.value)for f in row.facts]==values
    assert all(f.scope==a.BANK_SERVICE[selected][1]and f.period=='1 January–30 June 2026'and f.semantic_type=='reported'for f in row.facts)
    html=v.render('/industries/banking',{'stream':[stream],'selected':[selected],'agenda':['service-landscape']})
    assert 'different cohorts, not a service-quality ranking or backlog measure'in html
    assert html.count('data-region=')==3 and html.count('<h1')==1
    assert html.count('aria-label="Bank complaint profiles"')==1
    assert 'source_type_foundation_compatible'not in html and 'BIE3-NW-PBT'not in html

@pytest.mark.parametrize('mutation',['rights','malformed_rights','private','stale','withdrawn','retracted','contradiction','package_private','wrong_subject','canonical_mutation','source_host','missing'])
def test_denied_new_release_omits_selected_outcomes_and_selectors_preserving_bie2(mutation,tmp_path,monkeypatch):
    for key,(domain,name,*_)in a.EAI_RELEASES.items():
        if domain=='banking'and key!='bank-outcomes':(tmp_path/name).write_bytes((registry.snapshot_boundary(domain)/name).read_bytes())
    changed_release('bank-outcomes',mutation,tmp_path,monkeypatch)
    for selected in a.BANK_SERVICE:
        html=v.render('/industries/banking',{'selected':[selected],'agenda':['service-landscape']})
        assert 'Bank complaint profiles'not in html
        assert '55.31%'not in html and '59.09%'not in html and '48.06%'not in html
        assert '90,678'in html and '92,548'in html and '79,323'in html

@pytest.mark.parametrize('field,value',[('entity_scope','NatWest Group plc'),('metric_unit','percent of received complaints'),('reporting_period','1 July–30 September2026'),('canonical_acceptance','accepted'),('metric_value',999)])
def test_wrong_semantics_cannot_be_reintroduced_even_if_release_fingerprint_is_updated(field,value,tmp_path,monkeypatch):
    for key,(domain,name,*_)in a.EAI_RELEASES.items():
        if domain=='banking':(tmp_path/name).write_bytes((registry.snapshot_boundary(domain)/name).read_bytes())
    pkg=json.loads((tmp_path/'BIE3-FCA-Outcomes-Candidate.json').read_text());pkg['claims'][2][field]=value
    (tmp_path/'BIE3-FCA-Outcomes-Candidate.json').write_text(json.dumps(pkg))
    pins=deepcopy(a._pins());pins['eai_releases']['bank-outcomes']=a.fingerprint(pkg);monkeypatch.setattr(a,'_pins',lambda:pins)
    original=registry.snapshot_boundary;monkeypatch.setattr(registry,'snapshot_boundary',lambda d,repo=None:tmp_path if d=='banking'and repo is None else original(d,repo))
    assert a.bank_service_issue('natwest',model.load_assessment())is None

def test_duplicate_claim_identity_never_becomes_another_source_or_issue(tmp_path,monkeypatch):
    pkg=deepcopy(a._eai_release('bank-outcomes'));pkg['claims'].append(deepcopy(pkg['claims'][0]))
    for key,(domain,name,*_)in a.EAI_RELEASES.items():
        if domain=='banking':(tmp_path/name).write_bytes((registry.snapshot_boundary(domain)/name).read_bytes())
    (tmp_path/'BIE3-FCA-Outcomes-Candidate.json').write_text(json.dumps(pkg));pins=deepcopy(a._pins());pins['eai_releases']['bank-outcomes']=a.fingerprint(pkg);monkeypatch.setattr(a,'_pins',lambda:pins)
    original=registry.snapshot_boundary;monkeypatch.setattr(registry,'snapshot_boundary',lambda d,repo=None:tmp_path if d=='banking'and repo is None else original(d,repo))
    assert a.bank_service_issue('hsbc-uk',model.load_assessment())is None

@pytest.mark.parametrize('selected',a.BANK_SERVICE)
@pytest.mark.parametrize('field,value',[('scope','Foreign Group'),('period','Quarter ended30 September2026'),('unit','percent of received complaints'),('measurement_state','target')])
def test_service_composer_rejects_incompatible_owner_statements_independently_of_pins(selected,field,value,monkeypatch):
    data=model.load_assessment();facts=list(a.bank_service_issue(selected,data).facts)
    facts[1]=replace(facts[1],**{field:value});monkeypatch.setattr(a,'_claims',lambda *_:tuple(facts))
    assert a.bank_service_issue(selected,data)is None

def test_revoking_original_parent_source_removes_all_dependent_selected_views(tmp_path,monkeypatch):
    for key,(domain,name,*_)in a.EAI_RELEASES.items():
        if domain=='banking'and key!='peer-service':(tmp_path/name).write_bytes((registry.snapshot_boundary(domain)/name).read_bytes())
    changed_release('peer-service','rights',tmp_path,monkeypatch)
    for selected in a.BANK_SERVICE:
        html=v.render('/industries/banking',{'selected':[selected]})
        assert 'service-landscape'not in html and 'Bank complaint profiles'not in html

@pytest.mark.parametrize('field,value',[('owner_only',True),('freshness','stale'),('withdrawn',True),('core_contradiction',True)])
def test_whole_assessment_policy_still_controls_selected_profiles(field,value):
    d=deepcopy(model.load_assessment());d[field]=value
    assert all(a.agenda('banking',d,selected=bank)==()for bank in a.BANK_SERVICE)

def test_expired_review_excludes_runtime_but_does_not_claim_copyright_permission_expired(monkeypatch):
    class Later(date):
        @classmethod
        def today(cls):return cls(2026,12,16)
    monkeypatch.setattr(a,'date',Later)
    for bank in a.BANK_SERVICE:
        html=v.render('/industries/banking',{'selected':[bank]})
        assert 'Bank complaint profiles'not in html and '55.31%'not in html
    report=q.admission_report(q.load());public=report['rows'][24:]
    assert len(public)==7 and all(r['source_permitted']and not r['visible_runtime']for r in public)

def test_old_171_research_bytes_and_exact_comparator_preserved():
    source=subprocess.check_output(['git','show',BASE+':tools/research/history_integrity.py'],cwd=ROOT).decode();old=types.ModuleType('bie3_previous_history');exec(compile(source,'base_history','exec'),old.__dict__)
    before=old.approved_history(ROOT);after=h.approved_history(ROOT)
    assert len(before)==171 and len(after)==175 and {k:after[k]for k in before}==before
    assert set(after)-set(before)==set(h.BIE3_CANDIDATE_ADDITIONS) | set(h.F1_CANDIDATE_ADDITIONS)
    section=source.split('def compare_history(',1)[1].split('\n\ndef verify_history',1)[0]
    assert inspect.getsource(h.compare_history).split('def compare_history(',1)[1].strip()==section.strip()
    for path in h.BIE3_CANDIDATE_ADDITIONS:
        changed=deepcopy(after);changed[path]+=b'unapproved'
        with pytest.raises(AssertionError):h.compare_history(after,changed)
    changed=deepcopy(after);changed['enterprise-knowledge/banking/UNREVIEWED-BIE3.json']=b'{}'
    with pytest.raises(AssertionError):h.compare_history(after,changed)

def test_historical_bie2_pack_owners_and_unexecuted_decisions_unchanged():
    for name in ('Preserved-Owners','Preserved-BIE2-Pack'):
        manifest=json.loads((q.PACK/(name+'.json')).read_text());assert manifest['base']==BASE
        for path,sha in manifest['files'].items():
            content=(ROOT/path).read_bytes();assert hashlib.sha256(content).hexdigest()==sha
            assert content==subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
    for path in ['docs/flora-runtime/eai1-628/Eight-Evidence-Review-Proposals.json','docs/flora-runtime/eai1-628/Eight-Evidence-Reviews.md','architecture/decisions/ADR-027-Document-Scoped-Publisher-Admission-Proposal.md']:
        assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)

@pytest.mark.parametrize('target',['/docs/flora-runtime/bie3/Claim-Proposals.json','/docs/flora-runtime/bie3/Acceptance-Inventory.json','/visual-streams/assets/BIE3-FCA-Outcomes-Candidate','/industries/banking?selected=natwest&workspace=foreign','/industries/banking?selected=natwest&export=all','/enterprises/lloyds?selected=natwest','/?selected=natwest'])
def test_owner_review_pack_and_foreign_contexts_have_no_public_route(target,actor,web):
    assert web(target,authenticated=False)[0]in {403,404}
