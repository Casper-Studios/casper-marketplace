#!/usr/bin/env bash
# check_tokens.sh — source lint for the skill itself (not for a built deck).
#
# Guards the accent/accentText split. The bug this exists to prevent shipped in every layout
# for months and was invisible on the theme it was authored in: `accent` doubled as a text
# color, which is fine on casper (purple, 7.32:1) and unreadable on sphera (teal, 2.06:1).
# Emphasis literally INVERTED — the de-emphasised label out-read the highlighted one.
#
# Three checks, all fatal:
#   1. No layout uses T.accent as a TEXT color. Shape fills/strokes are fine and expected.
#   2. Every theme defines accentText.
#   3. Every theme's accentText clears 4.5:1 on its own paper AND out-contrasts its own muted
#      (a token that merely passes WCAG but ties `muted` still fails the design job).
#
# Usage: bash check_tokens.sh      (no args; paths are relative to the skill)
set -uo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

node - "$SKILL_DIR" <<'NODE'
const fs = require("fs");
const path = require("path");
const skillDir = process.argv[2];
let fail = 0;

// ---- 1. T.accent must never be a text color -------------------------------------------
// A `color:` key also appears INSIDE `fill: {...}` and `line: {...}`, so those sub-objects are
// stripped before looking for a text `color:`. Without this, the naive grep both misses real
// violations and flags every legitimate hot-bar fill.
const layoutsPath = path.join(skillDir, "assets", "layouts.js");
const lines = fs.readFileSync(layoutsPath, "utf8").split("\n");
const offenders = [];
lines.forEach((raw, i) => {
  if (!raw.includes("T.accent") || raw.trimStart().startsWith("//")) return;
  const stripped = raw
    .replace(/fill:\s*\{[^}]*\}/g, "")
    .replace(/line:\s*\{[^}]*\}/g, "");
  // Anything left that pairs a `color:` (or a *color/stroke-free* assignment feeding one)
  // with T.accent is a text usage.
  if (/color:\s*[^,]*T\.accent\b(?!Text)/.test(stripped)) {
    offenders.push(`  layouts.js:${i + 1}  ${raw.trim().slice(0, 100)}`);
  }
});
if (offenders.length) {
  console.error(`FAIL: T.accent used as a TEXT color in ${offenders.length} place(s).`);
  console.error("      Use T.accentText for text; keep T.accent for fills, bars and strokes.");
  offenders.forEach((o) => console.error(o));
  fail = 1;
} else {
  console.log("OK   accent/accentText split clean (no T.accent used as text)");
}

// ---- 2 + 3. every theme defines a readable accentText ---------------------------------
const { THEMES } = require(path.join(skillDir, "assets", "themes.js"));
const lum = (hex) => {
  const h = hex.replace("#", "");
  const ch = [0, 2, 4].map((i) => {
    const v = parseInt(h.slice(i, i + 2), 16) / 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2];
};
const ratio = (a, b) => {
  const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);
  return (x + 0.05) / (y + 0.05);
};

for (const [name, T] of Object.entries(THEMES)) {
  if (!T.accentText) {
    console.error(`FAIL: theme "${name}" does not define accentText`);
    fail = 1;
    continue;
  }
  const onPaper = ratio(T.accentText, T.paper);
  const vsMuted = ratio(T.muted, T.paper);
  const ok = onPaper >= 4.5 && onPaper > vsMuted;
  const verdict = ok ? "OK  " : "FAIL";
  console.log(
    `${verdict} ${name}: accentText #${T.accentText} = ${onPaper.toFixed(2)}:1 on paper ` +
    `(muted = ${vsMuted.toFixed(2)}:1)`
  );
  if (!ok) {
    console.error(
      onPaper < 4.5
        ? `      needs >= 4.5:1 for AA on body text`
        : `      passes AA but does not out-contrast muted — emphasis would invert`
    );
    fail = 1;
  }
}

process.exit(fail);
NODE
