#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, shutil, zipfile, re
ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/'dist'
MANDATORY={'CA-001','FP-010','FP-012','FP-009','ADR-016','ADR-014','ADR-024','REF-001','PRINCIPLES-001','CURRENT-PROGRAMME-STATE','FEIR-001','EIRP-001','EI-001','EI-002','EI-003','EI-012','EIF-001','KPS-001','CA-OG-001','CA-TEMPLATE-001','CA-SOURCE-MAP'}
RUNTIME={'FEIR-001','EIRP-001','ADR-014','ADR-024'}
PROGRAMME={'CURRENT-PROGRAMME-STATE'}
AUTH={'accepted-adr','accepted-reference','founding-paper','enterprise-intelligence-authority','runtime-baseline','programme-state','operating-guidance','template','source-map','knowledge-pack-specification','handbook','proposed-context'}
PLACEHOLDER=re.compile(r'^(#\s*)?(TBD|TODO|placeholder|lorem ipsum)\s*$',re.I|re.M)

def parse_manifest(path):
    docs=[]; cur=None
    for line in path.read_text().splitlines():
        if line.startswith('  - '):
            cur={}; docs.append(cur); line='    '+line[4:]
        if cur is not None and line.startswith('    '):
            k,v=line.strip().split(': ',1); cur[k]=v
    return docs

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def is_placeholder(path):
    txt=path.read_text(errors='ignore')
    return len(txt.strip()) < 400 or bool(PLACEHOLDER.search(txt[:1200]))

def validate(profile, docs):
    if profile!='chief-architect':
        raise SystemExit(f'Unsupported profile: {profile}')
    ids={d['document_id'] for d in docs}
    missing=MANDATORY-ids
    if missing: raise SystemExit(f'Missing required documents: {sorted(missing)}')
    if any(d['document_id']=='ROADMAP-001' and d['authority']=='canonical' for d in docs):
        raise SystemExit('Flora Roadmap must not be canonical or a programme-state freshness source')
    for d in docs:
        src=ROOT/d['source_path']
        if not src.exists(): raise SystemExit(f'Missing source: {d["source_path"]}')
        if sha(src)!=d['checksum']: raise SystemExit(f'Checksum mismatch: {d["source_path"]}')
        if d.get('authority') not in AUTH: raise SystemExit(f'Invalid authority for {d["document_id"]}: {d.get("authority")}')
        if d['document_id'] in MANDATORY and is_placeholder(src): raise SystemExit(f'Placeholder or materially empty mandatory source: {d["source_path"]}')
    handbook=(ROOT/[d for d in docs if d['document_id']=='CA-001'][0]['source_path']).read_text(errors='ignore')
    if 'No strong Recommendation without inspectable lineage' not in handbook:
        raise SystemExit('Recommendation readiness doctrine is missing')
    programme=(ROOT/[d for d in docs if d['document_id']=='CURRENT-PROGRAMME-STATE'][0]['source_path']).read_text(errors='ignore')
    m=re.search(r'Last updated:\*\*\s*(\d{4}-\d{2}-\d{2})', programme)
    if not m or m.group(1)<'2026-07-21':
        raise SystemExit('Programme-state freshness is stale')
    if 'Roadmaps are planning inputs only' not in programme:
        raise SystemExit('Programme-state source must reject roadmap freshness proxy')

def index(docs):
    lines=['# Document Index','','Recommended reading sequence: Chief Architect Handbook; CURRENT-PROGRAMME-STATE; Operating Guidance; FP-010; ADR-016; runtime baseline; core EI authorities; templates and source map.','', '| Document ID | Title | Purpose | Authority | Required reading | Canonical source path | Packaged path |','|---|---|---|---|---|---|---|']
    for d in docs:
        req='required' if d['document_id'] in MANDATORY else 'context'
        lines.append(f"| {d['document_id']} | {d['title']} | {d['inclusion_reason']} | {d['authority']} | {req} | {d['source_path']} | {d['pack_path']} |")
    return '\n'.join(lines)+'\n'

