#!/usr/bin/env python3
from pathlib import Path
import hashlib, shutil, zipfile, re, sys
ROOT=Path(__file__).resolve().parents[2]
PACK=ROOT/'knowledge-packs/researcher'
DIST=ROOT/'dist'
VERSION=(PACK/'VERSION').read_text().strip()
ZIP=DIST/f'CIOS-Researcher-Knowledge-Pack-v{VERSION}.zip'
REPORT=DIST/f'CIOS-Researcher-Knowledge-Pack-v{VERSION}-build-report.md'
RELEASE_SHA=DIST/f'CIOS-Researcher-Knowledge-Pack-v{VERSION}.zip.sha256'
STAGE=ROOT/'.tmp/researcher-pack-stage'

def parse_manifest(path):
    docs=[]; cur=None
    for line in path.read_text().splitlines():
        if line.startswith('  - '):
            cur={}; docs.append(cur); line='    '+line[4:]
        if cur is not None and line.startswith('    '):
            k,v=line.strip().split(': ',1); cur[k]=v
    return docs

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def validate(docs):
    req={'EI-001','EI-002','EI-003','EI-004','EI-012','FP-009','FP-010','FP-011','FP-012','ADR-016','RG-001','RKI-001','MISSION-UKCG-001','MPT-001','APPA-001','ITL-SPEC-001','EIF-001','EOD-001','OT-001','TEMPLATE-Market-Participant-Twin','TEMPLATE-Account-Participant-Position-Assessment','TEMPLATE-Opportunity-Hypothesis'}
    ids={d['document_id'] for d in docs}
    missing=req-ids
    if missing: raise SystemExit(f'Missing required documents: {sorted(missing)}')
    for d in docs:
        src=ROOT/d['source_path']
        if not src.exists(): raise SystemExit(f'Missing source: {d["source_path"]}')
        if sha(src)!=d['checksum']: raise SystemExit(f'Checksum mismatch: {d["source_path"]}')
        text=src.read_text(errors='ignore')
        if d['document_id'].startswith(('EI-','FP-','ADR-')) and d['document_id'] not in text[:2000]:
            raise SystemExit(f'Document ID not found near top: {d["source_path"]}')
    if any(d['document_id']=='FP-010' and 'Knowledge-Pack-Architecture' not in d['source_path'] for d in docs):
        raise SystemExit('FP-010 manifest path is stale')
    if any(d['document_id']=='FP-012' and 'Enterprise-Reinvention-Intelligence' not in d['source_path'] for d in docs):
        raise SystemExit('FP-012 manifest path is stale')
    content='\n'.join((ROOT/d['source_path']).read_text(errors='ignore') for d in docs)
    phrases=['Evidence proves change','Observations remember change','Enterprise Models accumulate change','Reports are views','Unknowns and contradictions are first-class','Human-supplied knowledge must be labelled','Recommendations require inspectable lineage','Research-ready gate','supplier, contract and procurement','Architecture Handover','UK Central Government','Market Participant Twin','Account-Participant Position Assessment','buyer-side evidence','participant-side evidence','participant-supplied assertion']
    for p in phrases:
        if p.lower() not in content.lower(): raise SystemExit(f'Missing doctrine/content phrase: {p}')
    # Participant-aware intelligence validation controls.
    hard=[]; warnings=[]; notices=[]
    if 'Market Participant Twin' in content and 'MPT-001' not in ids: hard.append('Market Participant Twin terminology requires MPT-001 owning specification')
    if 'Account-Participant Position Assessment' in content and 'APPA-001' not in ids: hard.append('Account-Participant Position Assessment references require APPA-001 owning specification')
    mission=(ROOT/'knowledge-packs/researcher/missions/UK-Central-Government-Industry-Twin-Mission.md').read_text(errors='ignore').lower()
    for term in ['market participant','contract','procurement','opportunity','incumbent','framework']:
        if term not in mission: hard.append(f'UK Government mission lacks {term} coverage')
    for did in ['TEMPLATE-Market-Participant-Twin','TEMPLATE-Account-Participant-Position-Assessment']:
        if did not in ids: hard.append(f'Pack lacks required template {did}')
    source_map=(PACK/'source-map.yaml').read_text(errors='ignore')
    for d in docs:
        if d.get('required')=='true' and not (ROOT/d['source_path']).exists(): hard.append(f'Required source absent: {d["source_path"]}')
        if d['document_id'] not in source_map and d['document_id'].startswith(('MPT','APPA','EOD','OT','EIF')): warnings.append(f'Participant-aware source not mapped: {d["document_id"]}')
    for did in ['EIF-001','EOD-001','OT-001']:
        if did in ids: notices.append(f'{did} packaged as Review-status source; not accepted production authority')
    if hard: raise SystemExit('Hard validation failures: '+ '; '.join(hard))
    validate.participant_results={'hard_failures':hard,'unresolved_source_warnings':warnings,'optional_document_notices':notices}


