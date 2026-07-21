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
    required={'CA-001','FP-010','FP-012','FP-009','ADR-016','ADR-014','ADR-024','REF-001','PRINCIPLES-001','CURRENT-PROGRAMME-STATE','WP-011','FEIR-001','EIRP-001','EI-001','EI-002','EI-003','EI-012','EIF-001','KPS-001','CA-OG-001','CA-TEMPLATE-001','CA-SOURCE-MAP'}
    assert required <= ids
    authorities={d['authority'] for d in ds}
    assert {'runtime-baseline','programme-state','operating-guidance','template','source-map','enterprise-intelligence-authority'} <= authorities
    for d in ds:
        src=ROOT/d['source_path']
        assert src.exists(), d
        assert hashlib.sha256(src.read_bytes()).hexdigest()==d['checksum']
    assert [d for d in ds if d['document_id']=='FP-010'][0]['source_path']=='architecture/founding-papers/FP-010-Knowledge-Pack-Architecture.md'
    assert [d for d in ds if d['document_id']=='FP-012'][0]['source_path']=='architecture/founding-papers/FP-012-Enterprise-Reinvention-Intelligence.md'

def test_recommendation_readiness_and_programme_state_freshness_use_current_programme_state():
    ds=docs(); by={d['document_id']:d for d in ds}
    handbook=(ROOT/by['CA-001']['source_path']).read_text()
    programme=(ROOT/by['CURRENT-PROGRAMME-STATE']['source_path']).read_text()
    roadmap=by['ROADMAP-001']
    assert 'No strong Recommendation without inspectable lineage' in handbook
    assert '**Last updated:** 2026-07-21' in programme
    assert 'Roadmaps are planning inputs only' in programme
    assert roadmap['authority']=='proposed-context'
    assert roadmap['inclusion_reason']!='Programme-state freshness source'

def test_runtime_programme_sources_are_not_absent_or_placeholder_like():
    ds=docs(); by={d['document_id']:d for d in ds}
    for did in ['CURRENT-PROGRAMME-STATE','WP-011','FEIR-001','EIRP-001','ADR-014','ADR-024']:
        text=(ROOT/by[did]['source_path']).read_text(errors='ignore')
        assert len(text.strip()) > 400
        assert not text.strip().lower().startswith('placeholder')
        assert text.strip() != 'TBD'

def test_deterministic_build_zip_checksum_index_pack_state_and_completeness_matrix():
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
    for needed in ['DOCUMENT-INDEX.md','PACK-STATE.md','checksums.sha256','handbook/CIOS-Chief-Architect-Handbook.md','architecture/FP-010-Knowledge-Pack-Architecture.md','programme/CURRENT-PROGRAMME-STATE.md','runtime/Flora-Runtime-Capability-Baseline.md','runtime/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md','runtime/EIRP-001-Enterprise-Intelligence-Reasoning-Pipeline-Specification.md','enterprise-intelligence/EI-001-Enterprise-Model-Specification.md','source-map.yaml','templates/Architecture-Decision-Review-Template.md','operating-guidance/Chief-Architect-Operating-Guidance.md']:
        assert needed in names
    assert 'Recommendation readiness: passed' in pack_state
    assert 'runtime_baseline:' in pack_state
    assert 'document: Flora Runtime Capability Baseline' in pack_state
    assert 'Runtime architecture and runtime implementation evidence: included' in pack_state
    assert 'Programme-state freshness: passed' in pack_state
    assert 'Roadmap freshness proxy: rejected' in pack_state
    assert '## WP-012 completeness matrix' in pack_state
    for criterion in ['Programme-state baseline','Runtime-baseline authority','Runtime implementation evidence','Operating guidance','Templates','Source map','Core Enterprise Intelligence authorities','Placeholder rejection']:
        assert criterion in pack_state
