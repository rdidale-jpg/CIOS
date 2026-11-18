"""Read-only documentary QA. No admission, model, finance-run or Pipeline engine."""
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE='df475865cc367a28f355c38bc4c23054abe88502'
sys.path.insert(0,str(ROOT))
STATUSES={'eligible_already_presented','eligible_not_presented','researched_awaiting_admission','missing_requires_enrichment','uncertain_stale_contradictory'}


def read(name):return json.loads((HERE/name).read_text())


def index(rows,key='id'):
    result={r[key]:r for r in rows}
    assert len(result)==len(rows),'Duplicate owner-qualified identity'
    return result


def research_available(claim,sources):
    """Documentary dependency check, never public-use or canonical authority."""
    from cios.applications.flora.research_intelligence.source_import import working_restricted
    return not working_restricted(claim) and all(
        sid in sources and not working_restricted(sources[sid])
        and sources[sid]['verification']=='direct_primary_review'
        for sid in claim['source_ids'])


def fixed_calculation(row):
    """Recompute four cited comparisons, not a generic financial engine."""
    spec={'CAA-DELTA':(['W-CAA'],'percentage_change','percent','journeys'),
          'NG-UK':(['W-NG'],'sum','GBP','million'),
          'NG-SHARE':(['W-NG'],'ratio_percent','percent',None),
          'NV-DELTA':(['W-NV2','W-NV3'],'percentage_change','USD','billion')}
    ids,op,unit,scale=spec[row['id']]
    assert row['source_ids']==ids and row['operation']==op
    assert row.get('currency',row.get('unit'))==unit,'Wrong unit/currency'
    assert row.get('scale')==scale,'Wrong scale'
    assert row['perimeter'] and row['not']
    a,b=map(Decimal,row['inputs'])
    assert a.is_finite() and b.is_finite() and b>0
    val=a+b if op=='sum'else a/b*100 if op=='ratio_percent'else(a/b-1)*100
    if 'expected_rounded'in row:assert val.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)==Decimal(row['expected_rounded'])
    else:assert val==Decimal(row['expected'])
    return str(val)


def claim_integrity(c,sources):
    assert c['source_ids'] and set(c['source_ids'])<=set(sources)
    assert all(sources[s]['verification']=='direct_primary_review'for s in c['source_ids']),'Unverified acquisition used as factual support'
    assert c['authority']=='research_candidate_not_canonical'
    assert c['canonical_evidence_id']is None
    for k in ('public_eligible','public_permission_granted','observation_imported','material_pressure_qualified','pipeline_created'):assert c[k]is False,'Authority/promotion was not authorised'
    assert c['semantic_type']in {'reported','calculated','estimated','assumed','insight','hypothesis'}
    assert c['subject']and c['period']and c['caveat']
    if c['semantic_type']in {'insight','hypothesis'}:assert c['reasoning']and c['falsifier']


def temporal_integrity(claims,sources):
    c=index(claims)
    expected={'C-RATE':'2026-11-04','C-MORTGAGE':'2026-07-28','C-EJ-SFP':'2023-11-03','C-EJ-ICC':'2024-05-22','C-BT-CHANGE':'2026-10-05','C-IFR':'2026-07-01'}
    for key,day in expected.items():assert c[key]['event_date']==day and c[key]['event_kind'],'Known event date lost or collapsed'
    assert c['C-RATE']['event_date']!=sources['W-BOE']['published']
    assert c['C-MORTGAGE']['effective_date']is None and c['C-IFR']['effective_date']is None
    assert c['C-BT-CHANGE']['events'][1]['occurred_on']is None


def coverage_integrity(c):
    rows=c['requirements'];index(rows,'key')
    assert {r['status']for r in rows}<=STATUSES
    for r in rows:
        assert r['existing_owner']and r['next_source']and r['owner_action']and r['affected_question']and r['materiality']
        if r['family']=='national'and r['information_element']=='economics':
            assert 'slice only'in r['requirement']and r['residual_demands'],'A GVA slice is not whole economic coverage'
        if r['family']=='technology'and r['scope']=='enterprise_profile':
            assert 'discovery_leads_not_verified_closure_sources'in r
            assert r['next_source']not in r['discovery_leads_not_verified_closure_sources'],'A first link is not an element-appropriate closure'
    claims=index(c['claim_coverage'],'key')
    for name in ('AV-FLEET','AV-NETWORK','AV-MRO','AV-CHAT'):
        row=next(r for k,r in claims.items()if k.endswith('::'+name))
        assert row['status']=='eligible_already_presented'and row['projection_owner']=='easyjet_capabilities.fact'and row['presentation_proof'],'Pinned editorial projection was lost by raw-text matching'
    for r in claims.values():
        if r['adapter_eligible']and not r['presentation_proof']:
            assert r['status']=='uncertain_stale_contradictory'and r['requires_new_research']is False
    return len(rows)