def index(docs):
    order=['Start here','Operating guidance','Enterprise Intelligence','Supporting architecture','Templates','Mission briefs','Governance references']
    def group(d):
        pp=d['pack_path']
        if pp.startswith('configuration') or pp=='README.md': return 'Start here'
        if pp.startswith('operating-guidance'): return 'Operating guidance'
        if pp.startswith('architecture'): return 'Enterprise Intelligence'
        if pp.startswith('context'): return 'Supporting architecture'
        if pp.startswith('templates'): return 'Templates'
        if pp.startswith('missions'): return 'Mission briefs'
        return 'Governance references'
    lines=['# Document Index','','Recommended reading sequence: Researcher GPT Instructions; Mission Brief; RG-001 Research Agent Guide; Enterprise Knowledge Production Protocol; EI-012 Observation Model; EI-001 Enterprise Model; EI-002 Knowledge Graph; EI-003 Behaviour Model; FP-009 Hypothesis Validation; Templates and readiness artefacts.','']
    for g in order:
        lines += [f'## {g}','','| Document ID | Title | Purpose | Authority | Required reading | Canonical source path | Packaged path |','|---|---|---|---|---|---|---|']
        for d in docs:
            if group(d)==g: lines.append(f"| {d['document_id']} | {d['title']} | {d['inclusion_reason']} | {d['authority']} | required | {d['source_path']} | {d['pack_path']} |")
        lines.append('')
    return '\n'.join(lines)

def main():
    docs=parse_manifest(PACK/'manifest.yaml'); validate(docs)
    if STAGE.exists(): shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    for extra in ['VERSION','manifest.yaml','source-map.yaml','CHANGELOG.md','MIGRATION.md']:
        shutil.copy2(PACK/extra, STAGE/extra)
    for d in docs:
        dest=STAGE/d['pack_path']; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/d['source_path'],dest)
    (STAGE/'DOCUMENT-INDEX.md').write_text(index(docs))
    checks=[]
    for p in sorted(STAGE.rglob('*')):
        if p.is_file(): checks.append(f'{sha(p)}  {p.relative_to(STAGE).as_posix()}')
    (STAGE/'checksums.sha256').write_text('\n'.join(checks)+'\n')
    DIST.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(STAGE.rglob('*')):
            if p.is_file():
                info=zipfile.ZipInfo(p.relative_to(STAGE).as_posix(), date_time=(2026,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16
                z.writestr(info,p.read_bytes())
    zsha=sha(ZIP)
    RELEASE_SHA.write_text(f'{zsha}  {ZIP.name}\n')
    results=getattr(validate,'participant_results',{'hard_failures':[],'unresolved_source_warnings':[],'optional_document_notices':[]})
    REPORT.write_text(f'# Researcher Knowledge Pack Build Report\n\nVersion: {VERSION}\n\nZIP: `{ZIP.relative_to(ROOT)}`\n\nZIP checksum: `{zsha}`\n\nDocuments packaged: {len(docs)}\n\nValidation: passed\n\n## Participant-aware intelligence validation results\n\nHard validation failures: {len(results["hard_failures"])}\n\nUnresolved-source warnings: {len(results["unresolved_source_warnings"])}\n\nOptional-document notices: {len(results["optional_document_notices"])}\n\n' + ''.join(f'- Notice: {n}\n' for n in results['optional_document_notices']))
    print(f'Built {ZIP} sha256={zsha}')
if __name__=='__main__': main()
