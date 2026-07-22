#!/usr/bin/env bash
# render_pdf.sh — turn a rendered .pptx into a review PDF + per-page JPEGs.
#
# Usage: bash render_pdf.sh <deck.pptx> [dpi]
#   deck.pptx  the file written by `node scripts/render.js`
#   dpi        page-image resolution (default 110)
#
# IMPORTANT (macOS + agent sandbox): `soffice` must run with the sandbox OFF, or it exits
# clean and writes NOTHING (it can't write its LibreOffice profile under the sandbox). The
# agent should invoke this script with sandbox disabled. `pdftoppm` itself is sandbox-safe.
set -euo pipefail

PPTX="${1:?usage: render_pdf.sh <deck.pptx> [dpi]}"
DPI="${2:-110}"
DIR="$(cd "$(dirname "$PPTX")" && pwd)"
BASE="$(basename "$PPTX" .pptx)"
PDF="$DIR/$BASE.pdf"

# The bundled headless LibreOffice runtime cannot see macOS user fonts. Prefer the
# Homebrew app wrapper when available so DM Sans, Inter, and Playfair survive export.
SOFFICE_BIN="$(command -v soffice)"
if [ -x /opt/homebrew/bin/soffice ]; then
  SOFFICE_BIN=/opt/homebrew/bin/soffice
fi

if [ ! -f "$PPTX" ]; then echo "No such file: $PPTX" >&2; exit 1; fi

# LibreOffice can keep a stale font cache in its normal user profile. A fresh, isolated
# profile makes newly installed/bundled brand fonts resolve consistently during export.
PROFILE_DIR="$(mktemp -d /private/tmp/slides-cs-lo-profile.XXXXXX)"
trap 'rm -rf "$PROFILE_DIR"' EXIT

# Clear any stale LibreOffice lock, then convert. --convert-to writes <base>.pdf into --outdir.
pkill -f soffice >/dev/null 2>&1 || true
sleep 1
rm -f "$PDF" "$DIR/$BASE"-*.jpg
"$SOFFICE_BIN" -env:UserInstallation="file://$PROFILE_DIR" --headless --convert-to pdf "$PPTX" --outdir "$DIR" >/dev/null 2>&1

if [ ! -f "$PDF" ]; then
  echo "PDF not produced — is the sandbox OFF for soffice? (see header)" >&2
  exit 2
fi

# Per-page JPEGs for visual review: <base>-01.jpg, -02.jpg, ...
pdftoppm -jpeg -r "$DPI" "$PDF" "$DIR/$BASE"

N=$(ls "$DIR/$BASE"-*.jpg 2>/dev/null | wc -l | tr -d ' ')
echo "PDF:   $PDF"
echo "Pages: $N JPEGs at $DIR/$BASE-NN.jpg (${DPI} dpi)"
echo "Note:  PDF export skips slides hidden in PowerPoint (show=0)."
