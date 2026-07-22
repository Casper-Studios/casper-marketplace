#!/usr/bin/env bash
# check_pptx.sh <deck.pptx> — validate the OOXML that PowerPoint will actually parse.
#
# WHY THIS EXISTS
# PowerPoint refuses to open a deck containing a shape with a NEGATIVE extent
# (<a:ext cx=".." cy="..">), offering only to "repair" it. The repair then clamps those
# shapes, so every rising line in a chart renders horizontal — a slope chart becomes a
# staircase and a trend line goes flat.
#
# LibreOffice silently normalises the same XML. That means `render_pdf.sh` output can look
# completely correct while the .pptx it came from is unopenable in the app the client uses.
# A PDF check is NOT a substitute for this one — run both before shipping a deck.
#
# Any sloped line must be drawn through the seg() helper in assets/layouts.js, which emits a
# positive extent from the min corner and carries direction with flipV.
set -euo pipefail

deck="${1:?usage: check_pptx.sh <deck.pptx>}"
[ -f "$deck" ] || { echo "FAIL: no such file: $deck"; exit 1; }

# Project-local scratch: the sandbox denies mkdtemp under $TMPDIR (see CLAUDE.md § Temp files).
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
work="$here/../../../tmp/.pptx-check-$$"
mkdir -p "$work"
trap 'rm -rf "$work"' EXIT

unzip -q "$deck" -d "$work"

neg=$(grep -ohE '<a:ext cx="-?[0-9]+" cy="-?[0-9]+"/>' "$work"/ppt/slides/*.xml \
      | grep -cE 'cx="-|cy="-' || true)

if [ "${neg:-0}" -gt 0 ]; then
  echo "FAIL: $neg shape(s) carry a negative extent — PowerPoint will demand repair,"
  echo "      and sloped lines will render flat after it repairs them."
  echo "      Draw every sloped line through seg() in assets/layouts.js."
  exit 1
fi

slides=$(find "$work/ppt/slides" -maxdepth 1 -name 'slide*.xml' | wc -l | tr -d ' ')

# Embedded fonts. Not fatal — a deck is still valid without them — but a deck that leaves this
# machine without them silently falls back to Calibri on any recipient who lacks the brand
# faces, and four of the families we name are renamed statics no standard install provides.
# render.js embeds by default; a zero here means the post-process failed and was warned past.
# Guard the directory test separately: under `set -o pipefail`, find failing on a missing
# ppt/fonts aborts the whole script — which would make an un-embedded deck look like a crash
# instead of a warning. Exactly the case this branch exists to report.
fonts=0
if [ -d "$work/ppt/fonts" ]; then
  fonts=$(find "$work/ppt/fonts" -maxdepth 1 -name '*.fntdata' | wc -l | tr -d ' ')
fi
if [ "${fonts:-0}" -gt 0 ]; then
  echo "OK: $(basename "$deck") — $slides slides, no negative extents, $fonts font(s) embedded."
else
  echo "OK: $(basename "$deck") — $slides slides, no negative extents."
  echo "    WARN: no embedded fonts. Fine locally; on a machine without the brand faces this"
  echo "          deck falls back to system fonts. Re-run render.js, or embed_fonts.py directly."
fi