def validate():
    files=read('File-Inventory.json');paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
    assert files['base']==BASE and {r['path']for r in files['files']}==set(paths)
    for r in files['files']:
        b=(ROOT/r['path']).read_bytes();assert len(b)==r['bytes']and sha256(b).hexdigest()==r['sha256'],'Existing file changed: '+r['path']
    archives=read('Archive-and-Record-Presence.json');assert 'Selected'in archives['record_extraction_scope']
    members=ndjson=0
    for a in archives['archives']:
        with zipfile.ZipFile(ROOT/a['path'])as z:
            assert {m['path']for m in a['members']}=={n for n in z.namelist()if not n.endswith('/')}
            for m in a['members']:
                b=z.read(m['path']);assert len(b)==m['bytes']and sha256(b).hexdigest()==m['sha256'];members+=1
                if m['path'].endswith(('.ndjson','.jsonl')):
                    count=sum(bool(x.strip())for x in b.decode().splitlines());assert count==m['ndjson_rows'];ndjson+=count
    packaged=read('Packaged-Record-Rows.json')['rows']
    assert len(packaged)==ndjson
    for row in packaged:
        archive,member=row['owner'].split('::',1)
        with zipfile.ZipFile(ROOT/archive)as z:
            line=z.read(member).decode().splitlines()[row['line']-1]
            assert sha256(line.encode()).hexdigest()==row['row_sha256']and row['state']=='packaged_row_not_live_record'
    subjects=read('Subjects.json')['subjects'];index(subjects,'key')
    tech=[r for r in subjects if r['level']=='enterprise_profile'and r['family']=='technology']
    assert len(tech)==80 and all(r['depth']=='partial profile'and r['object_kind']=='unbound_provider_or_brand'for r in tech)
    assert not any(r['family']=='transport'for r in subjects),'TMS means Telecoms/Media/Sport'
    tms=[r for r in subjects if 'TMS-001_Final_Package/02_priority_enterprise_twins.json'in r['owner']];assert len(tms)==14
    c=read('Coverage-and-Gaps.json');requirements=coverage_integrity(c)
    refs=read('Retained-Source-References.json')['references']
    assert all(r['status']in {'retained_reference_not_independently_verified_by_inventory','citation_lead_only_not_source_verification_or_permission'}for r in refs)
    sources=index(read('Wave-1-Sources.json')['sources'])
    for s in sources.values():
        u=urlsplit(s['url']);assert u.scheme=='https'and not u.username and not u.password
        b=(HERE/s['excerpt_path']).read_bytes();assert sha256(b).hexdigest()==s['excerpt_sha256']and len(b.decode().split())<=25
        assert s['original_content_sha256']is None and not s['original_bytes_retained']and not s['canonical_acceptance']
        assert s['public_projection']=='not_integrated'and not s['rights']['public_permission_added']
        if s['published']:assert s['published']<='2026-11-18'
    claims=read('Wave-1-Claims.json')['claims'];index(claims)
    for claim in claims:claim_integrity(claim,sources)
    temporal_integrity(claims,sources)
    design=read('Design-Reconciliation.json')
    assert len(index(design['requirements'],'design_requirement'))==16
    claim_ids={c['id']for c in claims}
    assert all(set(r['wave_claim_refs'])<=claim_ids for r in design['requirements'])
    assert design['base']==BASE
    pinned=subprocess.check_output(['git','show',design['head']+':'+design['source_path']],cwd=ROOT)
    assert sha256(pinned).hexdigest()==design['source_sha256']
    values={r['id']:fixed_calculation(r)for r in read('Financial-and-Temporal-QA.json')['calculations']}
    links=0
    for doc in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
            if target.startswith('https://'):continue
            assert (doc.parent/target.split('#')[0]).resolve().is_file(),'Missing link: '+target;links+=1
    changes=subprocess.check_output(['git','diff','--name-status',BASE,'HEAD'],cwd=ROOT,text=True).splitlines()
    for line in changes:
        status,path=line.split('\t',1);assert status=='A'and(path.startswith('docs/flora-runtime/research-enrich-all-681/')or path=='tests/test_flora_research_enrich_all_681.py'),'Out-of-scope mutation'
    return dict(head_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),base=BASE,baseline_files=len(paths),archives=len(archives['archives']),archive_members=members,ndjson_rows=ndjson,selected_heuristic_records=len(archives['records']),source_reference_occurrences=len(refs),subject_occurrences=len(subjects),requirements=requirements,overlay_claim_rows=len(c['claim_coverage']),public_paths=len(read('Public-Routes.json')['routes']),server_main_probes=len(read('Render-Probes.json')['probes']),wave_sources=len(sources),direct_primary_reviews=sum(s['verification']=='direct_primary_review'for s in sources.values()),wave_claims=len(claims),calculations=values,links=links,scope='research_QA_not_source_admission_or_production_verification',canonical_writes=0,runtime_changes=0)


if __name__=='__main__':print(json.dumps(validate(),indent=2))
