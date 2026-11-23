# Factory completion sprint · owner review

Baseline is main at `92927753e13ad54251d91cb01b8b726a47486304`, the exact tree approved for #718. Its [post-merge validation](https://github.com/rdidale-jpg/CIOS/actions/runs/45139773767) passed.

## Body extraction and conflict review

The existing discovery command now has an optional body pass. Start with the four enterprise identifiers, with no article URLs, claim text, or per-enterprise anchors. The original discovery limits, official paths, exclusions, dates and transport still apply.

```bash
printf '%s\n' '["lloyds-banking-group-plc","bt-group-plc","arm-holdings-plc","easyjet-plc"]' >/tmp/flora-completion-commission.json
python -m tools.research.initial_factory /tmp/flora-completion-commission.json --discover --extract-body /tmp/flora-body-first
python -m tools.research.initial_factory /tmp/flora-completion-commission.json --discover --extract-body \
  --previous-discovery /tmp/flora-body-first/discovery.json /tmp/flora-body-repeat
```

The body pass locates candidate sentences using generic event verbs, including announcements, investments, availability, supply, partnerships and rollout status. Where the text identifies a role, the report can suggest an explicitly worded partner, supplier or customer. It preserves original URL, raw-byte SHA-256, publisher, publication date and paragraph/sentence position. Mentioned dates remain separate from publication dates. The candidate excerpt stays in local review output. The repository [manifest](body-proof.json) omits excerpts and object text.

An exact claim ID identifies the same document revision and location. Event hints group matching actor and subject wording and report differences in dates, status or named relationship descriptions. A changed milestone or a later status may reflect real progression, so the assessment asks for review. Distinct publishers can still rely on the same release. A reviewer can supply links between claims about the same event and identify their underlying origins. That offline assessment never changes the claims or grants publication. Earlier wave claims remain available for comparison if the original report is retained. Withdrawn input is excluded from the comparison.

### Live checks on 23 November 2026

