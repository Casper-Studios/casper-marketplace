# Bundled fonts — attribution and licensing

The skill bundles its typefaces so a deck renders identically on any machine. All three families
are licensed under the **SIL Open Font License 1.1 (OFL-1.1)**, which permits bundling and
redistribution, and all faces report `fsType = 0x0000` (Installable Embedding) — so embedding
them inside a generated `.pptx` via `scripts/embed_fonts.py` is permitted, not merely tolerated.

| File | Family | Subfamily | Weight | Upstream |
|---|---|---|---|---|
| `DMSans-Regular.ttf` | DM Sans | Regular | 400 | Google Fonts — Colophon Foundry / Indian Type Foundry |
| `DMSans-Bold.ttf` | DM Sans | Bold | 700 | as above |
| `DMSans-Medium.ttf` | DM Sans Medium | Regular | 500 | as above |
| `Inter-Regular.ttf` | Inter | Regular | 400 | rsms/inter |
| `Inter-Bold.ttf` | Inter | Bold | 700 | as above |
| `Inter-Medium.ttf` | Inter Medium | Regular | 500 | as above |
| `PlayfairDisplay-SemiBold.ttf` | Playfair Display SemiBold | Regular | 600 | Claus Eggers Sørensen |
| `PlayfairDisplay-MediumItalic.ttf` | Playfair Display Italic | Italic | 500 | as above |

## Why some families are renamed

`DM Sans Medium`, `Inter Medium`, `Playfair Display SemiBold` and `Playfair Display Italic` are
shipped as **static single-weight faces whose family name IS the weight**. LibreOffice resolves a
face by its family string and cannot select a variable font's named instance, so a static named
this way is the only reliable route to a mid-weight during PDF export. `themes.js` documents the
same rule. Google Fonts uses this exact convention for non-RIBBI weights, so these family strings
are upstream naming, not a local rename.

## Reserved Font Names — read before renaming anything

Checked against each font's own `name` table rather than assumed:

| Family | Reserved Font Name? | Modified here? |
|---|---|---|
| DM Sans | **No** | **Yes** — instanced at wght 400/700 |
| Inter | **No** | No |
| Playfair Display | **YES** — `"Playfair Display"` | No (upstream statics, vendor `FTH`, v1.203) |

OFL-1.1 §3 forbids a **Modified Version** from using a Reserved Font Name without written
permission from the copyright holder. The two rows above interact, so state the consequence
plainly:

- **DM Sans carries no RFN, which is what makes the instancing legal.** `DMSans-Regular.ttf` and
  `DMSans-Bold.ttf` are modified versions that keep the family name "DM Sans". Permitted only
  because there is no reserved name to infringe. Had DM Sans carried one, those two files would
  have had to ship under a different family — and `themes.js` would have needed a new token.
- **Playfair Display DOES carry an RFN, so its files must stay unmodified.** Metadata indicates
  they are untouched upstream releases. **Do not instance, subset, or re-name them** the way
  DM Sans was: any modified Playfair keeping "Playfair Display" in its family string violates §3.
  If a Playfair variant is ever needed, rename the family to drop the reserved words first.

This is a documentation note by a non-lawyer, from font metadata. Flag it in the PR so someone
with authority over Casper's licensing signs off rather than inheriting it silently.

`DMSans-Regular.ttf` and `DMSans-Bold.ttf` are **instanced** from the upstream variable font at
wght 400 and 700 by `scripts/make_static_faces.py`. The variable source is kept at `_src/` for
regeneration and is deliberately **not shipped as a face** — it declares family `"DM Sans 9pt"`,
a near-miss name that caused `display: "DM Sans"` to silently fall back to Calibri on any machine
without DM Sans separately installed. Instancing is a modification under OFL-1.1 and is permitted
under the same terms.

## License texts — present

OFL-1.1 §2 requires the full license to accompany any redistribution of the fonts, in original or
modified form. All three ship here:

- `OFL-DMSans.txt`
- `OFL-Inter.txt`
- `OFL-PlayfairDisplay.txt`

**Provenance, so this is auditable.** Nothing was written from memory and nothing was downloaded.
The SIL OFL 1.1 body is a fixed document, byte-identical across every OFL font — verified: the
three files hash identically below their copyright lines. It was copied verbatim from an `OFL.txt`
already present on the build machine. Each **copyright and Reserved Font Name line** was read from
that family's own `name` table (nameID 0), so it is the string the foundry shipped rather than a
paraphrase — which also means the Playfair RFN above was discovered, not recalled.
