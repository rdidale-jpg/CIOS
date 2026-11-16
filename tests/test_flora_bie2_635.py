"""BIE-2 source/entity/temporal negatives and existing-owner read-only pilot."""
from copy import deepcopy
from dataclasses import replace
from datetime import date
import hashlib,inspect,json,subprocess,types
from pathlib import Path
import pytest
from cios.applications.flora import leadership_agenda as a,visual_streams as v,intelligence_presentation as p
from cios.applications.flora.research_intelligence import model,registry
from tools.research import bie2_quality as q,history_integrity as h
from tests.test_flora_eai2_integration import changed_release
from tests.test_flora_sales_pipeline import actor,web
from tests.test_flora_security_repair_01b import authority,signed

ROOT=q.ROOT;BASE='b5b05f841bc6f17f5ffe3286a65e8745e7c79ec3'

def test_reproducible_candidate_quality_and_honest_coverage():
    result=q.validate(q.load())
    assert result=={'sources':34,'actors':76,'deep_dossiers':6,'relationship_candidates':31,'event_records':17,'current_window_publications':10,'prior_90_day_publications':3,'runtime_source_releases':1,'canonical_imports':0,'source_bytes_archived':0}
    actors=q.load()['Actor-Register']['actors']
    assert sum(x['coverage_tier']=='identity_only'for x in actors)==25

@pytest.mark.parametrize('mutation',['source_id','canonical','hash','future','metric','currency','consolidation','group_on_bank','wrong_metric_entity','relationship','contract','announcement_as_start','revolut_join','nt_join','dedup','publication_date','event_window','news_admitted','issuer_admitted'])
def test_candidate_corpus_rejects_invalid_authority_identity_financial_or_temporal_joins(mutation):
    pack=q.load();ds=pack['Enterprise-Dossiers'];events=pack['News-Candidates']['events'];edges=pack['Relationship-Candidates']['edges']
    if mutation=='source_id':ds[0]['source_ids']=['nonexistent']
    elif mutation=='canonical':ds[0]['canonical_id']='accepted-fake'
    elif mutation=='hash':pack['Source-Ledger'][0]['original_bytes_sha256']='0'*64
    elif mutation=='future':pack['Source-Ledger'][0]['publication_date']='2027-01-01'
    elif mutation=='metric':next(m for m in ds[1]['metrics']if m['name']=='Profit before tax')['value']=6085
    elif mutation=='currency':ds[1]['currency']='GBP'
    elif mutation=='consolidation':ds[2]['period']='all nine months include TSB'
    elif mutation=='group_on_bank':ds[0]['actor_id']='actor:natwest'
    elif mutation=='wrong_metric_entity':ds[5]['metrics'][0]['subject_actor_id']='actor:clear-group'
    elif mutation=='relationship':edges[0]['object']='actor:invented'
    elif mutation=='contract':edges[0]['contract_value']=100000000
    elif mutation=='announcement_as_start':edges[12]['effective_date']='2026-10-14'
    elif mutation=='revolut_join':edges[0]['object']='actor:revolut-uk'
    elif mutation=='nt_join':edges[0].update(subject='actor:nt',object='actor:barclays-uk')
    elif mutation=='dedup':events.append(deepcopy(events[0]))
    elif mutation=='publication_date':events[0]['publication_date']='2026-08-01'
    elif mutation=='event_window':events[7]['event_window']='current_literal_window'
    elif mutation=='news_admitted':events[0]['production_news_eligible']=True
    elif mutation=='issuer_admitted':pack['Admission-and-Integration']['items'][3]['visible_in_runtime']=True
    with pytest.raises(AssertionError):q.validate(pack)

def test_existing_contract_disposable_composition_and_exact_legal_facts():
    before=model.load_assessment();copy=deepcopy(before);data=a._eai_bank_data(before,'peer-service');model.validate(data)
    assert before==copy and len(data['claims'])==len(before['claims'])+3
    release=a._eai_release('peer-service');assert release and not release['canonical_mutation']
    assert release['source']['primary_content_sha256']is None
    assert sum(len(e['quote'].split())for e in release['source']['excerpts'])<=25
    assert [c['metric_value']for c in release['claims']]==[90678,79323,92548]
    assert all(c['canonical_acceptance']=='not_accepted'for c in release['claims'])
    assert all(model.primary_claim_supported(data,c)for c in release['claims'])
    row=next(r for r in a.agenda('banking')if r.key=='service-landscape')
    assert len(row.facts)==3 and len({f.scope for f in row.facts})==3
    assert row.conclusion.semantic_type=='insight'
    assert all(f.semantic_type=='reported'for f in row.facts)
    assert 'not a customer-harm rate'in row.facts[0].caveats[0]

