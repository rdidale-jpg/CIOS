from __future__ import annotations


def test_production_application_imports():
    from cios.applications.flora.web.app import app

    assert app is not None
