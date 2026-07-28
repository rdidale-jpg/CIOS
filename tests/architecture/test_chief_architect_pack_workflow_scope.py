from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "knowledge-packs/chief-architect/manifest.yaml"
WORKFLOW = ROOT / ".github/workflows/validate-chief-architect-knowledge-pack.yml"


def _manifest_sources() -> set[str]:
    return {
        line.strip().split(": ", 1)[1]
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("source_path: ")
    }


def _pull_request_paths() -> set[str]:
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    start = lines.index("  pull_request:")
    end = lines.index("  push:")
    return {
        line.strip()[3:-1]
        for line in lines[start:end]
        if line.strip().startswith('- "')
    }


def test_proposed_navigation_does_not_enter_pack_source_validation():
    """Review discovery must not make a Proposed paper a production pack input."""
    paths = _pull_request_paths()

    assert paths == _manifest_sources() | {
        "knowledge-packs/chief-architect/**",
        "tests/knowledge_packs/test_chief_architect_pack.py",
        "tools/knowledge-packs/build_pack.py",
    }

    # FP-013 is registered and linked by review/navigation documents without
    # those documents (or the Proposed paper) becoming a pack checksum source.
    assert "architecture/founding-papers/FP-013-*.md" not in paths
    assert "architecture/founding-papers/FP-013-Executive-Intelligence-Workspace.md" not in _manifest_sources()
    assert "architecture/founding-papers/FP-014-*.md" not in paths
    assert "architecture/founding-papers/FP-014-Mission-Aware-Executive-Intelligence-Composition.md" not in _manifest_sources()
    assert "architecture/reference-architecture/**" not in paths
    assert "architecture/reference-architecture/Document-Map.md" not in paths
    assert "architecture/reference-architecture/Architecture-Authority-Registry.md" not in paths
