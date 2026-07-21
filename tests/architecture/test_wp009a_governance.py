from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[2]
SCOPE = ROOT / "architecture/governance/governed-architecture-scope.yaml"
ID_RE = re.compile(r"\b(?:ADR|AP|EIRP|EU|FEIR|RP)-\d{3}\b")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _scope():
    data = {"required_metadata": [], "valid_statuses": [], "governed_paths": [], "excluded_classifications": []}
    current = None
    for raw in _read(SCOPE).splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line:
            continue
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value.startswith("["):
                data[key] = [item.strip() for item in value.strip("[]").split(",") if item.strip()]
                current = None
            elif value:
                data[key] = value
                current = None
            else:
                data.setdefault(key, [])
                current = key
        elif current and line.strip().startswith("- "):
            data[current].append(line.strip()[2:])
    return data


def test_wp009a_scope_is_explicit_not_markdown_scan():
    scope = _scope()
    assert scope["canonical_adr_path"] == "architecture/decisions/"
    assert "governed_paths" in scope
    assert "excluded_classifications" in scope
    assert not any(item == "**/*.md" for item in scope["governed_paths"])


def test_known_duplicate_groups_have_one_canonical_owner():
    governed = [ROOT / p for p in _scope()["governed_paths"]]
    seen = {}
    for path in governed:
        text = _read(path)
        match = re.search(r"\*\*Identifier:\*\*\s*([^\n ]+)", text)
        assert match, f"Missing Identifier metadata: {path}"
        ident = match.group(1).strip()
        assert ident not in seen, f"Duplicate governed identifier {ident}: {seen[ident]} and {path}"
        seen[ident] = path
    for ident in ["ADR-003", "ADR-004", "ADR-015", "AP-001", "EIRP-001", "EU-001", "FEIR-001", "RP-001"]:
        assert ident in seen


def test_governed_metadata_complete_and_status_vocabulary():
    required = _scope()["required_metadata"]
    statuses = set(_scope()["valid_statuses"])
    for rel in _scope()["governed_paths"]:
        text = _read(ROOT / rel)
        for field in required:
            assert f"**{field}:**" in text[:1200] or (field == "Date" and ("**Last updated:**" in text[:1200] or "**Decision date:**" in text[:1200] or "**Date:**" in text[:1200])) or (field == "Title" and text.startswith("# ")), f"{rel} missing {field}"
        status = re.search(r"\*\*Status:\*\*\s*([^\n]+)", text).group(1).strip().split()[0]
        assert status in statuses, f"{rel} status {status} not in approved vocabulary"


def test_canonical_adrs_are_in_decisions_and_legacy_adrs_are_classified():
    assert not (ROOT / "architecture/adr/ADR-015-Runtime-Mission-Context.md").exists()
    for path in (ROOT / "architecture/decisions").glob("ADR-*.md"):
        assert path.parent.as_posix().endswith("architecture/decisions")
    for rel in [
        "architecture/decisions/Historical-Observation-Identity-and-Minimal-Model-Projection-Draft.md",
        "architecture/decisions/UK-Banking-Theme-Taxonomy-Decision.md",
        "docs/adr/commercial-intelligence-recommendations-ranking-valuation-decision.md",
    ]:
        text = _read(ROOT / rel)[:500]
        assert "**Governance classification:**" in text
        assert "**Canonical architecture identifier:** None" in text


def test_authority_registry_and_document_map_paths_resolve():
    for rel in ["architecture/reference-architecture/Architecture-Authority-Registry.md", "architecture/reference-architecture/Document-Map.md"]:
        base = (ROOT / rel).parent
        for target in re.findall(r"`([^`]+\.md)`", _read(ROOT / rel)):
            path = ROOT / target if not target.startswith("..") else (base / target).resolve()
            assert path.exists(), f"Broken path in {rel}: {target}"
