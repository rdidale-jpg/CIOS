# Research Mission activation report

## Discovery and duplication decision

| Concept | Repository location | Canonical owner | Version | Current behaviour | Gap found | Amendment |
|---|---|---|---|---|---|---|
| Researcher pack/source/build | `knowledge-packs/researcher`; `tools/knowledge-packs/build_researcher_pack.py` | Knowledge Pack owner | 2.8.0 | Deterministic governed distribution | Mission assets incomplete | Extended existing build and assets |
| Profile registry | `knowledge-packs/researcher/profile-versions.json` | IT-001 controlled profiles | 1.0.0 | Pins eight profiles | Compatibility not fully composed | Templates reference, never copy profiles |
| Research instructions | pack configuration and RG-001/RG-002 | Existing research guidance owners | repository-current | Governs researcher operation | Long briefs repeated method | Contracts are sole reusable mission-rule owners |
| Mission templates/manifests/generator | `research-missions`; `research_missions.py` | Researcher Knowledge Pack | 1.1.0 | Existing functional subsystem | Five templates and nine shallow modules | Extended in place to 10 templates and 20 modules |
| Generated brief | `research-missions/generated` | Derived output only | pinned | Deterministic Markdown | Wave 5 absent | Added four reproducible TEL-001 examples |
| Flora gaps/commission | Flora runtime commission services | Flora runtime | repository-current | Supplies operational gap/subject context | No governed manifest adapter | Interface documented; UI/runtime activation deferred |
| Package schemas/state | pack schemas, programme records and release manifest | Existing schema/programme owners | pinned | Govern exchange and current state | Mission schema incomplete | Manifest 1.1 composes references only |

Search found reusable rules repeated in TEL-001 briefs and guidance. Their canonical mission-level wording now exists once in the contract registry; templates contain references only. EI-001, EI-002, EI-012, FP-009, FP-012, EIRP-001 and IT-001 remain upstream authorities. The packaged baseline remains governed; newer merged mission infrastructure was extended rather than reverted.

## TEL-001 rule classification

| Class | Rules/content | Configuration owner |
|---|---|---|
| A — generic reusable | deterministic construction; evidence collection, closure and exhaustion; estimates; value/timing; commercial type; procurement; H1–H3; buyer; awards/residuals; frameworks; overlap; monitoring; falsification; Unknowns; Contradictions; validation; outcomes | Versioned contract modules |
| B — industry configuration | subsectors, geography, material-subject test, regulators, preferred source families and terminology | Industry mission manifest/profile |
| C — TEL-001 only | VodafoneThree, Network Services 4, Project Gigabit, Openreach, BT, VMO2, TalkTalk/PXC, nexfibre/Substantial, Ofcom targets, TEL-001 counts and gaps | TEL-001 example manifests only |

## Flora handoff

Flora remains an operational-input producer: Twin ID, release, gaps, subjects, Unknowns, Contradictions, triggers and pipeline state map to manifest fields. The stable handoff is a schema-valid manifest passed to the pack-owned generator. A larger runtime adapter and UI activation are deferred; no Home, import, truth or promotion behaviour changes here.

## Remaining limitation and next action

The included TEL-001 data is a reproducibility fixture, not new research and not a current factual baseline. Next, expose the schema-valid manifest adapter through the existing Flora commission service in a separately governed runtime increment.
