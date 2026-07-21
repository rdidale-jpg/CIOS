#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, shutil, zipfile, re
ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/'dist'
MANDATORY={'CA-001','FP-010','FP-012','FP-009','ADR-016','ADR-014','ADR-024','REF-001','PRINCIPLES-001','CURRENT-PROGRAMME-STATE','WP-011','FEIR-001','EIRP-001','EI-001','EI-002','EI-003','EI-004','EI-012','EIF-001','KPS-001','CA-OG-001','CA-TEMPLATE-001','CA-SOURCE-MAP'}
RUNTIME={'WP-011','FEIR-001','EIRP-001','ADR-014','ADR-024'}
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

def parse_source_map_ids(path):
    ids=[]
    for line in path.read_text().splitlines():
        m=re.search(r':\s*\[(.*?)\]\s*$', line)
        if m:
            ids.extend([x.strip() for x in m.group(1).split(',') if x.strip()])
    return ids

def validate(profile, docs):
    if profile!='chief-architect':
        raise SystemExit(f'Unsupported profile: {profile}')
    ids={d['document_id'] for d in docs}
    id_counts={document_id: sum(1 for d in docs if d['document_id']==document_id) for document_id in ids}
    duplicate_ids=sorted([document_id for document_id, count in id_counts.items() if count != 1])
    if duplicate_ids: raise SystemExit(f'Duplicate manifest document IDs: {duplicate_ids}')
    missing=MANDATORY-ids
    if missing: raise SystemExit(f'Missing required documents: {sorted(missing)}')
    source_map_doc=[d for d in docs if d['document_id']=='CA-SOURCE-MAP'][0]
    for source_map_id in parse_source_map_ids(ROOT/source_map_doc['source_path']):
        matches=[d for d in docs if d['document_id']==source_map_id]
        if len(matches)!=1:
            raise SystemExit(f'Source-map identifier {source_map_id} resolves to {len(matches)} manifest entries')
    if any(d['document_id']=='ROADMAP-001' and d['authority']=='canonical' for d in docs):
        raise SystemExit('Flora Roadmap must not be canonical or a programme-state freshness source')
    for d in docs:
        src=ROOT/d['source_path']
        if not src.exists(): raise SystemExit(f'Missing source: {d["source_path"]}')
        if sha(src)!=d['checksum']: raise SystemExit(f'Checksum mismatch: {d["source_path"]}')
        if d.get('authority') not in AUTH: raise SystemExit(f'Invalid authority for {d["document_id"]}: {d.get("authority")}')
        if d['document_id'] in MANDATORY and is_placeholder(src): raise SystemExit(f'Placeholder or materially empty mandatory source: {d["source_path"]}')
    runtime_capability_baselines=[d for d in docs if d['document_id']=='WP-011' or d['pack_path']=='runtime/Flora-Runtime-Capability-Baseline.md' or 'Runtime Capability Baseline' in d['title']]
    if len(runtime_capability_baselines)!=1:
        raise SystemExit(f'Runtime Capability Baseline must be packaged exactly once; found {len(runtime_capability_baselines)}')
    baseline=runtime_capability_baselines[0]
    if baseline['authority']!='runtime-baseline':
        raise SystemExit('Runtime Capability Baseline must use authority runtime-baseline')
    handbook=(ROOT/[d for d in docs if d['document_id']=='CA-001'][0]['source_path']).read_text(errors='ignore')
    if 'No strong Recommendation without inspectable lineage' not in handbook:
        raise SystemExit('Recommendation readiness doctrine is missing')
    programme=(ROOT/[d for d in docs if d['document_id']=='CURRENT-PROGRAMME-STATE'][0]['source_path']).read_text(errors='ignore')
    m=re.search(r'As of:\*\*\s*(\d{4}-\d{2}-\d{2})', programme)
    if not m or m.group(1)<'2026-07-21':
        raise SystemExit('Programme-state freshness is stale')
    if 'Roadmaps are planning inputs only' not in programme:
        raise SystemExit('Programme-state source must reject roadmap freshness proxy')
    required_programme_fields=['Architecture baseline','Runtime baseline','Active work package','Current delivery objective','Current product / twin focus','Demonstrable capability','Work in progress','Blockers','Risks','Open decisions','Next decision']
    missing_fields=[field for field in required_programme_fields if f'## {field}' not in programme]
    if missing_fields:
        raise SystemExit(f'Programme-state freshness missing substantive delivery-state fields: {missing_fields}')

def index(docs):
    lines=['# Document Index','','Recommended reading sequence: Chief Architect Handbook; CURRENT-PROGRAMME-STATE; Operating Guidance; FP-010; ADR-016; implemented runtime baseline; runtime architecture; core EI authorities; templates and source map.','', '| Document ID | Title | Purpose | Authority | Required reading | Canonical source path | Packaged path |','|---|---|---|---|---|---|---|']
    for d in docs:
        req='required' if d['document_id'] in MANDATORY else 'context'
        lines.append(f"| {d['document_id']} | {d['title']} | {d['inclusion_reason']} | {d['authority']} | {req} | {d['source_path']} | {d['pack_path']} |")
    return '\n'.join(lines)+'\n'

