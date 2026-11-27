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
    assert {k:v for k,v in new_review.items() if k!='baseline_digest'}=={k:v for k,v in old_review.items() if k!='baseline_digest'}
    allowed.add(review_path)
    assert set(changed)<=allowed,changed
    # Original source files, asset identities, rights, financial holds and
    # historical records are preserved; this returns the immutable prior cut
    # so older 39-claim/7-source assertions continue to check their own release.
    return baseline
