# Flora v2 — Enterprise Intelligence Product Experience Specification

**Document class:** Product experience specification  
**Status:** Proposed  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-18  
**Owning decision:** [ADR-024](../../decisions/ADR-024-Hybrid-Enterprise-Intelligence-Runtime.md)  
**Runtime architecture:** [FEIR-001](FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md)  
**Reasoning contract:** [EIRP-001](EIRP-001-Enterprise-Intelligence-Reasoning-Pipeline-Specification.md)  
**Authority:** UX and product experience guidance only. This specification does not redesign ADR-024, FEIR-001 or EIRP-001, does not introduce new runtime architecture, and does not change Enterprise Knowledge governance.

## 1. Product thesis

Flora v2 is an Enterprise Intelligence workspace for Strategic Sales Directors. It helps a user ask an important commercial question, understand what is changing, compare enterprises, prepare executive engagement and inspect the governed reasoning behind every answer.

The first impression must be:

> I can ask an important commercial question and Flora will help me understand it.

The experience must not feel like an administration system, document repository, dashboard, knowledge store or workflow console. Governance remains present and fully functional, but it is secondary to question-led intelligence work.

## 2. Design philosophy

Flora v2 combines three qualities:

1. **Conversational entry**: the user starts with a question rather than a data model.
2. **Terminal-grade intelligence**: evidence, movements, comparisons, confidence and change history are inspectable.
3. **Executive strategy workspace**: outputs are commercially useful, calm, readable and proportionate.

The design language is question-first, evidence-backed, calm, executive, explainable, minimal, inspectable, trustworthy, progressive and commercially useful.

Avoid busy dashboards, large card grids, feature-first navigation, repository terminology, technical runtime language and administration-first journeys.

## 3. Primary experience model

Flora v2 has five primary surfaces:

```text
Home
Explore
Focus
Shape
Governance
```

All other capabilities live beneath these surfaces. Home, Explore, Focus and Shape are the primary Enterprise Intelligence experience. Governance contains operational and administrative capabilities.

## 4. Information architecture

| Primary area | Purpose | Primary user question | Key secondary surfaces |
| --- | --- | --- | --- |
| Home | Start or resume an investigation. | What would you like to understand today? | Recent Intelligence Sessions, recent industries, recent enterprises, recent Strategic Sales Briefs. |
| Explore | Understand industries and changes. | What is changing, why now and what evidence supports it? | Industry overview, mechanisms, observations, hypotheses, evidence timeline, latest changes, Unknowns, Contradictions. |
| Focus | Compare enterprises and participants. | Which enterprise is more pressured, ready or commercially relevant? | Enterprise comparison, participant comparison, Digital Twin comparison, executive pressure comparison, Enterprise Canvas. |
| Shape | Prepare executive engagement. | What should I say, ask or avoid with this executive? | Strategic Sales Brief generation, executive role selection, recommended next action, what should not yet be done. |
| Governance | Operate and administer governed knowledge and runtime controls. | Is the system governed, valid and ready? | Import Blueprint, Import History, Knowledge Packages, Validation, Runtime, Settings, Users, Permissions. |

### Navigation map

```text
Home
├── Ask Flora
├── Recent Intelligence Sessions
├── Recent Industries
├── Recent Enterprises
└── Recent Strategic Sales Briefs

Explore
├── Industry selector
├── Industry overview
├── Mechanisms
├── Observations
├── Hypotheses
├── Evidence timeline
├── Latest changes
├── Unknowns
├── Contradictions
└── Suggested next questions

Focus
├── Compare enterprises
├── Compare participant types
├── Compare Digital Twins
├── Compare executive pressures
├── Compare transformation readiness
└── Enterprise Canvas

Shape
├── Select enterprise
├── Select executive role
├── Generate Strategic Sales Brief
├── Brief reader
├── Evidence and lineage inspection
└── Session continuation

Governance
├── Import Blueprint
├── Import History
├── Knowledge Packages
├── Validation
├── Runtime
├── Settings
├── Users
└── Permissions
```

## 5. Home redesign

### Purpose

Home starts with one question and makes the system immediately useful to a Strategic Sales Director.

### Desktop layout

