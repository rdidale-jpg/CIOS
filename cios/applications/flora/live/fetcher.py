"""Small, polite HTML fetcher for governed Flora sources."""
from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class FetchResult:
    url: str
    succeeded: bool
    status_code: int | None = None
    html: str = ""
    error: str = ""


def fetch_html(url: str, timeout: float = 8.0, max_bytes: int = 750_000) -> FetchResult:
    """Fetch one simple HTML page with timeout and bounded response size."""
    request = Request(url, headers={"User-Agent": "FloraPilotLiveEvidence/0.1 (+source-specific; no crawling)", "Accept": "text/html,application/xhtml+xml"})
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - governed allow-list URLs only
            status = getattr(response, "status", None)
            content_type = response.headers.get("Content-Type", "")
            if "html" not in content_type.lower():
                return FetchResult(url=url, succeeded=False, status_code=status, error=f"non-html content type: {content_type}")
            raw = response.read(max_bytes + 1)
            if len(raw) > max_bytes:
                return FetchResult(url=url, succeeded=False, status_code=status, error="response exceeded max_bytes")
            charset = response.headers.get_content_charset() or "utf-8"
            return FetchResult(url=url, succeeded=True, status_code=status, html=raw.decode(charset, errors="replace"))
    except HTTPError as exc:
        return FetchResult(url=url, succeeded=False, status_code=exc.code, error=f"HTTP {exc.code}: {exc.reason}")
    except (URLError, TimeoutError, OSError) as exc:
        return FetchResult(url=url, succeeded=False, error=str(exc))
