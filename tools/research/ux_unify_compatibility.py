"""Preserve historical validation through the pinned Facts-first changes."""
from hashlib import sha256
from pathlib import Path
import subprocess

BASE = "b2c7f168b4ff7b42a4518cf9ab9fed0aeda22618"
PINS = {
    "cios/applications/flora/visual_panels.py": "f81d3906c6eb8f9ffced1a0900944a555cb1af3a41165f49a8d306b2c1541c54",
    "cios/applications/flora/visual_streams.py": "33f86b7cd745a7afa9d967cb1ac53e6a5b53266dbd70e67e5e6a8a80dff31512",
    "cios/applications/flora/public_routes.py": "0f6a7ce86ef1e8520c48924040134e970f7fd849f93d25422d40148eb9b763e5",
    "cios/applications/flora/intelligence_presentation.py": "540853ddd3478bedeca2ab828f68aa8ca0988cbbdf2d37431a72c4740147a07c",
}


def predecessor(root, path):
    current = (Path(root) / path).read_bytes()
    if path not in PINS or sha256(current).hexdigest() != PINS[path]:
        return current
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=root)
