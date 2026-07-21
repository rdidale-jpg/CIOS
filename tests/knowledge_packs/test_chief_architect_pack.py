from pathlib import Path
import hashlib, subprocess, zipfile
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'knowledge-packs/chief-architect/manifest.yaml'

def docs():
    out=[]; cur=None
    for line in MANIFEST.read_text().splitlines():
        if line.startswith('  - '):
            cur={}; out.append(cur); line='    '+line[4:]
        if cur is not None and line.startswith('    '):
            k,v=line.strip().split(': ',1); cur[k]=v
    return out

def test_manifest_completeness_sources_and_shared_authorities():
    ds=docs(); ids={d['document_id'] for d in ds}
    assert {'CA-001','FP-010','FP-012','ADR-016','REF-001','PRINCIPLES-001','ROADMAP-001'} <= ids
    for d in ds:
        src=ROOT/d['source_path']
        assert src.exists(), d
        assert hashlib.sha256(src.read_bytes()).hexdigest()==d['checksum']
    assert [d for d in ds if d['document_id']=='FP-010'][0]['source_path']=='architecture/founding-papers/FP-010-Knowledge-Pack-Architecture.md'
    assert [d for d in ds if d['document_id']=='FP-012'][0]['source_path']=='architecture/founding-papers/FP-012-Enterprise-Reinvention-Intelligence.md'

def test_recommendation_readiness_and_programme_state_freshness():
    handbook=(ROOT/'architecture/handbook/CIOS-Chief-Architect-Handbook.md').read_text()
    assert 'No strong Recommendation without inspectable lineage' in handbook
    assert '**Last updated:** 2026-07-21' in handbook

def test_deterministic_build_zip_checksum_index_and_pack_state():
    cmd=['python3','tools/knowledge-packs/build_pack.py','--profile','chief-architect']
    subprocess.check_output(cmd,cwd=ROOT,text=True)
    zip_path=ROOT/'dist/CIOS-Chief-Architect-Knowledge-Pack-v1.0.0.zip'
    h1=hashlib.sha256(zip_path.read_bytes()).hexdigest()
    subprocess.check_output(cmd,cwd=ROOT,text=True)
    h2=hashlib.sha256(zip_path.read_bytes()).hexdigest()
    assert h1==h2
    with zipfile.ZipFile(zip_path) as z:
        names=set(z.namelist())
        pack_state=z.read('PACK-STATE.md').decode()
    for needed in ['DOCUMENT-INDEX.md','PACK-STATE.md','checksums.sha256','handbook/CIOS-Chief-Architect-Handbook.md','architecture/FP-010-Knowledge-Pack-Architecture.md']:
        assert needed in names
    assert 'Recommendation readiness: passed' in pack_state
    assert 'Programme-state freshness: passed' in pack_state
