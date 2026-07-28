"""Pilot-only Flora owner session support.

This is not the target enterprise identity architecture. It issues one
application-owned, tamper-evident cookie after validating a deployment-owned
secret, then derives the pilot owner, workspace and role from server-side
environment configuration.
"""
from __future__ import annotations

import base64, hashlib, hmac, json, logging, os, time
from email.utils import formatdate
from dataclasses import dataclass
from html import escape
from typing import Any

from cios.applications.flora.workspace.views import _page

COOKIE_NAME = "flora_pilot_session"
AUTO_SIGN_IN_ENV = "FLORA_PILOT_AUTO_SIGN_IN"
APPLICATION_ENV_ENV = "FLORA_ENVIRONMENT"
SESSION_SIGNING_KEY_ENV = "FLORA_PILOT_SESSION_SIGNING_KEY"
DEFAULT_SESSION_DAYS = 30
SESSION_DAYS_ENV = "FLORA_PILOT_SESSION_DAYS"
LOGGER = logging.getLogger(__name__)


def _enabled() -> bool:
    return os.getenv("FLORA_PILOT_AUTH_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}


def pilot_auto_sign_in_requested() -> bool:
    """Return true only for an explicit, valid auto-sign-in value."""
    return os.getenv(AUTO_SIGN_IN_ENV, "false").strip().lower() in {"1", "true", "yes", "on"}


def _secret() -> str:
    return os.getenv("FLORA_PILOT_ACCESS_SECRET", "")


def _owner_id() -> str:
    return os.getenv("FLORA_PILOT_OWNER_ID", "")


def _workspace() -> str:
    return os.getenv("FLORA_PILOT_WORKSPACE", "")


def _role() -> str:
    return os.getenv("FLORA_PILOT_ROLE", "cios_owner")


def _signing_key() -> bytes:
    key_material = os.getenv(SESSION_SIGNING_KEY_ENV, "") or _secret()
    return hashlib.sha256(("flora-pilot-session:" + key_material).encode()).digest()


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


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


def pilot_auto_sign_in_status() -> PilotAutoSignInStatus:
    """Validate the explicit, fail-closed operational pilot configuration."""
    requested = pilot_auto_sign_in_requested()
    environment = os.getenv(APPLICATION_ENV_ENV, "").strip().lower()
    if not requested:
        return PilotAutoSignInStatus(False, False, environment)
    checks = (
        (environment in {"pilot", "preview", "development", "test"}, "environment is not an explicit pilot or non-production environment"),
        (bool(_enabled()), "pilot authentication is not enabled"),
        (bool(_owner_id().strip()), "canonical pilot owner is not configured"),
        (bool(_workspace().strip()), "pilot workspace is not configured"),
        (bool(_role().strip()), "pilot owner membership or effective role is not configured"),
        (bool(os.getenv(SESSION_SIGNING_KEY_ENV, "").strip()), "pilot session signing key is not configured"),
    )
    for valid, failure in checks:
        if not valid:
            return PilotAutoSignInStatus(True, False, environment, failure)
    return PilotAutoSignInStatus(True, True, environment)


def session_ttl_seconds() -> int:
    raw = os.getenv(SESSION_DAYS_ENV, str(DEFAULT_SESSION_DAYS)).strip()
    try:
        days = int(raw)
    except ValueError:
        days = DEFAULT_SESSION_DAYS
    if days < 1:
        days = DEFAULT_SESSION_DAYS
    return days * 24 * 60 * 60


def issue_session_cookie(*, secure: bool | None = None, now: int | None = None) -> str:
    issued_at = int(time.time() if now is None else now)
    ttl = session_ttl_seconds()
    expires_at = issued_at + ttl
    payload = {"v": 1, "sub": _owner_id(), "workspace": _workspace(), "role": _role(), "iat": issued_at, "exp": expires_at}
    payload_b64 = _b64(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
    sig = _b64(hmac.new(_signing_key(), payload_b64.encode(), hashlib.sha256).digest())
    attrs = [
        f"{COOKIE_NAME}={payload_b64}.{sig}",
        "Path=/",
        "HttpOnly",
        "SameSite=Lax",
        f"Max-Age={ttl}",
        f"Expires={formatdate(expires_at, usegmt=True)}",
    ]
    if secure if secure is not None else _secure_cookies():
        attrs.append("Secure")
    return "; ".join(attrs)


def clear_session_cookie(*, secure: bool | None = None) -> str:
    attrs = [f"{COOKIE_NAME}=", "Path=/", "HttpOnly", "SameSite=Lax", "Max-Age=0", "Expires=Thu, 01 Jan 1970 00:00:00 GMT"]
    if secure if secure is not None else _secure_cookies():
        attrs.append("Secure")
    return "; ".join(attrs)


def _secure_cookies() -> bool:
    return os.getenv("RENDER", "").lower() in {"1", "true"} or os.getenv("FLORA_SECURE_COOKIES", "").lower() in {"1", "true", "yes"}


def parse_cookie_header(header: str, name: str = COOKIE_NAME) -> str:
    for part in (header or "").split(";"):
        if "=" not in part: continue
        k, v = part.strip().split("=", 1)
        if k == name: return v.strip()
    return ""


def resolve_pilot_session(headers: Any) -> PilotSession | None:
    signing_material = os.getenv(SESSION_SIGNING_KEY_ENV, "") or _secret()
    if not _enabled() or not signing_material or not _owner_id():
        return None
    raw = parse_cookie_header(headers.get("Cookie", ""))
    try:
        payload_b64, sig = raw.split(".", 1)
        expected = _b64(hmac.new(_signing_key(), payload_b64.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(_unb64(payload_b64))
        if int(payload.get("exp") or 0) < int(time.time()):
            return None
        if payload.get("sub") != _owner_id() or payload.get("workspace") != _workspace() or payload.get("role") != _role():
            return None
        return PilotSession(str(payload["sub"]), str(payload["workspace"]), str(payload["role"]), int(payload["exp"]))
    except Exception:
        return None


def validate_secret(candidate: str) -> bool:
    return bool(_enabled() and _secret() and hmac.compare_digest(candidate or "", _secret()))


def sign_in_page(error: str = "") -> str:
    status = pilot_auto_sign_in_status()
    if status.requested:
        detail = status.failed_condition or "auto-sign-in could not establish the canonical pilot session"
        return configuration_error_page(detail)
    notice = f"<p class='warn'>{escape(error)}</p>" if error else ""
    return _page("Pilot sign in", f"""<section class='hero'><h1>Flora pilot access</h1><p>This is a pilot-only authentication mechanism for the configured CIOS owner. It is not enterprise SSO.</p>{notice}</section><section class='card'><form method='post' action='/pilot-sign-in'><label for='pilot_secret'>Pilot access secret</label><input id='pilot_secret' name='pilot_secret' type='password' autocomplete='current-password' required><p><button type='submit'>Sign in for pilot access</button></p></form></section>""")


def configuration_error_page(failed_condition: str) -> str:
    return _page("Pilot configuration error", f"""<section class='hero'><h1>Pilot auto-sign-in configuration error</h1><p class='warn'>Flora did not create a privileged session because {escape(failed_condition)}.</p></section><section class='card'><h2>Security warning</h2><p>Pilot auto-sign-in grants the configured pilot identity to anyone able to reach this service.</p><p>No secret, credential, or session value has been displayed.</p></section>""")


def pilot_banner_html() -> str:
    return "<aside class='pilot-auto-banner' role='status' style='position:sticky;bottom:0;z-index:20;display:flex;justify-content:center;align-items:center;gap:.6rem;flex-wrap:wrap;padding:.45rem .8rem;background:#fff4c2;border-top:1px solid #b99319;color:#392f0b;font-size:.88rem'><strong>Pilot auto-sign-in active</strong> · Acting as configured pilot owner <form method='post' action='/pilot-sign-out' style='display:inline;margin:0'><button type='submit' style='padding:.3rem .65rem'>Sign out</button></form></aside>"


def audit(event: str, **payload: Any) -> None:
    safe = {k: v for k, v in payload.items() if "secret" not in k and "cookie" not in k and "signature" not in k}
    LOGGER.info("flora_pilot_auth", extra={"flora_event": {"event": event, **safe}})
