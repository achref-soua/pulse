"""PDF clinical-summary report generator — medical-grade layout with ReportLab."""

from __future__ import annotations

import io
from datetime import date
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

_W, _H = A4

# ── Palette ─────────────────────────────────────────────────────────────────
_INDIGO_DARK = colors.HexColor("#1e1b4b")
_INDIGO = colors.HexColor("#3730a3")
_INDIGO_LIGHT = colors.HexColor("#6366f1")
_INDIGO_PALE = colors.HexColor("#e0e7ff")
_SLATE = colors.HexColor("#475569")
_SLATE_LIGHT = colors.HexColor("#94a3b8")
_SLATE_PALE = colors.HexColor("#f1f5f9")
_ROSE = colors.HexColor("#e11d48")
_ROSE_PALE = colors.HexColor("#fff1f2")
_EMERALD = colors.HexColor("#059669")
_AMBER = colors.HexColor("#d97706")
_WHITE = colors.HexColor("#ffffff")
_BORDER = colors.HexColor("#e2e8f0")

_MARGIN_H = 1.8 * cm
_MARGIN_V = 1.6 * cm
_HEADER_H = 2.2 * cm
_FOOTER_H = 1.2 * cm


# ── Logo drawn with canvas primitives ───────────────────────────────────────

def _draw_ekg(c: Canvas, x: float, y: float, w: float, h: float) -> None:
    """Draw a stylised EKG waveform at (x, y) within w×h box."""
    pts = [
        (0.00, 0.50),
        (0.18, 0.50),
        (0.25, 0.50),
        (0.32, 0.15),
        (0.39, 0.85),
        (0.46, 0.02),
        (0.53, 0.98),
        (0.60, 0.50),
        (0.67, 0.50),
        (1.00, 0.50),
    ]
    path = c.beginPath()
    px, py = x + pts[0][0] * w, y + pts[0][1] * h
    path.moveTo(px, py)
    for rx, ry in pts[1:]:
        path.lineTo(x + rx * w, y + ry * h)
    c.setStrokeColor(_ROSE)
    c.setLineWidth(2.2)
    c.setLineCap(1)
    c.setLineJoin(1)
    c.drawPath(path)


def _draw_header(c: Canvas, doc: Any) -> None:  # noqa: ANN401
    c.saveState()

    # Full-width indigo band
    c.setFillColor(_INDIGO_DARK)
    c.rect(0, _H - _HEADER_H, _W, _HEADER_H, fill=1, stroke=0)

    # Rose accent strip on left
    c.setFillColor(_ROSE)
    c.rect(0, _H - _HEADER_H, 5 * mm, _HEADER_H, fill=1, stroke=0)

    # EKG logo mark (white)
    logo_x = 10 * mm
    logo_y = _H - _HEADER_H + (_HEADER_H - 12) / 2
    c.setStrokeColor(_WHITE)
    c.setFillColor(_WHITE)
    _draw_logo_white(c, logo_x, logo_y, 34, 12)

    # "PULSE" wordmark
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(_WHITE)
    c.drawString(logo_x + 40, _H - _HEADER_H + (_HEADER_H - 18) / 2 + 2, "PULSE")

    # Divider
    c.setStrokeColor(colors.HexColor("#4338ca"))
    c.setLineWidth(0.5)
    c.line(logo_x + 100, _H - _HEADER_H + 6, logo_x + 100, _H - 6)

    # Report title (right of divider)
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#c7d2fe"))
    c.drawString(logo_x + 107, _H - _HEADER_H + (_HEADER_H * 0.62), "CLINICAL SUMMARY REPORT")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.HexColor("#818cf8"))
    today = date.today().strftime("%d %B %Y")
    c.drawString(logo_x + 107, _H - _HEADER_H + (_HEADER_H * 0.3), f"Generated {today}")

    # Page number (right side)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.HexColor("#818cf8"))
    c.drawRightString(_W - 10 * mm, _H - _HEADER_H + (_HEADER_H * 0.45), f"Page {doc.page}")

    c.restoreState()


def _draw_logo_white(c: Canvas, x: float, y: float, w: float, h: float) -> None:
    pts = [
        (0.00, 0.50), (0.18, 0.50), (0.25, 0.50),
        (0.32, 0.15), (0.39, 0.85), (0.46, 0.02),
        (0.53, 0.98), (0.60, 0.50), (0.67, 0.50), (1.00, 0.50),
    ]
    path = c.beginPath()
    px, py = x + pts[0][0] * w, y + pts[0][1] * h
    path.moveTo(px, py)
    for rx, ry in pts[1:]:
        path.lineTo(x + rx * w, y + ry * h)
    c.setStrokeColor(_WHITE)
    c.setLineWidth(1.8)
    c.setLineCap(1)
    c.setLineJoin(1)
    c.drawPath(path)