def pack_state(docs):
    by={d['document_id']:d for d in docs}
    rows=[
('Programme-state baseline','CURRENT-PROGRAMME-STATE','programme/CURRENT-PROGRAMME-STATE.md'),
('Runtime-baseline authority','WP-011, FEIR-001, EIRP-001, ADR-014, ADR-024','runtime/'),
('Runtime implementation evidence','WP-011 Flora Runtime Capability Baseline','runtime/Flora-Runtime-Capability-Baseline.md'),
('Operating guidance','CA-OG-001','operating-guidance/Chief-Architect-Operating-Guidance.md'),
('Templates','CA-TEMPLATE-001','templates/Architecture-Decision-Review-Template.md'),
('Source map','CA-SOURCE-MAP','source-map.yaml'),
('Core Enterprise Intelligence authorities','EI-001, EI-002, EI-003, EI-012, EIF-001','enterprise-intelligence/'),
('Knowledge Pack authority','FP-010, ADR-016, KPS-001','architecture/'),
('Recommendation doctrine','CA-001, FP-009, FP-012, EI-004, EI-012','handbook/, architecture/ and enterprise-intelligence/'),
('Roadmap not canonical freshness','ROADMAP-001','context/Flora-Roadmap.md authority=proposed-context'),
('Checksum validation','all manifest documents','checksums.sha256'),
('Placeholder rejection','all mandatory documents','build validation'),
]
    lines=['# Pack State','','Validation: passed','Recommendation readiness: passed','Programme-state freshness: passed','','## Validation evidence','','Mandatory runtime validation: passed\nRuntime baseline included: WP-011 — Flora Runtime Capability Baseline — runtime/Flora-Runtime-Capability-Baseline.md\nRuntime architecture and runtime implementation evidence: included','Mandatory programme-state validation: passed','Roadmap freshness proxy: rejected','Placeholder mandatory-source validation: passed','','## WP-012 completeness matrix','','| WP-012 deliverable / acceptance criterion | Packaged evidence | Location |','|---|---|---|']
    for a,b,c in rows: lines.append(f'| {a} | {b} | {c} |')
    lines+=['','## Packaged authorities','']
    for d in docs: lines.append(f"- {d['document_id']} — {d['authority']} — `{d['pack_path']}` — checksum `{d['checksum']}`")
    wp011=by.get('WP-011')
    if wp011:
        lines += ['', '## Runtime baseline', '', f"runtime_baseline:", f"  document: {wp011['title']}", f"  authority: {wp011['authority']}", '  status: included', f"  packaged_path: {wp011['pack_path']}", f"  source_path: {wp011['source_path']}"]
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
    programme_doc=[d for d in docs if d['document_id']=='CURRENT-PROGRAMME-STATE'][0]
    runtime_docs=[d for d in docs if d['document_id'] in sorted(RUNTIME)]
    source_map_doc=[d for d in docs if d['document_id']=='CA-SOURCE-MAP'][0]
    report.write_text(f'# Chief Architect Knowledge Pack Build Report\n\nVersion: {version}\n\nZIP: `{zpath.relative_to(ROOT)}`\n\nZIP checksum: `{zsha}`\n\nDocuments packaged: {len(docs)}\n\nProgramme-state source used: {programme_doc["document_id"]} — {programme_doc["title"]} (`{programme_doc["source_path"]}` -> `{programme_doc["pack_path"]}`)\n\nRuntime-baseline sources used:\n' + ''.join(f'- {d["document_id"]} — {d["title"]} (`{d["source_path"]}` -> `{d["pack_path"]}`)\n' for d in runtime_docs) + f'\nRuntime Capability Baseline packaged: WP-011 — Flora Runtime Capability Baseline (`runtime/Flora-Runtime-Capability-Baseline.md`)\n\nSelection rationale: selected canonical source `docs/flora-runtime/wp-011/Flora-Runtime-Capability-Baseline.md` because it is the only repository document found with WP-011 and Flora Runtime Capability Baseline identifiers; no canonical successor or duplicate packaged baseline was found in the Authority Registry/ADR search.\n\nSource-map resolution: passed for `{source_map_doc["source_path"]}`; every source-map identifier resolves to exactly one manifest entry.\nProgramme-state freshness basis: passed using substantive delivery-state fields and As of date, not file date alone.\n\nValidation: passed\nRecommendation readiness: passed\nProgramme-state freshness: passed\n')
    print(f'Built {zpath} sha256={zsha}')
if __name__=='__main__': main()
