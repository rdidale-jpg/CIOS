# Flora initial discovery sprint

Baseline is the approved #716 merge `ff9871310e8b38641550c95c3b267bd74dd020a5`. This draft adds manually commissioned independent discovery to the existing factory command. The operator selects enterprise perimeters. The software follows first-party index links and reads individual dated disclosures within each perimeter. The commission supplies neither the article URLs nor the factual conclusions.

## Reproduce

```bash
printf '%s\n' '["lloyds-banking-group-plc","bt-group-plc","arm-holdings-plc","easyjet-plc"]' > /tmp/flora-commission.json
python -m tools.research.initial_factory /tmp/flora-commission.json --discover /tmp/flora-first
python -m tools.research.initial_factory /tmp/flora-commission.json --discover \
  --previous-discovery /tmp/flora-first/discovery.json /tmp/flora-repeat
```

Each subject can read one preconfigured official newsroom and at most eight candidate article links. The existing disclosure transport enforces HTTPS, a timeout, media and size checks, and no redirects. Links to other origins and report paths outside this wave are excluded. The scan retains metadata and a raw-document digest. It never archives article bodies, follows article links recursively, or falls back to recorded data. Use `--withdrawn-discovery` with exact excluded Source URLs supplied for the commission. Exclusions block reads. This local input does not replace a live Source lifecycle check.

The report separates first-party headline candidates, topic labels, questions for the researcher and technical status. Publication dates must agree across available publish-date fields. Exact dated headlines deduplicate within an enterprise. Repeat runs distinguish changed document bytes from revised headline/date metadata. A change in bytes can come from cookie banners, timestamps or unrelated markup. Revised headline/date metadata is flagged for review. Determining whether different wording describes the same event, or whether competing sources disagree about the event, still requires evidence review.

## Four-enterprise run

Live run on 23 November 2026. The [run manifest](proof.json) lists discovered article references, publication dates, content hashes, topic labels and the repeat comparison. It omits headline text. The interpretation column gives review questions for a seller or researcher. These are original hypotheses and questions about reported events.

| Enterprise | Article links checked | Dated leads | What changed and what to validate |
| --- | ---: | ---: | --- |
| Lloyds Banking Group · Banking | 6 | 1 | Lloyds published lessons from scaling AI responsibly. It is worth checking where governance and assurance tooling already supports delivery and where a team still has a documented gap. A publication alone establishes neither investment budget nor a procurement requirement. [Publisher](https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds-banking-group/responsible-ai-guide.html) |
| BT Group · Telecommunications | 3 | 2 | BT described upgrades to Scottish public-sector connectivity. Validate which organisations and services are already in scope before exploring an adjacent migration or managed-service requirement. The issuer announcement does not establish an open contract. [Publisher](https://newsroom.bt.com/bt-transforms-scotlands-public-sector-connectivity--upgrading-the-nations-digital-infrastructure/) |
| Arm · Technology | 8 | 6 | Arm announced general availability of Microsoft Azure Cobalt 200 virtual machines and described planned Oracle Cloud infrastructure availability separately. Different release stages matter to a seller assessing workload portability. Ask which workloads and regions are supported, and verify adoption separately. Two Arm items about Microsoft are related editorial material from the same publisher. [Microsoft announcement via Arm](https://newsroom.arm.com/news/arm-microsoft-azure-cobalt-200) · [Oracle announcement via Arm](https://newsroom.arm.com/news/arm-agi-cpu-oracle-cloud-infrastructure) |
| easyJet · Aviation | 3 | 2 | easyJet announced planned onboard Starlink connectivity from 2027 and additional summer 2027 routes. For connectivity, verify the rollout schedule, affected aircraft and service responsibilities before assessing adjacent integration work. A named provider is not an opportunity to displace it. [Publisher](https://www.easyjet.com/en/news/airline/story/easyjet-to-offer-connectivity-onboard-for-the-first-time-with-starlink-the-fastest-wi-fi-in-the-sky-with-rapid-roll-out-coming-from-2027) |

Five Lloyds links lacked sufficient supported date or headline metadata and yielded no lead. Two scans found 11 stable candidate headlines. No programme, supplier, buyer need, relationship or opportunity was added to an Enterprise Model or Pipeline. The run reads issuer statements. It establishes what was published and when, with independent factual corroboration still to be done.

## Handoff and acceptance boundary

1. **Discovery** reads the bounded first-party perimeter and stages a local review report. Selecting this perimeter supplies no permission to publish its output.
2. **Verification** checks the article, counterparty, dates, scope and permitted reuse using the existing Source import and review process. The company mentioned in a release can differ from the commissioned Enterprise. Keep material conflicts visible.
3. **Publication** uses the existing accepted Source decision, scoped Evidence review and Blueprint plan/approval path. Existing `candidate.promote`, workspace membership and Canvas ACL continue to govern accepted material. This sprint creates no promotable record or new public read path.
4. **Production execution** remains off. No scheduler or recurring research was added. Standing authority remains an owner decision.

Lloyds §2 remains held where applicable and §5 direct PDF links remain deferred. The existing easyJet financial admission and BT issuer-use boundaries remain active. The proof is candidate-only and has no new seller view. Existing [#716 desktop and tablet previews](../README.md#original-disclosures-and-existing-route-proof) remain the baseline. Native before/after captures of the new candidates are still outstanding.

## Commercial and visual critique

The strongest leads describe a concrete product availability milestone, a named rollout or a service upgrade. A seller can formulate a validation question from those leads. Publisher-led coverage overweights announcements, rarely establishes buyer intent and can return several articles about one event. The current output is useful for research triage. It has no accepted scoring or automatic opportunity action.

The incumbent Flora canvases should carry only the few changes that alter an executive reading of the account. A single short change statement with a date and a distinction between announced, available and planned would give more value than a full research card. Evidence needs a secondary inspection path. Since this change leaves Flora rendering unchanged, the visual assessment describes the existing baseline and a proposed next step.

Factory v1.0 remains incomplete. The next sprint should take one dated lead per enterprise through independent evidence review and the existing isolated Blueprint lifecycle, then integrate eligible changes into native Landscape / Inside / Forces components and test them on desktop and both iPad orientations. It needs a verified scope and named approver for the isolated publication proof. General source selection, body-level fact extraction, material conflict detection, broader commercial coverage and standing execution authority remain open.
