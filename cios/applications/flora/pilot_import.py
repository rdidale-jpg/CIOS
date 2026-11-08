"""Closed legacy pilot-import policy for Security Repair 01A.

Deployment mode is neither verified human identity nor proof of a restricted
service perimeter. Keep historical actor constants for reading old receipts;
none of these constants or environment variables grants authority.
"""
from __future__ import annotations
from dataclasses import dataclass
from cios.applications.flora.security import ACCESS_UNAVAILABLE
from cios.applications.flora.workspace.views import _page

PILOT_MODE_ENV = "FLORA_ENVIRONMENT"
PILOT_IMPORT_BYPASS_ENV = "FLORA_PILOT_IMPORT_BYPASS"  # retired
PILOT_AUTO_SIGN_IN_ENV = "FLORA_PILOT_AUTO_SIGN_IN"  # retired
PILOT_IMPORT_ACTOR = "flora-pilot-operator"
PILOT_IMPORT_WORKSPACE = "flora-pilot-import"
PILOT_IMPORT_AUTH_MODE = "pilot"
PILOT_BLUEPRINT_CAPABILITIES = frozenset()

@dataclass(frozen=True)
class PilotImportMode:
    enabled: bool
    conflict: str = ""


def pilot_import_mode() -> PilotImportMode:
    """Legacy flags cannot establish authority or disable public source reads."""
    return PilotImportMode(False)


def pilot_import_bypass_enabled() -> bool:
    """Compatibility query: no deployment-mode authentication bypass exists."""
    return False


def pilot_import_warning() -> str:
    return ""


def pilot_import_configuration_error(reason: str) -> str:
    return _page("Import access unavailable", f"<section class='card'><h1>Import access unavailable</h1><p>{ACCESS_UNAVAILABLE}</p></section>")
