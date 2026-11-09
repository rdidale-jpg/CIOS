"""Versioned, fail-closed FLORA CI selection and inherited-failure gate.

No baseline-writing mode. Updating an exception is a reviewed source change.
Only sanitized summaries are exported; runtime stores and raw diagnostics stay
outside the artifact directory. Python standard library only.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import xml.etree.ElementTree as ET

BASELINE = Path(__file__).with_name('flora-baseline-v1.json')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def signature(message, trace, *, test_id="", checkout_sha=""):
    # Fingerprint the first failing source assertion and the full exception
    # headline. Normalize only machine-specific absolute roots and addresses.
    frame = re.search(r'(tests/[^:\n]+):\d+: in ([^\n]+)\n\s+([^\n]+)', trace)
    headline = message.splitlines()[0] if message else ''
    headline = re.sub(r'(?:/[A-Za-z0-9_.-]+)+/(?=(?:tests|cios)/)', '<repo>/', headline)
    headline = re.sub(r'0x[0-9a-fA-F]+', '<address>', headline)
    if (test_id == 'tests/test_flora_pilot_import_bypass.py::test_deployment_endpoint_identifies_canonical_import_runtime'
            and re.fullmatch(r'[0-9a-f]{40}', checkout_sha)):
        # This historical test expects a fabricated Render SHA; the application
        # correctly reports its actual checkout revision. Normalize only the
        # observed first operand, and only when it matches the known checkout.
        def revision(match):
            value = match.group(2)
            parts = value.split('...')
            matches = value == checkout_sha if len(parts) == 1 else (
                len(parts) == 2 and len(parts[0])+len(parts[1]) <= 40
                and checkout_sha.startswith(parts[0]) and checkout_sha.endswith(parts[1]))
            return match.group(1) + '<checkout-sha>' + match.group(1) if matches else match.group(0)
        headline = re.sub(r"(?<=assert )(['\"])([0-9a-f]{7,40}(?:\.\.\.[0-9a-f]{7,40})?)\1", revision, headline, count=1)
    return {'frame': list(frame.groups()) if frame else None,
            'headline_sha256': hashlib.sha256(headline.encode()).hexdigest()}


def read_junit(paths, *, checkout_sha=""):
    cases = {}
    for path in paths:
        tree = ET.parse(path)
        for suite in tree.iter('testsuite'):
            if int(suite.get('errors', '0')):
                raise ValueError('Collection/infrastructure errors in JUnit')
        for node in tree.iter('testcase'):
            key = node.get('classname', '').replace('.', '/') + '.py::' + node.get('name', '')
            if key in cases:
                raise ValueError('Duplicate test identity: ' + key)
            failed, error, skip = node.find('failure'), node.find('error'), node.find('skipped')
            if error is not None:
                raise ValueError('Test setup/infrastructure error: ' + key)
            row = {'status': 'failed' if failed is not None else 'skipped' if skip is not None else 'passed'}
            if failed is not None:
                row['signature'] = signature(failed.get('message', ''), failed.text or '', test_id=key, checkout_sha=checkout_sha)
            if skip is not None:
                row['reason'] = skip.get('message', '')
            cases[key] = row
    if not cases:
        raise ValueError('No test results')
    return cases


def compare(expected, actual, *, strict=False):
    issues, inherited, fixed = [], [], []
    if set(expected) != set(actual):
        issues.append({'kind': 'identity_mismatch', 'missing': sorted(set(expected)-set(actual)),
                       'unexpected': sorted(set(actual)-set(expected))})
    for key in sorted(set(expected) & set(actual)):
        old, new = expected[key], actual[key]
        if strict and new['status'] != 'passed':
            issues.append({'kind': 'strict_security_failure_or_skip', 'test_id': key})
        elif new['status'] == 'failed':
            if old['status'] != 'failed':
                issues.append({'kind': 'new_failure', 'test_id': key})
            elif new.get('signature') != old.get('signature'):
                issues.append({'kind': 'changed_failure_signature', 'test_id': key})
            else:
                inherited.append(key)
        elif new['status'] == 'skipped':
            if old['status'] != 'skipped' or new.get('reason') != old.get('reason'):
                issues.append({'kind': 'unexpected_skip', 'test_id': key})
        elif old['status'] != 'passed':
            fixed.append(key)
    return {'counts': dict(Counter(r['status'] for r in actual.values())),
            'issues': issues, 'inherited': inherited, 'fixed': fixed, 'cases': actual}


def integrity(root):
    counts = {}
    for filename, expected in {'hash-comparison.json': 52, '01c-integrity.json': 9,
                               '01d-integrity.json': 62, 'acceptance-integrity.json': 5,
                               '01e-integrity.json': 18}.items():
        paths = list(root.rglob(filename))
        if len(paths) != expected:
            raise ValueError('Missing/extra integrity records: ' + filename)
        for path in paths:
            value = json.loads(path.read_text())
            if value.get('unchanged') is not True or value.get('before') != value.get('after'):
                raise ValueError('Protected-data integrity mismatch')
            if value.get('retained_journal'):
                # The focused test asserts retained recovery evidence and closed
                # authority. Never mistake that private evidence for data loss.
                full = value['full_after']
                if {k:v for k,v in full.items() if not k.startswith('security/protected-undo/')} != value['before']:
                    raise ValueError('Retained-journal protected data mismatch')
        counts[filename] = len(paths)
    prefixes = ('test_feedback_positive_scope', 'test_profile_authorised_edit_',
                'test_concurrent_feedback_appen', 'test_http_recent_scoped_cleanu',
                'test_http_cleanup_denials_pres', 'test_concurrent_actor_profiles',
                'test_previously_accepted_feedb', 'test_native_sqlite_contention_')
    chains = records = cleanup = 0
    for path in root.rglob('authority.sqlite3'):
        if not path.parents[2].name.startswith(prefixes):
            continue
        data_root = path.parent.parent
        with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
            previous = ''
            for at, event, payload, prev, stamp in db.execute('SELECT at,event,payload,previous,digest FROM audit ORDER BY seq'):
                if prev != previous or digest([at, event, payload, previous]) != stamp:
                    raise ValueError('Audit chain mismatch')
                previous = stamp
            chains += 1
            for event, payload in db.execute("SELECT event,payload FROM audit WHERE event IN ('feedback_mutation','commercial_profile_mutation')"):
                value = json.loads(payload)
                if event == 'feedback_mutation':
                    targets = [json.loads(s) for s in (data_root/'enterprise_canvas/feedback.jsonl').read_text().splitlines() if s.strip()]
                    matches = value['record_digest'] in {digest(r) for r in targets}
                else:
                    filename = value['resource_id'].split(':', 1)[0]
                    target = json.loads((data_root/'commercial_context'/filename).read_text())[value['user_id']]
                    matches = value['record_digest'] == digest(target)
                if not matches or value['workspace_id'] != 'synthetic-workspace' or not value['session_ref'] or value['membership_version'] < 1:
                    raise ValueError('Committed audit record mismatch')
                records += 1
            if path.parents[2].name.startswith('test_http_recent_scoped_cleanu'):
                rows = [json.loads(r[0]) for r in db.execute("SELECT payload FROM audit WHERE event='storage_history_cleanup'")]
                if len(rows) != 1 or not rows[0]['resource_ids'] or any((data_root/n).exists() for n in rows[0]['resource_ids']) or not rows[0]['session_ref']:
                    raise ValueError('Cleanup resource audit mismatch')
                cleanup += 1
    if (chains, records, cleanup) != (15, 17, 1):
        raise ValueError('Missing/extra audit verification records')
    return {'unchanged_comparisons': sum(counts.values()), 'counts': counts,
            'audit_chains': chains, 'audit_record_digests': records, 'cleanup_audits': cleanup}


def run(repo, output, profile='auto'):
    baseline = json.loads(BASELINE.read_text())
    if baseline.get('version') != 1:
        raise ValueError('Unsupported baseline version')
    detected = '01b' if (repo/'docs/flora-runtime/security-repair-01b/01E-Bounded-Remediation-Evidence.json').exists() else '01a'
    if profile != 'auto' and profile != detected:
        raise ValueError('Profile does not match source boundary')
    profile = detected
    spec = baseline['profiles'][profile]
    found = sorted(str(p.relative_to(repo)) for p in (repo/'tests').glob('test_flora_security*.py'))
    if found != spec['security_modules']:
        raise ValueError('Security discovery differs from approved profile')
    if output.exists():
        raise ValueError('Use a new empty output directory; do not overwrite evidence')
    output.mkdir(parents=True)
    private = output/'private'
    private.mkdir()
    artifacts = output/'artifacts'
    artifacts.mkdir()
    result = {'baseline_version': 1, 'profile': profile, 'suites': {}, 'issues': [],
              'head_sha': subprocess.check_output(['git','rev-parse','HEAD'], cwd=repo, text=True).strip(),
              'runtime': sys.version.split()[0]}
    for ref in ['GITHUB_SHA', 'GITHUB_HEAD_REF', 'GITHUB_BASE_REF']:
        result[ref.lower()] = os.environ.get(ref, '')
    def execute(label, args, fixture=False):
        xml = private/(label+'.xml')
        env = dict(os.environ)
        env.update(FLORA_DATA_DIR=str(private/(label+'-data')), FLORA_PILOT_DIR=str(private/(label+'-data')),
                   FLORA_ENVIRONMENT='development', PYTHONPATH=str(repo), PYTHONDONTWRITEBYTECODE='1')
        # The hosted job supplies no secrets. Drop common provider/runtime
        # credentials as a further local guard; this is not an OS sandbox.
        for key in list(env):
            if key in {'GITHUB_TOKEN','GH_TOKEN','OPENAI_API_KEY','FLORA_SESSION_SECRET','FLORA_PILOT_SECRET'}:
                env.pop(key)
        command = [sys.executable,'-m','pytest','-q','--tb=short','--basetemp='+str(private/(label+'-tmp')),
                   '--junitxml='+str(xml)]
        if fixture:
            command += ['-o','usefixtures=verified_flora_test_authority']
        command += args
        with (private/(label+'.log')).open('w') as log:
            proc = subprocess.run(command, cwd=repo, env=env, stdout=log, stderr=subprocess.STDOUT)
        if proc.returncode not in (0,1):
            raise ValueError('Test infrastructure/collection failed: ' + label)
        cases = read_junit([xml], checkout_sha=result['head_sha'])
        if (proc.returncode == 0) != all(row['status'] != 'failed' for row in cases.values()):
            raise ValueError('Process/result mismatch: ' + label)
        return cases
    try:
        for name, suite in spec['suites'].items():
            cases = {}
            for index, selection in enumerate(suite['selections']):
                rows = execute(name+'-'+str(index), selection, fixture=suite.get('fixture',False))
                if set(rows) & set(cases):
                    raise ValueError('Duplicate selection')
                cases.update(rows)
            report = compare(suite['cases'], cases, strict=name=='security')
            result['suites'][name] = report
            result['issues'] += [{'suite':name,**r} for r in report['issues']]
            print(name, json.dumps(report['counts']), 'issues', len(report['issues']), flush=True)
        all_ids = [k for v in result['suites'].values() for k in v['cases']]
        if len(set(all_ids)) != len(all_ids):
            raise ValueError('Duplicate cross-suite identities')
        result['unique_ids'] = len(all_ids)
        if profile == '01b':
            result['integrity'] = integrity(private)
        else:
            result['integrity'] = {'profile': '01A fail-closed tests assert rejection fingerprints; 01B journal/audit totals not applicable'}
    except (ValueError,OSError,KeyError,ET.ParseError,sqlite3.Error) as exc:
        # Raw exceptions may contain paths/data. Safe class and stage only.
        result['issues'].append({'kind':'validation_error','error_type':type(exc).__name__})
        (private/'validator-error.txt').write_text(str(exc)+'\n')
    result['passed'] = not result['issues']
    (artifacts/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    junit = ET.Element('testsuites')
    for name, report in result['suites'].items():
        suite = ET.SubElement(junit,'testsuite',name=name,tests=str(len(report['cases'])))
        for key,row in report['cases'].items():
            node = ET.SubElement(suite,'testcase',classname=key.split('::')[0],name=key.split('::',1)[1])
            if row['status']=='failed': ET.SubElement(node,'failure',message='Reported inherited or unexpected failure; consult sanitized summary')
            if row['status']=='skipped': ET.SubElement(node,'skipped',message='Reported retained-input skip; consult sanitized summary')
    ET.ElementTree(junit).write(artifacts/'results.xml',encoding='unicode')
    markdown = '# FLORA validation\n\nProfile: '+profile+'; gate: '+('PASS' if result['passed'] else 'FAIL')+'\n\n'
    markdown += '\n'.join('- '+name+': '+json.dumps(v['counts']) for name,v in result['suites'].items())+'\n'
    (artifacts/'summary.md').write_text(markdown)
    print(markdown,flush=True)
    return 0 if result['passed'] else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path.cwd())
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--profile',choices=['auto','01a','01b'],default='auto')
    args=parser.parse_args()
    try:
        return run(args.repo.resolve(),args.output.resolve(),args.profile)
    except (ValueError,OSError,KeyError,json.JSONDecodeError) as exc:
        print('FLORA CI preflight failed:',type(exc).__name__,file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
