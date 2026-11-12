"""Controlled semantic support and publication boundaries, not accuracy certification."""
from copy import deepcopy
from datetime import datetime,timedelta,timezone
import hashlib,json
from pathlib import Path
import pytest
from cios.applications.flora.research_intelligence.foundation.sprint2.assurance import Meaning,Passage,Proposal,assess,extract,statement,origin_count,canonical_candidates
from cios.applications.flora.research_intelligence.foundation.sprint2.evaluation import evaluate
from cios.applications.flora.research_intelligence.foundation.sprint2.snapshot import assets
from cios.applications.flora.research_intelligence.foundation.sprint2.views import render
from cios.applications.flora.research_intelligence.foundation.views import render as programme
from cios.applications.flora.public_routes import public_request_target

ROOT=Path(__file__).resolve().parents[1]
EVAL=ROOT/'tests/fixtures/research-sprint2/held-out-v1.json'
CASES=json.loads(EVAL.read_text())['cases']

@pytest.mark.parametrize('case',CASES,ids=[c['id'] for c in CASES])
def test_frozen_heldout_support_rubric(case):
    r=assess(case['proposal'],case['passages'],as_of='2026-11-12',run_id='HELDOUT-TEST',verifier_id='fixture-verifier')
    assert r['outcome']==case['reference_outcome'],r
    if 'reference_source_family_count' in case:assert r['source_family_count']==case['reference_source_family_count']
    assert not r['canonical_promotion'] and not r['pipeline_qualification']


def test_evaluation_denominators_and_calibration_limits_are_explicit():
    r=evaluate(EVAL);recorded=json.loads((ROOT/'docs/flora-runtime/research-sprint2/Held-Out-Results.json').read_text())
    assert r==recorded and not r['mismatches'] and len(r['cases'])==35
    assert r['false_acceptance']=={'count':0,'denominator':30,'rate':0.0}
    assert r['false_rejection']=={'count':0,'denominator':5,'rate':0.0}
    assert r['unresolved']['count']==11 and r['unresolved']['denominator']==35
    assert 'not measured' in r['general_semantic_accuracy'] and 'no external blinded annotation' in r['calibration_limit']


def test_original_foundation_assets_and_all_prior_identities_are_preserved():
    import subprocess
    for path in (ROOT/'enterprise-knowledge/technology/research-foundation-v1').glob('*.json'):
        name=str(path.relative_to(ROOT))
        assert path.read_bytes()==subprocess.check_output(['git','show','b4a2c2c680d21bc252f3bc7e365c7eb08af178d3:'+name],cwd=ROOT)
    old=json.loads(subprocess.check_output(['git','show','b4a2c2c680d21bc252f3bc7e365c7eb08af178d3:tools/ci/flora-baseline-v1.json'],cwd=ROOT))
    new=json.loads((ROOT/'tools/ci/flora-baseline-v1.json').read_text())
    for profile,spec in old['profiles'].items():
        assert new['profiles'][profile]['security_modules']==spec['security_modules']
        for name,suite in spec['suites'].items():assert new['profiles'][profile]['suites'][name]==suite


def test_actual_source_pairs_support_only_bounded_historical_plan():
    d=assets()['Assurance-v1.json'];q=Proposal(**d['proposal']);ps=[Passage(**p) for p in d['passages']]
    result=assess(q,ps,as_of='2026-11-12',run_id='LIVE-PROOF-REPLAY',verifier_id='sprint2-independent-retrieval')
    assert result['outcome']=='accept_bounded' and result['source_family_count']==1
    assert q.meaning.modality=='planned' and q.meaning.reporting_period=='five-year plan (endpoints unspecified)'
    assert q.meaning.amount==8000000000 and q.period_use=='historical'
    assert all(p.execution_kind=='live_web_bridge' for p in ps)
    assert ps[0].tool_reference!=ps[1].tool_reference
    for check in d['counterfactual_support_checks']:assert check['decision']['outcome']=='reject'


def test_stale_live_plan_cannot_be_silently_relabelled_current():
    d=assets()['Assurance-v1.json'];q=deepcopy(d['proposal']);q['period_use']='current'
    r=assess(q,d['passages'],as_of='2026-11-12',run_id='CURRENT-CLAIM',verifier_id='sprint2-independent-retrieval')
    assert r['outcome']=='unresolved' and 'Stale' in r['reasons'][0]


