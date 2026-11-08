# Representative local rendered views

Chromium / Playwright, 1440 × 1050 desktop viewport. Existing
`FloraWebHandler` routes served only on loopback over isolated retained-package
storage. Development test identity/approval are explicit fixture data. No production
application, authentication or intelligence was modified.

[Browser-Evidence.json](Browser-Evidence.json) records the tested paths, navigation
timings, HTTP outcomes, horizontal overflow and page errors. Screenshots are
viewport captures, sometimes scrolled to the relevant section. The completion
capture renders the actual saved approval handler POST response with `set_content`;
it is not represented as a GET response. Its Industry workspace link was then
followed on the local server.

| View | BNK W1 | TEL W6 |
| --- | --- | --- |
| Industry overview | [BNK](BNK-W1-industry-overview.png) | [TEL](TEL-W6-industry-overview.png) |
| Enterprise dossier | [Barclays](BNK-W1-enterprise-dossier.png) | [VodafoneThree](TEL-W6-enterprise-dossier.png) |
| Financial context | [Narrative, reporting references, explicit limits](BNK-W1-financial-context.png) | Covered by dossier handler test |
| Candidate programmes | [Directed relationship and source lineage](BNK-W1-programmes-opportunities.png) | Covered by retained handler test |
| Opportunity hypothesis | [Candidate, customer, Evidence, missing timing](BNK-W1-opportunity-hypotheses.png) | Covered by retained handler test |
| Evidence / provenance | [Barclays key report](BNK-W1-evidence-provenance.png) | Covered by retained handler test |
| Promotion completion | [Partial subset, counts, no full acceptance](BNK-W1-promotion-completion.png) | [TEL](TEL-W6-promotion-completion.png) |

Verified navigation: overview -> enterprise directory -> named dossier; saved
completion -> existing Industry workspace. All requested local GETs returned 200;
no page JavaScript errors or horizontal overflow occurred in these captures.
The programme/opportunity and financial/report screenshots were visually inspected:
source narratives, candidate labels, directional edge IDs, unavailable economics
and uncertain timing remain readable. No unrelated MOD strategy was present.
The broken Opportunities section anchor found during browser capture was corrected
and added to retained-package assertions.

This is desktop evidence, not a mobile/accessibility certification or deployed
acceptance. Legacy Telecoms/Media/Sport domain filters still appear on BNK and are
explicitly listed as a remaining limitation. The screenshot text is supplied
research in isolated fixtures; it is not newly accepted canonical truth.
