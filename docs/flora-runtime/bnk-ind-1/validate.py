"""Check research references and reviewed handoff boundaries using the stdlib."""
import json
from pathlib import Path
import re
import subprocess

PACK = Path(__file__).resolve().parent
ROOT = PACK.parents[2]
BASE = "fbac4c37910ed07b2baa516e1a5c8d7f329086de"
data = json.loads((PACK / "Handoff.json").read_text())
rows = {row["id"]: row for row in data["rows"]}
sources = data["sources"]

def baseline(path):
    return json.loads(subprocess.check_output(
        ["git", "show", f"{BASE}:{path}"], cwd=ROOT, text=True
    ))

base_paths = set(subprocess.check_output(
    ["git", "ls-tree", "-r", "--name-only", BASE], cwd=ROOT, text=True
).splitlines())
links = 0
for document in PACK.glob("*.md"):
    for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
        if target.startswith("https://"):
            continue
        resolved = (document.parent / target).resolve()
        assert resolved.is_file() or resolved.relative_to(ROOT).as_posix() in base_paths, target
        links += 1

assert len(rows) == len(data["rows"])
for source in sources.values():
    assert source["url"].startswith("https://")
    assert source["repo_anchor"] is None or source["repo_anchor"] in base_paths
    if digest := source.get("retrieved_html_sha256"):
        assert re.fullmatch(r"[a-f0-9]{64}", digest)

for row in rows.values():
    assert row["source_ids"] and set(row["source_ids"]) <= sources.keys()
    assert set(row["dates"]) == {"published", "event", "effective", "reporting", "retrieved"}
    assert row["subject"] and row["target"] and row["invalidation"]
    if row["status"].startswith("existing_eligible"):
        assert all("Research only" not in sources[s]["rights"] for s in row["source_ids"])

bie2 = "docs/flora-runtime/bie2/"
actors = baseline(bie2 + "Actor-Register.json")["actors"]
actor_ids = {actor["id"] for actor in actors}
assert len(actors) == len(actor_ids) == 76
assert len(baseline(bie2 + "Relationship-Candidates.json")["edges"]) == 31
news = baseline(bie2 + "News-Candidates.json")["events"]
assert len(news) == 17 and all(not event["production_news_eligible"] for event in news)
for row in rows.values():
    assert {ref for ref in row["existing_refs"] if ref.startswith("actor:")} <= actor_ids

assert rows["IND-REJECT"]["status"] == "suppress"
assert rows["IND-REJECT"]["scene"] == "none"
assert rows["IND-ENVOY"]["subject"] == "BK-ENT-001"
assert rows["IND-ENVOY"]["target"] == "SUP-GOOGLE"
assert rows["IND-ENVOY"]["dates"]["event"] is None
assert rows["IND-CTP"]["dates"]["effective"] == "2026-07-13"
for participant in ("LLOYDS", "NATIONWIDE"):
    role = rows[f"IND-PART-{participant}"]
    assert role["subject"] == f"actor:{participant.lower()}" and role["target"] == "actor:fps"
    assert role["predicate"] == "operator_lists_participant_in" and role["status"] == "review_only"

measures = data["measures"]
nbs = measures["nationwide_gbp_million"]
assert nbs["income"] - nbs["operating_costs"] - nbs["impairment"] == nbs["underlying_pbt"]
assert (nbs["underlying_pbt"] + nbs["income_adjustment"]
        - nbs["acquisition_expense_adjustment"] - nbs["member_rewards"]) == nbs["statutory_pbt"]
assert nbs["integration_in_operating_costs"] == 127
for rail, rounded in {"Bacs": 882, "FPS": 872}.items():
    activity = measures["rail_principal"][rail]
    assert round(activity["principal_gbp_trillions"] * 1000 / activity["transaction_billions"]) == rounded
switches = measures["cass_switches"]
assert round(100 * (switches["2026-Q3"] / switches["2025-Q3"] - 1)) == 55

print(f"{links} documentation links, {len(sources)} inputs and {len(rows)} handoff rows checked")
print("BIE-2 identity, News isolation, legal endpoint, financial bridge and comparison checks passed")
