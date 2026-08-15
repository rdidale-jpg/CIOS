# Flora Deployment-to-Runtime Proof Audit

## 1. Existing architecture

Flora already owns build identity in `live/runtime.py`: Render environment values are read first and checkout Git is only a fallback application revision. `render.yaml` starts `python -m cios.applications.flora.web.app`. The Import screen's operational acceptance owner is `blueprint_import/deployment_status.py`; its declaration is loaded by `blueprint_import/pilot_change.py` from `config/current_pilot_change.json`. This audit reuses those owners and adds only a read-only proof projection in `runtime_proof.py`.

## 2. Current Change provenance

The canonical declaration is the static repository JSON file. It supplies the title, objective, visible outcomes, fresh-import policy, validation claims, and deployment placeholders. Its visibility proves only that this JSON was readable by the loaded application. It does **not** prove that another implementation module loaded or that a route called it. Declaration and feature proof are therefore displayed separately.

## 3. Repository and deployment identity

The repository examined before this audit commit was `a3d8ca70e8064b6f32d80e5de5f2f62a613e27dc` on `work`. The TEL-001 fixture SHA-256 was independently verified as `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`.

Render configuration declares service `flora`, build command `pip install -r requirements.txt`, and the application entrypoint above. Render's `RENDER_GIT_COMMIT` is treated as authoritative when present. Service name, version, branch and timestamps are useful identity context but are not commit-equality proof. In the local validation environment no authoritative deployed SHA is present, so deployed commit and commit match remain `unavailable` and `UNKNOWN`; a Render mismatch is not proven.

## 4. Loaded runtime and BT route trace

The expected marker is `enterprise_factual_synthesis`, revision `1`, owned by `canonical_factual_projection.enterprise_factual_synthesis`. The module imports and the callable exists. The actual HTTP route is `/blueprint-import/<run>/enterprises/BT%20Group`, dispatched by `web.app` to `executive_workspace_page`. Its `_dossier` constructor obtains `factual_projection_for_enterprise(ent)`, reads the carried `enterprise_synthesis`, and passes a generated statement to Organisation Overview. Focused real-page rendering produced the BT statement and therefore establishes: reachable YES, executed YES, output YES, consumed YES, rendered YES in the checked-out runtime.

## 5. Advanced Inspection trace

The route `/blueprint-import/<run>/explore` also dispatches to `executive_workspace_page`. `_explorer` now renders the deployment-to-runtime trace. The existing `_enterprise_factual_synthesis_diagnostics` callable produces `ENTERPRISE FACTUAL SYNTHESIS TRACE` and is invoked by the actual workspace assembly. Focused rendering establishes repository presence, loaded callable, invocation and output as YES for this checkout.

## 6. Feature proof and classification

The checked-out repository is internally connected on both paths. The supplied earlier runtime output nevertheless showed a declaration that appeared to imply active implementation without independent provenance. The evidence-backed classification is **H — CURRENT CHANGE DECLARATION FALSELY IMPLIES FEATURE PRESENCE**. The first divergence is between a loaded static declaration and absent independent loaded-route proof. Neither a Render/repository mismatch nor a synthesis defect can be proven from that supplied output because it contains no authoritative deployed SHA.

The new proof evaluates commit equality only from authoritative deployment SHA, imports the implementation, inspects both real route owners, and keeps `UNKNOWN` distinct from mismatch. Missing optional commit metadata does not change the existing functional-test readiness decision.

## 7. Recommended next correction (do not implement in this sprint)

Deploy this observability change, capture the Import and Advanced Inspection proof panels from Render, and compare `RENDER_GIT_COMMIT` with the expected merge commit. If commits match and either route reports disconnected, inspect the reported loaded owner/entrypoint in the next sprint. If both routes report connected but BT produces no output, open a separate factual-synthesis defect sprint using that proven runtime evidence. Do not change synthesis before collecting it.