@pytest.mark.parametrize('mutation',['rights','malformed_rights','private','stale','withdrawn','retracted','contradiction','package_private','wrong_subject','canonical_mutation','source_host','missing'])
def test_revocation_private_expiry_rights_and_scope_fail_closed_without_erasing_other_agendas(mutation,tmp_path,monkeypatch):
    # Redirect only the reviewed release; retain other fixed Banking packages.
    for key in ('provider','service'):
        domain,name,*_=a.EAI_RELEASES[key]
        (tmp_path/name).write_bytes((registry.snapshot_boundary(domain)/name).read_bytes())
    changed_release('peer-service',mutation,tmp_path,monkeypatch)
    html=v.render('/industries/banking',{})
    assert 'service-landscape'not in html and '90,678'not in html and '79,323'not in html
    assert 'provider-oversight'in html and 'funding-economics'in html
    assert 'data-region="main"'in html

@pytest.mark.parametrize('field,value',[('owner_only',True),('freshness','stale'),('retracted',True),('core_contradiction',True)])
def test_existing_assessment_denial_controls_new_peer_projection(field,value):
    data=deepcopy(model.load_assessment());data[field]=value
    assert a.agenda('banking',data)==()

@pytest.mark.parametrize('scope,stream',[(s,t)for s,b in v.SCOPES.items()for t in b['streams']])
def test_old_nine_keys_all_addresses_and_context_preserved(scope,stream):
    ctx=v.Context(scope,stream);html=v.render(v.SCOPES[scope]['route'],{'stream':[stream]})
    old={'uk':{'growth-mix','public-value','cyber-resilience'},'banking':{'funding-economics','reporting-change','provider-oversight'},'lloyds':{'service-recovery','ai-benefits','funding-base'}}
    keys={r.key for r in a.agenda(scope)}
    assert keys==old[scope]|({'service-landscape'}if scope=='banking'else set())
    assert html.count('data-region=')==3 and html.count('<h1')==1
    for d in v.destinations(ctx,v.current_data(ctx)):
        if d['href']:assert d['href'].replace('&','&amp;')in html
    assert 'Banking-Corpus'not in html and 'gap:'not in html

def test_all_169_previous_research_bytes_and_byte_comparator_unchanged():
    source=subprocess.check_output(['git','show',BASE+':tools/research/history_integrity.py'],cwd=ROOT).decode()
    old=types.ModuleType('bie2_base_history');exec(compile(source,'base_history','exec'),old.__dict__)
    previous=old.approved_history(ROOT);current=h.approved_history(ROOT)
    assert len(previous)==169 and len(current)==175
    assert {k:current[k]for k in previous}==previous
    assert set(current)-set(previous)==set(h.BIE2_CANDIDATE_ADDITIONS)|set(h.BIE3_CANDIDATE_ADDITIONS)|set(h.F1_CANDIDATE_ADDITIONS)
    original=source.split('def compare_history(',1)[1].split('\n\ndef verify_history',1)[0]
    assert inspect.getsource(h.compare_history).split('def compare_history(',1)[1].strip()==original.strip()
    for path in h.BIE2_CANDIDATE_ADDITIONS:
        changed=deepcopy(current);changed[path]+=b'unsafe'
        with pytest.raises(AssertionError):h.compare_history(current,changed)
    changed=deepcopy(current);changed['enterprise-knowledge/banking/UNREVIEWED.json']=b'{}'
    with pytest.raises(AssertionError):h.compare_history(current,changed)

def test_protected_owners_forms_and_proposed_adr_unchanged():
    manifest=json.loads((q.PACK/'Preserved-Owners.json').read_text())
    assert manifest['base']==BASE
    for path,sha in manifest['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
        assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
    for path in ['docs/flora-runtime/eai1-628/Eight-Evidence-Review-Proposals.json','docs/flora-runtime/eai1-628/Eight-Evidence-Reviews.md','architecture/decisions/ADR-027-Document-Scoped-Publisher-Admission-Proposal.md']:
        assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)

@pytest.mark.parametrize('target',['/docs/flora-runtime/bie2/Enterprise-Dossiers.json','/docs/flora-runtime/bie2/News-Candidates.json','/visual-streams/assets/BIE2-FCA-Peers-Candidate','/industries/banking?workspace=foreign&agenda=service-landscape','/enterprises/lloyds?agenda=service-landscape','/?agenda=service-landscape'])
def test_research_artifacts_and_foreign_contexts_not_public_routes(target,actor,web):
    assert web(target,authenticated=False)[0]in {403,404}
