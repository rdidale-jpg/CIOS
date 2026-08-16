"""Human-readable translations of canonical imported factual statements."""


def human_readable_fact(value: str) -> str:
    """Translate schema-labelled prose while preserving its uncertainty."""
    if value.casefold().startswith("ai pressure:"):
        source = value.split(":", 1)[1].strip()
        if source.casefold() == "evidenced or hypothesised by function; budget unknown unless stated":
            return "AI-enabled change is evidenced or hypothesised by function; investment budget remains unknown unless stated."
    return value
