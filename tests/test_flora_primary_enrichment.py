"""Primary provenance, historical preservation and evidence-led reassessment."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from cios.applications.flora.research_intelligence import model, views
from cios.applications.flora.research_intelligence.source_import import import_proposal
from tests.test_flora_research_intelligence import web
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_sales_pipeline import actor


def prior():
    data=model.load_assessment()
    return json.loads((model.REPO/data['revision']['previous_snapshot']).read_text())


def download(tmp_path, suffix='.txt', text='Verified synthetic disclosure: a dated delivery priority.'):
    path=tmp_path/('source'+suffix)
    if suffix=='.pdf':
        import fitz
        with fitz.open() as doc:
            page=doc.new_page();page.insert_text((60,60),text);doc.save(path)
    else:path.write_text('<html><script>private-code-must-not-be-extracted</script><p>'+text+'</p></html>' if suffix=='.html' else text)
    metadata={'title':'Synthetic source fixture, not company evidence','publisher':'Lloyds Banking Group',
              'url':'https://www.lloydsbankinggroup.com/test-fixture.html','retrieval_url':'https://www.lloydsbankinggroup.com/test-fixture.html',
              'retrieved_at':datetime.now(timezone.utc).isoformat(),'publication_date':'2026-10-29',
              'publication_date_evidence':'Synthetic fixture header, test only','reporting_period':'Synthetic period',
              'reviewed_by':'Synthetic test reviewer','review_notes':'Synthetic local file; not a real publisher retrieval.',
              'provenance_verified':True,'expected_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
              'reviewed_quotes':[{'quote':'a dated delivery priority','locator':'Synthetic paragraph 1'}]}
    return path,metadata


@pytest.mark.parametrize('suffix',['.txt','.html','.pdf'])
def test_verified_download_import_supports_text_html_pdf_without_acceptance(tmp_path,suffix):
    path,metadata=download(tmp_path,suffix)
    result=import_proposal(path,metadata)
    assert result['status']=='review_ready_not_accepted'
    assert result['raw']==path.read_bytes() and 'a dated delivery priority' in result['text']
    assert 'private-code-must-not-be-extracted' not in result['text']
    assert not result['automatic_claim_verification'] and not result['automatic_qualification'] and not result['canonical_mutation']
    assert result['metadata']==metadata


def test_import_rejects_wrong_bytes_unattested_origin_and_missing_quotation(tmp_path):
    path,metadata=download(tmp_path)
    for change in [{'expected_sha256':'0'*64},{'provenance_verified':False},{'reviewed_quotes':[]},
                   {'reviewed_quotes':[{'quote':'Not in file','locator':'Paragraph 1'}]}]:
        with pytest.raises(ValueError):import_proposal(path,{**metadata,**change})


@pytest.mark.parametrize('url',['http://www.lloydsbankinggroup.com/report','https://unapproved.example/report','https://user:pass@www.lloydsbankinggroup.com/report'])
def test_offline_import_does_not_invent_official_provenance(tmp_path,url):
    path,metadata=download(tmp_path)
    with pytest.raises(ValueError):import_proposal(path,{**metadata,'url':url})


def test_import_keeps_unknown_publication_and_rejects_future_or_undated_retrieval(tmp_path):
    path,metadata=download(tmp_path)
    result=import_proposal(path,{**metadata,'publication_date':None,'publication_date_evidence':None})
    assert result['metadata']['publication_date'] is None
    redirected=import_proposal(path,{**metadata,'retrieval_url':'https://www.lloydsbankinggroup.com/resolved-report.txt'})
    assert redirected['metadata']['retrieval_url']!=redirected['metadata']['url']
    for change in [{'publication_date':'2030-01-01'},{'publication_date_evidence':None},
                   {'retrieved_at':'2026-11-09T12:00:00'},{'retrieved_at':'2030-01-01T00:00:00+00:00'}]:
        with pytest.raises(ValueError):import_proposal(path,{**metadata,**change})


def test_import_cli_writes_only_new_scratch_proposal(tmp_path):
    path,metadata=download(tmp_path);meta=tmp_path/'metadata.json';meta.write_text(json.dumps(metadata))
    before=model.DATA.read_bytes();output=tmp_path/'review-output'
    command=[sys.executable,str(model.REPO/'tools/import_flora_primary_source.py'),'--file',str(path),'--metadata',str(meta),'--output',str(output)]
    result=subprocess.run(command,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert (output/'original.txt').read_bytes()==path.read_bytes()
    assert json.loads((output/'review-proposal.json').read_text())['status']=='review_ready_not_accepted'
    assert model.DATA.read_bytes()==before
    assert subprocess.run(command,capture_output=True).returncode!=0
    command[-1]=str(model.REPO/'unwanted-import-output')
    assert subprocess.run(command,capture_output=True).returncode!=0
    assert not (model.REPO/'unwanted-import-output').exists()


def test_previous_claims_sources_and_original_assessment_are_preserved_byte_for_byte():
    data=model.load_assessment();revision=data['revision'];path=revision['previous_snapshot']
    original=subprocess.check_output(['git','show',revision['previous_commit']+':enterprise-knowledge/banking/research-model/Assessment-Overlay.json'],cwd=model.REPO)
    assert (model.REPO/path).read_bytes()==original
    assert hashlib.sha256(original).hexdigest()==revision['previous_sha256']
    old=json.loads(original)
    assert data['claims'][:len(old['claims'])]==old['claims']
    assert data['sources'][:len(old['sources'])]==old['sources']
    comparison=model.compare_revision(old,data)
    assert len(comparison['added'])==24 and comparison['not_in_proposed']==[] and comparison['corroborated']==[]


def test_reviewed_web_excerpts_never_claim_original_binary_integrity():
    data=model.load_assessment();sources=[s for s in data['sources'] if s['verification']=='primary_retrieved']
    assert len(sources)==12 and all(s['content_kind']=='reviewed_web_excerpt' for s in sources)
    for source in sources:
        assert source['primary_content_sha256'] is None and source['retrieval_reference']
        assert len(model.primary_text(source).split())<=25
    bad=deepcopy(data);next(s for s in bad['sources'] if s['verification']=='primary_retrieved')['primary_content_sha256']='f'*64
    with pytest.raises(ValueError):model.validate(bad)


def test_new_primary_claims_require_real_snapshot_quotes_not_a_status_flag():
    data=model.load_assessment();supported=[c for c in data['claims'] if c['verification']=='source_supported']
    assert len(supported)==24 and all(model.primary_claim_supported(data,c) for c in supported)
    bad=deepcopy(data);bad['claims'][-1]['primary_quotes']={bad['claims'][-1]['source_ids'][0]:'Unsupported invented quotation'}
    with pytest.raises(ValueError):model.validate(bad)
    bad=deepcopy(data);bad['sources'][-1]['text_sha256']='0'*64
    with pytest.raises(ValueError):model.validate(bad)


def test_financial_periods_targets_and_publication_dates_remain_distinct():
    data=model.load_assessment();claims={c['id']:c for c in data['claims']};sources={s['id']:s for s in data['sources']}
    assert claims['LBG-Q326-DEPOSITS']['metric_value']==502.8 and '30 September' in claims['LBG-Q326-DEPOSITS']['reporting_period']
    assert claims['LBG-AR25-DEPOSITS']['metric_value']==496.5 and claims['LBG-AR25-DEPOSITS']['reporting_period']=='31 December 2025'
    assert sources['PR-LBG-Q326']['publication_date']=='2026-10-29'
    assert sources['PR-LBG-AR25']['publication_date']=='2026-02-13'
    assert sources['PR-FCA-RES26']['publication_date']=='2017-05-13' and sources['PR-FCA-RES26']['updated_at']=='2026-09-15'
    assert sources['PR-LBG-A2030']['publication_date'] is None
    assert claims['LBG-AI26-EXPECTED']['kind']=='management_expectation'
    assert 'not procurement' in claims['LBG-A2030-SAVINGS']['metric_unit']


def test_industry_links_do_not_promote_bank_facts_to_sector_trends():
    data=model.load_assessment();claims={c['id']:c for c in data['claims']}
    for identifier in ['UK-RATE-NOV26','UK-PRA-REPORT27','UK-FCA-REPORT27']:
        assert claims[identifier]['asset_id']=='BK-IND-002'
    for identifier in ['LBG-ENVOY-GOOGLE','LBG-Q326-DEPOSITS','LBG-A2030-PLATFORMS']:
        assert claims[identifier]['asset_id']=='BK-ENT-001'
    assert any(r['predicate']=='enterprise_case_example_only' for r in data['relationships'])
    assert all(not r['verified'] for r in data['relationships'] if r['predicate']=='enterprise_case_example_only')


def test_all_eight_hypotheses_reassessed_one_specific_new_candidate_and_no_sales_qualification():
    data=model.load_assessment();old=prior();candidates={c['id']:c for c in data['candidates']}
    assert {c['id'] for c in old['candidates']}<=candidates.keys()
    assert len(candidates)==9 and candidates['RCO-LBG-009']['review']['change']=='added'
    assert candidates['RCO-LBG-004']['review']['change']=='weakened_and_retargeted'
    assert candidates['RCO-LBG-008']['review']['change']=='weakened_as_standalone'
    for row in candidates.values():
        assert row['review']['added_claim_ids'] and row['review']['next_action']
        assert row['estimated_value'] is None and row['procurement_date'] is None
        assert 'no customer' in row['review']['buying_signal'].lower() or 'no confirmed' in row['review']['buying_signal'].lower()
        assert row['review']['funding_signal'] and row['review']['procurement_signal']
    assert {r['id']:r['rank'] for r in model.ranked_candidates()}=={
        'RCO-LBG-001':1,'RCO-LBG-002':2,'RCO-LBG-005':3,'RCO-LBG-003':4,'RCO-LBG-009':5,
        'RCO-LBG-004':6,'RCO-LBG-006':7,'RCO-LBG-008':8,'RCO-LBG-007':9}


def test_completion_resolves_only_transaction_status_not_customer_integration_need():
    data=model.load_assessment();gap=next(g for g in data['gaps'] if g['id']=='G-CURVE')
    assert gap['status']=='partially_resolved' and gap['resolved_claim_ids']==['LBG-Q326-CURVE']
    assert 'procurement remain unknown' in gap['resolution']
    assert 'RCO-LBG-009' in next(w['reason'] for w in data['watchlist'] if 'Curve' in w['title'])
    assert 'does not evidence an outsourcing mandate' in next(c['statement'] for c in data['claims'] if c['id']=='LBG-BRAND26-NO-ROLES')


def test_public_views_expose_updated_provenance_comparison_and_full_original_limit(web):
    for path in ['/lloyds','/opportunities','/candidates/RCO-LBG-009','/evidence/LBG-Q326-CURVE','/sources']:
        status,body=web(model.ROOT+path)
        assert status==200 and '12 reviewed primary-source records' in body
    assert 'Before and after primary research' in views.opportunities_page()
    assert 'full original PDF/HTML bytes were not downloaded' in views.evidence_page('LBG-Q326-CURVE')
    assert 'No hypotheses are merged' in views.opportunities_page()


def test_old_captured_opportunity_stays_unchanged_after_primary_enrichment(actor,monkeypatch):
    from cios.applications.flora import sales_pipeline as sales
    old=prior();original=model.load_assessment
    monkeypatch.setattr(model,'load_assessment',lambda:old)
    captured=sales.create_opportunity('lloyds','RCO-LBG-001',headers=actor[3])
    monkeypatch.setattr(model,'load_assessment',original)
    again=sales.create_opportunity('lloyds','RCO-LBG-001',headers=actor[3])
    assert again==captured
    assert len(again['provenance']['claim_ids'])==2
    assert again['stage']=='Discovered' and again['qualification']=={}
    new=sales.create_opportunity('lloyds','RCO-LBG-009',headers=actor[3])
    assert new['stage']=='Discovered' and new['qualification']=={} and new['amount']==''
    assert any('reviewed primary excerpt' in label for label in new['provenance']['source_labels'])
    assert not new['evidence_reviewed'] and sales.qualification(new)['percent']==0
