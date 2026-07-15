# ADR-0011: Clinical Cobalt design tokens with light/dark theming

**Status:** Accepted
**Date:** 2026-07-12

## Context

The original UI was the stock shadcn slate/indigo theme, hardcoded to dark (`<html className="dark">`). There was no light mode, no theme toggle, and no real token system: pages hand-rolled inline Tailwind with literal palette classes (`indigo-700`, `text-red-400`, hardcoded chart hex) that could not respond to a theme change. Two competing, unused brand definitions existed. `@pulse/ui` and every installed Radix primitive were unused.

## Decision

Adopt a **Clinical Cobalt** token system as the single source of colour truth, correct in both light and dark:

- `globals.css` defines HSL variables for a light `:root` and a dark `.dark` set — background/foreground/card/primary/secondary/muted/accent/destructive/border/ring, plus **status** tokens (success/warning/info/critical) and **chart** tokens (`--chart-1..5`).
- `tailwind.config.ts` maps `primary`/`accent`/etc. to the CSS variables; the stale literals are deleted.
- Cobalt (`#2563EB`) is the primary; warm-slate neutrals; **pulse-red (`#E11D48`) is reserved as an alert signal only**.
- `next-themes` drives light/system/dark; the hardcoded `dark` class is removed and the toggle is wired into the shell + Settings.
- `@pulse/ui` is fleshed out with token-based Radix wrappers (Button/Badge/Input + Tabs/Dialog/Select/DropdownMenu/Tooltip/…), and the nine app pages are tokenized. Recharts read a CSS-var-driven `useChartColors()` so charts track the theme.

## Rationale

- **One choke-point.** Colour changes happen in one place; a page cannot drift off-palette or break in light mode.
- **Clinical legibility.** A calm cobalt/slate system with red reserved strictly for alerts matches how clinical software should read — the alert colour means something.
- **Accessibility.** Real tokens make WCAG-AA contrast checkable in both themes; charts stay readable in both.

## Consequences

- `tailwindcss-animate` is the one added dependency (motion keyframes).
- Every new surface must consume tokens, never literal palette classes — enforced by review.
- Charts must use `useChartColors()` rather than hardcoded hex.
