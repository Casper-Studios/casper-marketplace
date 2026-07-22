#!/usr/bin/env bash
# check_content.sh — free, mechanical pre-review checks for a deck folder.
#
# Usage: bash check_content.sh <deck-folder>
#   expects <deck-folder>/content.js, and (optionally) outline.md and deck.pdf alongside.
#
# Catches the cheap, deterministic problems before any review agent runs:
#   1. content.js is valid and loads (require() it via node).
#   2. Every layout named in content.js exists in the skill's layouts.js.
#   3. Every slide that shows a number (has statValue/stats/bars/rows) also has a `source`.
#   4. Every slide has `notes`.
#   5. If outline.md exists: each outline header line appears (loosely) in content.js — catches the
#      outline→content translation drift (the real drift point; both are plain text, no pptx parsing).
#   6. If deck.pdf exists: pdftotext spot-check that the PDF actually carries text (not a blank render).
# Exit non-zero if any hard check (1–4) fails; 5–6 warn only.
set -uo pipefail

DECK="${1:?usage: check_content.sh <deck-folder>}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTENT="$DECK/content.js"
[ -f "$CONTENT" ] || { echo "FAIL: no content.js in $DECK" >&2; exit 1; }

node - "$CONTENT" "$SKILL_DIR" <<'NODE'
const path = require("path");
const [contentPath, skillDir] = process.argv.slice(2);
let fail = 0, warn = 0;
const say = (t, m) => { if (t === "FAIL") { fail++; console.error("FAIL: " + m); } else { warn++; console.warn("WARN: " + m); } };

let content, layouts;
try { content = require(path.resolve(contentPath)); }
catch (e) { console.error("FAIL: content.js did not load — " + e.message); process.exit(1); }
try { ({ layouts } = require(path.join(skillDir, "assets", "layouts.js"))); }
catch (e) { console.error("FAIL: could not load layouts.js — " + e.message); process.exit(1); }

const slides = content.slides || [];
if (!slides.length) say("FAIL", "content.js has no slides");
const dataKeys = ["statValue", "stats", "bars", "rows"];
slides.forEach((sl, i) => {
  const n = i + 1;
  if (!layouts[sl.layout]) say("FAIL", `slide ${n}: unknown layout "${sl.layout}"`);
  const showsData = dataKeys.some((k) => sl[k] != null);
  if (showsData && !sl.source && sl.layout !== "sources") say("FAIL", `slide ${n} (${sl.layout}): shows a number but has no source`);
  if (!sl.notes && sl.layout !== "cover" && sl.layout !== "closing") say("WARN", `slide ${n} (${sl.layout}): no speaker notes`);
});
console.log(`checked ${slides.length} slides — ${fail} fail, ${warn} warn`);
process.exit(fail ? 1 : 0);
NODE
HARD=$?

# 5 · outline ↔ content drift (loose): each non-empty outline header line should appear in content.js text.
if [ -f "$DECK/outline.md" ]; then
  MISS=0
  while IFS= read -r line; do
    h="$(printf '%s' "$line" | sed -E 's/^#+ +//; s/^[-*] +//; s/^[0-9]+\. +//' | tr -d '\r')"
    [ ${#h} -lt 12 ] && continue
    key="$(printf '%s' "$h" | cut -c1-24)"
    grep -qF "$key" "$CONTENT" || { echo "WARN: outline header not found in content.js: \"$h\""; MISS=$((MISS+1)); }
  done < "$DECK/outline.md"
  [ "$MISS" -eq 0 ] && echo "outline↔content: headers reconcile"
fi

# 6 · PDF carries text
if [ -f "$DECK/deck.pdf" ] && command -v pdftotext >/dev/null 2>&1; then
  CHARS=$(pdftotext "$DECK/deck.pdf" - 2>/dev/null | tr -d '[:space:]' | wc -c | tr -d ' ')
  if [ "$CHARS" -lt 100 ]; then echo "WARN: deck.pdf has almost no extractable text ($CHARS chars) — blank render?"; else echo "pdf text: $CHARS chars extracted"; fi
fi

exit $HARD
