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


COHORT_BASE = "9a1e69fed6e1cf25c99476351232d69e9307a610"
COHORT = {
    "cios/applications/flora/visual_panels.py": "ac2b26a81307d3ffe6420e3032dd64fcba9587b7219f5f4a39d7c8c65809cf03",
    "cios/applications/flora/visual_streams.py": "27b74b09e2619d476404739a419379b9945798b1ab55014f02fa778d5a5ec17c",
}


LVIR_BASE = "2757e459f90fc4e1156180acf5f7ed9a40c292d9"
LVIR = {
    "cios/applications/flora/visual_panels.py": "c35485b91557d25124ad7a7e2c3b3b268d0e3c11dd3aeadb68df63b63e22429f",
    "cios/applications/flora/visual_streams.py": "69299c919ecbedd26b50d2f0d1b0ea42ec74e3cf164065ab7e06a17ed1a2f7fe",
}


# Route continuity changes one exact public dispatch branch. Historical owner
# checks still receive their original bytes after matching the entire new file.
AVIATION_JOURNEY_BASE = "088275e75365f1f251537d21e2601f10aa8e861a"
AVIATION_JOURNEY_APP = "cios/applications/flora/web/app.py"
AVIATION_JOURNEY_SHA256 = "547a14898b829af23e711ff4d97a332dc7f10bfbb5bd9f88b7dd3560f40ca446"


# Exact draft Factory presentation hook. Security dispatch and the earlier
# owner files are still checked against their independently pinned versions.
FACTORY_PREVIEW_BASE = "3e5aa2fc5dc1531ffb305374c91fad831b998fad"
FACTORY_PREVIEW_APP = "2c2d58493e6ff23ed8864cd6c0c71aa9377400a7aa3b7994efcbf4bb61c59385"


# Finite optional Lloyds preview routes. Match entire files before exposing
# their exact predecessor to historical checks; no unknown evolution is accepted.
PREVIEW_ROUTE_BASE = '97d316c640c96d99c2301819f8aac00b3b9c1398'
PREVIEW_ROUTE_PINS = {'cios/applications/flora/web/app.py': '232d7d9fbf736adc1d1c9735038a53cb0508af5e8c18b29ee46582fc0d47ec69', 'cios/applications/flora/public_routes.py': '17a39084779442cdea73a0bd9922be6722c815ac0ee3dfa2b164810472575916'}


# Gold Standard: one optional finite route and stylesheet. Historical pins stay
# immutable; only the entire reviewed bytes may resolve to #730's predecessor.
GOLD_ROUTE_BASE = 'eaca26f2b31c3c9227bb797d60f7d3492a8313d1'
GOLD_ROUTE_PINS = {'cios/applications/flora/web/app.py': '4cd79245a09eb776effa62e1276b33abaada8980c4cd87b485f1bc6de1e45990', 'cios/applications/flora/public_routes.py': 'ec4fc4eabb697ce7d1eec8f69e9dc361179faed37dbc145d517c233ac35a94e9'}

def gold_route_predecessor(root, path, current):
    if path in GOLD_ROUTE_PINS and sha256(current).hexdigest() == GOLD_ROUTE_PINS[path]:
        return subprocess.check_output(['git', 'show', f'{GOLD_ROUTE_BASE}:{path}'], cwd=root)
    return current


# CEO default: exact reviewed evolution; every earlier pin remains immutable.
CEO_BASE = '1c13e6962516dbb071b2133f2c1a3de87647e2ac'
CEO_PINS = {'cios/applications/flora/web/app.py': '4bfa58b674ffc293300626632d894894e9543e862386bebc92646ad835b05b2c', 'cios/applications/flora/public_routes.py': 'a9da56cb647eeecf1e8e3b0aae0454c577fdb670a220d84a79b53fbbb5c21662', 'cios/applications/flora/visual_streams.py': '5dc89b7988f0a45e4fbcad94c015a0d0e9735fbddaa513f53c42aeacf171270f', 'cios/applications/flora/research_intelligence/source_import.py': '4ec4d32e8ff09d3e5de187bcab2969618e5d4084a9a4da0cc0804fabcd54e6fa', 'tools/research/history_integrity.py': 'cd7715aa1065f6384fd2f342377e6b465dd3e29e631a806082a3f29a839ef323'}

def ceo_predecessor(root,path,current):
    if path in CEO_PINS and sha256(current).hexdigest()==CEO_PINS[path]:
        return subprocess.check_output(['git','show',CEO_BASE+':'+path],cwd=root)
    return current


def predecessor(root, path):
    current = (Path(root) / path).read_bytes()
    # This exact history-checker evolution admits only the two additive FCA
    # product files. Historical checks still receive their original checker;
    # an unrecognised change is never projected back to an approved cut.
    if (path == 'tools/research/history_integrity.py'
            and sha256(current).hexdigest() == '210b4e636268b0132529af7a6963ad3034c6986791b115c68c3344950d3db0c6'):
        current = subprocess.check_output(['git', 'show', '6b10935a31079d27fe00c88bf241d3d6bf1e3c98:'+path], cwd=root)
    current = ceo_predecessor(root,path,current)
    current = gold_route_predecessor(root, path, current)
    if path in PREVIEW_ROUTE_PINS and sha256(current).hexdigest() == PREVIEW_ROUTE_PINS[path]:
        current = subprocess.check_output(["git", "show", f"{PREVIEW_ROUTE_BASE}:{path}"], cwd=root)
    if path == AVIATION_JOURNEY_APP and sha256(current).hexdigest() == FACTORY_PREVIEW_APP:
        current = subprocess.check_output(["git", "show", f"{FACTORY_PREVIEW_BASE}:{path}"], cwd=root)
    if path == AVIATION_JOURNEY_APP and sha256(current).hexdigest() == AVIATION_JOURNEY_SHA256:
        current = subprocess.check_output(["git", "show", f"{AVIATION_JOURNEY_BASE}:{path}"], cwd=root)
    if path == "cios/applications/flora/public_routes.py" and sha256(current).hexdigest() == "0dc12bc420aa94b669253579ff312798d84c5c06a7af775cdc4ef6b194ee5442":
        current = subprocess.check_output(["git", "show", "df6173c186e6469783c732247f4c13aaa961aec4:" + path], cwd=root)
    from tools.research.enterprise_economics_compatibility import predecessor as economics_predecessor
    current = economics_predecessor(root, path, current)
    from tools.research.public_financial_compatibility import predecessor as public_predecessor
    current = public_predecessor(root, path, current)
    if path in LVIR and sha256(current).hexdigest() == LVIR[path]:
        current = subprocess.check_output(["git", "show", f"{LVIR_BASE}:{path}"], cwd=root)
    if path in COHORT and sha256(current).hexdigest() == COHORT[path]:
        current = subprocess.check_output(["git", "show", f"{COHORT_BASE}:{path}"], cwd=root)
    if path in EXPERIENCE and sha256(current).hexdigest() == EXPERIENCE[path]:
        current = subprocess.check_output(["git", "show", f"{EXPERIENCE_BASE}:{path}"], cwd=root)
    if path in BANKING and sha256(current).hexdigest() == BANKING[path]:
        current = subprocess.check_output(["git", "show", f"{BANKING_BASE}:{path}"], cwd=root)
    if path in INTEGRATION and sha256(current).hexdigest() == INTEGRATION[path]:
        current = subprocess.check_output(["git", "show", f"{INTEGRATION_BASE}:{path}"], cwd=root)
    if path not in PINS or sha256(current).hexdigest() != PINS[path]:
        return current
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=root)
