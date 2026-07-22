#!/usr/bin/env bash
# setup-fonts.sh — install the deck fonts (DM Sans, Inter, Playfair Display) so LibreOffice
# renders and QA previews are accurate. Includes the STATIC named faces the deck relies on:
# "DM Sans Medium", "Inter Medium", "Playfair Display SemiBold", "Playfair Display Italic" —
# LibreOffice resolves those by face string but cannot pull a named instance from a variable
# TTF, which is why the static faces are bundled. Cross-platform: macOS uses ~/Library/Fonts,
# Linux uses fontconfig (~/.fonts + fc-cache). Idempotent; safe to run from anywhere.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FONT_SRC="$SCRIPT_DIR/../assets/fonts"

if [ ! -d "$FONT_SRC" ]; then
  echo "error: font source dir not found at $FONT_SRC" >&2
  exit 1
fi

case "$(uname -s)" in
  Darwin)
    DEST="$HOME/Library/Fonts"
    mkdir -p "$DEST"
    cp -f "$FONT_SRC"/*.ttf "$DEST"/
    echo "fonts installed to $DEST (macOS)"
    ;;
  Linux)
    DEST="$HOME/.fonts"
    mkdir -p "$DEST"
    cp -f "$FONT_SRC"/*.ttf "$DEST"/
    if command -v fc-cache >/dev/null 2>&1; then
      fc-cache -f "$DEST" >/dev/null 2>&1 || true
      echo "fonts installed to $DEST and cache refreshed (Linux)"
    else
      echo "fonts copied to $DEST — fc-cache not found, you may need to refresh manually"
    fi
    ;;
  *)
    echo "unsupported OS $(uname -s); copy $FONT_SRC/*.ttf into your system fonts manually" >&2
    exit 1
    ;;
esac

# Verification: base families (DM Sans, Inter) render bold via family+bold; the Medium and
# serif tiers resolve by their own named faces, so all three families must be visible.
if command -v fc-list >/dev/null 2>&1; then
  echo "check: $(fc-list | grep -ci 'DM Sans') DM Sans, $(fc-list | grep -ci 'Inter') Inter, $(fc-list | grep -ci 'Playfair') Playfair face(s) visible to fontconfig"
fi
