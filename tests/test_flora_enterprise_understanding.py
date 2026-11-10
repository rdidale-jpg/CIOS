"""Candidate evidence quality, provenance, causal limits and read-only journeys."""
from copy import deepcopy
from datetime import date
import hashlib
import json

import pytest
from cios.applications.flora.research_intelligence import understanding as u, model, cycle
from cios.applications.flora.research_intelligence.understanding_views import render
from cios.applications.flora.research_intelligence.source_import import official_url
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_research_intelligence import web

ASOF='2026-11-10'


@pytest.mark.parametrize('domain',['banking','aviation'])
def test_assessments_are_reproducible_scoped_and_read_only(domain):
    data=model.load_assessment(domain);r=u.load_review(domain);before=deepcopy((data,r))
    x=u.assess(data,r,ASOF)
    assert x==u.assess(data,r,ASOF)
    assert (data,r)==before
    assert x['authority']=='candidate_intelligence' and not x['automatic_acceptance'] and not x['pipeline_mutation']
    assert len(x['dossier'])==14 and 'not certified' in x['maturity']
    assert x['retained_unknowns']==data['gaps']
    assert all(t.get('prior_question') and t.get('refinement_claim_ids') for t in x['next_research'][:3])
    assert all(c['authority']=='candidate_intelligence' and c['support'] and c['missing_evidence'] for c in x['conclusions'])
    assert {c['id'] for c in data['claims']} <= {c['id'] for c in x['claims']}
    assert {e['id'] for e in data['relationships']} <= {e['id'] for e in x['relationships']}


def test_all_evidence_classes_and_secondary_never_relabelled_primary(tmp_path,monkeypatch):
    bank=model.load_assessment();av=model.load_assessment('aviation')
    assert u.source_quality(bank['sources'][0],ASOF)['kind']=='Unverified source reference'
    assert u.source_quality(next(s for s in av['sources'] if s['id']=='SRC-AV-Q326'),ASOF)['kind']=='Search-index-only excerpt'
    secondary=next(s for s in u.load_review('banking')['sources'] if s['verification']=='secondary_reviewed')
    assert u.source_quality(secondary,ASOF)['kind']=='Independent-publisher secondary excerpt'
    with pytest.raises(ValueError):official_url(secondary['url'])
    primary=u.load_review('banking')['sources'][0]
    assert u.source_quality(primary,ASOF)['kind']=='Reviewed primary excerpt'
    root=tmp_path/'enterprise-knowledge/banking/research-model/source-snapshots';root.mkdir(parents=True)
    raw=b'Synthetic primary original: measured latency was ten milliseconds.'
    (root/'original.txt').write_bytes(raw);(root/'text.txt').write_bytes(raw)
    source={**primary,'content_kind':'verified_download','primary_content_sha256':hashlib.sha256(raw).hexdigest(),
        'raw_path':str((root/'original.txt').relative_to(tmp_path)),'text_path':str((root/'text.txt').relative_to(tmp_path)),
        'text_sha256':hashlib.sha256(raw).hexdigest()}
    monkeypatch.setattr(model,'REPO',tmp_path)
    assert u.source_quality(source,ASOF)['kind']=='Original primary document'
    (root/'original.txt').write_bytes(b'corrupted')
    with pytest.raises(ValueError):u.source_quality(source,ASOF)


def test_independent_publisher_repeating_management_is_not_independent_outcome_verification():
    r=u.load_review('banking');s=next(s for s in r['sources'] if s['id']=='V3-LBG-SECONDARY')
    assert u.publisher_group(s)=='Guardian' and s['assertion_origin']=='Lloyds management'
    assert u.assess(model.load_assessment(),r,ASOF)['stats']['independent_corroborated_claims']==0
    # Add another real company passage as contextual candidate provenance,
    # retaining the Observation identity and without manufacturing corroboration.
    target=r['claim_reviews'][0];source=next(s for s in r['sources'] if s['id']=='V3-LBG-STRATEGY')
    target.update(additional_source_ids=[source['id']],source_link_reason='Contrast the two dated/scope-limited estate accounts; do not merge their denominators')
    target['links'].append({**deepcopy(target['links'][0]),'source_id':source['id'],'quote':source['excerpts'][0]['quote'],'locator':source['excerpts'][0]['locator'],'support':'context'})
    result=u.assess(model.load_assessment(),r,ASOF)
    claim=next(c for c in result['claims'] if c['id']==target['claim_id'])
    assert claim['candidate_additional_source_ids']==[source['id']]
    assert claim['original_source_ids'] and not claim['independent_corroboration']