def test_uncontrolled_prose_is_not_proven_by_matching_words():
    c=deepcopy(CASES[0]);c['proposal']['statement']='Every matching source word is present; investment guarantees successful transformation.'
    r=assess(c['proposal'],c['passages'],as_of='2026-11-12',run_id='PROSE',verifier_id='fixture-verifier')
    assert r['outcome']=='unresolved'


@pytest.mark.parametrize('bad', ['NaN','Infinity','-1'])
def test_nonfinite_or_negative_financial_claims_are_invalid(bad):
    q=deepcopy(CASES[0]['proposal']['meaning']);q['amount']=bad
    with pytest.raises(ValueError):Meaning(**q)


def test_sensitive_private_passage_contract_rejects_visibility_override():
    p=deepcopy(CASES[0]['passages'][0]);p['visibility']='tenant_private'
    with pytest.raises(ValueError):Passage(**p)


def test_located_passage_hash_and_date_cannot_be_fabricated():
    p=deepcopy(CASES[0]['passages'][0])
    for patch in ({'sha256':'invented'},{'publication_date':'2099-01-01'},{'locator':''},{'rights':{}},{'retrieved_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()}):
        with pytest.raises(ValueError):Passage(**{**p,**patch})


def test_source_content_has_no_permission_or_tool_policy_channel():
    p=deepcopy(CASES[0]['passages'][0]);p['tool_permission']='administrator'
    with pytest.raises(ValueError):Passage(**p)


def test_model_processing_unknown_does_not_enable_a_model_client():
    c=deepcopy(next(c for c in CASES if c['id']=='H-positive-scope'))
    for p in c['passages']:p['rights']['model_processing']='unknown'
    r=assess(c['proposal'],c['passages'],as_of='2026-11-12',run_id='DETERMINISTIC-ONLY',verifier_id='fixture-verifier')
    assert r['outcome']=='accept_bounded' and 'general natural-language semantic verifier unavailable' in r['assurance']


def test_retry_cap_is_bounded_and_decisions_have_no_model_reasoning():
    c=CASES[0]
    with pytest.raises(ValueError):assess(c['proposal'],c['passages'],as_of='2026-11-12',run_id='R',verifier_id='fixture-verifier',max_attempts=100)
    r=assess(c['proposal'],c['passages'],as_of='2026-11-12',run_id='R',verifier_id='fixture-verifier')
    assert r['attempts_used']==1 and r['attempt_cap']==2 and 'no private model reasoning' in r['decision_reasoning']


def test_scope_evidence_ids_must_belong_to_the_proposal():
    c=deepcopy(CASES[0]);c['proposal']['source_segments']=['UNRELATED']
    assert assess(c['proposal'],c['passages'],as_of='2026-11-12',run_id='R',verifier_id='fixture-verifier')['outcome']=='reject'


def test_candidate_handoff_uses_existing_models_and_stays_withheld():
    c=next(c for c in CASES if c['id']=='H-positive-scope');q=Proposal(**c['proposal']);p=Passage(**c['passages'][0]);segment,claim=canonical_candidates(q,p)
    from cios.applications.flora.enterprise_intelligence.semantic import SourceSegment,CandidateClaim
    assert isinstance(segment,SourceSegment) and isinstance(claim,CandidateClaim) and claim.status=='withheld' and claim.authority=='candidate_intelligence'


def test_seven_segment_coverage_does_not_double_count_enterprises():
    d=assets()['Research-v1.json'];assert len(d['profiles'])==6 and len({p['id'] for p in d['profiles']})==6
    segments={s for p in d['profiles'] for s in p['segments']}
    assert segments=={'software','infrastructure','data-ai','cyber','services','channels','emerging'}
    assert len(d['inventory'])==21 and all('partial' in p['status'] for p in d['profiles'])
    assert all(p['gaps'] for p in d['profiles']) and not d['canonical_promotion'] and not d['pipeline_changes']


def test_source_origins_and_legal_temporal_limitations_remain_visible():
    d=assets()['Research-v1.json'];sources={s['id']:s for s in d['sources']}
    assert len(sources)==7 and len({s['origin_id'] for s in sources.values()})>1
    assert 'superseded' in sources['CLOUD-SCOPE']['limitations'][-1]
    assert all(s['original_bytes_sha256'] is None for s in sources.values())
    for s in sources.values():
        assert hashlib.sha256(s['excerpt'].encode()).hexdigest()==s['excerpt_sha256'] and s['verifier_tool_references']
        assert s['rights']['redistribution']=='allowed'


def test_banking_aviation_journeys_preserve_unknown_deployment_and_buying_intent():
    d=assets()['Research-v1.json'];assert {j['industry'] for j in d['journeys']}=={'Banking','Aviation'}
    for j in d['journeys']:
        assert j['truth_class']=='interpretation' and j['deployment']==j['buyer_budget_procurement']=='unknown'
        assert j['enterprise_claim_id'] and 'lens=opportunities' in j['target']


@pytest.mark.parametrize('query',['view=research&provider=private','view=briefings&provider=../../private','view=assurance&workspace=other','view=research&view=briefings','view=research&segment=unknown'])
def test_public_selectors_cannot_find_private_records(query):
    with pytest.raises(ValueError):render(query)


def test_views_reuse_existing_programme_and_have_no_mutation_form():
    for q in ('view=research','view=briefings&provider=oxford-ionics','view=journeys','view=assurance'):
        h=programme(q)
        assert 'Research drafts and controlled semantic proofs' in h and '<form' not in h
    assert 'Industry research' in programme()
    assert public_request_target('/research/programmes/uk-technology?view=briefings&provider=aws')
    assert not public_request_target('/research/programmes/uk-technology?workspace=secret')


def test_semantic_decision_withdrawal_propagates_in_existing_scoped_ledger(tmp_path):
    from cios.applications.flora.research_intelligence.foundation.operations import Operations
    from cios.applications.flora.research_intelligence.foundation.workflow import establish
    from cios.applications.flora.research_intelligence.foundation.sprint2.ledger import record_decision
    from tests.test_flora_autonomous_research_v1 import receipt
    p=json.loads((ROOT/'enterprise-knowledge/technology/research-foundation-v1/Programme.json').read_text());p['sources']=p['sources'][:1];p['as_of']=datetime.now(timezone.utc).date().isoformat()
    o=Operations(tmp_path/'ledger');j=o.create(p,'semantic-fixture');r=establish(o,j,receipt)['release'];cid=r['content']['claims'][0]['candidate']['claim_id']
    case=deepcopy(CASES[0]);case['proposal']['id']=cid;case['proposal']['statement']=r['content']['claims'][0]['candidate']['statement']
    for row in case['passages']:row['source_id']='TECH-SOFTWARE'
    case['proposal']['source_ids']=['TECH-SOFTWARE']
    decision=assess(case['proposal'],case['passages'],as_of='2026-11-12',run_id='FIXTURE-LEDGER',verifier_id='fixture-verifier')
    sid=record_decision(o,j,case['proposal'],decision,cid)
    o.add_dependent(j,'SEM-VIS','visual_projection',[cid],{'label':'Withheld semantic fixture'})
    o.add_dependent(j,'SEM-REL','relationship',[cid],{'id':'SEM-REL','subject':'fixture','predicate':'industry_relevance','object':'software','truth_class':'interpretation','claim_ids':[cid],'entity_id':None,'jurisdiction':'GB','limitations':'Fixture only'})
    o.add_dependent(j,'SEM-HYP','hypothesis',['SEM-REL'],{'id':'SEM-HYP','truth_class':'scenario','statement':'Fixture only','claim_ids':[cid],'assumptions':['Unverified'],'limitations':'Fixture only'})
    affected=o.withdraw(j,cid,'Synthetic semantic correction drill')
    assert {cid,sid,'SEM-VIS','SEM-REL','SEM-HYP'}<=set(affected)
    next_release=o.release(j)
    assert not next_release['content']['claims'] and r['content']['claims']
    with o.db() as db:states={row['id']:row['state'] for row in db.execute('SELECT id,state FROM objects WHERE job=?',(j,))}
    (tmp_path/'semantic-correction-proof.json').write_text(json.dumps({'execution_kind':'synthetic_fixture','real_source_withdrawal':False,'before_release_digest':r['digest'],'after_release_digest':next_release['digest'],'after_claim_count':0,'invalidated':affected,'object_states':states,'prior_release_preserved':True,'canonical_or_pipeline_writes':False},indent=2))
    bad=deepcopy(decision);bad['passage_refs'][0]['source_id']='OUTSIDE'
    with pytest.raises((PermissionError,ValueError)):record_decision(o,j,case['proposal'],bad,cid)
