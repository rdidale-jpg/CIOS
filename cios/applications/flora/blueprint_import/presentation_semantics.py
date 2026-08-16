"""Human-readable translations of canonical imported factual statements.

The imported keys remain untouched. This is the presentation boundary that
stops schema vocabulary becoming executive copy.
"""

_EXECUTIVE_LABELS = {
    "ai": "AI capability",
    "ai pressure": "AI-enabled change",
    "oss bss": "Operations and business support systems",
}


def human_readable_fact(value: str) -> str:
    """Translate schema-labelled prose while preserving its uncertainty."""
    value = value.strip()
    label, separator, detail = value.partition(":")
    executive_label = _EXECUTIVE_LABELS.get(label.casefold()) if separator else None
    source = detail.strip() if executive_label else value
    if source.casefold() == "evidenced or hypothesised by function; budget unknown unless stated":
        return ("AI-enabled operational change is evidenced in identified functions, with other functional activity "
                "remaining hypothesis; the associated investment level is not established.")
    return f"{executive_label}: {detail.strip()}" if executive_label else value


def executive_fact_parts(value: str) -> tuple[str, str]:
    """Return an executive label and detail without altering the governed fact."""
    rendered = human_readable_fact(value)
    if value.partition(":")[0].casefold() == "ai pressure":
        return "AI-enabled change", rendered
    label, separator, detail = rendered.partition(":")
    return (label.strip(), detail.strip()) if separator else ("Governed change", rendered)
