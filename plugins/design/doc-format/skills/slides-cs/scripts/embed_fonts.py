#!/usr/bin/env python3
"""embed_fonts.py — embed the bundled brand fonts INTO a rendered .pptx.

    python3 scripts/embed_fonts.py <deck.pptx> [-o out.pptx] [--report]

WHY THIS EXISTS
---------------
The skill's core promise is that any machine renders the deck identically. It bundles the
fonts to keep that promise — but nothing ever put them in the .pptx. A deck handed to a client
carries only font NAMES, and four of the names it carries are faces that no standard install
provides, because the bundle deliberately RENAMES static weights so LibreOffice can resolve
them by face string (themes.js documents the rename). That optimises for the PDF generator,
and the PDF is precisely the artifact that then cannot detect a substitution.

It is the same blind spot as the negative-extent bug: the QA pipeline could not see the defect
because the QA pipeline was the thing causing it to look fine. Worse here, the dev machine has
24 DM Sans faces installed system-wide, so every render this project has ever done resolved
against SYSTEM fonts and never once exercised the bundle.

pptxgenjs cannot emit <p:embeddedFontLst>, so this is a post-process on the package.

STATUS: OPT-IN. Not wired into render.js. Embedding writes binary parts that only PowerPoint
can truly adjudicate, and there is no PowerPoint on the build machine — so the default ship
path is left untouched until someone opens an embedded deck and confirms no repair prompt.

LICENSING: checked, not assumed. All bundled faces are fsType=0x0000 (Installable), so
embedding is permitted. This script RE-CHECKS at runtime and refuses to embed a restricted
font rather than trusting this comment.

SPEC NOTES (MS-OE376 / ECMA-376):
  * parts live at ppt/fonts/fontN.fntdata, content type application/x-fontdata
  * payload is the plain TTF/OTF byte stream (PowerPoint's own writer may obfuscate; readers
    accept the unobfuscated form, which is what the non-Microsoft toolchain emits)
  * every typeface listed MUST be unique AND actually used in the presentation — so the embed
    set is derived from the DECK, never from the bundle directory
  * <p:embeddedFontLst> has a fixed slot in the CT_Presentation sequence: after notesSz/
    smartTags, before custShowLst/defaultTextStyle. Wrong position = schema-invalid = the
    repair prompt this project has already shipped once.
"""
import argparse
import re
import shutil
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
FONTS = SKILL / "assets" / "fonts"

REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

# typeface string as written by themes.js  ->  { variant: bundled filename }
# Variants are the four OOXML slots: regular / bold / italic / boldItalic.
FACE_MAP = {
    "Inter":                     {"regular": "Inter-Regular.ttf", "bold": "Inter-Bold.ttf"},
    "Inter Medium":              {"regular": "Inter-Medium.ttf"},
    # Used BOLD-ONLY (27 header runs — the largest text on every slide). Both faces are now real
    # statics instanced from the variable source by scripts/make_static_faces.py, so family+bold
    # resolves properly instead of falling back to Calibri on a machine without DM Sans.
    "DM Sans":                   {"regular": "DMSans-Regular.ttf", "bold": "DMSans-Bold.ttf"},
    "DM Sans Medium":            {"regular": "DMSans-Medium.ttf"},
    "Playfair Display SemiBold": {"regular": "PlayfairDisplay-SemiBold.ttf"},
    "Playfair Display Italic":   {"regular": "PlayfairDisplay-MediumItalic.ttf"},
}


def fs_type(path: Path):
    """OS/2 fsType embedding-permission bits. 2 = restricted, refuse to embed."""
    d = path.read_bytes()
    for i in range(struct.unpack(">H", d[4:6])[0]):
        r = 12 + i * 16
        if d[r:r + 4] == b"OS/2":
            off = struct.unpack(">I", d[r + 8:r + 12])[0]
            return struct.unpack(">H", d[off + 8:off + 10])[0]
    return None