def reviewed_pair():
    statement='Synthetic laboratory measurement was 10 ms.'
    claim={'id':'SYNTHETIC','statement':statement,'subject':'BK-ENT-001','period':'Synthetic period','kind':'candidate_observation','source_ids':['A','B']}
    sources={'A':{'id':'A','url':'https://www.lloydsbankinggroup.com/synthetic','entity_ids':['BK-ENT-001'],'assertion_origin':'Synthetic company measurement','text_sha256':'a'*64},
             'B':{'id':'B','url':'https://www.theguardian.com/synthetic','entity_ids':['BK-ENT-001'],'assertion_origin':'Synthetic independently sampled experiment','text_sha256':'b'*64}}
    quality={k:{'text':statement+' Synthetic context '+k,'eligible_at_cutoff':True,'kind':'Reviewed primary excerpt' if k=='A' else 'Independent-publisher secondary excerpt','publisher_group':u.publisher_group(s),'document_key':u.document_key(s)} for k,s in sources.items()}
    review={'assertion_digest':cycle.digest(statement),'entity_id':'BK-ENT-001','period':'Synthetic period','links':[
      {'source_id':k,'quote':statement,'locator':'Synthetic section 1','support':'direct','reason':'Synthetic explicit direct support review','reviewed_by':'Synthetic test fixture','reviewed_at':ASOF,'assertion_digest':cycle.digest(statement),'independence_basis':'Synthetic separate sampling protocol described in each fixture'} for k in sources]}
    return claim,sources,quality,review


def test_genuinely_reviewed_independent_origins_can_be_reported_without_acceptance():
    c,s,q,r=reviewed_pair();x=u.claim_quality(c,s,q,r,ASOF)
    assert x['independent_corroboration'] and x['independent_pairs']==[['A','B']]
    assert 'candidate only' in x['quality_state']


@pytest.mark.parametrize('defect',['same_origin','same_publisher','same_document','same_content','missing_basis','future','wrong_quote'])
def test_fabricated_corroboration_cannot_inflate_evidence(defect):
    c,s,q,r=reviewed_pair()
    if defect=='same_origin':s['B']['assertion_origin']=s['A']['assertion_origin']
    elif defect=='same_publisher':q['B']['publisher_group']=q['A']['publisher_group'];s['B']['publisher']='Invented separate publisher name'
    elif defect=='same_document':q['B']['document_key']=q['A']['document_key']
    elif defect=='same_content':s['B']['text_sha256']=s['A']['text_sha256']
    elif defect=='missing_basis':r['links'][1].pop('independence_basis')
    elif defect=='future':q['B']['eligible_at_cutoff']=False
    else:r['links'][1]['quote']='Not in the source'
    assert not u.claim_quality(c,s,q,r,ASOF)['independent_corroboration']


def test_query_variants_and_publisher_names_cannot_create_independence():
    a={'url':'https://www.lloydsbankinggroup.com/path?utm_source=a#fragment','publisher':'A'}
    b={'url':'https://www.lloydsbankinggroup.com/path/?utm_source=b','publisher':'Totally independent company'}
    assert u.document_key(a)==u.document_key(b)
    assert u.publisher_group(a)==u.publisher_group(b)=='Lloyds'


@pytest.mark.parametrize('field,value',[('entity_id','AV-ENT-001'),('period','Another period'),('assertion_digest','wrong')])
def test_support_review_cannot_be_reused_for_other_scope_or_assertion(field,value):
    c,s,q,r=reviewed_pair();r[field]=value
    with pytest.raises(ValueError):u.claim_quality(c,s,q,r,ASOF)


