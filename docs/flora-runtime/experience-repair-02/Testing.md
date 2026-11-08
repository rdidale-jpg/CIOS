# Reproduce Repair 02 acceptance

Use a disposable checkout and temporary directories, never production data.
Python 3.11+, project dependencies and pytest are required. Browser acceptance
also requires Playwright and local Chromium (`/usr/bin/chromium` in this run).
Supply original retained archives through `FLORA_AUDIT_TEL_W6` and
`FLORA_AUDIT_BNK_W1`; TEL W5 is already retained in the repository. Tests check
exact artifact hashes; absent external artifacts are explicit skips, not passes.

```bash
export FLORA_AUDIT_TEL_W6=/absolute/path/to/original-tel-w6.zip
export FLORA_AUDIT_BNK_W1=/absolute/path/to/original-bnk-w1.zip
python docs/flora-runtime/experience-repair-02/run_regressions.py --output=/tmp/repair02-after
```

The runner exits nonzero while inherited failures remain. Compare the same
modules at pinned main `acaf99cd26c5faf7719cf0fbda48edef6bc97c59` in a separate
checkout, copying only the new regression module for the before run. Each module
runs separately with isolated `FLORA_DATA_DIR`, `FLORA_PILOT_DIR` and pytest temp
root. Do not interpret the absence of the new API at baseline as an existing test
regression; those 27 new failing cases establish the repair's before state.

## Browser fixtures and server

The supplied harness is an audit/test utility, not a production launcher.
Use a fresh evidence directory. `prepare_browser.py` intentionally creates
synthetic model/access/ambiguity fixtures and uses the existing Factory Repair 03
retained BNK test flow in disposable storage. Its historical fixture uses a
synthetic successor reference, not a real accepted successor.

```bash
export PYTHONPATH=.
export FLORA_DISCOVERY_BROWSER_EVIDENCE=/tmp/repair02-browser
mkdir -p "$FLORA_DISCOVERY_BROWSER_EVIDENCE"
python docs/flora-runtime/experience-repair-02/prepare_browser.py
```

Copy the fixture `current` directory to `before-current` before any browsing.
Launch four local server processes with `FLORA_ENVIRONMENT=development`,
`FLORA_TRUST_PROXY_HEADERS=1`, and both `FLORA_DATA_DIR` and `FLORA_PILOT_DIR`
pointing to their respective fixture roots. Use the supplied `serve.py`:

| Port / checkout | Root below `$FLORA_DISCOVERY_BROWSER_EVIDENCE/browser-fixtures` |
| --- | --- |
| 18800 / pinned main | before-current |
| 18801 / Repair 02 | current |
| 18802 / Repair 02 | history |
| 18803 / Repair 02 | empty |

Run `python /absolute/path/to/serve.py <port>` from the appropriate checkout;
`PYTHONPATH=.` must resolve that checkout. Each server uses the existing handler,
not application startup/migration. The helper directs pre-existing derived
Banking output outside the owner stores. Development trusted headers are used
only for local synthetic identities; do not expose these servers externally.

Run `python docs/flora-runtime/experience-repair-02/browser_acceptance.py` with a
Python environment containing Playwright. It writes screenshots, visible route
text and JSON under the evidence root, compares entire store fingerprints, and
exits nonzero if any after observation fails. Stop the four local processes when
finished. Main's alias 404 and absent shared discovery are expected before defects.
