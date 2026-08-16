"""Human-readable translations of canonical imported factual statements."""


def human_readable_fact(value: str) -> str:
    """Translate schema-labelled prose while preserving its uncertainty."""
    source = value.split(":", 1)[1].strip() if value.casefold().startswith("ai pressure:") else value.strip()
    if source.casefold() == "evidenced or hypothesised by function; budget unknown unless stated":
        return ("AI-enabled operational change is evidenced in identified functions, with other functional activity "
                "remaining hypothesis; the associated investment level is not established.")
    return value
