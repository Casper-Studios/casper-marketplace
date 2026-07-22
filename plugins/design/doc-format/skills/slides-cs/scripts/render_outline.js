#!/usr/bin/env node
// render_outline.js <outline.js> [out.html]
//
// Renders the deck OUTLINE — the plan, before any slide is built — as a self-contained,
// brand-coloured storyboard the user can approve at a glance. One card per planned slide:
// running number, the layout it will use (tagged), the talking header, and the evidence line.
//
// WHY THIS EXISTS: the outline gate used to be markdown + chat. A visual storyboard lets the
// user see "here are the 12 slides, here are their types, here's the flow" and sign off on the
// PLAN before the expensive build. It is the companion to outline.md, not a replacement — the
// .md stays the editable source; this is the read view.
//
// Input is a small outline module (NOT content.js — no slot data, just the plan):
//   module.exports = {
//     theme: "casper" | "sphera",
//     title: "Deck title",
//     slides: [ { header: "talking header", layout: "chartTakeaway", evidence: "one line" }, ... ]
//   }
// Self-contained output: inline CSS, system fonts, the theme's accent/ink/muted for brand flavour.
// No embedded brand fonts (this is a plan preview, not the deck), so it stays small and instant.

const fs = require("fs");
const path = require("path");
const { getTheme } = require("../assets/themes.js");

const esc = (s) => String(s == null ? "" : s)
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const hx = (c) => "#" + String(c).replace(/^#/, "");

function build(outline, T) {
  const slides = outline.slides || [];
  const title = outline.title || "Deck outline";
  const themeName = (outline.theme || "casper");

  // A layout used more than once is flagged, since a repeated component is the "template-stamped"
  // tell the writing contract warns about — worth seeing at the plan stage.
  const counts = {};
  slides.forEach((s) => { counts[s.layout] = (counts[s.layout] || 0) + 1; });

  const cards = slides.map((s, i) => {
    const dup = counts[s.layout] > 1;
    return `      <li class="card">
        <div class="num">${String(i + 1).padStart(2, "0")}</div>
        <div class="body">
          <span class="layout${dup ? " dup" : ""}">${esc(s.layout || "—")}${dup ? " · repeated" : ""}</span>
          <h2>${esc(s.header)}</h2>
          ${s.evidence ? `<p class="ev">${esc(s.evidence)}</p>` : ""}
        </div>
      </li>`;
  }).join("\n");

  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} — outline</title>
<style>
  :root {
    --paper:${hx(T.paper)}; --ink:${hx(T.ink)}; --accent:${hx(T.accent)};
    --accentText:${hx(T.accentText || T.accent)}; --muted:${hx(T.muted)};
    --hair:${hx(T.hair)}; --surface:${hx(T.surface)};
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink);
    font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; }
  .wrap { max-width: 820px; margin: 0 auto; padding: 56px 28px 72px; }
  .eyebrow { font-size: 12px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase;
    color: var(--accentText); margin-bottom: 12px; }
  h1 { margin: 0 0 8px; font-size: clamp(26px, 4vw, 38px); letter-spacing: -.02em; }
  .meta { margin: 0 0 8px; color: var(--muted); font-size: 14px; }
  .deck { list-style: none; margin: 34px 0 0; padding: 0; counter-reset: none; }
  .card { display: grid; grid-template-columns: 52px 1fr; gap: 20px; align-items: start;
    padding: 20px 0; border-top: 1px solid var(--hair); }
  .card:last-child { border-bottom: 1px solid var(--hair); }
  .num { font-size: 20px; font-weight: 700; color: var(--accentText);
    font-variant-numeric: tabular-nums; padding-top: 2px; }
  .layout { display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: .04em;
    text-transform: none; color: var(--accentText); background: var(--surface);
    border: 1px solid var(--hair); border-radius: 6px; padding: 2px 8px; margin-bottom: 8px; }
  .layout.dup { color: #b45309; }
  .card h2 { margin: 0; font-size: 17px; font-weight: 650; line-height: 1.35; letter-spacing: -.01em; }
  .card .ev { margin: 6px 0 0; color: var(--muted); font-size: 14px; }
  .foot { margin-top: 30px; color: var(--muted); font-size: 13px; }
  .foot b { color: var(--ink); }
</style></head>
<body><div class="wrap">
  <div class="eyebrow">Outline for review · ${esc(themeName)} theme</div>
  <h1>${esc(title)}</h1>
  <p class="meta">${slides.length} slide${slides.length === 1 ? "" : "s"}. Approve the plan, then I build the deck.</p>
  <ol class="deck">
${cards}
  </ol>
  <p class="foot"><b>Read it top to bottom:</b> the headers should tell the argument on their own. Say the word and I render it, or point at any slide to change the plan first.</p>
</div></body></html>`;
}

// The markdown twin: the same plan as a plain list, so the outline exists in HTML (the read
// view) AND MD (the editable source) from one authored file, never double-typed.
function buildMd(outline) {
  const slides = outline.slides || [];
  const lines = [`# ${outline.title || "Deck outline"} — outline`, "",
    `_${slides.length} slides · ${outline.theme || "casper"} theme · approve the plan, then build._`, ""];
  slides.forEach((s, i) => {
    lines.push(`${i + 1}. **${s.header || ""}** \`${s.layout || "—"}\`${s.evidence ? `  \n   ${s.evidence}` : ""}`);
  });
  return lines.join("\n") + "\n";
}

function main() {
  const inPath = process.argv[2];
  if (!inPath) { console.error("Usage: node render_outline.js <outline.js> [out.html]"); process.exit(1); }
  const resolved = path.resolve(process.cwd(), inPath);
  const outline = require(resolved);
  const T = getTheme(outline.theme || "casper");
  const outHtml = process.argv[3] ? path.resolve(process.cwd(), process.argv[3]) : resolved.replace(/\.js$/, ".html");
  const outMd = outHtml.replace(/\.html$/, ".md");
  fs.writeFileSync(outHtml, build(outline, T));
  fs.writeFileSync(outMd, buildMd(outline));
  const n = (outline.slides || []).length;
  console.log(`Wrote ${outHtml} + ${path.basename(outMd)} — ${n}-slide outline, theme "${outline.theme || "casper"}".`);
}

if (require.main === module) main();
module.exports = { build };
