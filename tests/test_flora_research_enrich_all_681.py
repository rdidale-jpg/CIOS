"""Portfolio research QA only. No private stores or network source collection."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest

PACK=Path(__file__).resolve().parents[1]/'docs/flora-runtime/research-enrich-all-681'
spec=importlib.util.spec_from_file_location('rea_qa',PACK/'validate.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)


def test_full_tracked_file_archive_and_owner_scope():
    result=qa.validate()
    assert result['baseline_files']==3942 and result['archives']==9
    assert result['runtime_changes']==result['canonical_writes']==0


@pytest.mark.parametrize('flag',['withdrawn','retracted','revoked','denied','contradictory','stale','superseded','core_contradiction'])
def test_restricted_source_removes_its_research_dependants_not_unrelated_work(flag):
    sources=qa.index(qa.read('Wave-1-Sources.json')['sources'])
    claims=qa.index(qa.read('Wave-1-Claims.json')['claims'])
    assert qa.research_available(claims['C-NV3'],sources)
    sources['W-NV3'][flag]=True
    assert not qa.research_available(claims['C-NV3'],sources)
    assert not qa.research_available(claims['C-NV-MECH'],sources)
    assert qa.research_available(claims['C-BT-FIN'],sources)


@pytest.mark.parametrize('sid',['X-BBC','X-BARCLAYS','X-EJ-Q3'])
def test_index_or_blocked_acquisition_cannot_substitute_original_verification(sid):
    sources=qa.index(qa.read('Wave-1-Sources.json')['sources'])
    c=deepcopy(qa.read('Wave-1-Claims.json')['claims'][0]);c['source_ids']=[sid]
    assert not qa.research_available(c,sources)
    with pytest.raises(AssertionError,match='Unverified'):qa.claim_integrity(c,sources)


@pytest.mark.parametrize('flag',['public_eligible','public_permission_granted','observation_imported','material_pressure_qualified','pipeline_created'])
def test_candidate_documentation_cannot_grant_authority_or_qualify_pipeline(flag):
    c=deepcopy(qa.read('Wave-1-Claims.json')['claims'][0]);c[flag]=True
    with pytest.raises(AssertionError,match='Authority'):qa.claim_integrity(c,qa.index(qa.read('Wave-1-Sources.json')['sources']))


@pytest.mark.parametrize('case',['CAA-DELTA','NG-UK','NG-SHARE','NV-DELTA'])
def test_sourced_comparisons_reproduce(case):
    row=next(r for r in qa.read('Financial-and-Temporal-QA.json')['calculations']if r['id']==case)
    assert qa.fixed_calculation(row)


@pytest.mark.parametrize('change',['currency','scale','value','source'])
def test_wrong_financial_definition_or_inputs_are_rejected(change):
    r=next(r for r in qa.read('Financial-and-Temporal-QA.json')['calculations']if r['id']=='NG-UK')
    if change=='currency':r['currency']='USD'
    if change=='scale':r['scale']='billion'
    if change=='value':r['inputs'][0]='288.8'
    if change=='source':r['source_ids']=['W-NV3']
    with pytest.raises(AssertionError):qa.fixed_calculation(r)


@pytest.mark.parametrize('claim_id',['AV-FLEET','AV-MRO','AV-NETWORK','AV-CHAT'])
def test_pinned_easyjet_editorial_projection_is_not_reported_missing(claim_id):
    c=qa.read('Coverage-and-Gaps.json')
    row=next(r for r in c['claim_coverage']if r['key'].endswith('::'+claim_id))
    assert row['projection_owner']=='easyjet_capabilities.fact'and row['presentation_proof']
    row['status']='eligible_not_presented'
    with pytest.raises(AssertionError,match='Pinned'):qa.coverage_integrity(c)


def test_global_gva_slice_cannot_mean_complete_economics():
    c=qa.read('Coverage-and-Gaps.json')
    row=next(r for r in c['requirements']if r['family']=='national'and r['information_element']=='economics')
    row['requirement']='Revenue,cost,cash,capital allcovered'
    with pytest.raises(AssertionError,match='GVA slice'):qa.coverage_integrity(c)


def test_provider_discovery_link_is_not_universal_closure_source():
    c=qa.read('Coverage-and-Gaps.json')
    row=next(r for r in c['requirements']if r['family']=='technology'and r['scope']=='enterprise_profile'and r['discovery_leads_not_verified_closure_sources'])
    row['next_source']=row['discovery_leads_not_verified_closure_sources'][0]
    with pytest.raises(AssertionError,match='first link'):qa.coverage_integrity(c)


def test_unmatched_render_sample_does_not_prove_absence_or_new_research_need():
    c=qa.read('Coverage-and-Gaps.json')
    row=next(r for r in c['claim_coverage']if r['adapter_eligible']and not r['presentation_proof'])
    row['requires_new_research']=True
    with pytest.raises(AssertionError):qa.coverage_integrity(c)


def test_legacy_bare_ids_and_tms_completion_do_not_establish_canonical_models():
    import json,zipfile
    subjects=qa.read('Subjects.json')['subjects']
    ids=[s for s in subjects if s['local_id']=='BK-ENT-003']
    assert ids and all(s['canonical_existence'].startswith('unverified')for s in ids)
    with zipfile.ZipFile(qa.ROOT/'enterprise-knowledge/TMS-001_High_Fidelity_Industry_Twin_Upgrade.zip')as z:
        m=json.loads(z.read('TMS-001_Final_Package/00_manifest.json'))
    assert m['mission_outcome']=='COMPLETE'and m['validation_state']['promotion_readiness']=='fail_not_ready'


@pytest.mark.parametrize('claim_id',['C-RATE','C-MORTGAGE','C-EJ-SFP','C-EJ-ICC','C-BT-CHANGE','C-IFR'])
def test_established_event_dates_are_not_unknown_or_publication_dates(claim_id):
    claims=qa.read('Wave-1-Claims.json')['claims']
    next(c for c in claims if c['id']==claim_id)['event_date']=None
    with pytest.raises(AssertionError,match='Known event'):
        qa.temporal_integrity(claims,qa.index(qa.read('Wave-1-Sources.json')['sources']))
