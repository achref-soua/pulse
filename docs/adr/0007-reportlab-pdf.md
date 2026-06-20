# ADR-0007: ReportLab for PDF report generation

**Status:** Accepted  
**Date:** 2026-06-20

## Context

Each patient's AI Summary tab offers a downloadable clinical summary PDF containing the AI narrative, patient metadata, risk scores, and referenced sources. Options for server-side PDF generation in Python:

- **WeasyPrint** — HTML/CSS → PDF; excellent for web-to-print but adds a heavy libpango/libcairo dependency (difficult in slim containers)
- **Puppeteer / Playwright headless Chrome** — HTML → PDF via Chrome; adds ~300 MB to the container image
- **fpdf2** — lightweight but limited layout control; no frame/template system
- **ReportLab** (`reportlab`) — mature, pure-Python, ships a full platypus layout engine with `BaseDocTemplate`, `Frame`, `PageTemplate`, `Canvas` callbacks

## Decision

Use `reportlab` with `BaseDocTemplate` and per-page canvas callbacks for header/footer.

## Rationale

- Pure Python with no native library dependencies — works in the existing `python:3.12-slim` base image
- `BaseDocTemplate` + `PageTemplate` + canvas `onPage` callbacks give full control over the header band (indigo bar with Pulse logo drawn via `canvas` primitives), page numbers, and confidentiality footer — none of which are easily achievable with fpdf2
- The logo is drawn as a polyline via `canvas.beginPath()`, eliminating any SVG/image dependency at PDF-generation time
- Risk score cells can be colour-coded programmatically via `TableStyle` — not possible in an HTML-to-PDF workflow without CSS hacks

## Consequences

- The PDF layout is defined in Python, not in a template file — design changes require code changes
- ReportLab's free open-source version (`reportlab`) does not include CMYK colour or some advanced typography features; those are not needed here
- PDF bytes are streamed back via a FastAPI `Response(content=..., media_type="application/pdf")` and downloaded client-side using `fetch()` + `URL.createObjectURL()` — never via a URL query parameter (see ADR-0008)