| Enterprise | Body candidates | Checked interpretation |
| --- | ---: | --- |
| Lloyds | 1 | The report caught publication of the responsible AI guide. The narrower accepted committee evidence still depends on the separately reviewed #718 proof. [Issuer release](https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds-banking-group/responsible-ai-guide.html) |
| BT | 3 | It caught BT's reported SWAN completion and a supplier appointment statement. The latter's scope and date need verification. The same release includes context about a separate planned joint venture in its body. It belongs in a different event review. [Issuer release](https://newsroom.bt.com/bt-transforms-scotlands-public-sector-connectivity--upgrading-the-nations-digital-infrastructure/) |
| Arm | 2 | The Cobalt 200 availability sentence was located beyond the headline. The other article describes engineering optimisations. Both originate from Arm and cover related subject matter. They provide no independent confirmation of Microsoft availability. [Availability release](https://newsroom.arm.com/news/arm-microsoft-azure-cobalt-200) · [Separate engineering article](https://newsroom.arm.com/blog/arm-neoverse-based-microsoft-cobal-200-vms-cloud-agentic-ai-performance) |
| easyJet | 4 | The report distinguished a planned Starlink rollout from the dated publication. A newly processed article described additional summer 2027 routes. The same article includes an older roadmap reference, which needs to be kept separate from the route announcement. [Starlink release](https://www.easyjet.com/en/news/airline/story/easyjet-to-offer-connectivity-onboard-for-the-first-time-with-starlink-the-fastest-wi-fi-in-the-sky-with-rapid-roll-out-coming-from-2027) · [Routes release](https://www.easyjet.com/en/news/airline/story/easyjet-announces-additional-new-routes-for-summer-2027) |

20 article links yielded 11 dated discovery leads and 10 candidate body excerpts. The analysis sampled the excerpts against the source wording. No material contradiction was established in the live sample. Controlled tests demonstrate conflicting milestones and counterparties, repeat suppression, and shared versus distinct reviewed origins. Issuer claims stay labelled as candidates. The renderer uses only reviewed, accepted isolated Evidence. No extracted candidate in this run entered an Enterprise Model or Pipeline.

## Research operations preview

`python -m tools.research.factory_operations_preview OWNER_STATE.json REVIEW_INTENT.json` reads the existing revision envelope described in the [verified proof](../verified/README.md#source-revision-withdrawal). The intent requires `enterprise`, `workspace`, a time-zoned `run_after` and an optional `withdrawals` array of exact URL and SHA-256 pairs. The command emits a deterministic intent ID, proposed transition, existing approval requirements and a reverse-diff preview. It performs no writes. A rollback preview is audit information and confers no authority to restore a withdrawn source. Timing is a review field. There is no scheduler, worker or standing execution grant. Before a future operation, the Source owner still owns lifecycle state and the existing scoped Blueprint approver owns acceptance and publication. Lloyds §2 and §5, BT and easyJet issuer-use limits and the Financial boundary are preserved.

## Visual comparisons

Comparisons use the same accepted fixture records rendered on main and on the draft. Cases cover Lloyds Forces, BT Canvas, Arm Landscape and easyJet Inside. The compact disclosure keeps the headline and confidence label visible. Its first expansion gives the date, why it matters and the investigation question. The second shows supporting evidence. Both can be opened by keyboard or simulated touch.

| Enterprise | Desktop | iPad portrait | iPad landscape |
| --- | --- | --- | --- |
| Lloyds | [Desktop](previews/lloyds-banking-group-plc-route-desktop.jpg) | [Portrait](previews/lloyds-banking-group-plc-route-ipad-portrait.jpg) | [Landscape](previews/lloyds-banking-group-plc-route-ipad-landscape.jpg) |
| BT | [Desktop](previews/bt-group-plc-route-desktop.jpg) | [Portrait](previews/bt-group-plc-route-ipad-portrait.jpg) | [Landscape](previews/bt-group-plc-route-ipad-landscape.jpg) |
| Arm | [Desktop](previews/arm-holdings-plc-route-desktop.jpg) | [Portrait](previews/arm-holdings-plc-route-ipad-portrait.jpg) | [Landscape](previews/arm-holdings-plc-route-ipad-landscape.jpg) |
| easyJet | [Desktop](previews/easyjet-plc-route-desktop.jpg) | [Portrait](previews/easyjet-plc-route-ipad-portrait.jpg) | [Landscape](previews/easyjet-plc-route-ipad-landscape.jpg) |

For a comparison, run `CIOS_VERIFIED_ROUTE_OUTPUT=/tmp/flora-before python -m pytest -q tests/test_flora_verified_factory.py` at the baseline. Run the same test at the draft with `CIOS_VERIFIED_ROUTE_OUTPUT=/tmp/flora-after`. Then run `PYTHONPATH=. python docs/research/initial-factory/verified/browser.py /tmp/flora-after --baseline-responses /tmp/flora-before --output /tmp/flora-captures`. The proof checks pre-approval absence, repeat execution, denied access, and removal on a withdrawn or missing Source revision. It uses temporary storage throughout.

## Commercial and design critique

The strongest sales intelligence in this wave distinguishes product availability, rollout plans and reported delivery milestones. Those distinctions support different questions. Arm needs regional and workload eligibility checks, easyJet needs rollout ownership, and BT needs buyer-side acceptance evidence. A second article from the same source can help locate context while adding no independent proof.

The compact easyJet card brings the existing workflow and capability tiles back into the first iPad landscape screen. The collapsed cards preserve artwork and navigation, with confidence visible before expansion. The trade-off is two actions to reach evidence and a dense summary when a long title wraps in portrait. The comparison uses Chromium emulation. Physical iPad and Safari checks remain open.

Factory v1.0 remains incomplete. The rules miss paraphrases and some long-form or nested claims, can admit boilerplate, and cannot resolve commercial identities or assess source independence without review. A high-value next step is a representative reviewed corpus, semantic event and party resolution, and a controlled path from extracted claim to eligible Source/Blueprint review. Owner decisions remain required for a live lifecycle feed, actual approver and executor, publication audience, and any scheduling or operational policy. No deploy, production activation, live publication, access grant or Pipeline write is part of this draft.
