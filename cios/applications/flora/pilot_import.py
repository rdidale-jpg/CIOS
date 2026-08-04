"""Canonical, explicit pilot-mode policy for candidate Twin imports.

Pilot mode is a deployment mode, not authentication.  It establishes one
repository-defined operator for the narrow receive/inspect/candidate-read path;
promotion and every unrelated capability continue to use normal authorisation.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from html import escape

from cios.applications.flora.workspace.views import _page

PILOT_MODE_ENV = "FLORA_ENVIRONMENT"
PILOT_IMPORT_BYPASS_ENV = "FLORA_PILOT_IMPORT_BYPASS"  # deprecated
PILOT_AUTO_SIGN_IN_ENV = "FLORA_PILOT_AUTO_SIGN_IN"  # deprecated for imports
PILOT_IMPORT_ACTOR = "flora-pilot-operator"
PILOT_IMPORT_WORKSPACE = "flora-pilot-import"
PILOT_IMPORT_AUTH_MODE = "pilot"
# Canonical capabilities of the repository-defined pilot operator.  Keep this
# grant deliberately narrower than owner authority: candidate review records are
# non-canonical, while candidate.promote remains absent and separately guarded.
PILOT_BLUEPRINT_CAPABILITIES = frozenset({
    "package.upload",
    "package.inspect",
    "package.review",
})


def _truthy(name: str) -> bool:
    return os.getenv(name, "").strip().casefold() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class PilotImportMode:
    enabled: bool
    conflict: str = ""


def pilot_import_mode() -> PilotImportMode:
    """Resolve the one supported pilot configuration and reject old overlays."""
    enabled = os.getenv(PILOT_MODE_ENV, "").strip().casefold() == "pilot"
    legacy = [name for name in (PILOT_IMPORT_BYPASS_ENV, PILOT_AUTO_SIGN_IN_ENV) if _truthy(name)]
    if legacy:
        return PilotImportMode(False, "conflicting deprecated pilot mode enabled: " + ", ".join(legacy))
    return PilotImportMode(enabled)


def pilot_import_bypass_enabled() -> bool:
    """Compatibility name for callers; authority is solely FLORA_ENVIRONMENT."""
    status = pilot_import_mode()
    return status.enabled and not status.conflict


def pilot_import_warning() -> str:
    if not pilot_import_bypass_enabled():
        return ""
    return ("<section class='card warning' role='status'><h2>Pilot import mode</h2>"
            "<p>Acting as the repository-defined pilot import operator. Identity, workspace and "
            "package upload authorisation are not applicable in pilot import mode.</p>"
            "<p>Import creates candidate intelligence only; canonical promotion remains separately authorised.</p></section>")


def pilot_import_configuration_error(reason: str) -> str:
    return _page("Pilot import configuration error", "<section class='hero'><h1>Pilot import configuration error</h1>"
                 f"<p class='warn'>{escape(reason)}</p></section><section class='card'><p>Remove deprecated pilot flags and "
                 "use only <code>FLORA_ENVIRONMENT=pilot</code>. No pilot actor was established.</p></section>")
