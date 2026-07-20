from pathlib import Path
import hashlib, subprocess, zipfile
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'knowledge-packs/researcher/manifest.yaml'

def docs():
    out=[]; cur=None
    for line in MANIFEST.read_text().splitlines():
        if line.startswith('  - '):
            cur={}; out.append(cur); line='    '+line[4:]
        if cur is not None and line.startswith('    '):
            k,v=line.strip().split(': ',1); cur[k]=v
    return out

def test_manifest_completeness_and_sources():
    ds=docs(); ids={d['document_id'] for d in ds}
    required={'RG-001','RKI-001','RKI-003','EI-001','EI-002','EI-003','EI-012','FP-009','FP-010','FP-012','ADR-016','MISSION-UKCG-001'}
    assert required <= ids
    for d in ds:
        src=ROOT/d['source_path']
        assert src.exists(), d
        assert hashlib.sha256(src.read_bytes()).hexdigest()==d['checksum']

def test_fp_identity_and_no_stale_paths():
    ds=docs()
    assert [d for d in ds if d['document_id']=='FP-010'][0]['source_path']=='architecture/founding-papers/FP-010-Knowledge-Pack-Architecture.md'
    assert [d for d in ds if d['document_id']=='FP-012'][0]['source_path']=='architecture/founding-papers/FP-012-Enterprise-Reinvention-Intelligence.md'
    assert not any('obsolete' in d['source_path'].lower() or 'collision' in d['source_path'].lower() for d in ds)

def test_required_content_and_instruction_ownership():
    text=(ROOT/'knowledge-packs/researcher/configuration/Researcher-GPT-Instructions.md').read_text()
    for phrase in ['Research-ready','Architecture-ready','Human-supplied knowledge must record','No strong Recommendation may exist without inspectable lineage']:
        assert phrase in text
    rg=(ROOT/'knowledge-packs/researcher/operating-guidance/RG-001-Commercial-Digital-Twin-Research-Agent-Guide.md').read_text()
    for phrase in ['Minimum Research-ready gate','Supplier, contract and procurement checklist','Enduring Banking research-method lessons','Architecture handover requirements']:
        assert phrase in rg

def test_deterministic_build_and_zip_contents():
    cmd=['python3','tools/knowledge-packs/build_researcher_pack.py']
    a=subprocess.check_output(cmd,cwd=ROOT,text=True)
    zip_path=ROOT/'dist/CIOS-Researcher-Knowledge-Pack-v2.1.0.zip'
    h1=hashlib.sha256(zip_path.read_bytes()).hexdigest()
    b=subprocess.check_output(cmd,cwd=ROOT,text=True)
    h2=hashlib.sha256(zip_path.read_bytes()).hexdigest()
    assert h1==h2
    with zipfile.ZipFile(zip_path) as z:
        names=set(z.namelist())
    for needed in ['DOCUMENT-INDEX.md','checksums.sha256','configuration/Researcher-GPT-Instructions.md','missions/UK-Central-Government-Industry-Twin-Mission.md','architecture/EI-001-Enterprise-Model-Specification.md']:
        assert needed in names
    assert not any(n.startswith('enterprise-knowledge/banking/') for n in names)
