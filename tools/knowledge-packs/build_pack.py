#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, shutil, zipfile, re
ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/'dist'

def parse_manifest(path):
    docs=[]; cur=None
    for line in path.read_text().splitlines():
        if line.startswith('  - '):
            cur={}; docs.append(cur); line='    '+line[4:]
        if cur is not None and line.startswith('    '):
            k,v=line.strip().split(': ',1); cur[k]=v
    return docs

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def validate(profile, docs):
    if profile!='chief-architect':
        raise SystemExit(f'Unsupported profile: {profile}')
    required={'CA-001','FP-010','FP-012','ADR-016','REF-001','PRINCIPLES-001','ROADMAP-001'}
    ids={d['document_id'] for d in docs}
    missing=required-ids
    if missing: raise SystemExit(f'Missing required documents: {sorted(missing)}')
    for d in docs:
        src=ROOT/d['source_path']
        if not src.exists(): raise SystemExit(f'Missing source: {d["source_path"]}')
        if sha(src)!=d['checksum']: raise SystemExit(f'Checksum mismatch: {d["source_path"]}')
    if any(d['document_id']=='FP-010' and 'Knowledge-Pack-Architecture' not in d['source_path'] for d in docs):
        raise SystemExit('FP-010 manifest path is stale')
    if any(d['document_id']=='FP-012' and 'Enterprise-Reinvention-Intelligence' not in d['source_path'] for d in docs):
        raise SystemExit('FP-012 manifest path is stale')
    handbook=(ROOT/[d for d in docs if d['document_id']=='CA-001'][0]['source_path']).read_text(errors='ignore')
    if 'Recommendation' not in handbook or 'inspectable lineage' not in handbook:
        raise SystemExit('Recommendation readiness doctrine is missing')
    m=re.search(r'Last updated:\*\*\s*(\d{4}-\d{2}-\d{2})', handbook)
    if not m or m.group(1)<'2026-07-21':
        raise SystemExit('Programme-state freshness is stale')

def index(docs):
    lines=['# Document Index','','Recommended reading sequence: Chief Architect Handbook; FP-010 Knowledge Pack Architecture; ADR-016; FP-012; Reference Architecture; Architecture Principles; Flora Roadmap.','', '| Document ID | Title | Purpose | Authority | Required reading | Canonical source path | Packaged path |','|---|---|---|---|---|---|---|']
    for d in docs:
        lines.append(f"| {d['document_id']} | {d['title']} | {d['inclusion_reason']} | {d['authority']} | required | {d['source_path']} | {d['pack_path']} |")
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
    (stage/'PACK-STATE.md').write_text('# Pack State\n\nValidation: passed\nRecommendation readiness: passed\nProgramme-state freshness: passed\n')
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
