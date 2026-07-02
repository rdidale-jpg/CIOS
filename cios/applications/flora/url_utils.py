"""URL handling helpers for Flora reports and exported artefacts."""
from __future__ import annotations

import os
from urllib.parse import urljoin, urlparse

BASE_URL_ENV = "BASE_URL"


def base_url() -> str:
    return os.environ.get(BASE_URL_ENV, "").rstrip("/")


def report_href(path: str) -> str:
    """Return an absolute report link when BASE_URL is configured."""
    if not path:
        return ""
    parsed = urlparse(path)
    if parsed.scheme in {"http", "https", "mailto"}:
        return path
    if path.startswith("/") and base_url():
        return f"{base_url()}{path}"
    return path


def normalise_public_url(url: object) -> str:
    raw = str(url or "").strip().replace("\n", "").replace("\r", "")
    if not raw:
        return ""
    if raw.startswith("www."):
        raw = "https://" + raw
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return raw


def link_or_label(url: object, label: str | None = None) -> str:
    from html import escape
    good = normalise_public_url(url)
    if not good:
        shown = str(url or "missing URL").strip() or "missing URL"
        return f"<span class='muted'>not linked: {escape(shown)}</span>"
    return f"<a href='{escape(good)}'>{escape(label or good)}</a>"
