"use client";

import { Fragment } from "react";

// Minimal markdown for the copilot's output: headings, bullet lists, bold, and
// inline code. Deliberately not a full parser — the model emits a narrow subset,
// and a dependency-free renderer keeps the bundle lean.
// ponytail: covers the model's actual output; swap for react-markdown only if it emits richer md.

function inline(text: string, keyBase: string) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return parts.map((p, i) => {
    if (p.startsWith("**") && p.endsWith("**")) {
      return (
        <strong key={`${keyBase}-${i}`} className="font-semibold text-foreground">
          {p.slice(2, -2)}
        </strong>
      );
    }
    if (p.startsWith("`") && p.endsWith("`")) {
      return (
        <code key={`${keyBase}-${i}`} className="rounded bg-muted px-1 py-0.5 font-mono text-[0.85em]">
          {p.slice(1, -1)}
        </code>
      );
    }
    return <Fragment key={`${keyBase}-${i}`}>{p}</Fragment>;
  });
}

export function Markdown({ content }: { content: string }) {
  const lines = content.split("\n");
  const blocks: React.ReactNode[] = [];
  let list: string[] = [];

  const flushList = () => {
    if (!list.length) return;
    const items = list;
    blocks.push(
      <ul key={`ul-${blocks.length}`} className="my-1.5 ml-4 list-disc space-y-1 marker:text-primary">
        {items.map((li, i) => (
          <li key={i}>{inline(li, `li-${blocks.length}-${i}`)}</li>
        ))}
      </ul>,
    );
    list = [];
  };

  lines.forEach((raw, i) => {
    const line = raw.trimEnd();
    const bullet = line.match(/^\s*[-*]\s+(.*)/);
    const heading = line.match(/^(#{1,3})\s+(.*)/);
    if (bullet) {
      list.push(bullet[1]);
      return;
    }
    flushList();
    if (heading) {
      blocks.push(
        <p key={`h-${i}`} className="mt-2 mb-1 text-sm font-semibold text-foreground">
          {inline(heading[2], `h-${i}`)}
        </p>,
      );
    } else if (line.trim()) {
      blocks.push(
        <p key={`p-${i}`} className="leading-relaxed">
          {inline(line, `p-${i}`)}
        </p>,
      );
    }
  });
  flushList();

  return <div className="space-y-1.5">{blocks}</div>;
}
