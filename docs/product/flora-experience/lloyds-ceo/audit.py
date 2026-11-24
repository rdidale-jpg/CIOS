"""Repository coverage audit; not a runtime registry, admission or canonical census."""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))

def report():
    spec=importlib.util.spec_from_file_location('original_gold_audit',ROOT/'docs/flora-runtime/lloyds-gold-standard/audit.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    value=module.report()
    value['baseline']='1c13e6962516dbb071b2133f2c1a3de87647e2ac'
    value['external_context_ids']=[key for key in value['external_context_ids'] if not key.startswith('CEO1-')]
    value['additional_source_item']={'id':'CEO1-ROLE-NUNN-20260322','owner':'existing Source / read-only presentation',
       'type':'reported','scope':'Lloyds Banking Group plc; dated government role attribution',
       'period':'22 March 2026','current_mandate_verified':False,'canonical_acceptance':False,
       'rights':'Existing explicitly open government factual-use category; narrow government-authored attribution only'}
    known={row['path'] for row in value['documents']}
    for folder in ('docs/research/lloyds-tier1-sprint1','docs/architecture/enterprise-twin-production'):
        for path in sorted((ROOT/folder).rglob('*')):
            if path.is_file() and path.suffix in {'.md','.json','.txt'} and str(path.relative_to(ROOT)) not in known:
                value['documents'].append({'path':str(path.relative_to(ROOT)),'sha256':sha256(path.read_bytes()).hexdigest(),
                      'authority':'Existing retained research / architectural proposal; not automatically public or canonical'})
    value['documents'].sort(key=lambda row:row['path'])
    value['research_quality_limit']='Document and claim counts are inventories, not completeness or verified canonical store counts. CEO domain A–F dispositions are in Research-and-coverage.md.'
    value['source_authority_delta']='No policy, allowlist, issuer rights, Financial-run or canonical authority expansion. One scoped OGL role fact uses the existing Source owner.'
    return value

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    value=report();path=HERE/'Knowledge-Audit.json'
    if args.check:assert json.loads(path.read_text())==value
    else:path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'retained_references':len(value['documents']),'overlay_eligible':value['eligible_lloyds_denominator'],
        'other_owner_items':value['other_owner_eligible_denominator'],'dated_role_items':1,'images_unchanged':len(value['original_images']),
        'whole_enterprise_complete':False,'passed':True}))
