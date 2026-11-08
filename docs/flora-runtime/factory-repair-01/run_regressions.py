"""Run Repair 01 regressions with a separate temporary data root per module.

Run from a Flora checkout using its test environment. External retained artifacts
are optional and selected by FLORA_AUDIT_TEL_W6 / FLORA_AUDIT_BNK_W1. Missing
artifacts produce explicit skips; the tests verify their SHA-256 when supplied.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

MODULES = [
    'test_flora_twin_import_lifecycle.py', 'test_wp1_006_twin_governance.py',
    'test_flora_enterprise_memory.py', 'test_material_pressure_qualification.py',
    'test_tel001_blueprint_import_regression.py', 'test_tel001_evidence_utilisation_key_reports.py',
    'test_tel001_enterprise_factual_presentation.py', 'test_tel001_executive_enterprise_intelligence.py',
    'test_flora_banking_industry_reinvention_increment42.py', 'test_industry_twin_semantic_reconciliation.py',
    'test_blueprint_manifest_contract.py', 'knowledge_packs/test_flora_blueprint_portable_contract.py',
    'test_flora_blueprint_import_registry.py', 'test_flora_blueprint_import_validation.py',
    'test_flora_blueprint_import_review_planning.py', 'test_flora_blueprint_import_promotion.py',
    'test_flora_blueprint_import_executive_review.py', 'test_flora_blueprint_import_restage.py',
    'test_flora_pilot_blueprint_review.py', 'test_flora_blueprint_import_interface.py',
    'test_flora_twin_inspection.py', 'test_flora_import_model_reconciliation.py',
    'test_flora_material_pressure_lifecycle.py', 'test_flora_external_change_interpretation.py',
    'test_evidence_provenance_applicability.py', 'test_flora_deployment_runtime_proof.py',
    'test_flora_intelligence_integrity.py', 'test_enterprise_intelligence_reasoning.py',
    'test_flora_factory_evidence_release_repair.py',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = args.output or Path(tempfile.mkdtemp(prefix='flora-factory-repair-01-'))
    root.mkdir(parents=True, exist_ok=True)
    (root / 'pytest').mkdir(exist_ok=True)
    rows = []
    for module in MODULES:
        tag = module.replace('/', '__')
        data = root / (tag + '.data')
        data.mkdir(exist_ok=True)
        env = dict(os.environ, FLORA_DATA_DIR=str(data), FLORA_PILOT_DIR=str(data),
                   PYTHONPATH='.', FLORA_ENVIRONMENT='development')
        command = [sys.executable, '-m', 'pytest', '-q', '--tb=short',
                   '--basetemp=' + str(root / 'pytest' / tag),
                   '--junitxml=' + str(root / (tag + '.xml')), 'tests/' + module]
        start = time.monotonic()
        result = subprocess.run(command, env=env, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        (root / (tag + '.log')).write_text(result.stdout)
        rows.append(dict(file=module, exit_code=result.returncode,
                         duration_seconds=round(time.monotonic() - start, 2),
                         summary=result.stdout.splitlines()[-1],
                         failures=[line for line in result.stdout.splitlines()
                                   if line.startswith(('FAILED ', 'ERROR '))]))
        (root / 'results.json').write_text(json.dumps(rows, indent=2))
        print(module + ': ' + rows[-1]['summary'], flush=True)
    print('Evidence:', root)
    return int(any(row['exit_code'] for row in rows))


if __name__ == '__main__':
    raise SystemExit(main())
