from pathlib import Path
from datetime import date, timedelta
import hashlib, subprocess, zipfile
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'knowledge-packs/chief-architect/manifest.yaml'

def docs():
    out=[]; cur=None
    for line in MANIFEST.read_text().splitlines():
        if line.startswith('  - '):
            cur={}; out.append(cur); line='    '+line[4:]
        if cur is not None and line.startswith('    ') and ': ' in line:
            k,v=line.strip().split(': ',1); cur[k]=v
    return out

def test_required_chief_architect_sources_and_authority():
    ds=docs(); ids={d['document_id'] for d in ds}
    required={'RP-003','CAI-001','CAOG-001','EI-001','EI-002','EI-003','EI-012','FP-009','FEIR-001','EIRP-001','WP-011-RUNTIME-BASELINE','PROGRAMME-STATE'}
    assert required <= ids
    allowed={'canonical_architecture','accepted_decision','operating_guidance','runtime_baseline','programme_state','template','reference'}
    assert len(ids)==len(ds)
    for d in ds:
        assert d['authority'] in allowed
        src=ROOT/d['source_path']
        assert src.exists(), d
        assert hashlib.sha256(src.read_bytes()).hexdigest()==d['checksum']
        if d['authority']=='canonical_architecture':
            assert d['source_path'].startswith('architecture/')

def test_not_every_markdown_is_implicitly_copied_and_runtime_baseline_included():
    subprocess.check_output(['python3','tools/knowledge-packs/build_pack.py','--profile','chief-architect'],cwd=ROOT,text=True)
    zip_path=ROOT/'dist/CIOS-Chief-Architect-Knowledge-Pack-v1.0.0.zip'
    with zipfile.ZipFile(zip_path) as z:
        names=set(z.namelist())
    assert 'programme/Flora-Runtime-Capability-Baseline.md' in names
    assert 'DOCUMENT-INDEX.md' in names
    assert 'PACK-STATE.md' in names
    assert not any(n.startswith('enterprise-knowledge/banking/') for n in names)
    assert 'architecture/programmes/cios-architecture-v2/PHASE-1-CONFLICT-AND-RECONCILIATION-REPORT.md' not in names

def test_programme_state_required_fields_and_instructions_rules():
    ps=(ROOT/'knowledge-packs/chief-architect/programme/CURRENT-PROGRAMME-STATE.md').read_text()
    for phrase in ['programme_state_version:','as_of:','owner:','Flora operational','Banking is the strongest demonstrable journey','UK Government/MOD validation is in progress','Market Participant Twin runtime is planned']:
        assert phrase in ps
    inst=(ROOT/'knowledge-packs/chief-architect/configuration/Chief-Architect-GPT-Instructions.md').read_text()
    for phrase in ['Programme-state rule','Existing-capability rule','Evidence rule','Commercial-delta rule','Authority rule','Staleness rule','Human-state rule']:
        assert phrase in inst

def test_generated_index_checksums_and_determinism():
    subprocess.check_output(['python3','tools/knowledge-packs/build_pack.py','--profile','chief-architect'],cwd=ROOT,text=True)
    zip_path=ROOT/'dist/CIOS-Chief-Architect-Knowledge-Pack-v1.0.0.zip'
    h1=hashlib.sha256(zip_path.read_bytes()).hexdigest()
    subprocess.check_output(['python3','tools/knowledge-packs/build_pack.py','--profile','chief-architect'],cwd=ROOT,text=True)
    h2=hashlib.sha256(zip_path.read_bytes()).hexdigest()
    assert h1==h2
    with zipfile.ZipFile(zip_path) as z:
        index=z.read('DOCUMENT-INDEX.md').decode()
        checks=z.read('checksums.sha256').decode().splitlines()
        names=set(z.namelist())
        for d in docs():
            assert d['document_id'] in index
            assert d['pack_path'] in names
        for row in checks:
            expected,name=row.split('  ',1)
            assert hashlib.sha256(z.read(name)).hexdigest()==expected

def test_stale_programme_state_detection(tmp_path):
    ps=ROOT/'knowledge-packs/chief-architect/programme/CURRENT-PROGRAMME-STATE.md'
    original=ps.read_text()
    stale=(date.today()-timedelta(days=30)).isoformat()
    try:
        ps.write_text(original.replace('as_of: 2026-07-21',f'as_of: {stale}'))
        # checksum must be updated for this focused freshness check
        manifest=MANIFEST.read_text()
        old=[d for d in docs() if d['document_id']=='PROGRAMME-STATE'][0]['checksum']
        new=hashlib.sha256(ps.read_bytes()).hexdigest()
        MANIFEST.write_text(manifest.replace(old,new))
        out=subprocess.check_output(['python3','tools/knowledge-packs/build_pack.py','--profile','chief-architect'],cwd=ROOT,text=True)
        assert 'freshness=stale' in out
        with zipfile.ZipFile(ROOT/'dist/CIOS-Chief-Architect-Knowledge-Pack-v1.0.0.zip') as z:
            assert 'PROGRAMME STATE STALE' in z.read('PACK-STATE.md').decode()
    finally:
        ps.write_text(original)
        # restore manifest checksum
        text=MANIFEST.read_text()
        restored=hashlib.sha256(ps.read_bytes()).hexdigest()
        text=text.replace(hashlib.sha256((original.replace('as_of: 2026-07-21',f'as_of: {stale}')).encode()).hexdigest(), restored)
        MANIFEST.write_text(text)
