#!/usr/bin/env python3
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import os
import platform
import re
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'knowledge-packs/researcher'
DIST = ROOT / 'dist'
STAGE = ROOT / '.tmp/researcher-pack-stage'
SEMVER_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+$')
PACK_ID = 'CIOS-Researcher-Knowledge-Pack'


def fail(message):
    raise SystemExit(message)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_version_field(path, field_name, pattern):
    text = path.read_text(errors='ignore')
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        fail(f'Missing governed version field: requested version unknown; source file: {path.relative_to(ROOT)}; field: {field_name}')
    return match.group(1)


def require_version_match(requested, path, field_name, found):
    if found != requested:
        fail(
            f'Version mismatch: requested version {requested}; conflicting version {found}; '
            f'source file: {path.relative_to(ROOT)}; field: {field_name}'
        )


def parse_manifest(path):
    docs=[]; cur=None
    for line in path.read_text().splitlines():
        if line.startswith('  - '):
            cur={}; docs.append(cur); line='    '+line[4:]
        if cur is not None and line.startswith('    '):
            k,v=line.strip().split(': ',1); cur[k]=v
    return docs


def validate_source_versions(version, basename, zip_path, report_path):
    governed = [
        (PACK / 'VERSION', 'VERSION', lambda p: p.read_text().strip()),
        (PACK / 'manifest.yaml', 'pack.version', lambda p: read_version_field(p, 'pack.version', r'^  version: ([0-9]+\.[0-9]+\.[0-9]+)$')),
        (PACK / 'README.md', 'README Version', lambda p: read_version_field(p, 'README Version', r'^\*\*Version:\*\* ([0-9]+\.[0-9]+\.[0-9]+)')),
        (PACK / 'CHANGELOG.md', 'changelog target version', lambda p: read_version_field(p, 'changelog target version', r'^## ([0-9]+\.[0-9]+\.[0-9]+)$')),
        (PACK / 'MIGRATION.md', 'migration target version', lambda p: read_version_field(p, 'migration target version', r'^# Migration to Researcher Knowledge Pack v([0-9]+\.[0-9]+\.[0-9]+)$')),
    ]
    for path, field, reader in governed:
        require_version_match(version, path, field, reader(path))
    generated = [
        ('root directory name', basename, f'{PACK_ID}-v{version}'),
        ('release filename', zip_path.name, f'{PACK_ID}-v{version}.zip'),
        ('build-report filename', report_path.name, f'{PACK_ID}-v{version}-build-report.md'),
        ('pack-state version', version, version),
        ('source-map release metadata', version, version),
    ]
    for field, found, expected in generated:
        if found != expected:
            fail(f'Version mismatch: requested version {version}; conflicting version {found}; source file: generated output; field: {field}')


def validate(docs):
    req={'EI-001','EI-002','EI-003','EI-004','EI-012','FP-009','FP-010','FP-011','FP-012','ADR-016','RG-001','RG-002','RKI-001','MISSION-UKCG-001','MPT-001','APPA-001','IT-001','ITL-SPEC-001','EIF-001','EOD-001','OT-001','TEMPLATE-Market-Participant-Twin','TEMPLATE-Account-Participant-Position-Assessment','TEMPLATE-Opportunity-Hypothesis','TEMPLATE-Industry-Twin-Maturity-Assessment','TEMPLATE-Executive-Intelligence-Handover'}
    ids={d['document_id'] for d in docs}
    missing=req-ids
    if missing: fail(f'Missing required documents: {sorted(missing)}')
    for d in docs:
        src=ROOT/d['source_path']
        if not src.exists(): fail(f'Missing source: {d["source_path"]}')
        if sha(src)!=d['checksum']: fail(f'Checksum mismatch: {d["source_path"]}')
        text=src.read_text(errors='ignore')
        if d['document_id'].startswith(('EI-','FP-','ADR-')) and d['document_id'] not in text[:2000]:
            fail(f'Document ID not found near top: {d["source_path"]}')
    if any(d['document_id']=='FP-010' and 'Knowledge-Pack-Architecture' not in d['source_path'] for d in docs): fail('FP-010 manifest path is stale')
    if any(d['document_id']=='FP-012' and 'Enterprise-Reinvention-Intelligence' not in d['source_path'] for d in docs): fail('FP-012 manifest path is stale')
    content='\n'.join((ROOT/d['source_path']).read_text(errors='ignore') for d in docs)
    phrases=['Evidence proves change','Observations remember change','Enterprise Models accumulate change','Reports are views','Unknowns and contradictions are first-class','Human-supplied knowledge must be labelled','Recommendations require inspectable lineage','Research-ready gate','supplier, contract and procurement','Architecture Handover','UK Central Government','Market Participant Twin','Account-Participant Position Assessment','buyer-side evidence','participant-side evidence','participant-supplied assertion','bounded completion','Industry Twin Maturity Assessment','Executive Intelligence handover','Research Mission Workspace','CONTINUE','COMPLETE','EVIDENCE EXHAUSTED','Technical interruption is an execution condition recorded as resumable','No generic BLOCKED mission state shall be introduced','Do not invent a parallel arbitrary archive format']
    for p in phrases:
        if p.lower() not in content.lower(): fail(f'Missing doctrine/content phrase: {p}')
    hard=[]; warnings=[]; notices=[]
    if 'Market Participant Twin' in content and 'MPT-001' not in ids: hard.append('Market Participant Twin terminology requires MPT-001 owning specification')
    if 'Account-Participant Position Assessment' in content and 'APPA-001' not in ids: hard.append('Account-Participant Position Assessment references require APPA-001 owning specification')
    mission=(PACK/'missions/UK-Central-Government-Industry-Twin-Mission.md').read_text(errors='ignore').lower()
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
    if hard: fail('Hard validation failures: '+ '; '.join(hard))
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