def _draw_footer(c: Canvas, _doc: Any) -> None:  # noqa: ANN401
    c.saveState()

    # Footer bar
    c.setFillColor(_SLATE_PALE)
    c.rect(0, 0, _W, _FOOTER_H, fill=1, stroke=0)
    c.setStrokeColor(_BORDER)
    c.setLineWidth(0.5)
    c.line(0, _FOOTER_H, _W, _FOOTER_H)

    # Disclaimer
    c.setFont("Helvetica-Oblique", 6.5)
    c.setFillColor(_SLATE)
    disclaimer = (
        "CONFIDENTIAL — Educational demonstration on synthetic patient data. "
        "Not for clinical use. Not medical advice. Do not rely on this report for patient care."
    )
    c.drawCentredString(_W / 2, _FOOTER_H / 2 + 1, disclaimer)

    c.restoreState()


class _MedicalDoc(BaseDocTemplate):
    def __init__(self, buf: io.BytesIO) -> None:
        super().__init__(
            buf,
            pagesize=A4,
            leftMargin=_MARGIN_H,
            rightMargin=_MARGIN_H,
            topMargin=_HEADER_H + _MARGIN_V,
            bottomMargin=_FOOTER_H + _MARGIN_V,
        )
        frame = Frame(
            _MARGIN_H, _FOOTER_H + _MARGIN_V,
            _W - 2 * _MARGIN_H,
            _H - _HEADER_H - _FOOTER_H - 2 * _MARGIN_V,
            id="body",
        )
        template = PageTemplate(
            id="medical",
            frames=[frame],
            onPage=self._on_page,
        )
        self.addPageTemplates([template])

    @staticmethod
    def _on_page(c: Canvas, doc: Any) -> None:  # noqa: ANN401
        _draw_header(c, doc)
        _draw_footer(c, doc)


# ── Typography ───────────────────────────────────────────────────────────────

def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "section_title": ParagraphStyle(
            "SectionTitle",
            parent=base["Normal"],
            fontSize=10,
            fontName="Helvetica-Bold",
            textColor=_INDIGO,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=9,
            leading=14,
            textColor=_SLATE,
        ),
        "body_sm": ParagraphStyle(
            "BodySm",
            parent=base["Normal"],
            fontSize=8,
            leading=12,
            textColor=_SLATE,
        ),
        "disclaimer": ParagraphStyle(
            "Disclaimer",
            parent=base["Normal"],
            fontSize=7.5,
            leading=11,
            textColor=_ROSE,
            backColor=_ROSE_PALE,
            borderPad=5,
            borderColor=_ROSE,
            borderWidth=0.5,
            leftIndent=4,
            rightIndent=4,
        ),
        "source": ParagraphStyle(
            "Source",
            parent=base["Normal"],
            fontSize=8,
            leading=11,
            textColor=_SLATE,
            fontName="Courier",
        ),
        "source_ref": ParagraphStyle(
            "SourceRef",
            parent=base["Normal"],
            fontSize=7.5,
            leading=10,
            textColor=_SLATE_LIGHT,
            fontName="Courier-Oblique",
            leftIndent=8,
        ),
        "label": ParagraphStyle(
            "Label",
            parent=base["Normal"],
            fontSize=8,
            fontName="Helvetica-Bold",
            textColor=_SLATE,
        ),
    }


# ── Section helper ───────────────────────────────────────────────────────────

def _section(title: str, style: ParagraphStyle) -> list:
    return [
        Spacer(1, 0.2 * cm),
        Paragraph(title.upper(), style),
        HRFlowable(width="100%", color=_INDIGO_PALE, thickness=1, spaceAfter=4),
    ]


# ── Risk colour helper ───────────────────────────────────────────────────────

def _risk_color(risk_str: str) -> colors.Color:
    r = risk_str.lower()
    if any(w in r for w in ("high", "major", "severe", "unstable", "critical")):
        return _ROSE
    if any(w in r for w in ("moderate", "intermediate", "elevated")):
        return _AMBER
    return _EMERALD


# ── Public API ───────────────────────────────────────────────────────────────

