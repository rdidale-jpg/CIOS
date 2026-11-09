"""Compare exact JUnit case IDs from pinned main and the repair.

python compare_results.py --before DIR --after DIR --security-before FILE \
  --security-after FILE --output FILE

The two checkouts must use identical test/fixture overlays as described in
Testing.md. This script does not run tests or touch any application data.
"""
import argparse
from collections import Counter
import json
from hashlib import sha256
import re
from pathlib import Path
import xml.etree.ElementTree as ET


def read(paths):
    out={}
    for path in paths:
        for case in ET.parse(path).iter('testcase'):
            test_id=case.get('classname','').replace('.','/')+'.py::'+case.get('name','')
            if test_id in out:raise ValueError('Duplicate case: '+test_id)
            failure=case.find('failure')
            if failure is None:failure=case.find('error')
            skipped=case.find('skipped')
            out[test_id]={'status':'failed' if failure is not None else 'skipped' if skipped is not None else 'passed'}
            if failure is not None:
                message=failure.get('message','')
                kind=message.split(':',1)[0].splitlines()[0] if message else 'TestFailure'
                if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.]*(?:Error|Exception|Failed)',kind):
                    kind='AssertionError' if 'assert ' in message else 'TestFailure'
                out[test_id].update(failure=kind, failure_sha256=sha256(message.encode()).hexdigest(),
                                    failure_details='Raw diagnostics retained locally; omitted from public output')
            if skipped is not None:
                message=skipped.get('message','')
                out[test_id].update(skip='Retained input unavailable' if 'artifact' in message.lower() else 'Skipped',
                                    skip_sha256=sha256(message.encode()).hexdigest())
    return out


def group(before,after):
    if set(before)!=set(after):raise ValueError('Case sets differ: '+str(set(before)^set(after)))
    rows=[{'test_id':k,'before':before[k],'after':after[k]} for k in sorted(before)]
    new=[r['test_id'] for r in rows if r['after']['status']=='failed' and r['before']['status']!='failed']
    return {'case_count':len(rows),'before':dict(Counter(v['status'] for v in before.values())),
            'after':dict(Counter(v['status'] for v in after.values())),
            'new_failures':new,'cases':rows}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('before','after','security-before','security-after','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    result={'baseline_sha':'dc9203e6880f8722e821d39cf53b689732edb0e7',
        'test_overlay':'Identical test sources and explicit domain service fixtures on both checkouts; production security module does not install fixture authentication.',
        'registry_test_contract_change':{'original_id':'test_canonical_owner_alias_and_encoded_cookie_inherit_blueprint_permissions','revised_id':'test_canonical_owner_alias_requires_verified_context_and_encoded_cookie_is_rejected','reason':'Unsigned cookie acceptance is replaced with rejection; legitimate owner alias has a positive explicit fixture-context assertion.'},
        'domain':group(read(a.before.glob('*.xml')),read(a.after.glob('*.xml'))),
        'security':group(read([a.security_before]),read([a.security_after]))}
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    for name in ('domain','security'):
        print(name,result[name]['case_count'],result[name]['before'],result[name]['after'],'new failures',len(result[name]['new_failures']))
    return int(any(result[name]['new_failures'] for name in ('domain','security')))

if __name__=='__main__':raise SystemExit(main())
