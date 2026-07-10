from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _legacy_flora_header_trust_for_existing_tests(monkeypatch):
    """Keep legacy unit tests explicit while production defaults remain off."""
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
