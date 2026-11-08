from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _legacy_flora_header_trust_for_existing_tests(monkeypatch):
    """Keep legacy unit tests explicit while production defaults remain off."""
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")

@pytest.fixture
def verified_flora_test_authority(monkeypatch, request):
    """Explicit service fixture, separate from production-boundary acceptance."""
    if request.node.get_closest_marker('real_security_boundary'):
        raise AssertionError('Production security checks cannot install fixture authentication')
    from cios.applications.flora import access
    from tests.flora_security_fixtures import fixture_context
    monkeypatch.setattr(access,'verified_context',fixture_context,raising=False)
    try:
        from cios.applications.flora import security
    except ImportError:
        pass  # Same test overlay is used against pinned main.
    else:
        monkeypatch.setattr(security,'verified_context',fixture_context)
