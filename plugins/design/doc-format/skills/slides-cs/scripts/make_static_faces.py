#!/usr/bin/env python3
"""make_static_faces.py — instance the bundled DM Sans variable font into real static faces.

    python3 scripts/make_static_faces.py [--check]

WHY
---
`themes.js` asks for `display: "DM Sans"` and sets `bold: true` on every talking header — 27 runs,
the largest text on every slide. But the bundle only shipped `DMSans-Variable.ttf`, whose
family(1) is **"DM Sans 9pt"**, not "DM Sans". So on any machine without DM Sans separately
installed, the header family does not resolve at all and falls back to Calibri/Arial. Worse,
there was no DM Sans **Bold** anywhere in the bundle in any form, so even a resolving renderer
had to synthesize one.

Nobody caught it because this dev machine has 24 DM Sans faces in ~/Library/Fonts AND
`render_pdf.sh` prefers the Homebrew LibreOffice specifically so it can see system fonts — the
bundle's own coverage was never once exercised. Same shape as the negative-extent bug: the QA
pipeline was supplying what the artifact was missing.

The variable font carries a wght axis spanning 100-1000, so the true Bold is already in the file
we ship — it just needs instancing into a static face a renderer can select by name. No download,
no new dependency, and no visual compromise: this is the same design at weight 700, not a
SemiBold substitute. `themes.js` needs no change, because the output declares family "DM Sans"
with a proper Bold subfamily, which is exactly what family+bold asks for.

Keeping the naming discipline the file already documents: STATIC single-weight faces whose name
a renderer can resolve, because LibreOffice cannot select a variable font's named instance.
"""
import argparse
import shutil
import sys
from pathlib import Path

try:
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
except ImportError:
    sys.exit("FAIL: fontTools required — pip install fonttools")

FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"
SRC = FONTS / "DMSans-Variable.ttf"

# (output, weight, family, subfamily, full, postscript)
TARGETS = [
    ("DMSans-Regular.ttf", 400, "DM Sans", "Regular", "DM Sans", "DMSans-Regular"),
    ("DMSans-Bold.ttf",    700, "DM Sans", "Bold",    "DM Sans Bold", "DMSans-Bold"),
]

MAC, WIN = (1, 0, 0), (3, 1, 0x409)


def set_name(font, nid, value):
    for pid, eid, lid in (MAC, WIN):
        font["name"].setName(value, nid, pid, eid, lid)


def build(out, weight, family, sub, full, ps):
    f = TTFont(SRC)
    # Pin BOTH axes. opsz stays at its default (9) so the static matches what a renderer
    # resolving the variable font would already produce — this fixes resolution, it does not
    # redesign the type.
    axes = {a.axisTag: a.defaultValue for a in f["fvar"].axes}
    axes["wght"] = weight
    inst = instancer.instantiateVariableFont(f, axes, inplace=False, updateFontNames=False)

    set_name(inst, 1, family)
    set_name(inst, 2, sub)
    set_name(inst, 4, full)
    set_name(inst, 6, ps)
    # Typographic names would otherwise still claim the variable family and override 1/2 on
    # renderers that prefer them — drop so family+subfamily is the single source of truth.
    for nid in (16, 17, 21, 22, 25):
        for pid, eid, lid in (MAC, WIN):
            try:
                inst["name"].removeNames(nid, pid, eid, lid)
            except Exception:
                pass

    os2, head = inst["OS/2"], inst["head"]
    os2.usWeightClass = weight
    bold = weight >= 700
    os2.fsSelection = (os2.fsSelection & ~0x60) | (0x20 if bold else 0x40)  # BOLD / REGULAR
    head.macStyle = (head.macStyle & ~0x01) | (0x01 if bold else 0x00)
    assert os2.fsType == 0, f"{out}: fsType must stay 0 (installable) — got {os2.fsType}"

    path = FONTS / out
    inst.save(path)
    return path


def report():
    print("bundled faces (family / subfamily / weight / fsType):")
    for p in sorted(FONTS.glob("*.ttf")):
        f = TTFont(p)
        n = f["name"]
        fam = n.getDebugName(1)
        sub = n.getDebugName(2)
        var = " [VARIABLE]" if "fvar" in f else ""
        print(f"  {p.name:26s} {fam!r:26s} {sub!r:10s} w={f['OS/2'].usWeightClass:4d} "
              f"fsType={f['OS/2'].fsType}{var}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="list bundled faces, build nothing")
    a = ap.parse_args()
    if a.check:
        return report()

    if not SRC.exists():
        sys.exit(f"FAIL: {SRC} not found")
    for out, w, fam, sub, full, ps in TARGETS:
        p = build(out, w, fam, sub, full, ps)
        print(f"  wrote {p.name:22s} {fam!r} / {sub!r}  w={w}  {p.stat().st_size/1024:.0f} KB")

    # The variable source is now redundant AND actively harmful: it declares the near-miss
    # family "DM Sans 9pt", which invites a renderer to resolve the wrong thing.
    archive = FONTS / "_src"
    archive.mkdir(exist_ok=True)
    shutil.move(str(SRC), str(archive / SRC.name))
    print(f"  moved  {SRC.name} -> _src/ (kept as the instancing source, no longer shipped as a face)")
    print()
    report()


if __name__ == "__main__":
    main()