def test_industry_material_cannot_become_enterprise_proof():
    c,s,q,r=reviewed_pair();s['A']['entity_ids']=['BK-IND-002']
    with pytest.raises(ValueError,match='entity-specific'):u.claim_quality(c,s,q,r,ASOF)
    x=u.assess(model.load_assessment('aviation'),u.load_review('aviation'),ASOF)
    gov=next(c for c in x['claims'] if 'V3-UK-SAF' in c['source_ids'])
    assert gov['subject']=='AV-IND-001'
    edge=next(e for e in x['relationships'] if e['id']=='V3-EJ-SAF-APPLICABILITY')
    assert edge['state']=='Plausible unverified hypothesis' and not edge['causation_proven']


def test_wrong_locator_and_tampered_passage_are_not_direct_support():
    r=u.load_review('banking');r['claim_reviews'][0]['links'][0]['locator']='Invented page 999'
    x=u.assess(model.load_assessment(),r,ASOF)
    assert not next(c for c in x['claims'] if c['id']==r['claim_reviews'][0]['claim_id'])['direct_support_reviewed']
    r=u.load_review('banking');r['observations'][0]['segment']['content']='fabricated'
    with pytest.raises(ValueError):u.assess(model.load_assessment(),r,ASOF)


def edge_digest(edge):
    edge['assessment']['edge_digest']=cycle.digest({k:edge[k] for k in ('id','subject','predicate','object','claim_ids','temporal_scope')})


def test_factual_supplier_edge_is_explicit_historical_and_not_causal():
    x=u.assess(model.load_assessment('aviation'),u.load_review('aviation'),ASOF)
    edge=next(e for e in x['relationships'] if e['id']=='V3-EJ-MRO-FACT')
    assert edge['state']=='Verified factual relationship'
    assert '2023' in edge['period'] and edge['claim_ids'] and edge['evidence_ids']
    assert not edge['causation_proven'] and edge['missing_evidence']


def test_shared_context_and_two_evidenced_endpoints_do_not_prove_causation():
    data=model.load_assessment();r=u.load_review('banking');e=r['relationships'][0]
    e['predicate']='causes';e['assessment']['causal']=True;edge_digest(e)
    with pytest.raises(ValueError,match='causation'):u.assess(data,r,ASOF)
    r=u.load_review('banking');e=r['relationships'][1];e['assessment']['status']='factual';edge_digest(e)
    x=u.assess(data,r,ASOF)
    assert next(a for a in x['relationships'] if a['id']==e['id'])['state']=='Plausible unverified hypothesis'


def test_inference_needs_real_passages_not_context_flags():
    r=u.load_review('banking')
    for cr in r['claim_reviews']:
        for link in cr['links']:link['quote']='Absent synthetic quote'
    x=u.assess(model.load_assessment(),r,ASOF)
    assert all(e['state']!='Supported analytical inference' for e in x['relationships'])


def test_contradiction_and_supersession_keep_predecessor_and_counterevidence():
    data=model.load_assessment();r=u.load_review('banking');old=r['relationships'][1];successor=deepcopy(old)
    successor['id']='SYNTHETIC-SUCCESSOR';edge_digest(successor);r['relationships'].append(successor)
    old['assessment'].update(status='superseded',superseded_by=successor['id']);edge_digest(old)
    other=r['relationships'][2];other['assessment'].update(status='contradicted',contradicting_claim_ids=old['claim_ids']);edge_digest(other)
    x=u.assess(data,r,ASOF);edges={e['id']:e for e in x['relationships']}
    assert edges[old['id']]['state']=='Superseded relationship'
    assert edges[old['id']]['superseded_by']==successor['id'] and old['id'] in edges
    assert edges[other['id']]['state']=='Contradicted relationship' and edges[other['id']]['contradicting_claim_ids']
    assert x['contradictions'][0]['status'].startswith('Unresolved scope/time')
    successor['assessment'].update(status='superseded',superseded_by=old['id']);edge_digest(successor)
    with pytest.raises(ValueError,match='Cyclic'):u.assess(data,r,ASOF)


