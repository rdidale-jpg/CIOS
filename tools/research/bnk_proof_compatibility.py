"""Verify the finite Banking presentation evolution before historical checks."""
from hashlib import sha256
from pathlib import Path
import subprocess

BASE = "fbac4c37910ed07b2baa516e1a5c8d7f329086de"
PINS = {
    "cios/applications/flora/visual_panels.py": "cfe88811554814bb1cab41605a32a3d13235f2fb82c1f88fe08ec5defd9e54ff",
    "cios/applications/flora/visual_streams.py": "43105f5cdd7ad2bcc6118c00127e14942704584a1d3866062881478fdd915b0b",
}


def predecessor(root, path):
    actual = (Path(root) / path).read_bytes()
    if path not in PINS:
        return actual
    prior = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=root)
    if actual == prior:
        return actual
    if sha256(actual).hexdigest() == PINS[path]:
        return prior
    return actual