```text
┌────────────────────────────────────────────────────────────────────┐
│ Flora                                  Home Explore Focus Shape Gov │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│        What would you like to understand today?                    │
│        ┌────────────────────────────────────────────────────┐      │
│        │ Ask about an industry, enterprise or executive...  │      │
│        └────────────────────────────────────────────────────┘      │
│        [Ask Flora]   Explore industries   Compare enterprises       │
│                      Shape executive engagement                     │
│                                                                    │
│  Recent Intelligence Sessions                 Recent Briefs         │
│  • What is changing in Banking?               • HSBC COO brief      │
│  • Which banks are most exposed?              • Lloyds CIO brief    │
│                                                                    │
│  Recent Industries        Recent Enterprises                       │
│  Banking                  HSBC, Barclays, Lloyds                    │
└────────────────────────────────────────────────────────────────────┘
```

### Rules

- The question input is the visual centre of the page.
- Governance actions are not shown in the top content area.
- Recent items resume context rather than opening isolated files.
- Empty state examples should be commercial questions, not feature prompts.

## 6. Explore redesign

Explore helps the user understand industries.

### Required sections

- Industry selector.
- Industry overview.
- Mechanisms.
- Observations.
- Hypotheses.
- Evidence timeline.
- Latest changes.
- Unknowns.
- Contradictions.
- Suggested next questions.

### Desktop layout

```text
┌─ Explore Banking ──────────────────────────────────────────────────┐
│ [Industry selector: Banking ▾]                                      │
│                                                                    │
│ What is changing?                                                   │
│ Large narrative summary with confidence and evidence badge.          │
│                                                                    │
│ ┌ Mechanisms ┐ ┌ Observations ┐ ┌ Hypotheses ┐                      │
│ │ pressure   │ │ evidenced    │ │ candidate  │                      │
│ │ loops      │ │ changes      │ │ explanations│                     │
│ └────────────┘ └──────────────┘ └────────────┘                      │
│                                                                    │
│ Evidence timeline                                                   │
│ 2024 ── 2025 ── 2026                                                │
│                                                                    │
│ Unknowns            Contradictions          Suggested next questions │
└────────────────────────────────────────────────────────────────────┘
```

### Interaction principles

- Start with a readable answer, then allow inspection.
- Unknowns and Contradictions are first-class, visible and never hidden behind error states.
- Evidence timeline entries open evidence detail panels with lineage chips.
- Suggested next questions continue the current Intelligence Session.

## 7. Focus redesign

Focus supports visual comparison.

### Supported comparisons

- Enterprises.
- Participant types.
- Digital Twins.
- Executive pressures.
- Transformation readiness.

### Desktop layout

```text
┌─ Focus ─────────────────────────────────────────────────────────────┐
│ Compare [Enterprise ▾]  A [HSBC ▾]  B [Lloyds ▾]  + Add             │
│                                                                    │
│ Pressure / Readiness comparison                                    │
│ ┌──────────────┬──────────────┬──────────────┐                     │
│ │ Dimension    │ HSBC         │ Lloyds       │                     │
│ ├──────────────┼──────────────┼──────────────┤                     │
│ │ Why now      │ ...          │ ...          │                     │
│ │ Mechanisms   │ ...          │ ...          │                     │
│ │ Evidence     │ badges       │ badges       │                     │
│ │ Unknowns     │ visible      │ visible      │                     │
│ └──────────────┴──────────────┴──────────────┘                     │
│ [Open Enterprise Canvas] [Shape a brief] [Inspect reasoning]        │
└────────────────────────────────────────────────────────────────────┘
```

Comparison must not collapse nuance into arbitrary scores. Confidence is displayed as labelled confidence with rationale, evidence count, Unknowns and Contradictions.

## 8. Shape redesign

Shape is Flora's flagship commercial experience. It prepares executive engagement.

### Journey

1. Select enterprise.
2. Select executive role.
3. Ask or confirm the engagement question.
4. Generate Strategic Sales Brief.
5. Read the brief.
6. Inspect evidence, Unknowns, Contradictions and lineage.
7. Continue the Intelligence Session with the next suggested question.

### Required brief fields

- Who.
- Why now.
- Why them.
- Evidence.
- Observations.
- Mechanisms.
- Hypotheses.
- Unknowns.
- Contradictions.
- Confidence.
- Recommended next action.
- What should not yet be done.

