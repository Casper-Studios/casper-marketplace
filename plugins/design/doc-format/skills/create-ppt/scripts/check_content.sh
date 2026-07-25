#!/usr/bin/env bash
# Deterministic content checks for a deck folder.
# Usage: bash check_content.sh <deck-folder>
#
# The script loads trusted, agent-authored JavaScript modules. Never point it at a
# content.js or outline.js supplied by an untrusted source.
set -uo pipefail

DECK="${1:?usage: check_content.sh <deck-folder>}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTENT="$DECK/content.js"

[ -f "$CONTENT" ] || {
  echo "FAIL: no content.js in $DECK" >&2
  exit 1
}

node - "$CONTENT" "$SKILL_DIR" "$DECK/outline.js" <<'NODE'
const path = require("path");
const fs = require("fs");
const [contentPath, skillDir, outlinePath] = process.argv.slice(2);
let fail = 0;
let warn = 0;

const say = (level, message) => {
  if (level === "FAIL") {
    fail += 1;
    console.error(`FAIL: ${message}`);
  } else {
    warn += 1;
    console.warn(`WARN: ${message}`);
  }
};

let content;
let sharedLayouts;
try {
  content = require(path.resolve(contentPath));
} catch (error) {
  console.error(`FAIL: content.js did not load — ${error.message}`);
  process.exit(1);
}

try {
  ({ layouts: sharedLayouts } = require(path.join(skillDir, "assets", "layouts.js")));
} catch (error) {
  console.error(`FAIL: could not load layouts.js — ${error.message}`);
  process.exit(1);
}

const customLayouts = content.customLayouts || {};
const layouts = { ...sharedLayouts, ...customLayouts };
const slides = content.slides || [];
if (!slides.length) say("FAIL", "content.js has no slides");

const dataKeys = new Set([
  "statValue", "stats", "bars", "rows", "deltas", "points", "series",
  "milestones", "events", "values", "actual", "target", "pct", "amount",
]);

const containsData = (value, key = "") => {
  if (dataKeys.has(key)) return value != null;
  if (Array.isArray(value)) return value.some((item) => containsData(item));
  if (value && typeof value === "object") {
    return Object.entries(value).some(([childKey, childValue]) => containsData(childValue, childKey));
  }
  return false;
};

slides.forEach((slide, index) => {
  const number = index + 1;
  if (!layouts[slide.layout]) {
    say("FAIL", `slide ${number}: unknown layout "${slide.layout}"`);
  }
  if (containsData(slide) && !slide.source && slide.layout !== "sources") {
    say("FAIL", `slide ${number} (${slide.layout}): contains data but has no source`);
  }
  if (!String(slide.notes || "").trim()) {
    say("FAIL", `slide ${number} (${slide.layout}): no speaker notes`);
  }
});

if (fs.existsSync(outlinePath)) {
  let outline;
  try {
    outline = require(path.resolve(outlinePath));
  } catch (error) {
    say("FAIL", `outline.js did not load — ${error.message}`);
  }
  if (outline) {
    const visible = slides.filter((slide) => !slide.hidden && slide.header);
    const planned = (outline.slides || []).map((slide) => String(slide.header || "").trim()).filter(Boolean);
    const built = visible.map((slide) => String(slide.header || "").trim());
    if (planned.length !== built.length) {
      say("WARN", `outline has ${planned.length} headers; content has ${built.length} visible content headers`);
    }
    planned.forEach((header, index) => {
      if (built[index] !== header) {
        say("WARN", `outline/content drift at content slide ${index + 1}: "${header}"`);
      }
    });
    if (!warn) console.log("outline↔content: structured headers reconcile");
  }
}

console.log(`checked ${slides.length} slides — ${fail} fail, ${warn} warn`);
process.exit(fail ? 1 : 0);
NODE
HARD=$?

PDF="$(find "$DECK" -maxdepth 1 -type f -name '*.pdf' | sort | head -1)"
if [ -n "$PDF" ]; then
  if command -v pdftotext >/dev/null 2>&1; then
    CHARS="$(pdftotext "$PDF" - 2>/dev/null | tr -d '[:space:]' | wc -c | tr -d ' ')"
    if [ "$CHARS" -lt 100 ]; then
      echo "WARN: $(basename "$PDF") has almost no extractable text ($CHARS chars)"
    else
      echo "pdf text: $CHARS chars extracted from $(basename "$PDF")"
    fi
  else
    echo "WARN: pdftotext unavailable; skipped PDF text extraction"
  fi
fi

exit "$HARD"
