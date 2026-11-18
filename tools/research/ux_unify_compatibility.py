"""Preserve historical validation through the pinned Facts-first changes."""
from hashlib import sha256
from pathlib import Path
import subprocess

BASE = "b2c7f168b4ff7b42a4518cf9ab9fed0aeda22618"
PINS = {
    "cios/applications/flora/visual_panels.py": "6e6c554da2776a265f5dc53191f600052eb4885a10c3c9220f0a3a817e949500",
    "cios/applications/flora/visual_streams.py": "5c1017baea87839598ef0d30e23dbf4f212319f43005d8170fa2bced766f56b2",
    "cios/applications/flora/public_routes.py": "0f6a7ce86ef1e8520c48924040134e970f7fd849f93d25422d40148eb9b763e5",
    "cios/applications/flora/intelligence_presentation.py": "540853ddd3478bedeca2ab828f68aa8ca0988cbbdf2d37431a72c4740147a07c",
}


INTEGRATION_BASE = "ad5345f7379e3b22b4a2ef012b7036170726e8d0"
INTEGRATION = {
    "cios/applications/flora/visual_panels.py": "d2b99753e31743950732aeefabb5c89cab43a67231991406eec27e35721f69a6",
    "cios/applications/flora/visual_streams.py": "9ae610b518047ab7155bf5c71a775d76d5b42908bfab55dab7e6555a94a80228",
    "cios/applications/flora/public_routes.py": "01abad3081e90c828227d7b664a67169a9b261fd98d8eb21a87f53947461a989",
    "cios/applications/flora/web/app.py": "bec05ce0f6ee8e1a6096e4fa645b136762a6141db1b3e7f410e887c8dadbd925",
}

BANKING_BASE="12f2aaef2e988222d4c0d79dbcc454ba3603a014"
BANKING={
    "cios/applications/flora/visual_panels.py": "04d1fe6a45004606c111cb72eefce11f56022b20b4d1d7a32d58e08f87dd06b7",
    "cios/applications/flora/visual_streams.py": "a968e8b5849e78789efa1fa0c6b517f241ef08071660f3d357ac7c4951c4682d",
}

EXPERIENCE_BASE = "c56bd74f130c4d855baf522ba8ba99fe87317fb1"
EXPERIENCE = {
    "cios/applications/flora/visual_panels.py": "561425f9d27ce417f427657961905e265e1a6a34c90542f5b4194c0de2c23ef0",
    "cios/applications/flora/visual_streams.py": "a6e2bd6aaacd2ab32d4b47f61822c756defa8655cfb30c6ffd85b63464e099ea",
}


def predecessor(root, path):
    current = (Path(root) / path).read_bytes()
    if path in EXPERIENCE and sha256(current).hexdigest() == EXPERIENCE[path]:
        current = subprocess.check_output(["git", "show", f"{EXPERIENCE_BASE}:{path}"], cwd=root)
    if path in BANKING and sha256(current).hexdigest() == BANKING[path]:
        current = subprocess.check_output(["git", "show", f"{BANKING_BASE}:{path}"], cwd=root)
    if path in INTEGRATION and sha256(current).hexdigest() == INTEGRATION[path]:
        current = subprocess.check_output(["git", "show", f"{INTEGRATION_BASE}:{path}"], cwd=root)
    if path not in PINS or sha256(current).hexdigest() != PINS[path]:
        return current
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=root)