### Desktop layout

```text
┌─ Shape ─────────────────────────────────────────────────────────────┐
│ Enterprise [HSBC ▾]  Executive role [COO ▾]                         │
│ Question [What should I ask the COO about operational reinvention?] │
│ [Generate Strategic Sales Brief]                                    │
│                                                                    │
│ ┌ Strategic Sales Brief ─────────────────────────────────────────┐  │
│ │ Question                                                       │  │
│ │ Current interpretation                                         │  │
│ │ Who should care / Why now / Why them                           │  │
│ │ Evidence-backed narrative                                      │  │
│ │ Unknowns and Contradictions                                    │  │
│ │ Confidence and recommended next action                         │  │
│ │ What should not yet be done                                    │  │
│ │ Lineage                                                       │  │
│ └────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

## 9. Strategic Sales Brief reading experience

The brief should feel premium, composed and executive. It is not a generated chat transcript.

### Structure

1. Question.
2. Current interpretation.
3. Who should care.
4. Why now.
5. Why them.
6. Evidence.
7. Observations.
8. Mechanisms.
9. Hypotheses.
10. Unknowns.
11. Contradictions.
12. Confidence.
13. Recommended next action.
14. What should not yet be done.
15. Lineage.

### Presentation rules

- Use a single-column reading layout on desktop with a right-side inspection rail.
- Evidence, Unknowns and Contradictions have persistent anchors.
- Recommendations are proportionate and labelled by eligibility.
- Export is a future enhancement; the v2 specification only reserves space for later export affordances.

## 10. Enterprise Canvas redesign

The Enterprise Canvas is an Enterprise Intelligence view, not a repository view.

### Canvas sections

- Current understanding.
- Transformation pressures.
- Business mechanisms.
- Evidence.
- Observations.
- Hypotheses.
- Executive landscape.
- Commercial opportunities.
- Learning history.
- Lineage.

### Canvas layout

```text
┌─ Enterprise Canvas: HSBC ───────────────────────────────────────────┐
│ Current understanding                                               │
│ Flora currently believes... because...                              │
│                                                                    │
│ Pressures             Mechanisms            Executive landscape      │
│ Evidence              Observations          Hypotheses               │
│ Commercial opps       Learning history      Lineage                  │
│                                                                    │
│ [Why does Flora believe this?] opens pipeline and lineage detail.    │
└────────────────────────────────────────────────────────────────────┘
```

The Canvas must explain why Flora currently believes something. Every belief summary should expose evidence lineage, confidence, Unknowns, Contradictions and learning history.

## 11. Intelligence Sessions

An Intelligence Session represents one investigation, even when it moves across Home, Explore, Focus and Shape.

Example session:

```text
What is changing in Banking?
→ Which banks?
→ Why HSBC?
→ What should I ask the COO?
```

### Session experience

- Session title from the initiating question.
- Timeline of questions asked.
- Pipeline runs.
- Generated briefs.
- Evidence collected.
- Learning captured.
- Open Unknowns.
- Contradictions.
- Next suggested question.

Sessions should reduce fragmentation: users resume an investigation, not a page state.

## 12. Pipeline Inspection experience

Pipeline Inspection exposes reasoning as an explainability tool, not a debugging console.

### Canonical inspection stages

```text
Question
→ Intent
→ Context Plan
→ Retrieved Assets
→ Observations
→ Mechanisms
→ Hypotheses
→ Challenge
→ Commercial Assessment
→ Recommendation Eligibility
→ Strategic Sales Brief
```

Each stage exposes:

- Inputs.
- Outputs.
- Confidence.
- Unknowns.
- Contradictions.
- Lineage.
- Duration.
- Validation status.

### Inspection design

- Use plain language stage labels.
- Show a left-to-right stage progress path on desktop and a vertical path on mobile.
- Each stage has a short executive summary and an expandable detail drawer.
- Validation failures are explanatory and actionable, not technical stack traces.
- Hidden model chain-of-thought is not exposed; inspectable structured reasoning, inputs, outputs, lineage and validation status are exposed.

## 13. Governance redesign

Governance contains all operational features:

- Import Blueprint.
- Import History.
- Knowledge Packages.
- Validation.
- Runtime.
- Settings.
- Users.
- Permissions.

Governance must remain reliable and complete, but it must not dominate Home or top-level user journeys. Settings live in Governance.

## 14. Responsive guidance

### Desktop

Desktop is primary. It supports full comparison tables, Strategic Sales Brief reader with inspection rail, Enterprise Canvas, and horizontal Pipeline Inspection.

### Tablet

Tablet prioritises comparison, Pipeline Inspection and Enterprise Canvas. Use two-column layouts where space permits; move inspection rails into slide-over panels.

### Mobile

Mobile prioritises Question, Brief and Sessions. Comparison becomes stacked, Pipeline Inspection becomes vertical, and governance tables become summary lists with detail drill-in.

## 15. Design system

### Colour palette

| Token | Use | Value |
| --- | --- | --- |
| `color.surface` | App background | `#F7F4EF` |
| `color.panel` | Panels and cards | `#FFFFFF` |
| `color.text.primary` | Primary text | `#1E2428` |
| `color.text.secondary` | Secondary text | `#5D6670` |
| `color.accent` | Primary action and focus | `#2F5D62` |
| `color.evidence` | Evidence badges | `#2563EB` |
| `color.unknown` | Unknown indicators | `#B7791F` |
| `color.contradiction` | Contradiction indicators | `#B42318` |
| `color.confidence.high` | High confidence | `#237A57` |
| `color.confidence.medium` | Medium confidence | `#8A6D1D` |
| `color.confidence.low` | Low confidence | `#8A3A2B` |

