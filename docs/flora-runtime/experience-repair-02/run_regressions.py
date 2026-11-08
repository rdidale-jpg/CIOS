"""Run Repair 02 relevant modules in separate temporary data roots.

Run from a Flora checkout. Supply the actual retained W6 and BNK ZIP paths with
FLORA_AUDIT_TEL_W6 and FLORA_AUDIT_BNK_W1; unavailable artifacts are explicit skips
inside the existing hash-pinned package tests. No production data is required.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

MODULES = ['test_flora_v2_information_architecture.py', 'test_flora_banking_portfolio_increment3.py', 'test_flora_banking_opportunity_pipeline.py', 'test_flora_banking_semantic.py', 'test_flora_banking_v2_web.py', 'test_flora_banking_final_pilot.py', 'test_flora_banking_increment44_executive_navigation.py', 'test_flora_banking_increment45_visual_intelligence.py', 'test_flora_banking_increment451_visual_correction.py', 'test_flora_banking_industry_reinvention_increment42.py', 'test_flora_banking_enterprise_intelligence.py', 'test_flora_observatory.py', 'test_enterprise_intelligence_reasoning.py', 'test_flora_factory_presentation_repair.py', 'test_flora_factory_researcher_model_repair.py', 'test_flora_enterprise_canvas.py', 'test_wp1_006_twin_governance.py', 'test_flora_intelligence_integrity.py', 'test_flora_material_pressure_lifecycle.py', 'test_flora_blueprint_import_promotion.py', 'test_flora_blueprint_import_registry.py', 'test_flora_blueprint_import_validation.py', 'test_flora_factory_evidence_release_repair.py', 'test_flora_twin_inspection.py', 'test_flora_experience_assurance_repair.py', 'test_flora_experience_discovery_repair.py']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=True)
    rows = []
    for module in MODULES:
        tag = module.removesuffix('.py')
        env = dict(os.environ, PYTHONPATH='.', FLORA_DATA_DIR=str(root / (tag + '-data')),
                   FLORA_PILOT_DIR=str(root / (tag + '-data')), FLORA_ENVIRONMENT='development')
        command = [sys.executable, '-m', 'pytest', '-q', '--tb=short',
                   '--basetemp=' + str(root / (tag + '-pytest')),
                   '--junitxml=' + str(root / (tag + '.xml')), 'tests/' + module]
        started = time.monotonic()
        result = subprocess.run(command, env=env, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        (root / (tag + '.log')).write_text(result.stdout)
        row = dict(module=module, command=command, exit_code=result.returncode,
                   duration_seconds=round(time.monotonic() - started, 2),
                   summary=result.stdout.splitlines()[-1],
                   failures=[line for line in result.stdout.splitlines()
                             if line.startswith(('FAILED', 'ERROR'))])
        rows.append(row)
        (root / 'results.json').write_text(json.dumps(rows, indent=2))
        print(module + ': ' + row['summary'], flush=True)
    return int(any(row['exit_code'] for row in rows))


if __name__ == '__main__':
    raise SystemExit(main())