def build_report(version, zip_path, zsha, docs, results):
    timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    return f'''# Researcher Knowledge Pack Build Report\n\nRequested pack version: {version}\n\nVersion: {version}\n\nZIP: `{zip_path.relative_to(ROOT)}`\n\nZIP checksum: `{zsha}`\n\nDocuments packaged: {len(docs)}\n\nValidation: passed\n\n## Build provenance\n\n- Git commit SHA: {os.environ.get('GITHUB_SHA', 'local-unset')}\n- Git ref: {os.environ.get('GITHUB_REF', os.environ.get('GITHUB_REF_NAME', 'local-unset'))}\n- Workflow run ID: {os.environ.get('GITHUB_RUN_ID', 'local-unset')}\n- Build timestamp UTC: {timestamp}\n- Python version: {platform.python_version()}\n- Builder script path: {Path(__file__).relative_to(ROOT)}\n- Requested pack version: {version}\n\n## Participant-aware intelligence validation results\n\nHard validation failures: {len(results["hard_failures"])}\n\nUnresolved-source warnings: {len(results["unresolved_source_warnings"])}\n\nOptional-document notices: {len(results["optional_document_notices"])}\n\n''' + ''.join(f'- Notice: {n}\n' for n in results['optional_document_notices'])


def main(argv=None):
    parser = argparse.ArgumentParser(description='Build the CIOS Researcher Knowledge Pack release artefacts.')
    parser.add_argument('--version', required=True, help='Bare semantic version, for example 2.2.0')
    parser.add_argument('--output-dir', default=str(DIST), help='Directory for release artefacts')
    args = parser.parse_args(argv)
    version = args.version.strip()
    if not SEMVER_RE.fullmatch(version):
        fail(f'Invalid Researcher Knowledge Pack version: {version}. Expected MAJOR.MINOR.PATCH.')
    dist = Path(args.output_dir)
    if not dist.is_absolute():
        dist = ROOT / dist
    basename = f'{PACK_ID}-v{version}'
    zip_path = dist / f'{basename}.zip'
    report_path = dist / f'{basename}-build-report.md'
    validate_source_versions(version, basename, zip_path, report_path)
    docs=parse_manifest(PACK/'manifest.yaml'); validate(docs)
    if STAGE.exists(): shutil.rmtree(STAGE)
    root_stage = STAGE / basename
    root_stage.mkdir(parents=True)
    for extra in ['VERSION','manifest.yaml','source-map.yaml','CHANGELOG.md','MIGRATION.md']:
        shutil.copy2(PACK/extra, root_stage/extra)
    (root_stage/'pack-state.yaml').write_text(f'pack_id: {PACK_ID}\nversion: {version}\nroot_directory: {basename}\nrelease_zip: {zip_path.name}\nbuild_report: {report_path.name}\n')
    for d in docs:
        dest=root_stage/d['pack_path']; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/d['source_path'],dest)
    (root_stage/'DOCUMENT-INDEX.md').write_text(index(docs))
    checks=[]
    for p in sorted(root_stage.rglob('*')):
        if p.is_file(): checks.append(f'{sha(p)}  {p.relative_to(root_stage).as_posix()}')
    (root_stage/'checksums.sha256').write_text('\n'.join(checks)+'\n')
    dist.mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(root_stage.rglob('*')):
            if p.is_file():
                info=zipfile.ZipInfo(p.relative_to(STAGE).as_posix(), date_time=(2026,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16
                z.writestr(info,p.read_bytes())
    zsha=sha(zip_path)
    results=getattr(validate,'participant_results',{'hard_failures':[],'unresolved_source_warnings':[],'optional_document_notices':[]})
    report_path.write_text(build_report(version, zip_path, zsha, docs, results))
    print(f'Built {zip_path} sha256={zsha}')

if __name__=='__main__': main()