def test_missing_and_foreign_endpoints_are_unknown_not_fabricated_nodes():
    r=u.load_review('banking');e=r['relationships'][0];e['object']='AV-SUP-AIRBUS';edge_digest(e)
    x=u.assess(model.load_assessment(),r,ASOF)
    assert next(a for a in x['relationships'] if a['id']==e['id'])['state']=='Unknown / missing relationship'


def test_arbitrary_factual_conclusion_cannot_borrow_true_support():
    r=u.load_review('banking');r['conclusions'][0].update(kind='factual',statement='AI caused all savings and has an available budget.')
    with pytest.raises(ValueError,match='Factual conclusion'):u.assess(model.load_assessment(),r,ASOF)


@pytest.mark.parametrize('domain',['banking','aviation'])
def test_before_after_distinguishes_understanding_from_record_counts(domain):
    data=model.load_assessment(domain);r=u.load_review(domain);comparison=u.before_after(data,r,ASOF)
    assert comparison['after']['exact_support_reviewed']>comparison['before']['exact_support_reviewed']
    assert comparison['after']['independent_corroborated_claims']==0
    assert comparison['after']['evidence_supported_causal_outcomes']==0
    assert comparison['gaps_automatically_closed']==[] and not comparison['canonical_mutation']
    assert comparison['unchanged_existing_claim_ids']==sorted(c['id'] for c in data['claims'])
    if domain=='aviation':assert comparison['after']['reviewed_company_outcome_observations']==1


def test_cycle_revisit_preserves_history_and_requires_bound_reason():
    data=model.load_assessment();source=u.load_review('banking')['sources'][0]
    item={'task_id':'R-BK-ENT-001-operations','source':source,'effect':'new','target_claim_id':None,'rationale':'Synthetic test of the real provenance route, not canonical acceptance'}
    first=cycle.run_cycle(data,ASOF,[item]);second=cycle.run_cycle(data,ASOF,[{**item,'revisit_reason':'Compare another located passage'}],previous=first,revisit_task_ids=[item['task_id']])
    assert second['waves'][0]==first['waves'][0] and len(second['waves'])==2
    with pytest.raises(ValueError,match='reason'):cycle.run_cycle(data,ASOF,[item],previous=first,revisit_task_ids=[item['task_id']])
    with pytest.raises(ValueError):cycle.run_cycle(data,ASOF,[],previous=first,revisit_task_ids=['not-a-task'])


@pytest.mark.parametrize('slug',['lloyds','easyjet'])
def test_finite_public_understanding_route_and_navigation(web,slug):
    path='/enterprises/'+slug+'/understanding'
    assert public_request_target(path)
    for suffix in ('?workspace_id=private','/private','?enterprise_id=other'):
        assert not public_request_target(path+suffix)
    status,html=web(path);assert status==200
    assert 'What the evidence supports' in html and 'Question map, not a proven causal chain' in html
    assert 'Text alternative to relationship map' in html and 'No canonical acceptance' in html
    status,enterprise=web('/enterprises/'+slug);assert status==200 and path in enterprise


def test_html_safety_and_conclusion_lineage_are_enforced():
    data=model.load_assessment();r=u.load_review('banking');r['conclusions'][0]['title']='<script>bad</script>'
    assert '<script>bad' not in render(data,r,ASOF) and '&lt;script&gt;' in render(data,r,ASOF)
    r['conclusions'][0]['claim_ids']=['AV-NOT-HERE']
    with pytest.raises(ValueError):u.assess(data,r,ASOF)


def test_cross_enterprise_source_and_baseline_replacement_are_rejected():
    r=u.load_review('banking');r['sources'][0]['research_domain']='aviation'
    with pytest.raises(ValueError):u.assess(model.load_assessment(),r,ASOF)
    r=u.load_review('banking');r['baseline_digest']='invented'
    with pytest.raises(ValueError):u.assess(model.load_assessment(),r,ASOF)


