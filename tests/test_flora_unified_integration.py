"""Cross-workstream acceptance without new authority, source truth or opportunity IDs."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
from html import unescape
import pytest
from tools.research.history_integrity import approved_history, compare_history, verify_history, REVIEW
from cios.applications.flora.research_intelligence import macro_intelligence as macro, macro_trace
from cios.applications.flora.research_intelligence.model import load_assessment
from cios.applications.flora import sales_pipeline as sales
from tests.test_flora_sales_pipeline import actor, web
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_commercial_visual_v3 import store_hash

ROOT=Path(__file__).resolve().parents[1]


def test_both_reviewed_workstreams_remain_ancestors_with_exact_source_cuts():
    for head in ('6988ba50d29c1f238293fc7fe110d6182f055e68','5fa5d2f197893a6fd64b3344354c039eaad629f7',
                 '4c374ac2d326639245b60967aa64e934e0c1d7a3','111600a56ca0edba0d47d1a8a0c92068060d83a8'):
        assert subprocess.run(['git','merge-base','--is-ancestor',head,'HEAD'],cwd=ROOT).returncode==0
    assert verify_history(ROOT)=={'historical_files':142,'depth_additions':4,'macro_additions':14,'trigger_candidate_additions':1,'total':161,'old_review_records_retained':True}


@pytest.mark.parametrize('change',['historical_byte','approved_macro_byte','approved_depth_byte','old_review_record','missing','unknown','ignored_unknown'])
def test_history_guard_rejects_every_unapproved_change(change):
    expected=approved_history(ROOT);actual=deepcopy(expected)
    if change=='historical_byte':actual['enterprise-knowledge/banking/research-model/Assessment-Overlay.json']+=b' '
    elif change=='approved_macro_byte':actual['enterprise-knowledge/macro/research-model/source-snapshots/GM-CYBER-GB.txt']+=b' '
    elif change=='approved_depth_byte':actual['enterprise-knowledge/banking/research-model/source-snapshots/DEPTH-LBG-AI.txt']+=b' '
    elif change=='old_review_record':
        review=json.loads(actual[REVIEW]);review['sources'][0]['title']='UNAPPROVED';actual[REVIEW]=json.dumps(review).encode()
    elif change=='missing':actual.pop(next(iter(actual)))
    else:actual['enterprise-knowledge/'+('.ignored.tmp' if change=='ignored_unknown' else 'UNAPPROVED.txt')]=b'unapproved'
    with pytest.raises(AssertionError):compare_history(expected,actual)


def test_baseline_union_keeps_original_cases_signatures_and_skip_reasons():
    current=json.loads((ROOT/'tools/ci/flora-baseline-v1.json').read_text())
    for ref in ('adf205993cc0857183d77766ce4882bf48326fb4','5fa5d2f197893a6fd64b3344354c039eaad629f7','111600a56ca0edba0d47d1a8a0c92068060d83a8'):
        old=json.loads(subprocess.check_output(['git','show',ref+':tools/ci/flora-baseline-v1.json'],cwd=ROOT))
        for profile,config in old['profiles'].items():
            assert current['profiles'][profile]['security_modules']==config['security_modules']
            for name,suite in config['suites'].items():assert current['profiles'][profile]['suites'][name]==suite,(profile,name)


def test_cyber_reuses_one_visual_story_cockpit_and_deliberate_full_evidence(web):
    status,html,_=web('/flora/banking/research/candidates/RCO-LBG-005',authenticated=False)
    assert status==200
    assert html.count("class='eo-module'")==8 and html.count("class='eo-story-node'")==4
    assert html.count("id='full-research-evidence'")==1
    assert "id='full-research-evidence' open" not in html
    assert "class='depth-executive'" in html and 'depth-print-citations' in html
    assert 'Business owner, addressable spend, budget, demand and procurement: Unknown' in html
    assert 'Current source support missing' not in html.split('eo-story')[0] # no fabricated removal of supported context


def test_macro_to_enterprise_link_preserves_separate_identity_and_unknown_applicability(web):
    status,html,_=web('/macro?market=GB&view=enterprise',authenticated=False)
    assert status==200 and "href='/enterprises/lloyds'" in html
    assert 'Formal applicability: Unknown' in unescape(html)
    fr=macro.context_spec(macro.selection('market=FR&category=sustainability&force=eu-csrd&view=enterprise'))
    assert fr['enterprise_trace']['entity']['status']=='unknown' and fr['enterprise_trace']['hypothesis_id'] is None
    assert not fr['candidates']


def test_integrated_public_journey_cannot_enumerate_or_modify_private_pipeline(web,actor,monkeypatch):
    record=sales.create_opportunity('lloyds','RCO-LBG-005',headers=actor[3]);before=store_hash()
    def forbidden(*a,**k):raise AssertionError('Public integration read private Pipeline')
    monkeypatch.setattr(sales,'list_opportunities',forbidden)
    for path in ('/macro?market=GB&offering=cyber','/macro?market=GB&view=industry','/macro?market=GB&view=enterprise',
                 '/industries/banking','/industries/aviation','/enterprises/lloyds','/enterprises/lloyds?lens=opportunities',
                 '/enterprises/easyjet','/flora/banking/research/candidates/RCO-LBG-005'):
        status,html,_=web(path,authenticated=False)
        assert status==200 and record['id'] not in html and 'synthetic-workspace' not in html
    assert store_hash()==before


@pytest.mark.parametrize('origin',['RCO-LBG-002','RCO-LBG-005'])
def test_deliberate_capture_preserves_original_identity_review_and_stage_gate(web,actor,origin):
    record=sales.create_opportunity('lloyds',origin,headers=actor[3]);frozen=deepcopy(record);before=store_hash()
    assert record['origin_id']==origin and record['stage']=='Discovered'
    assert record['provenance']['commercial_review']
    assert sales.create_opportunity('lloyds',origin,headers=actor[3])==frozen
    # Public Macro inspection and reference design cannot append to this snapshot.
    macro_trace.capture_reference(macro.selection('market=GB'),'RCO-LBG-005')
    status,html,_=web('/macro/evidence?market=GB',authenticated=False);assert status==200
    with pytest.raises(sales.SalesValidationError):sales.update_opportunity(record['id'],record['version'],{'stage':'Qualified','confirm':'yes'},headers=actor[3])
    assert sales.get_opportunity(record['id'],headers=actor[3])==frozen and store_hash()==before


def test_all_original_hypothesis_identities_are_retained():
    assert {c['id'] for c in load_assessment('banking')['candidates']}=={'RCO-LBG-'+str(n).zfill(3) for n in range(1,10)}
    assert {c['id'] for c in load_assessment('aviation')['candidates']}=={'RCO-EJ-'+str(n).zfill(3) for n in range(1,7)}
