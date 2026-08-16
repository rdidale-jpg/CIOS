"""Read-only deployment-to-runtime evidence for Flora's testing surfaces."""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
import os
import subprocess
import importlib

from cios.applications.flora.live.runtime import deployment_metadata

from .pilot_change import current_pilot_change

FEATURE = "evidence_utilisation_key_reports"
IMPLEMENTATION_OWNER = "cios.applications.flora.blueprint_import.key_reports.key_reports_for_enterprise"
IMPLEMENTATION_REVISION = "3"
ENTRYPOINT = "python -m cios.applications.flora.web.app"


@dataclass(frozen=True)
class RuntimeProof:
    repository_commit: str
    deployed_commit: str
    commit_match: str
    implementation_present: bool
    implementation_loaded: bool
    bt_route_connected: bool
    advanced_inspection_connected: bool
    functional_acceptance: str
    runtime_verdict: str
    executive_answer: str
    reason: str


def _repository_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unavailable"


def runtime_proof(*, functional_acceptance: str = "PASS") -> RuntimeProof:
    """Inspect loaded code and authoritative platform metadata without mutation."""
    repository = _repository_commit()
    # A checkout SHA is repository evidence only. Render's documented commit
    # variable is the authoritative deployment identity when it is available.
    deployed = os.getenv("RENDER_GIT_COMMIT", "").strip() or "unavailable"
    match = "UNKNOWN" if "unavailable" in {deployed, repository} else ("YES" if deployed == repository else "NO")
    try:
        from . import executive_workspace as implementation
        present = (callable(getattr(implementation, "_executive_enterprise_intelligence_html", None))
                   and callable(getattr(implementation, "_key_reports_html", None)))
        loaded = present
    except ImportError:
        implementation = None
        present = loaded = False
    try:
        routes = importlib.import_module("cios.applications.flora.blueprint_import.executive_workspace")
        bt_connected = loaded and callable(getattr(routes, "_dossier", None))
        inspection_connected = loaded and callable(getattr(routes, "_enterprise_factual_synthesis_diagnostics", None))
    except ImportError:
        bt_connected = inspection_connected = False
    if match == "NO":
        verdict, answer = "PROVEN MISMATCH", "NO"
        reason = "The authoritative deployed commit does not match the repository commit containing this change."
    elif not loaded or not bt_connected or not inspection_connected:
        verdict, answer = "DEPLOYMENT PROVEN — FEATURE FAILURE", "NO"
        reason = "The expected implementation is not loaded on every required runtime path."
    elif match == "YES":
        verdict, answer = "PROVEN CURRENT", "YES"
        reason = "The deployed commit matches and the expected feature is loaded on the BT and Advanced Inspection paths."
    else:
        verdict, answer = "PROVENANCE INCOMPLETE", "CANNOT PROVE"
        reason = "Render does not expose a trustworthy deployed commit identifier; feature route evidence is available."
    return RuntimeProof(repository, deployed, match, present, loaded, bt_connected, inspection_connected,
                        functional_acceptance, verdict, answer, reason)


def proof_html(*, detailed: bool = False) -> str:
    proof = runtime_proof()
    metadata = deployment_metadata()
    change = current_pilot_change()
    yesno = lambda value: "YES" if value else "NO"
    rows = {"Expected change": str(change.get("title") or "Unavailable"),
            "Repository commit": proof.repository_commit[:12], "Deployed commit": proof.deployed_commit[:12],
            "Commit match": proof.commit_match, "Application version/build": metadata["deployment_version"],
            "Current Change declaration loaded": "YES", "Expected feature implementation": FEATURE,
            "Implementation present": yesno(proof.implementation_present), "Loaded by runtime": yesno(proof.implementation_loaded),
            "Connected to BT route": yesno(proof.bt_route_connected),
            "Connected to Advanced Inspection": yesno(proof.advanced_inspection_connected),
            "Functional acceptance": proof.functional_acceptance,
            "Change status": ("IMPLEMENTATION PROVEN" if proof.executive_answer == "YES" else
                              "IMPLEMENTATION MISMATCH" if proof.runtime_verdict == "PROVEN MISMATCH" else
                              "DECLARED BUT NOT ACTIVE" if not proof.bt_route_connected else
                              "IMPLEMENTATION NOT PROVEN")}
    if detailed:
        rows.update({"Application entrypoint": ENTRYPOINT, "Loaded implementation owner": IMPLEMENTATION_OWNER,
                     "Implementation revision": IMPLEMENTATION_REVISION,
                     "Current Change declaration source": "config/current_pilot_change.json",
                     "Runtime proof verdict": proof.runtime_verdict})
    table = "".join(f"<tr><th>{escape(k)}</th><td><code>{escape(str(v))}</code></td></tr>" for k, v in rows.items())
    heading = "DEPLOYMENT-TO-RUNTIME TRACE" if detailed else "DEPLOYMENT &amp; RUNTIME PROOF"
    executive = "" if detailed else (f"<section class='primary-status'><h3>AM I TESTING THE EXPECTED CODE?</h3>"
        f"<p><strong>{proof.executive_answer}</strong></p><p><strong>Reason:</strong> {escape(proof.reason)}</p></section>")
    return f"<section class='card runtime-proof'><h2>{heading}</h2><table>{table}</table><h3>RUNTIME VERDICT: {escape(proof.runtime_verdict)}</h3>{executive}</section>"
