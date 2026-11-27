"""Finite additive-research exception to earlier presentation-only scope tests."""
import json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='201fe851a531ecb854d3ba8e3416bc667ab8c860'
DATA='enterprise-knowledge/banking/research-model/Assessment-Overlay.json'
SOURCES={'LCE-WORKFORCE','LCE-ANNUAL-OPERATIONS','LCE-VERTEX','LCE-DELIVERY','LCE-BOARD','LCE-SETTLEMENT','LCE-LAUNCH'}

def preserved_research_cut():
    from cios.applications.flora.research_intelligence import model
    from cios.applications.flora import lloyds_gold as g
    baseline=json.loads(subprocess.check_output(['git','show',BASE+':'+DATA],cwd=ROOT))
    current=model.load_assessment()
    for key,value in baseline.items():
        if key in {'sources','claims','suppliers','relationships'}:assert current[key][:len(value)]==value,key
        else:assert current[key]==value,key
    new_sources=current['sources'][len(baseline['sources']):]
    new_claims=current['claims'][len(baseline['claims']):]
    assert {s['id'] for s in new_sources}==SOURCES
    assert {c['id'] for c in new_claims}=={'LBG-CE-'+k for k in g.CEO_KEYS}
    assert len(new_sources)==7 and len(new_claims)==58
    assert all(set(c['source_ids'])<=SOURCES for c in new_claims)
    assert all(c['asset_id']=='BK-ENT-001' and c['entity_scope']==g.recovery.GROUP for c in new_claims)
    assert {s['id'] for s in current['suppliers'][len(baseline['suppliers']):]}=={'SUP-VISA','SUP-ARCHAX','SUP-CAURA','SUP-PLANNA'}
    assert {r['id'] for r in current['relationships'][len(baseline['relationships']):]}=={'LCE-REL-'+k for k in ('VERTEX','VISAPILOT','ARCHAX','CAURA','PLANNARELATION')}
    changed=subprocess.check_output(['git','diff','--name-only',BASE,'--','enterprise-knowledge'],cwd=ROOT,text=True).splitlines()
    allowed={DATA}|{'enterprise-knowledge/banking/research-model/source-snapshots/'+s+'.txt' for s in SOURCES}
    review_path='enterprise-knowledge/banking/research-model/Understanding-Review.json'
    from cios.applications.flora.research_intelligence.cycle import digest
    old_review=json.loads(subprocess.check_output(['git','show',BASE+':'+review_path],cwd=ROOT))
    new_review=json.loads((ROOT/review_path).read_text())
    assert old_review['baseline_digest']==digest(baseline)
    assert new_review['baseline_digest']==digest(current)
    assert {k:v for k,v in new_review.items() if k not in {'baseline_digest','sources'}}=={k:v for k,v in old_review.items() if k not in {'baseline_digest','sources'}}
    assert len(new_review['sources'])==len(old_review['sources'])
    rebound=[]
    for before,after in zip(old_review['sources'],new_review['sources']):
        assert {k:v for k,v in before.items() if k!='assessment_digest'}=={k:v for k,v in after.items() if k!='assessment_digest'}
        if 'assessment_digest' in before:
            assert before['assessment_digest']==old_review['baseline_digest']
            assert after['assessment_digest']==new_review['baseline_digest']
            rebound.append(before['id'])
        else:assert before==after
    assert set(rebound)=={'DEPTH-LBG-AI','DEPTH-LBG-LEGACY','DEPTH-LBG-WALLET','DEPTH-LBG-CURVE'}
    allowed.add(review_path)
    allowed.update({'enterprise-knowledge/banking/research-model/source-snapshots/PFI-Lloyds-Q326.json','enterprise-knowledge/banking/research-model/source-snapshots/LEI-Lloyds-H126.json'})
    original_facts=json.loads(subprocess.check_output(['git','show','8be67e3d49ad17886c1cc14da3c646271b21017e:enterprise-knowledge/banking/research-model/source-snapshots/PFI-Lloyds-Q326.json'],cwd=ROOT))['fact_bindings']
    current_facts=json.loads((ROOT/'enterprise-knowledge/banking/research-model/source-snapshots/PFI-Lloyds-Q326.json').read_text())['fact_bindings']
    for a,b in zip(original_facts,current_facts):
        assert a['key']==b['key'] and all(b['facts'][k]==v for k,v in a['facts'].items())
    assert set(changed)<=allowed,changed
    # Original source files, asset identities, prior research rights and
    # historical records are preserved; this returns the immutable prior cut
    # so older 39-claim/7-source assertions continue to check their own release.
    return baseline