def used_faces(zf: zipfile.ZipFile) -> Counter:
    """(typeface, bold, italic) combos actually present in slides + notes."""
    combos = Counter()
    for n in zf.namelist():
        if not re.match(r"ppt/(slides|notesSlides)/\w+\.xml$", n):
            continue
        xml = zf.read(n).decode("utf-8")
        for m in re.finditer(r"<a:rPr\b([^>]*)/?>(.*?)(?=<a:rPr|\Z)", xml, re.S):
            tf = re.search(r'<a:latin typeface="([^"]+)"', m.group(2))
            if tf:
                combos[(tf.group(1), 'b="1"' in m.group(1), 'i="1"' in m.group(1))] += 1
    return combos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("-o", "--out", help="default: alongside input, '-embedded' suffix")
    ap.add_argument("--report", action="store_true", help="analyse only; write nothing")
    a = ap.parse_args()

    src = Path(a.pptx)
    if not src.exists():
        sys.exit(f"FAIL: {src} not found")

    with zipfile.ZipFile(src) as z:
        combos = used_faces(z)
        names = z.namelist()
        pres = z.read("ppt/presentation.xml").decode("utf-8")
        rels = z.read("ppt/_rels/presentation.xml.rels").decode("utf-8")
        ctypes = z.read("[Content_Types].xml").decode("utf-8")

    if "embeddedFontLst" in pres:
        sys.exit("FAIL: this deck already declares <p:embeddedFontLst>; refusing to double-embed.")

    used_typefaces = sorted({tf for (tf, _b, _i) in combos})

    # --- gaps: a face the deck asks for that the bundle cannot supply -------------------
    gaps = []
    for (tf, b, i), count in sorted(combos.items(), key=lambda kv: -kv[1]):
        variant = "boldItalic" if b and i else "bold" if b else "italic" if i else "regular"
        have = FACE_MAP.get(tf, {})
        if variant not in have:
            gaps.append((tf, variant, count, "regular" in have))

    print("=== faces the deck asks for ===")
    for (tf, b, i), c in sorted(combos.items(), key=lambda kv: -kv[1]):
        flags = "".join(x for x, on in (("B", b), ("I", i)) if on) or "—"
        print(f"  {c:5d} runs  {tf:28s} {flags}")

    if gaps:
        print("\n=== GAPS: asked for, not bundled (will be SYNTHESIZED by the renderer) ===")
        for tf, variant, count, has_reg in gaps:
            note = "a real base face IS embedded, so it synthesizes from the right family" \
                if has_reg else "NOTHING of this family is embedded — falls back entirely"
            print(f"  {count:5d} runs  {tf} [{variant}] — {note}")

    if a.report:
        return

    # --- assemble the embed set, re-checking licence per file ---------------------------
    parts, entries, idx = [], [], 0
    rid_base = max(int(m) for m in re.findall(r'Id="rId(\d+)"', rels)) + 1

    for tf in used_typefaces:
        variants = FACE_MAP.get(tf)
        if not variants:
            print(f"  skip  {tf}: no bundled source at all")
            continue
        frags = []
        for variant, fname in variants.items():
            fp = FONTS / fname
            if not fp.exists():
                sys.exit(f"FAIL: bundled font missing: {fp}")
            ft = fs_type(fp)
            if ft is not None and (ft & 0x000F) == 2:
                sys.exit(f"FAIL: {fname} is fsType=RESTRICTED — embedding is not permitted. "
                         f"Refusing rather than shipping a licence violation.")
            idx += 1
            part = f"ppt/fonts/font{idx}.fntdata"
            rid = f"rId{rid_base + idx - 1}"
            parts.append((part, fp.read_bytes()))
            frags.append(f'<p:{variant} r:id="{rid}"/>')
            entries.append((rid, f"fonts/font{idx}.fntdata"))
        # Child order within CT_EmbeddedFontDataId: regular, bold, italic, boldItalic
        order = {"regular": 0, "bold": 1, "italic": 2, "boldItalic": 3}
        frags.sort(key=lambda s: order[re.match(r"<p:(\w+)", s).group(1)])
        esc = tf.replace("&", "&amp;").replace('"', "&quot;")
        parts_xml = f'<p:embeddedFont><p:font typeface="{esc}"/>{"".join(frags)}</p:embeddedFont>'
        parts.append(("__xml__", parts_xml))

    font_xml = "".join(p[1] for p in parts if p[0] == "__xml__")
    binaries = [(n, b) for n, b in parts if n != "__xml__"]
    if not binaries:
        sys.exit("FAIL: nothing to embed")

    # --- splice presentation.xml at its ONE schema-legal position ----------------------
    anchor = "<p:defaultTextStyle>"
    if anchor not in pres:
        sys.exit("FAIL: could not find <p:defaultTextStyle> — refusing to guess the insert point")
    pres = pres.replace(anchor, f"<p:embeddedFontLst>{font_xml}</p:embeddedFontLst>{anchor}", 1)

    new_rels = "".join(
        f'<Relationship Id="{rid}" Type="{REL_NS}/font" Target="{tgt}"/>' for rid, tgt in entries
    )
    rels = rels.replace("</Relationships>", new_rels + "</Relationships>", 1)

    if 'Extension="fntdata"' not in ctypes:
        # Anchor on the END of the <Types ...> OPEN TAG, not on the first ">" in the file — the
        # first ">" belongs to the XML declaration, and splicing there produces a document with
        # content before the prolog. That exact mistake was made here and caught only because a
        # strict parser (python-pptx/lxml) was in the verification loop; LibreOffice-based QA
        # would very likely have rendered it anyway. Same lesson as the negative-extent bug.
        m = re.search(r"<Types\b[^>]*>", ctypes)
        if not m:
            sys.exit("FAIL: could not find the <Types> element in [Content_Types].xml")
        ctypes = (ctypes[:m.end()]
                  + '<Default Extension="fntdata" ContentType="application/x-fontdata"/>'
                  + ctypes[m.end():])

    out = Path(a.out) if a.out else src.with_name(src.stem + "-embedded.pptx")
    rewritten = {
        "ppt/presentation.xml": pres.encode("utf-8"),
        "ppt/_rels/presentation.xml.rels": rels.encode("utf-8"),
        "[Content_Types].xml": ctypes.encode("utf-8"),
    }
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():           # preserve original part order
            zout.writestr(item, rewritten.get(item.filename, zin.read(item.filename)))
        for name, blob in binaries:
            zout.writestr(name, blob)

    added = sum(len(b) for _n, b in binaries)
    print(f"\nwrote {out}")
    print(f"  embedded {len(binaries)} font part(s) across {len(used_typefaces)} typeface(s), "
          f"+{added/1024:.0f} KB")
    print(f"  size {src.stat().st_size/1024:.0f} KB -> {out.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
