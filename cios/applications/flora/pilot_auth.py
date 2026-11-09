"""Disabled legacy pilot authentication compatibility surface.

Legacy sessions are not verified memberships and have no server-side revocation.
No password, cookie or auto-sign-in configuration can enable owner access in 01A.
Historical audit records are untouched.
"""
from __future__ import annotations
from dataclasses import dataclass
import logging
from typing import Any
from cios.applications.flora.security import ACCESS_UNAVAILABLE
from cios.applications.flora.workspace.views import _page

COOKIE_NAME = "flora_pilot_session"
AUTO_SIGN_IN_ENV = "FLORA_PILOT_AUTO_SIGN_IN"
APPLICATION_ENV_ENV = "FLORA_ENVIRONMENT"
SESSION_SIGNING_KEY_ENV = "FLORA_PILOT_SESSION_SIGNING_KEY"
SESSION_DAYS_ENV = "FLORA_PILOT_SESSION_DAYS"
DEFAULT_SESSION_DAYS = 30
LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True)
class PilotSession:
    user_id: str
    workspace: str
    role: str
    expires_at: int

@dataclass(frozen=True)
class PilotAutoSignInStatus:
    requested: bool
    active: bool
    environment: str
    failed_condition: str = ""


def pilot_auto_sign_in_requested() -> bool:
    import os
    return os.getenv(AUTO_SIGN_IN_ENV, "").strip().casefold() in {"1", "true", "yes", "on"}


def pilot_auto_sign_in_status() -> PilotAutoSignInStatus:
    import os
    return PilotAutoSignInStatus(pilot_auto_sign_in_requested(), False,
                                os.getenv(APPLICATION_ENV_ENV, ""), ACCESS_UNAVAILABLE)


def session_ttl_seconds() -> int:
    return 0


def issue_session_cookie(*, secure: bool | None = None, now: int | None = None) -> str:
    raise PermissionError(ACCESS_UNAVAILABLE)


def clear_session_cookie(*, secure: bool | None = None) -> str:
    return f"{COOKIE_NAME}=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT"


def parse_cookie_header(header: str, name: str = COOKIE_NAME) -> str:
    for item in (header or "").split(";"):
        key, separator, value = item.strip().partition("=")
        if separator and key == name:
            return value
    return ""


def resolve_pilot_session(headers: Any) -> PilotSession | None:
    return None


def validate_secret(candidate: str) -> bool:
    return False


def sign_in_page(error: str = "") -> str:
    return _page("Owner access unavailable", f"<section class='card'><h1>Owner access unavailable</h1><p>{ACCESS_UNAVAILABLE}</p><p>Public curated intelligence remains readable. Existing intelligence has not been changed.</p></section>")


def configuration_error_page(failed_condition: str) -> str:
    return sign_in_page()


def pilot_banner_html() -> str:
    return ""


def audit(event: str, **payload: Any) -> None:
    safe = {key: value for key, value in payload.items() if not any(word in key.lower() for word in ("secret", "cookie", "signature", "token", "password"))}
    LOGGER.info("flora_pilot_auth", extra={"flora_event": {"event": event, **safe}})
