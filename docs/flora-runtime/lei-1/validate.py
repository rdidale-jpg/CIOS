"""Reproduce LEI calculations with the existing Wave 3 checks and Decimal."""
from decimal import Decimal
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = "434129b100f556c6e82acfaa162f6db3a322b017"


def main():
    pack = json.loads((HERE / "reconciliations.json").read_text())
    checks = pack["checks"]
    assert len({row["id"] for row in checks}) == len(checks)
    source_text = (HERE / "sources.md").read_text()
    for row in checks:
        assert row["operation"] == "sum"
        assert all(row[field] for field in ("period", "subject", "basis", "interpretation"))
        assert f'| {row["locator"].split()[0]} |' in source_text
        values = [Decimal(value) for value in row["inputs"]]
        assert all(value.is_finite() for value in values)
        assert sum(values) == Decimal(row["expected"]), row["id"]
    wave3 = HERE.parent / "research-enrich-all-w3-689"
    spec = spec_from_file_location("wave3_reconciliation", wave3 / "validate.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    measurements = module.index(module.read("Financial-Measurements.json"))
    recipes = module.index(module.read("Financial-Reconciliations.json"))
    for key in pack["reused_wave3"]:
        module.check_bridge(recipes[key], measurements)
    for report in HERE.glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", report.read_text()):
            if not target.startswith("https://"):
                assert (HERE / target).is_file(), (report.name, target)
    prefix = "docs/flora-runtime/lei-1/"
    changed = subprocess.check_output(["git", "diff", "--name-only", BASE], cwd=ROOT, text=True)
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True
    )
    assert all(path.startswith(prefix) for path in (changed + untracked).splitlines())
    print(f"{len(checks)} LEI and {len(pack['reused_wave3'])} Wave 3 checks passed. Research-only boundary intact.")


if __name__ == "__main__":
    main()
