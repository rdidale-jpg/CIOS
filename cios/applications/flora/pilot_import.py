"""Explicit, route-scoped pilot import access configuration."""
from __future__ import annotations

import os

PILOT_IMPORT_BYPASS_ENV = "FLORA_PILOT_IMPORT_BYPASS"
PILOT_IMPORT_ACTOR = "flora-pilot"
PILOT_IMPORT_WORKSPACE = "flora-pilot-workspace"
PILOT_IMPORT_AUTH_MODE = "pilot_import_bypass"


def pilot_import_bypass_enabled() -> bool:
    """Enable only for the explicit string ``true`` (case-insensitive)."""
    return os.getenv(PILOT_IMPORT_BYPASS_ENV, "").strip().casefold() == "true"


def pilot_import_warning() -> str:
    if not pilot_import_bypass_enabled():
        return ""
    return ("<section class='card warning' role='alert'><h2>Pilot import bypass active</h2>"
            "<p>Pilot import bypass active - access controls are temporarily disabled for package import.</p>"
            "<p>Package import authorisation is temporarily disabled for this pilot environment.</p></section>")
