# ADR-0008: JWT via `Authorization: Bearer` header only — never in URLs

**Status:** Accepted  
**Date:** 2026-06-20

## Context

The PDF report endpoint (`GET /ai/report/{id}`) returns a binary response. An early implementation used an `<a href="...?token=...">` link so the browser could initiate the download directly. This embeds the JWT in the URL query string.

## Decision

JWTs must only be transmitted via the `Authorization: Bearer <token>` request header. No endpoint in Pulse accepts or reads a token from a URL query parameter.

The PDF download is implemented as:
```ts
const res = await fetch(`${API_URL}/ai/report/${patientId}`, {
  headers: { Authorization: `Bearer ${token}` },
});
const blob = await res.blob();
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = `pulse-report-${patientId}.pdf`;
a.click();
URL.revokeObjectURL(url);
```

## Rationale

Tokens in URLs are:
- Logged verbatim by web servers, reverse proxies, and CDNs
- Stored in browser history and bookmarks
- Leaked via the `Referer` header to third-party origins
- Visible in server access logs accessible to anyone with infrastructure access

OWASP ASVS V3.1 and RFC 6750 §5.3 explicitly prohibit bearer tokens in query strings. Even in a demo, establishing this pattern matters for portfolio credibility — the wrong pattern copied into a real app becomes a real vulnerability.

## Consequences

- The PDF download requires JavaScript; it cannot be a plain `<a href>` link
- The download button shows a loading state (`Generating…`) while the fetch is in flight
- `URL.revokeObjectURL` is called immediately after the programmatic click to avoid memory leaks