def build_pdf(patient: dict, summary_text: str, risk_scores: dict, sources: list[dict]) -> bytes:
    """Render a beautifully formatted PDF clinical-summary report and return bytes."""
    buf = io.BytesIO()
    doc = _MedicalDoc(buf)
    s = _build_styles()
    story: list = []

    # ── Clinical disclaimer ─────────────────────────────────────────────────
    story.append(Paragraph(
        "⚠  EDUCATIONAL DEMONSTRATION — SYNTHETIC DATA ONLY — NOT FOR CLINICAL USE",
        s["disclaimer"],
    ))
    story.append(Spacer(1, 0.4 * cm))

    # ── Patient information ──────────────────────────────────────────────────
    story.extend(_section("Patient Information", s["section_title"]))

    phase = patient.get("phase", "—")
    intervention = (patient.get("planned_intervention") or "—").replace("_", " ").upper()
    meta_rows = [
        [Paragraph("Patient ID", s["label"]), patient.get("patient_id", "—")],
        [Paragraph("Full Name", s["label"]), patient.get("name", "—")],
        [Paragraph("Age / Sex", s["label"]),
         f"{patient.get('age', '—')} years / {patient.get('sex', '—')}"],
        [Paragraph("Aneurysm Type", s["label"]), patient.get("aneurysm_type") or "—"],
        [Paragraph("Clinical Phase", s["label"]), phase.capitalize()],
        [Paragraph("Planned Intervention", s["label"]), intervention],
        [Paragraph("Attending Physician", s["label"]), patient.get("attending_physician", "—")],
        [Paragraph("Report Date", s["label"]), date.today().strftime("%d %B %Y")],
    ]
    meta_tbl = Table(meta_rows, colWidths=[4.2 * cm, 12.5 * cm])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), _INDIGO_PALE),
        ("TEXTCOLOR", (0, 0), (0, -1), _INDIGO),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEADING", (0, 0), (-1, -1), 13),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [_WHITE, _SLATE_PALE]),
        ("GRID", (0, 0), (-1, -1), 0.4, _BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROUNDEDCORNERS", [3, 3, 3, 3]),
    ]))
    story.append(meta_tbl)

    # ── AI-generated clinical summary ────────────────────────────────────────
    story.extend(_section("AI-Generated Clinical Summary", s["section_title"]))
    story.append(Paragraph(
        "The following narrative was generated by an AI language model using retrieval-augmented "
        "generation over the clinical knowledge base. It must not be used for clinical decisions.",
        s["body_sm"],
    ))
    story.append(Spacer(1, 0.25 * cm))

    for line in summary_text.split("\n"):
        line = line.strip()
        if line:
            # Render markdown-style bold (**text**) as normal body for PDF
            clean = line.replace("**", "")
            story.append(Paragraph(clean, s["body"]))
            story.append(Spacer(1, 0.12 * cm))

    # ── Risk scores ──────────────────────────────────────────────────────────
    if risk_scores:
        has_rows = False
        rows = [[
            Paragraph("Calculator", s["label"]),
            Paragraph("Score", s["label"]),
            Paragraph("Risk Classification", s["label"]),
        ]]
        for name, val in risk_scores.items():
            if not isinstance(val, dict):
                continue
            score = str(val.get("score", val.get("total_score", "—")))
            risk = str(val.get("risk_class", val.get("risk_category", val.get("response_level", "—"))))
            rows.append([name, score, Paragraph(risk, s["body"])])
            has_rows = True

        if has_rows:
            story.extend(_section("Risk Assessment Summary", s["section_title"]))
            rt = Table(rows, colWidths=[5.5 * cm, 3.2 * cm, 8 * cm])

            risk_styles = [
                ("BACKGROUND", (0, 0), (-1, 0), _INDIGO),
                ("TEXTCOLOR", (0, 0), (-1, 0), _WHITE),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEADING", (0, 0), (-1, -1), 13),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_WHITE, _SLATE_PALE]),
                ("GRID", (0, 0), (-1, -1), 0.4, _BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
            # Colour-code risk cells
            for i, (_, val) in enumerate(risk_scores.items(), start=1):
                if not isinstance(val, dict):
                    continue
                risk = str(val.get("risk_class", val.get("risk_category", val.get("response_level", ""))))
                risk_styles.append(("TEXTCOLOR", (2, i), (2, i), _risk_color(risk)))
                risk_styles.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))

            rt.setStyle(TableStyle(risk_styles))
            story.append(rt)
            story.append(Spacer(1, 0.2 * cm))

    # ── Knowledge base sources ───────────────────────────────────────────────
    if sources:
        story.extend(_section("Referenced Clinical Sources", s["section_title"]))
        story.append(Paragraph(
            "The AI synthesis above drew on the following guidelines and literature:",
            s["body_sm"],
        ))
        story.append(Spacer(1, 0.2 * cm))

        src_rows = [[
            Paragraph("#", s["label"]),
            Paragraph("Type", s["label"]),
            Paragraph("Title", s["label"]),
            Paragraph("Source / DOI", s["label"]),
        ]]
        for i, src in enumerate(sources, 1):
            type_tag = src.get("type", "—").upper()
            src_rows.append([
                str(i),
                type_tag,
                Paragraph(src.get("title", "—"), s["body_sm"]),
                Paragraph(src.get("source", "—"), s["source_ref"]),
            ])

        st = Table(src_rows, colWidths=[0.8 * cm, 2.2 * cm, 8.5 * cm, 5.2 * cm])
        src_styles = [
            ("BACKGROUND", (0, 0), (-1, 0), _INDIGO_PALE),
            ("TEXTCOLOR", (0, 0), (-1, 0), _INDIGO),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEADING", (0, 0), (-1, -1), 11),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_WHITE, _SLATE_PALE]),
            ("GRID", (0, 0), (-1, -1), 0.3, _BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
        # Highlight type badge
        for i, src in enumerate(sources, 1):
            if src.get("type") == "guideline":
                src_styles.append(("TEXTCOLOR", (1, i), (1, i), _INDIGO_LIGHT))
            else:
                src_styles.append(("TEXTCOLOR", (1, i), (1, i), _AMBER))
        st.setStyle(TableStyle(src_styles))
        story.append(st)

    story.append(Spacer(1, 0.4 * cm))

    doc.build(story)
    return buf.getvalue()
