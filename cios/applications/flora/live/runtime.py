"""Runtime build identification helpers for Flora live collection."""
from __future__ import annotations

import os
import subprocess
from functools import lru_cache

REVISION_ENV_NAMES = ("RENDER_GIT_COMMIT", "APPLICATION_REVISION", "APP_REVISION", "GIT_COMMIT", "SOURCE_VERSION")

@lru_cache(maxsize=1)
def application_revision() -> str:
    """Return a bounded non-secret application revision identifier."""
    for name in REVISION_ENV_NAMES:
        value = os.environ.get(name, "").strip()
        if value:
            return value[:64]
    try:
        return subprocess.check_output(["git", "rev-parse", "--short=12", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"