### Typography

| Token | Use |
| --- | --- |
| `font.family.sans` | Executive UI text; neutral sans serif. |
| `font.size.hero` | Home question heading; 48px desktop, 36px tablet, 28px mobile. |
| `font.size.title` | Page title; 32px desktop. |
| `font.size.body` | Main reading text; 17-18px desktop. |
| `font.size.meta` | Labels and chips; 13-14px. |

### Spacing

Use an 8px base grid:

- `space.1` = 4px.
- `space.2` = 8px.
- `space.3` = 12px.
- `space.4` = 16px.
- `space.6` = 24px.
- `space.8` = 32px.
- `space.12` = 48px.
- `space.16` = 64px.

### Component inventory

| Component | Purpose |
| --- | --- |
| Question input | Large natural-language question entry with Ask Flora action. |
| Primary navigation | Five-item navigation: Home, Explore, Focus, Shape, Governance. |
| Intelligence Session timeline | Shows investigation progression, questions, briefs, evidence and next question. |
| Evidence badge | Displays evidence count, type and lineage availability. |
| Confidence indicator | Labelled High / Medium / Low with rationale and non-colour icon. |
| Unknown indicator | Amber icon plus text; never colour-only. |
| Contradiction indicator | Red icon plus text; never colour-only. |
| Lineage chip | Compact source, object or stage reference. |
| Status chip | Validation, candidate, approved, stale or not executed state. |
| Pipeline progress | Inspectable stage path with validation status. |
| Brief reader | Premium single-column reading surface with inspection rail. |
| Comparison matrix | Visual cross-enterprise comparison without arbitrary numeric scoring. |
| Canvas section | Enterprise Canvas module with evidence and belief rationale. |
| Empty state | Suggests example commercial questions and explains what evidence is needed. |
| Loading state | Shows pipeline stage progress in plain language. |

## 16. Interaction principles

- Ask before showing structure.
- Summarise first, inspect second.
- Preserve evidence lineage at every point of confidence.
- Show Unknowns and Contradictions beside the claim they affect.
- Distinguish observations, mechanisms and hypotheses.
- Avoid arbitrary scores; use labelled confidence with rationale.
- Keep governance available but subordinate.
- Continue investigations through Intelligence Sessions.
- Do not imply named executive ownership where only generic role evidence exists.
- Do not present a recommendation stronger than the evidence and validation permit.

## 17. Accessibility guidance

Flora v2 must comply with WCAG AA:

- Full keyboard navigation for primary navigation, question input, filters, drawers, timelines and pipeline stages.
- Visible focus states using both outline and contrast.
- Screen reader labels for evidence badges, lineage chips, confidence indicators, Unknowns and Contradictions.
- Colour-independent status communication through icon, text and shape.
- Minimum contrast ratio of 4.5:1 for normal text and 3:1 for large text and graphical status indicators.
- Skip links to main question, brief content and inspection rail.
- Reduced-motion alternatives for timeline and pipeline progress animations.

