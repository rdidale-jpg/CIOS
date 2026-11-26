"""Check live candidate browser evidence, separately from frozen PR scope audits."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]


def check(directory):
    proof = json.loads((directory / 'Browser-after.json').read_text())
    assert proof['phase'] == 'after'
    assert proof['sha'] == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert proof['runtime_hashes']
    for name, digest in proof['runtime_hashes'].items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    assert proof['no_javascript'] and proof['withdrawal_history_reload_print_accessibility']
    devices = {'desktop', 'ipad-landscape', 'ipad-portrait', 'mobile'}
    assert len(proof['devices']) == 4 and {d['device'] for d in proof['devices']} == devices
    assert all(d['physical_hits'] and d['inspection_visible_and_44px'] and d['no_overflow']
               and not d['errors'] for d in proof['devices'])
    assert proof['audits'] and all(any(key.startswith(device + ':') for key in proof['audits'])
                                  for device in devices)
    assert all(not row['underlined'] and not row['small'] and not row['bare']
               and not row['nested'] and row['regions'] > 0 for row in proof['audits'].values())
    assert proof['screenshots']
    for name, digest in proof['screenshots'].items():
        assert Path(name).name == name
        assert sha256((directory / name).read_bytes()).hexdigest() == digest, name
    return {'head': proof['sha'], 'devices': 4, 'screenshots': len(proof['screenshots']),
            'runtime_bound': True, 'interaction_and_withdrawal_checks': True, 'passed': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    print(json.dumps(check(parser.parse_args().directory), indent=2))
