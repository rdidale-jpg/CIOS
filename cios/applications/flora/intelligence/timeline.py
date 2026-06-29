"""Commercial timeline construction for Flora case files."""
from __future__ import annotations
from datetime import date
from pydantic import BaseModel
from cios.applications.flora.intelligence.evidence_engine import CommercialEvidence
from cios.applications.flora.intelligence.insight_engine import CommercialInsight

class TimelineEntry(BaseModel):
    entry_date: date
    entry_type: str
    title: str
    description: str
    reference_id: str


def build_timeline(evidence: list[CommercialEvidence], insights: list[CommercialInsight] | None = None) -> list[TimelineEntry]:
    entries = [TimelineEntry(entry_date=e.publication_date, entry_type="Evidence", title=e.title, description=e.extracted_observation, reference_id=e.evidence_id) for e in evidence]
    if insights and evidence:
        final_date = max(e.publication_date for e in evidence)
        entries.extend(TimelineEntry(entry_date=final_date, entry_type="Insight", title=i.title, description=i.narrative, reference_id=i.insight_id) for i in insights)
    return sorted(entries, key=lambda entry: (entry.entry_date, entry.entry_type, entry.reference_id))
