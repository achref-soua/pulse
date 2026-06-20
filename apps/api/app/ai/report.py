"""PDF clinical-summary report generator using ReportLab."""

from __future__ import annotations

import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

_W, _H = A4
_INDIGO = colors.HexColor("#3730a3")
_SLATE = colors.HexColor("#475569")
_ROSE = colors.HexColor("#e11d48")
_LIGHT = colors.HexColor("#f1f5f9")


def _styles():
    base = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=base["Heading1"], textColor=_INDIGO, fontSize=16, spaceAfter=4)
    h2 = ParagraphStyle("H2", parent=base["Heading2"], textColor=_SLATE, fontSize=11, spaceAfter=2)
    body = ParagraphStyle("Body", parent=base["Normal"], fontSize=9, leading=13)
    warn = ParagraphStyle("Warn", parent=base["Normal"], fontSize=8, textColor=_ROSE, leading=11)
    mono = ParagraphStyle("Mono", parent=base["Normal"], fontSize=8, fontName="Courier", leading=11)
    return h1, h2, body, warn, mono


def build_pdf(patient: dict, summary_text: str, risk_scores: dict, sources: list[dict]) -> bytes:
    """Render a PDF clinical-summary report and return the raw bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    h1, h2, body, warn, mono = _styles()
    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph("Pulse — Clinical Summary Report", h1))
    story.append(HRFlowable(width="100%", color=_INDIGO, thickness=1))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "⚠️  Educational demo on synthetic data — not for clinical use; not medical advice.",
        warn,
    ))
    story.append(Spacer(1, 0.4 * cm))

    # ── Patient header ───────────────────────────────────────────────────────
    story.append(Paragraph("Patient Information", h2))
    meta = [
        ["Patient ID", patient.get("patient_id", "—")],
        ["Name", patient.get("name", "—")],
        ["Age / Sex", f"{patient.get('age', '—')} / {patient.get('sex', '—')}"],
        ["Aneurysm Type", patient.get("aneurysm_type") or "—"],
        ["Phase", patient.get("phase", "—").capitalize()],
        ["Planned Intervention", (patient.get("planned_intervention") or "—").replace("_", " ").upper()],
        ["Report Date", date.today().isoformat()],
    ]
    tbl = Table(meta, colWidths=[4.5 * cm, 12 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), _LIGHT),
        ("TEXTCOLOR", (0, 0), (0, -1), _SLATE),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, _LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.5 * cm))

    # ── AI summary ───────────────────────────────────────────────────────────
    story.append(Paragraph("AI-Generated Clinical Summary", h2))
    for line in summary_text.split("\n"):
        line = line.strip()
        if line:
            story.append(Paragraph(line, body))
            story.append(Spacer(1, 0.15 * cm))
    story.append(Spacer(1, 0.3 * cm))

    # ── Risk scores ──────────────────────────────────────────────────────────
    if risk_scores:
        story.append(Paragraph("Risk Scores", h2))
        rows = [["Calculator", "Score / Result", "Risk Class"]]
        for name, val in risk_scores.items():
            if isinstance(val, dict):
                rows.append([
                    name,
                    str(val.get("score", val.get("total_score", "—"))),
                    str(val.get("risk_class", val.get("risk_category", val.get("response_level", "—")))),
                ])
        if len(rows) > 1:
            rt = Table(rows, colWidths=[5 * cm, 5 * cm, 6.5 * cm])
            rt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), _INDIGO),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(rt)
            story.append(Spacer(1, 0.3 * cm))

    # ── Sources ──────────────────────────────────────────────────────────────
    if sources:
        story.append(Paragraph("Knowledge Base Sources Referenced", h2))
        for i, s in enumerate(sources, 1):
            story.append(Paragraph(f"[{i}] {s['type'].upper()} — {s['title']}", mono))
            story.append(Paragraph(f"    {s['source']}", warn))
            story.append(Spacer(1, 0.1 * cm))

    doc.build(story)
    return buf.getvalue()
