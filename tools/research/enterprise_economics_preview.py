"""Real loopback browser captures; isolated research/storage, no live services."""
import argparse
from hashlib import sha256
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def run(output, before=False):
    import pytest
    from cios.applications.flora.research_intelligence import model, registry
    from cios.applications.flora.web.app import FloraWebHandler

    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="flora-economics-") as scratch, pytest.MonkeyPatch.context() as patch:
        isolated = Path(scratch)
        shutil.copytree(ROOT / "enterprise-knowledge", isolated / "enterprise-knowledge")
        patch.setattr(model, "REPO", isolated)
        patch.setattr(model, "DATA", isolated / 'enterprise-knowledge/banking/research-model/Assessment-Overlay.json')
        patch.setattr(registry, "REPO", isolated)
        patch.setenv("FLORA_DATA_DIR", str(isolated / "app"))
        patch.setenv("FLORA_ENVIRONMENT", "development")
        patch.setenv("FLORA_AUTH_PROVIDER", "local")
        patch.delenv("FLORA_PILOT_DIR", raising=False)

        class Quiet(FloraWebHandler):
            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Quiet)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        config = isolated / "browser.json"
        config.write_text(json.dumps({"base": f"http://127.0.0.1:{server.server_port}",
                                     "repo": str(isolated), "output": str(output), "before": before}))
        try:
            subprocess.run(["node", str(ROOT / "tools/ci/flora_enterprise_economics_preview.cjs"), str(config)], check=True)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(2)
    (output / ("Before-Proof.json" if before else "Browser-Proof.json")).write_text(json.dumps({
        "checkout_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "runtime_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                           for p in sorted((ROOT / 'cios/applications/flora').glob('*.py'))}
                           | {"cios/applications/flora/visual_stream_assets/economics.css": sha256((ROOT / 'cios/applications/flora/visual_stream_assets/economics.css').read_bytes()).hexdigest()}
                           if not before else {},
        "mode": "baseline" if before else "implementation", "live_services": False,
        "production_or_canonical_writes": 0,
        "images": {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(output.glob(("before-" if before else "after-") + "*.jpg"))},
    }, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--before", action="store_true")
    args = parser.parse_args()
    run(args.output, args.before)
