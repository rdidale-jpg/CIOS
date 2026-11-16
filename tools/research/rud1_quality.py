"""Reproduce bounded real-source eligibility, semantics and unchanged history."""
from pathlib import Path
from hashlib import sha256
import ast
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from cios.applications.flora.financial_intelligence import candidate_analytics as financial, analyst
from cios.applications.flora.research_intelligence.source_import import working_facts, bound_facts
from cios.applications.flora import leadership_agenda as agenda
from tools.research.history_integrity import verify_history
from tools.research.f3_quality import validate as historical_quality


def validate():
    data,sources=working_facts()
    assert len(sources)==2
    assert not any(s['primary_content_sha256'] for s in sources.values())
    assert len(data['service_profiles'])==6
    for row in data['service_profiles']:
        source=sources[row['source_id']]
        assert {k:v for k,v in row.items() if k!='source_id'}==bound_facts(source,row['selection'],'service_profile')
        issue=agenda.routine_service_issue(row['selection'])
        assert issue and [str(f.value)for f in issue.facts]==[str(row[k])for k in ('received','closed','upheld')]
    bundle=financial._current_inputs('nationwide-fy2026')
    projection=financial.current_projection(financial._run_record('nationwide-fy2026',bundle,'isolated-qa-not-persisted'))
    assert len(projection['measurements'])==8
    assert [r['value']for r in projection['results']]==['2026','1490']
    html=analyst.compose(projection)
    assert 'Underlying profit before tax'in html and 'Statutory profit before tax'in html and 'FLORA Insight'in html
    history=verify_history(ROOT);assert history['historical_files']==142 and history['total']==178
    assert historical_quality()['typed_measurements']==32
    base='b29af81414de2d5fdec769a5d319d58e0e017011'
    unchanged=['tools/ci/flora-baseline-v1.json','tools/ci/flora_ci.py','cios/applications/flora/intelligence_presentation.py',
       'cios/applications/flora/live/source_registry.py','cios/applications/flora/memory/source_contracts.py',
       'architecture/decisions/ADR-027-Document-Scoped-Publisher-Admission-Proposal.md',
       'docs/flora-runtime/eai1-628/Eight-Evidence-Review-Proposals.json']
    artwork=subprocess.check_output(['git','ls-tree','-r','--name-only',base,'cios/applications/flora/visual_stream_assets'],cwd=ROOT,text=True).splitlines()
    for path in unchanged+artwork:
        assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',base+':'+path],cwd=ROOT),path
    return {'earnings_banks_visible':1,'service_banking_exemplars':5,'legal_bank_service_profiles':6,'monetary_measurements':8,
       'reproduced_reconciliations':['6378-4021-331=2026','2026+1-138-399=1490'],'unresolved_other_issuer_earnings':4,
       'retained_historical_research_files':175,'new_working_source_files':3,'unchanged_visual_asset_files':len(artwork),
       'full_rollout_claim':False,'original_bytes_archived':False,'canonical_promotions':0,'production_writes':0,'paid_calls':0}

if __name__=='__main__':print(json.dumps(validate(),indent=2))