## 18. Complete user journeys

### First-time Strategic Sales Director

1. Opens Flora on Home.
2. Sees the question: “What would you like to understand today?”
3. Enters “What is changing in Banking?”
4. Flora starts an Intelligence Session.
5. Home transitions to a summarised answer with evidence and Unknown markers.
6. User chooses a suggested next question: “Which banks are most affected?”
7. Flora moves to Focus with the same session context.
8. User selects HSBC and COO in Shape.
9. Flora generates a Strategic Sales Brief.
10. User inspects why the recommendation is proportionate before preparing engagement.

### Industry exploration

1. Open Explore.
2. Select Banking.
3. Read what is changing.
4. Inspect mechanisms and observations.
5. Open Evidence timeline.
6. Review Unknowns and Contradictions.
7. Continue with a suggested next question.

### Enterprise comparison

1. Open Focus.
2. Select compare enterprises.
3. Choose HSBC and Lloyds.
4. Compare pressures, mechanisms, readiness, Unknowns and evidence.
5. Open HSBC Enterprise Canvas.
6. Inspect why Flora believes HSBC is commercially relevant.
7. Move to Shape.

### Executive engagement preparation

1. Open Shape.
2. Select enterprise and executive role.
3. Confirm the question.
4. Generate Strategic Sales Brief.
5. Read current interpretation, why now, why them and recommended next action.
6. Review what should not yet be done.
7. Inspect lineage before using the brief.

### Pipeline inspection

1. From a brief, select “Inspect reasoning.”
2. Review stage path from Question to Strategic Sales Brief.
3. Open Retrieved Assets and Observations.
4. Check Confidence, Unknowns, Contradictions and validation status.
5. Return to brief with a clearer trust basis.

### Knowledge governance

1. Open Governance.
2. Review Knowledge Packages.
3. Check Validation status.
4. Inspect Runtime status and Settings.
5. Manage Users and Permissions if authorised.

### Blueprint import

1. Open Governance.
2. Select Import Blueprint.
3. Upload or select blueprint package.
4. Review import pre-checks.
5. Run validation.
6. View Import History and package status.
7. Return to Explore or Focus after governed availability is confirmed.

## 19. Validation against architecture and policy

| Validation criterion | Flora v2 UX position |
| --- | --- |
| Aligns with ADR-024 | Preserves hybrid governed runtime and does not alter the accepted decision. |
| Aligns with FEIR-001 | Uses FEIR-001 as owning runtime architecture and keeps UI views subordinate to runtime boundaries. |
| Aligns with EIRP-001 | Represents pipeline stages as inspectable experience surfaces without changing stage contracts. |
| Question-first interaction preserved | Home, sessions and all journeys start from natural-language questions. |
| Enterprise Intelligence primary | Home, Explore, Focus and Shape dominate the IA. |
| Governance secondary | Operational actions move under Governance and are absent from Home hero. |
| Evidence lineage visible | Evidence badges, lineage chips, brief lineage and Pipeline Inspection expose lineage. |
| Unknowns visible | Unknown indicators appear in Explore, Focus, Shape, Brief, Canvas, Sessions and Pipeline Inspection. |
| Contradictions visible | Contradiction indicators appear beside affected claims and in inspection views. |
| Strategic Sales Brief flagship | Shape and Brief reader are designed as the premium outcome. |
| No architecture decisions changed | This document is explicitly UX-only and records no runtime architecture decision. |

## 20. Future enhancements

- Clickable prototype in Figma or code once a frontend stack is commissioned.
- Exportable Strategic Sales Briefs with governance-aware sharing controls.
- Saved executive engagement plans.
- Watchlists for evidence changes that affect active sessions.
- Personalised suggested questions by role and territory.
- Human approval workflow visualisation when recommendation governance is defined.
- Accessibility user testing with Strategic Sales and governance personas.

## 21. Prototype status

No clickable prototype was produced in this commission. The wireframes and layouts above are implementation-ready experience specifications, but they intentionally avoid frontend technology decisions.
