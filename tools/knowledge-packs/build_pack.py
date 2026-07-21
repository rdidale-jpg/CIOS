#!/usr/bin/env python3
from pathlib import Path
from datetime import date, datetime, timezone
import argparse, hashlib, re, shutil, subprocess, sys, zipfile
ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/'dist'
ALLOWED={'canonical_architecture','accepted_decision','operating_guidance','runtime_baseline','programme_state','template','reference'}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def parse_manifest(path):
    docs=[]; cur=None; meta={}; freshness={}
    section=None; sub=None
    for line in path.read_text().splitlines():
        if not line.strip(): continue
        if not line.startswith(' '):
            section=line.rstrip(':'); sub=None; continue
        if section=='pack' and line.startswith('  ') and ': ' in line:
            k,v=line.strip().split(': ',1); meta[k]=v
        elif section=='freshness':
            if line.startswith('  ') and not line.startswith('    '):
                k=line.strip().rstrip(':');
                if ': ' in line.strip(): k,v=line.strip().split(': ',1); freshness[k]=v; sub=None
                else: sub=k; freshness[sub]={}
            elif sub and line.startswith('    ') and ': ' in line:
                k,v=line.strip().split(': ',1); freshness[sub][k]=int(v) if v.isdigit() else v
        elif section=='documents':
            if line.startswith('  - '):
                cur={}; docs.append(cur); line='    '+line[4:]
            if cur is not None and line.startswith('    ') and ': ' in line:
                k,v=line.strip().split(': ',1); cur[k]=v
    return meta, freshness, docs

def extract_as_of(path):
    m=re.search(r'^as_of:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$', Path(path).read_text(errors='ignore'), re.M)
    return date.fromisoformat(m.group(1)) if m else None

def repo_commit():
    try: return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    except Exception: return 'unknown'

def validate(docs, freshness):
    required={'RP-003','CAI-001','CAOG-001','EI-001','EI-002','EI-003','EI-012','FP-009','FEIR-001','EIRP-001','WP-011-RUNTIME-BASELINE','PROGRAMME-STATE'}
    ids=[d['document_id'] for d in docs]
    if len(ids)!=len(set(ids)): raise SystemExit('Duplicate canonical document identifiers in manifest')
    missing=required-set(ids)
    if missing: raise SystemExit(f'Missing required documents: {sorted(missing)}')
    for d in docs:
        if d.get('authority') not in ALLOWED: raise SystemExit(f'Invalid authority for {d.get("document_id")}: {d.get("authority")}')
        src=ROOT/d['source_path']
        if not src.exists(): raise SystemExit(f'Missing source: {d["source_path"]}')
        if sha(src)!=d.get('checksum'): raise SystemExit(f'Checksum mismatch: {d["source_path"]}')
        if d['authority']=='canonical_architecture' and not d['source_path'].startswith('architecture/'):
            raise SystemExit(f'Canonical architecture outside architecture/: {d["source_path"]}')
    ps=[d for d in docs if d['document_id']=='PROGRAMME-STATE'][0]
    ps_text=(ROOT/ps['source_path']).read_text()
    for f in ['programme_state_version:','as_of:','owner:','## Architecture','## Runtime','## Current delivery','## Operational capabilities','## In progress','## Open decisions','## Known risks','## Next decision']:
        if f not in ps_text: raise SystemExit(f'Missing programme-state field: {f}')
    asof=extract_as_of(ROOT/ps['source_path'])
    max_age=freshness.get('programme_state',{}).get('maximum_age_days',14)
    freshness_state='unknown' if not asof else ('stale' if (date.today()-asof).days>max_age else 'current')
    return asof, freshness_state

def document_index(docs):
    lines=['# Document Index','','| Document ID | Title | Authority | Canonical source path | Packaged path |','|---|---|---|---|---|']
    for d in docs: lines.append(f"| {d['document_id']} | {d['title']} | {d['authority']} | {d['source_path']} | {d['pack_path']} |")
    return '\n'.join(lines)+'\n'

def pack_state(meta, asof, freshness_state):
    status='ready' if freshness_state=='current' else 'conditional'
    reasons=['All required manifest sources validated.']
    if freshness_state!='current': reasons.append('PROGRAMME STATE STALE — STRATEGIC RECOMMENDATIONS REQUIRE VERIFICATION')
    rs='\n'.join(f'  - {r}' for r in reasons)
    return f"# Pack State\n\n```yaml\npack:\n  name: {meta.get('title')}\n  version: {meta.get('version')}\n  built_at: {datetime(2026,1,1,tzinfo=timezone.utc).isoformat()}\n  repository_commit: {repo_commit()}\narchitecture:\n  baseline: RP-003 / governed architecture sources\n  validation: pass\nruntime:\n  baseline: WP-011 Flora Runtime Capability Baseline\n  validation: pass\nprogramme:\n  as_of: {asof or 'unknown'}\n  freshness: {freshness_state}\nrecommendation_readiness:\n  status: {status}\n  reasons:\n{rs}\n```\n"

def build(profile):
    pack=ROOT/'knowledge-packs'/profile; meta,freshness,docs=parse_manifest(pack/'manifest.yaml'); asof,fs=validate(docs,freshness)
    stage=ROOT/'.tmp'/f'{profile}-pack-stage'; shutil.rmtree(stage,ignore_errors=True); stage.mkdir(parents=True)
    for extra in ['VERSION','manifest.yaml','source-map.yaml']:
        shutil.copy2(pack/extra, stage/extra)
    for d in docs:
        dest=stage/d['pack_path']; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/d['source_path'],dest)
    (stage/'DOCUMENT-INDEX.md').write_text(document_index(docs))
    (stage/'PACK-STATE.md').write_text(pack_state(meta,asof,fs))
    checks=[f'{sha(p)}  {p.relative_to(stage).as_posix()}' for p in sorted(stage.rglob('*')) if p.is_file()]
    (stage/'checksums.sha256').write_text('\n'.join(checks)+'\n')
    DIST.mkdir(exist_ok=True); name=meta['id']; version=meta['version']; zip_path=DIST/f'{name}-v{version}.zip'
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():
                info=zipfile.ZipInfo(p.relative_to(stage).as_posix(),(2026,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16; z.writestr(info,p.read_bytes())
    print(f'Built {zip_path} sha256={sha(zip_path)} freshness={fs}')
    return zip_path
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--profile',required=True); args=ap.parse_args(); build(args.profile)
