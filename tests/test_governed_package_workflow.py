from pathlib import Path


WORKFLOW = Path(".github/workflows/validate-governed-industry-twin-package.yml")


def test_obsolete_ukcg_workflow_is_removed():
    assert not Path(".github/workflows/validate-ukcg-candidate-blueprint.yml").exists()
    assert WORKFLOW.exists()


def test_governed_contract_workflow_is_path_scoped_and_not_ukcg_coupled():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "pull_request:" in text and "push:" in text and "paths:" in text
    assert "cios/applications/flora/blueprint_import/**" in text
    assert "test_flora_package_contracts.py" in text
    assert "UKCG" not in text and "uk-government" not in text
    assert "docs/**" not in text