def test_source_supersession_retains_history_without_current_corroboration():
    r=u.load_review('banking');old=r['sources'][0];new=deepcopy(old)
    new.update(id='SYNTHETIC-SOURCE-SUCCESSOR',supersedes_source_id=old['id'],supersession_reason='Synthetic same-period provenance revision fixture')
    r['sources'].append(new)
    x=u.assess(model.load_assessment(),r,ASOF)
    assert any(s['id']==old['id'] and s['superseded_by']==new['id'] for s in x['sources'])
    cid=next(o['candidate']['claim_id'] for o in r['observations'] if o['source_id']==old['id'])
    claim=next(c for c in x['claims'] if c['id']==cid)
    assert claim['links'][0]['passage_present'] and not claim['direct_support_reviewed']
    assert 'Historical support retained' in claim['quality_state']
    new['reporting_period']='Another period is history, not a correction'
    with pytest.raises(ValueError,match='same-period'):u.assess(model.load_assessment(),r,ASOF)


def test_unverified_counterevidence_cannot_mark_relationship_contradicted():
    r=u.load_review('banking');edge=r['relationships'][0]
    edge['assessment'].update(status='contradicted',contradicting_claim_ids=['LBG-DEPOSITS']);edge_digest(edge)
    with pytest.raises(ValueError,match='supported counterevidence'):u.assess(model.load_assessment(),r,ASOF)


def test_future_and_index_only_passages_never_establish_exact_support():
    c,s,q,r=reviewed_pair()
    for row in q.values():row['kind']='Search-index-only excerpt'
    assert not u.claim_quality(c,s,q,r,ASOF)['direct_support_reviewed']
    for row in q.values():row.update(kind='Reviewed primary excerpt',eligible_at_cutoff=False)
    assert not u.claim_quality(c,s,q,r,ASOF)['direct_support_reviewed']


def test_checkpoint_replay_and_cli_export_are_reproducible(tmp_path):
    import subprocess,sys
    data=model.load_assessment('aviation');r=u.load_review('aviation')
    replay=u.replay_research(data,r)
    receipts=[{'id':w['id'],'selected_task_ids':w['selected_task_ids'],'revisit_task_ids':w['revisit_task_ids'],'proposal_ids':[p['id'] for p in w['proposals']]} for w in replay['waves']]
    assert receipts==r['cycle_receipts'] and not replay['canonical_mutation']
    assert replay['retained_history']==data and len(replay['waves'])==3
    ids={c['candidate']['claim_id'] for w in replay['waves'] for p in w['proposals'] for c in p['candidates']}
    assert ids=={o['candidate']['claim_id'] for o in r['observations']}
    output=tmp_path/'report'
    cmd=[sys.executable,'tools/research/flora_understanding.py','--enterprise','easyjet','--as-of',ASOF,'--output',str(output)]
    result=subprocess.run(cmd,cwd=model.REPO,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert sorted(p.name for p in output.iterdir())==['assessment.json','comparison.json','replayed-checkpoint.json','report.md']
    before={p.name:p.read_bytes() for p in output.iterdir()}
    assert subprocess.run(cmd,cwd=model.REPO,capture_output=True).returncode!=0
    assert before=={p.name:p.read_bytes() for p in output.iterdir()}


def test_contradictory_passage_is_retained_without_automatic_invalidation():
    c,s,q,r=reviewed_pair();q['B']['text']='Synthetic laboratory measurement was 20 ms.'
    r['links'][1].update(quote=q['B']['text'],support='contradicts',reason='Synthetic countermeasurement on the same entity and period; adjudication outstanding')
    result=u.claim_quality(c,s,q,r,ASOF)
    assert result['quality_state']=='Contradictory evidence requires treatment'
    assert result['contradictory_source_ids']==['B'] and result['statement']==c['statement']
    assert result['links'][0]['passage_present'] and result['links'][1]['passage_present']
