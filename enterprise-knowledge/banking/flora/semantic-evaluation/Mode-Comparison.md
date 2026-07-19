# Mode Comparison

## Comparative results

| Test | Mode A | Mode B | Mode C | Best mode | Key finding |
|---|---:|---:|---:|---|---|
| Claim Extraction | Weak | Pass | Strong | Mode C | Text enables extraction; governed Evidence improves boundary control. |
| Lloyds Specificity | Weak | Strong | Strong | Mode C | Mode B already separates P10 sector context; Mode C makes scope boundaries auditable. |
| Change Detection | Weak | Pass | Strong | Mode C | Mode B uses dates and quantities; Mode C preserves missing baselines and forecast/result separation more consistently. |
| Semantic Equivalence | Weak | Pass | Strong | Mode C | Mode B resolves scopes; Mode C adds lineage-backed equivalence reasoning. |
| Contradiction Understanding | Weak | Pass | Strong | Mode C | Apparent contradictions are tensions or different aspects, not true conflicts. |
| Materiality | Fail | Pass | Strong | Mode C | Mode A over-relies on labels; Mode C ties materiality to content and Unknowns. |
| Evidence Sufficiency | Fail | Pass | Strong | Mode C | Mode C best maps support, contrary evidence, Unknowns and unsupported inferential steps. |
| Explanation Without Paraphrase | Fail | Pass | Strong | Mode C | Mode C explains why Evidence belongs together rather than restating source text. |

## Required analysis answers

- Does Mode B materially outperform Mode A? Yes. Mode B extracts quantities, entities, dates, claim boundaries, semantic differences and unsupported inferential steps that Mode A cannot recover from structure alone.
- Does Mode C materially outperform Mode B? Yes, but in a narrower way. Mode C does not add many new raw facts; it improves evidence discipline, lineage, Unknown preservation, contradiction framing and explanation quality.
- Does governance improve accuracy or merely improve presentation? Governance improves accuracy where errors are over-attribution, unsupported causality, materiality overreach or hidden uncertainty. It also improves presentation, but the important gain is constraint on inference.
- Can Flora explain why Evidence belongs together? In Mode C, yes for bounded packages such as personal current accounts, structural hedge balance and hedge income, and Lloyds Google Cloud usage plus sector CTP context.
- Can Flora distinguish Lloyds-specific content from sector-general content? Yes in Mode B and Mode C. P10 remains sector-general unless related through P09.
- Can Flora separate content understanding from pre-authored interpretation? Yes at the mode-comparison level: Mode B demonstrates substantive understanding without authored Observations, while Mode C demonstrates the additional value and risk of governed interpretation.

## Reviewer comparison and disagreements

Reviewer 1 and Reviewer 2 agreed that Mode A fails semantic understanding, Mode B materially outperforms Mode A and Mode C materially improves governed explainability. The only material nuance was strategic coherence: Reviewer 2 held Mode C at 2 rather than 3 because the corpus is too narrow to prove broad Lloyds strategy or capital allocation. Final adjudication: this is a corpus-boundary condition, not a runtime failure.
