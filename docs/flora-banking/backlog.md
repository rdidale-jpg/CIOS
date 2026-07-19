# Flora UK Banking Governed Product Backlog

Detailed evidence UX work is deferred, not rejected.

| ID | Outcome | User | Priority | Status | Dependencies | Acceptance signal | Architecture implications |
|---|---|---|---|---|---|---|---|
| FLR-001 Banking portfolio home | Open five-bank portfolio | Sales director | High | Done | Focus objects | Five account cards render | Presentation projection only |
| FLR-002 Bank executive briefing | Prepare account view | Sales director | High | Done | Evidence, Unknowns | Bounded briefing/safe state | Transient |
| FLR-003 Peer comparison | Compare through themes | Sales director | High | Done | Theme taxonomy | No ranking/scoring | Common taxonomy |
| FLR-004 Strategic themes view | Inspect shared themes | Sales director | High | Done | ADR-003 | All themes visible | Governed mappings |
| FLR-005 Why them / why now | Explain attention timing | Sales director | High | Done | Observations | Lineage visible | Not Recommendation |
| FLR-006 Account preparation mode | One-page preparation | Sales director | High | Done | Briefing | Printable briefing route | Non-canonical |
| FLR-007 Evidence-backed discussion questions | Learn before selling | Sales director | High | Done | Unknowns/tensions | Questions expose origin | Presentation transform |
| FLR-008 Cross-bank signal detection | See sector patterns | Sales director | Medium | Done | Comparison | Sector labels visible | Deterministic |
| FLR-009 Commercial implication framing | Translate change | Sales director | Medium | Done | Observations | Commercial significance shown | Bounded interpretation |
| FLR-010 Change significance | Limit to material changes | Sales director | Medium | Done | Briefing | <=5 changes | No scoring |
| FLR-011 Momentum and timing | Recency context | Sales director | Medium | Done | Evidence periods | Why now section | Qualitative only |
| FLR-012 Enterprise-specificity | Prevent overclaiming | Architecture reviewer | High | Done | Scope classifier | Scope labels render | Claim guardrail |
| FLR-013 Contradiction and tension experience | Preserve tensions | Sales director | High | Done | Unknowns | Two tensions render | No collapsed conclusion |
| FLR-014 Trusted-adviser narrative | Improve point of view | Sales director | Medium | In progress | Reviewer feedback | Less generic feedback | Narrative remains bounded |
| FLR-015 Briefing export | Export briefing | Sales director | Low | Deferred | Print CSS/PDF | Download artefact | Non-canonical output |
| FLR-016 Executive evidence summary | Compact trust statement | Sales director | High | Done | Evidence state | Statement visible | Diagnostics behind inspect |
| FLR-017 Progressive evidence disclosure | Inspect on demand | Sales director | High | Done | Evidence route | Expanded evidence route | No default diagnostics |
| FLR-018 Terminology cleanup | Remove increment journey terms | User | Medium | Done | Navigation | Home uses UK Banking | Technical docs may retain |
| FLR-019 Short-page design | Fit two screens | Sales director | Medium | In progress | UI review | Reviewer says concise | Presentation only |
| FLR-020 Saved views | Persist view state | Sales director | Low | Deferred | Storage policy | Saved transient state | Non-canonical audit |
| FLR-021 Executive evidence trust lens | Better evidence UX | Sales director | Medium | Deferred | FLR-016/017 | Reviewer approves evidence lens | Deferred not rejected |
| FLR-022 Corroboration enrichment | More source diversity | Analyst | Medium | Deferred | Source acquisition | Corroboration fields populated | No invented corroboration |
| FLR-023 Date-quality repair | Improve periods | Analyst | Medium | Deferred | Source cleanup | Incomplete dates labelled | Deterministic dates |
| FLR-024 Evidence sufficiency rules | Formal fail-closed | Architecture reviewer | High | In progress | Validation | Safe unavailable tests | Reusable validator |
| FLR-025 Human judgement annotation | Label curated mappings | Analyst | Medium | Done | Fixtures | Human-supplied labels | Audit lineage |