def pack_state(docs):
    by={d['document_id']:d for d in docs}
    rows=[
('Programme-state baseline','CURRENT-PROGRAMME-STATE','programme/CURRENT-PROGRAMME-STATE.md'),
('Runtime-baseline authority','FEIR-001, EIRP-001, ADR-014, ADR-024','runtime/'),
('Operating guidance','CA-OG-001','operating-guidance/Chief-Architect-Operating-Guidance.md'),
('Templates','CA-TEMPLATE-001','templates/Architecture-Decision-Review-Template.md'),
('Source map','CA-SOURCE-MAP','source-map.yaml'),
('Core Enterprise Intelligence authorities','EI-001, EI-002, EI-003, EI-012, EIF-001','enterprise-intelligence/'),
('Knowledge Pack authority','FP-010, ADR-016, KPS-001','architecture/'),
('Recommendation doctrine','CA-001, FP-009, FP-012, EI-012','handbook/ and architecture/'),
('Roadmap not canonical freshness','ROADMAP-001','context/Flora-Roadmap.md authority=proposed-context'),
('Checksum validation','all manifest documents','checksums.sha256'),
('Placeholder rejection','all mandatory documents','build validation'),
]
    lines=['# Pack State','','Validation: passed','Recommendation readiness: passed','Programme-state freshness: passed','','## Validation evidence','','Mandatory runtime validation: passed','Mandatory programme-state validation: passed','Roadmap freshness proxy: rejected','Placeholder mandatory-source validation: passed','','## WP-012 completeness matrix','','| WP-012 deliverable / acceptance criterion | Packaged evidence | Location |','|---|---|---|']
    for a,b,c in rows: lines.append(f'| {a} | {b} | {c} |')
    lines+=['','## Packaged authorities','']
    for d in docs: lines.append(f"- {d['document_id']} — {d['authority']} — `{d['pack_path']}` — checksum `{d['checksum']}`")
    return '\n'.join(lines)+'\n'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--profile',required=True); args=ap.parse_args()
    pack=ROOT/'knowledge-packs'/args.profile; version=(pack/'VERSION').read_text().strip()
    docs=parse_manifest(pack/'manifest.yaml'); validate(args.profile, docs)
    stage=ROOT/'.tmp'/f'{args.profile}-pack-stage'
    if stage.exists(): shutil.rmtree(stage)
    stage.mkdir(parents=True)
    for extra in ['VERSION','README.md','manifest.yaml']:
        shutil.copy2(pack/extra, stage/extra)
    cfg=pack/'configuration/Chief-Architect-GPT-Instructions.md'
    (stage/'configuration').mkdir(exist_ok=True); shutil.copy2(cfg, stage/'configuration/Chief-Architect-GPT-Instructions.md')
    for d in docs:
        dest=stage/d['pack_path']; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT/d['source_path'], dest)
    (stage/'DOCUMENT-INDEX.md').write_text(index(docs))
    (stage/'PACK-STATE.md').write_text(pack_state(docs))
    checks=[f'{sha(p)}  {p.relative_to(stage).as_posix()}' for p in sorted(stage.rglob('*')) if p.is_file()]
    (stage/'checksums.sha256').write_text('\n'.join(checks)+'\n')
    DIST.mkdir(exist_ok=True); zpath=DIST/f'CIOS-Chief-Architect-Knowledge-Pack-v{version}.zip'
    with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():
                info=zipfile.ZipInfo(p.relative_to(stage).as_posix(), date_time=(2026,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16; z.writestr(info,p.read_bytes())
    zsha=sha(zpath); report=DIST/f'CIOS-Chief-Architect-Knowledge-Pack-v{version}-build-report.md'
    report.write_text(f'# Chief Architect Knowledge Pack Build Report\n\nVersion: {version}\n\nZIP: `{zpath.relative_to(ROOT)}`\n\nZIP checksum: `{zsha}`\n\nDocuments packaged: {len(docs)}\n\nValidation: passed\nRecommendation readiness: passed\nProgramme-state freshness: passed\n')
    print(f'Built {zpath} sha256={zsha}')
if __name__=='__main__': main()
