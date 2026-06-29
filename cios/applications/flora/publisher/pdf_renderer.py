"""ReportLab PDF renderer for Flora executive publications."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BLUE = colors.HexColor("#0B4F8A")
NAVY = colors.HexColor("#102033")
MUTED = colors.HexColor("#64748B")
LINE = colors.HexColor("#DBE4EF")


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("FloraTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=42, leading=48, textColor=BLUE, spaceAfter=8),
        "subtitle": ParagraphStyle("Subtitle", parent=base["Title"], fontName="Helvetica", fontSize=28, leading=34, textColor=NAVY, spaceAfter=24),
        "h1": ParagraphStyle("Heading", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=25, textColor=BLUE, borderColor=LINE, borderWidth=0, borderPadding=0, spaceAfter=16),
        "h2": ParagraphStyle("SubHeading", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=BLUE, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.5, leading=13, textColor=NAVY, alignment=TA_LEFT),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontName="Helvetica", fontSize=8, leading=10, textColor=MUTED),
        "bullet": ParagraphStyle("Bullet", parent=base["BodyText"], fontName="Helvetica", fontSize=10.5, leading=15, textColor=NAVY, leftIndent=12, firstLineIndent=-8, spaceAfter=7),
    }


def _p(text: Any, style: ParagraphStyle) -> Paragraph:
    safe = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(safe, style)


def _footer(canvas, doc, ctx: dict[str, Any]) -> None:  # noqa: ANN001
    canvas.saveState()
    w, _h = A4
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, w - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, f"Flora Pilot · Version {ctx['version']}")
    canvas.drawCentredString(w / 2, 9 * mm, f"Generated {ctx['generated_timestamp']}")
    canvas.drawRightString(w - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _section_title(story: list[Any], title: str, s: dict[str, ParagraphStyle]) -> None:
    story.append(_p(title, s["h1"]))
    story.append(Spacer(1, 3 * mm))


def _table(data: list[list[Any]], widths: list[float] | None = None) -> Table:
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF2FB")),
        ("TEXTCOLOR", (0, 0), (-1, 0), BLUE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("LEADING", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FBFDFF")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def render_pdf(ctx: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    s = _styles()
    story: list[Any] = []
    story += [_p("Confidential (Pilot)", s["small"]), Spacer(1, 35 * mm), _p("FLORA", s["title"]), _p("Morning Edition", s["subtitle"]), Spacer(1, 20 * mm)]
    story.append(_table([["Date", ctx["publication_date_label"]], ["Reading time", f"{ctx['reading_time']} minutes"], ["Version", ctx["version"]], ["Edition", "Executive intelligence briefing"]], [45 * mm, 95 * mm]))
    story.append(PageBreak())
    _section_title(story, "Executive Summary", s)
    for bullet in ctx["executive_summary"]:
        story.append(_p(f"• {bullet}", s["bullet"]))
    story.append(PageBreak())
    _section_title(story, "Today's Priority Opportunity", s)
    for key, value in ctx["priority_opportunity"].items():
        story += [_p(key, s["h2"]), _p(value, s["body"])]
    story.append(PageBreak())
    _section_title(story, "Top Five Organisations", s)
    story.append(_table([["Organisation", "Sector", "Condition Strength", "AI Reinvention Opportunity", "Movement", "Confidence"]] + [[r["organisation"], r["sector"], r["condition_strength"], r["ai_opportunity"], r["movement"], r["confidence"]] for r in ctx["top_organisations"]], [30*mm, 27*mm, 29*mm, 32*mm, 22*mm, 23*mm]))
    story.append(PageBreak())
    _section_title(story, "Emerging Commercial Conditions", s)
    for c in ctx["conditions"]:
        story += [_p(c["condition"], s["h2"]), _p(f"Strength: {c['strength']} · Trend: {c['trend']}", s["body"]), _p(f"Affected Organisations: {', '.join(c['affected_organisations'])}", s["body"]), _p(f"Primary Drivers: {c['primary_drivers']}", s["body"]), Spacer(1, 2*mm)]
    story.append(PageBreak())
    _section_title(story, "Executive & Market Movements", s)
    for section in ctx["movements"]:
        story.append(_p(section["title"], s["h2"]))
        for item in section["items"]:
            story.append(_p(f"• {item}", s["body"]))
    story.append(PageBreak())
    _section_title(story, "Competitive Intelligence", s)
    for company, observation in ctx["competitive_intelligence"].items():
        story += [_p(company, s["h2"]), _p(observation, s["body"])]
    story.append(PageBreak())
    _section_title(story, "Recommended Actions", s)
    for a in ctx["recommended_actions"]:
        story += [_p(f"Priority {a['priority']} · {a['organisation']}", s["h2"]), _p(f"Reason: {a['reason']}", s["body"]), _p(f"Expected Commercial Value: {a['expected_value']}", s["body"]), _p(f"Confidence: {a['confidence']}", s["body"]), _p(f"Evidence references: {', '.join(a['evidence_references'])}", s["body"]), Spacer(1, 2*mm)]
    story.append(PageBreak())
    _section_title(story, "Teach Flora", s)
    for key, value in ctx["teach_flora"].items():
        story += [_p(key, s["h2"]), _p(value, s["body"])]
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=20*mm, bottomMargin=20*mm, title="Flora Morning Edition")
    doc.build(story, onFirstPage=lambda c, d: _footer(c, d, ctx), onLaterPages=lambda c, d: _footer(c, d, ctx))
    return output_path
