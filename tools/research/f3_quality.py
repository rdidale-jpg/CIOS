"""F3 owner-review arithmetic and current-policy audit. No source grants/writes.

Original issuer assertions live only in the owner-review pack, never an app
source adapter or seller renderer. Successful QA is not source-use permission.
"""
from collections import Counter
from decimal import Decimal
import inspect
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from cios.applications.flora.financial_intelligence import candidate_analytics as f
from cios.applications.flora.research_intelligence.source_use_review import SeriesUseProposal,SeriesUseRequest,assess_proposed_use,inspect_current_origin
from cios.applications.flora.enterprise_intelligence.models import stable_hash

PACK=ROOT/'docs/flora-runtime/f3-646'
BASE='45f7e32676769a5829d8a9399c0b8c4f3ddb7b0b'


def load(name):return json.loads((PACK/name).read_text())


def validate():
    sources=load('Source-Use-Register.json');banks=load('Five-Bank-Candidates.json')
    proposals=[SeriesUseProposal.model_validate(p) for p in load('Series-Use-Proposals.json')]
    assert len(sources)==len(banks)==len(proposals)==5
    assert len({s['source_id'] for s in sources})==len({b['id'] for b in banks})==5
    source_by_id={s['source_id']:s for s in sources}
    counts=Counter();bank_results={}
    for bank,proposal in zip(banks,proposals):
        source=source_by_id[bank['source_id']]
        assert source['review_record_revision']==stable_hash({k:v for k,v in source.items() if k!='review_record_revision'})
        assert source['original_bytes_sha256']is None and not source['retained_original_bytes'] and not source['retained_full_text']
        assert not source['current_permission_granted'] and source['rights_status']=='unresolved_for_proposed_commercial_uses'
        assert inspect_current_origin(source['original_url'])['origin_admission']==('current_origin_check_passed' if source['source_id']=='F3-NB-REVIEW' else 'blocked')
        assert bank['resource_ref']is None and bank['authority']=='owner_review_candidate_not_admitted_or_canonical'
        states=bank['states']
        assert not any(states[k] for k in ('source_use_eligible','technical_origin_admitted','resource_authority_bound','financial_run_persisted','actually_visible'))
        assert states['canonical_acceptance']=='not_requested'
        rows=[f.Measurement.model_validate(m) for m in bank['measurements']]
        assert len({r.measurement_id for r in rows})==len(rows)
        for row in rows:
            assert row.source.owner=='unadmitted_owner_review' and row.source.source_revision==source['review_record_revision']
            assert row.source.url==source['original_url'] and row.source.published==(None if source['publication_date']is None else __import__('datetime').date.fromisoformat(source['publication_date']))
            assert row.subject_id.startswith('research-subject:') and row.semantic_type=='reported'
            assert f.Measurement.model_validate_json(row.model_dump_json())==row
        values=[]
        for record in bank['recipes']:
            assert record['contract']=='Reconciliation'
            recipe=f.Reconciliation.model_validate(record['recipe'])
            result=f.reconcile(recipe,rows)
            assert result['value']==record['expected_value'] and result['canonical_status']=='derived_view_not_canonical'
            values.append(result['value']);counts['reconciliations']+=1
        assert bank['counter_evidence'] and bank['gaps'] and bank['context']
        request=SeriesUseRequest(category=proposal.category,publisher=proposal.publisher,document_url=source['original_url'],
            reporting_subject=bank['reported_subject'],terms_review_record_revision=source['review_record_revision'],purpose=proposal.purpose,
            uses=('numerical_reuse','measurement_retention','seller_display'),audience='private_seller',retained_form='minimal_measurements_and_provenance',
            measurements_in_document=len(rows),documents_in_window=1,cumulative_extraction_review='No recurring collection executed; future cumulative scope requires legal/source review.',as_of='2026-11-16')
        disposition=assess_proposed_use(proposal,request)
        assert disposition['authority']=='proposed_review_only_not_source_permission'
        assert disposition['disposition']in {'owner_decision_required','exception_review_required'}
        assert disposition['technical_admission']==disposition['canonical_acceptance']=='not_granted'
        counts['typed_measurements']+=len(rows)
        bank_results[bank['id']]={'typed':len(rows),'offline_reconciliations':values,'origin':'blocked','review':disposition['disposition'],'persisted_issuer_runs':0,'visible_issuer_runs':0}
    assert counts=={'typed_measurements':32,'reconciliations':5}
    # Independent paper reconciliation, not a financial-perimeter override.
    starling=banks[-1];assert starling['id']=='starling'
    assert Decimal('887.4')-Decimal('940.0')==Decimal(starling['review_arithmetic'][0]['value'])
    assert Decimal('217.1')-Decimal('223.4')==Decimal(starling['review_arithmetic'][1]['value'])
    assert len({m['perimeter'] for m in starling['measurements']})==2
    assert f.permitted_selection_keys()==('boe-household-deposit-stocks','nationwide-fy2026')
    actual=f._run_record('boe-household-deposit-stocks',f._current_inputs('boe-household-deposit-stocks'),'synthetic-f3-compatibility')
    assert actual==load('F1-Compatibility.json')
    protected=['cios/applications/flora/research_intelligence/source_import.py','cios/applications/flora/live/source_registry.py',
        'cios/applications/flora/memory/source_contracts.py','cios/applications/flora/public_routes.py','cios/applications/flora/security_web.py',
        'cios/applications/flora/visual_streams.py','cios/applications/flora/visual_panels.py',
        'tools/ci/flora-baseline-v1.json','tools/ci/flora_ci.py','tools/research/history_integrity.py',
        'architecture/decisions/ADR-027-Document-Scoped-Publisher-Admission-Proposal.md',
        'docs/flora-runtime/eai1-628/Eight-Evidence-Review-Proposals.json']
    for path in protected:
        previous = subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
        if (ROOT/path).read_bytes() != previous:
            from tools.research.rud1_compatibility import assert_evolution
            assert_evolution(ROOT, path, previous)
    # Existing admitted-source and run-ownership boundaries remain exact.
    original=subprocess.check_output(['git','show',BASE+':cios/applications/flora/financial_intelligence/candidate_analytics.py'],cwd=ROOT,text=True)
    import ast
    old=ast.parse(original);current=ast.parse(inspect.getsource(f))
    for name in ('create_run','find_existing_run','read_analysis'):
        one=lambda tree:ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name),include_attributes=False)
        assert one(old)==one(current),name
    # RUD's Source adapter and projection now add routine lawful research.
    # Preserve the original BoE adapter AST and exact persisted v1 identity.
    old_adapter = next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='_current_inputs')
    new_adapter = next(n for n in current.body if isinstance(n,ast.FunctionDef) and n.name=='_boe_inputs')
    new_adapter.name = '_current_inputs'
    assert ast.dump(old_adapter,include_attributes=False)==ast.dump(new_adapter,include_attributes=False)
    from tools.research.rud1_compatibility import assert_evolution
    path='cios/applications/flora/financial_intelligence/candidate_analytics.py'
    assert_evolution(ROOT,path,original.encode())
    return {'status':'PARTIAL F3','banks':bank_results,**counts,'new_issuer_permissions':0,'new_issuer_persisted_runs':0,'new_issuer_runtime_visibility':0,
        'canonical_promotions':0,'production_writes':0,'paid_calls':0,'current_BoE_identity_unchanged':True,
        'scope':'Offline typed/arithmetic review and source-use proposals, not a five-bank rollout'}


if __name__=='__main__':print(json.dumps(validate(),ensure_ascii=False,indent=2))
