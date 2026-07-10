"""Pilot-only Flora owner session support.

This is not the target enterprise identity architecture. It issues one
application-owned, tamper-evident cookie after validating a deployment-owned
secret, then derives the pilot owner, workspace and role from server-side
environment configuration.
"""
from __future__ import annotations

import base64, hashlib, hmac, json, logging, os, time
from dataclasses import dataclass
from html import escape
from typing import Any

from cios.applications.flora.workspace.views import _page

COOKIE_NAME = "flora_pilot_session"
SESSION_TTL_SECONDS = 8 * 60 * 60
LOGGER = logging.getLogger(__name__)


def _enabled() -> bool:
    return os.getenv("FLORA_PILOT_AUTH_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}


def _secret() -> str:
    return os.getenv("FLORA_PILOT_ACCESS_SECRET", "")


def _owner_id() -> str:
    return os.getenv("FLORA_PILOT_OWNER_ID", "")


def _workspace() -> str:
    return os.getenv("FLORA_PILOT_WORKSPACE", "CIOS")


def _role() -> str:
    return os.getenv("FLORA_PILOT_ROLE", "cios_owner")


def _signing_key() -> bytes:
    secret = _secret()
    return hashlib.sha256(("flora-pilot-session:" + secret).encode()).digest()


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


def issue_session_cookie(*, secure: bool | None = None) -> str:
    now = int(time.time())
    payload = {"v": 1, "sub": _owner_id(), "workspace": _workspace(), "role": _role(), "iat": now, "exp": now + SESSION_TTL_SECONDS}
    payload_b64 = _b64(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
    sig = _b64(hmac.new(_signing_key(), payload_b64.encode(), hashlib.sha256).digest())
    attrs = [f"{COOKIE_NAME}={payload_b64}.{sig}", "Path=/", "HttpOnly", "SameSite=Lax", f"Max-Age={SESSION_TTL_SECONDS}"]
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
    if not _enabled() or not _secret() or not _owner_id():
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
    notice = f"<p class='warn'>{escape(error)}</p>" if error else ""
    return _page("Pilot sign in", f"""<section class='hero'><h1>Flora pilot access</h1><p>This is a pilot-only authentication mechanism for the configured CIOS owner. It is not enterprise SSO.</p>{notice}</section><section class='card'><form method='post' action='/pilot-sign-in'><label for='pilot_secret'>Pilot access secret</label><input id='pilot_secret' name='pilot_secret' type='password' autocomplete='current-password' required><p><button type='submit'>Sign in for pilot access</button></p></form></section>""")


def audit(event: str, **payload: Any) -> None:
    safe = {k: v for k, v in payload.items() if "secret" not in k and "cookie" not in k and "signature" not in k}
    LOGGER.info("flora_pilot_auth", extra={"flora_event": {"event": event, **safe}})
