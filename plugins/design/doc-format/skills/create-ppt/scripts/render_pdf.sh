#!/usr/bin/env bash
# Convert a rendered .pptx into a review PDF and per-page JPEGs.
# Usage: bash render_pdf.sh <deck.pptx> [dpi]
#
# Supported conversion hosts: macOS and Linux with LibreOffice + Poppler installed.
# In agent sandboxes, LibreOffice may need to run outside the sandbox so it can create
# its profile and lock files.
set -euo pipefail

PPTX="${1:?usage: render_pdf.sh <deck.pptx> [dpi]}"
DPI="${2:-110}"

if [ ! -f "$PPTX" ]; then
  echo "No such file: $PPTX" >&2
  exit 1
fi

if ! command -v pdftoppm >/dev/null 2>&1; then
  echo "Missing pdftoppm. Install Poppler before requesting PDF page images." >&2
  exit 1
fi

SOFFICE_BIN=""
PATH_SO="$(command -v soffice 2>/dev/null || true)"
for CANDIDATE in \
  "$PATH_SO" \
  "/opt/homebrew/bin/soffice" \
  "/usr/local/bin/soffice" \
  "/Applications/LibreOffice.app/Contents/MacOS/soffice"
do
  if [ -n "$CANDIDATE" ] && [ -x "$CANDIDATE" ]; then
    SOFFICE_BIN="$CANDIDATE"
    break
  fi
done

if [ -z "$SOFFICE_BIN" ]; then
  echo "LibreOffice not found. The .pptx is still usable; install LibreOffice to add a review PDF." >&2
  exit 1
fi

DIR="$(cd "$(dirname "$PPTX")" && pwd)"
BASE="$(basename "$PPTX" .pptx)"
PDF="$DIR/$BASE.pdf"
PAGES_DIR="$DIR/$BASE-review-pages"
TEMP_ROOT="${TMPDIR:-/tmp}"
PROFILE_DIR="$(mktemp -d "$TEMP_ROOT/create-ppt-lo.XXXXXX")"
CONVERT_LOG="$PROFILE_DIR/convert.log"
CONVERT_DIR="$PROFILE_DIR/output"
STAGE_PAGES="$PROFILE_DIR/pages"
mkdir -p "$CONVERT_DIR" "$STAGE_PAGES"

cleanup() {
  rm -rf "$PROFILE_DIR"
}
trap cleanup EXIT

if ! "$SOFFICE_BIN" \
  -env:UserInstallation="file://$PROFILE_DIR" \
  --headless \
  --convert-to pdf \
  "$PPTX" \
  --outdir "$CONVERT_DIR" >"$CONVERT_LOG" 2>&1
then
  echo "LibreOffice conversion failed:" >&2
  tail -20 "$CONVERT_LOG" >&2
  exit 2
fi

CONVERTED_PDF="$CONVERT_DIR/$BASE.pdf"
if [ ! -f "$CONVERTED_PDF" ]; then
  echo "LibreOffice reported success but did not produce $PDF." >&2
  tail -20 "$CONVERT_LOG" >&2
  exit 2
fi

pdftoppm -jpeg -r "$DPI" "$CONVERTED_PDF" "$STAGE_PAGES/page"

mv -f "$CONVERTED_PDF" "$PDF"
mkdir -p "$PAGES_DIR"
find "$PAGES_DIR" -maxdepth 1 -type f -name 'page-*.jpg' -delete
find "$STAGE_PAGES" -maxdepth 1 -type f -name 'page-*.jpg' -exec mv -f {} "$PAGES_DIR/" \;
N="$(find "$PAGES_DIR" -maxdepth 1 -type f -name 'page-*.jpg' | wc -l | tr -d ' ')"
echo "PDF:   $PDF"
echo "Pages: $N JPEGs at $PAGES_DIR/page-NN.jpg (${DPI} dpi)"
echo "Note:  PDF export skips slides hidden in PowerPoint (show=0)."
