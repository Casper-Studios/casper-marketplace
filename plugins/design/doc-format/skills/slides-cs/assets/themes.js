// themes.js — token objects for the code-native deck skill.
// Layout geometry (layouts.js) is theme-independent; only these tokens swap.
// Two themes today: casper (agency brand) and sphera (approved Sphera corporate navy + teal).
// The Sphera theme is the corporate brand, not the separate cream Casper x Sphera blend.
//
// Colors are pptxgenjs hex WITHOUT the leading '#'. Fonts are family names. We bundle
// STATIC single-weight TTFs whose family name IS the weight ("DM Sans Medium", "Playfair
// Display SemiBold") — LibreOffice resolves these by face string, which it cannot do for a
// variable TTF's named instance. So `bold:true` is used only on the base families; the
// Medium tier and the serif are separate family strings (displayMedium/bodyMedium/serif).
//
// The BASE families are now static too (2026-07-19). `DMSans-Variable.ttf` used to be the only
// DM Sans we shipped, and it declares family "DM Sans 9pt" — so `display: "DM Sans"` + bold
// resolved to NOTHING on a machine without DM Sans installed, and there was no DM Sans Bold in
// the bundle in any form. That is 27 runs: every talking header, the largest text on each slide.
// `scripts/make_static_faces.py` instances the variable source at wght 400/700 into real
// "DM Sans" Regular + Bold faces, so family+bold now resolves by name. Do NOT re-introduce the
// variable file as a shipped face — the near-miss family name is what caused the silent fallback.
//
// Token roles (every theme defines all of them):
//   paper        slide background (the only background)
//   surface      flat tint blocks, comparison "weaker" side, image placeholders
//   ink          primary text, keylines
//   sec          body / subtitle text
//   muted        source notes, page numbers, de-emphasized captions
//   hair         1px hairlines and grids (the only divider)
//   bar          de-emphasized chart marks / neutral bars
//   accent       THE single emphasis, AS A SHAPE: accent bar, hot bars/dots/strokes, fills.
//                NEVER use it as a `color:` (text) value — see accentText.
//   accentText   THE single emphasis, AS TEXT: kickers, hot labels, accent numerals, the
//                manifesto stop. Split out from `accent` because a token cannot serve both
//                jobs: a fill only needs 3:1 against its neighbours, but text needs 4.5:1
//                against paper AND must out-contrast `muted`, or emphasis INVERTS (the
//                de-emphasised label out-reads the highlighted one). Casper's accent is dark
//                enough to do both (7.32:1); sphera's brand teal is not (2.06:1), which went
//                unnoticed for 23 layouts because it renders correctly on the theme it was
//                authored in. Scripts/check_tokens.sh gates the rule.
//   accentDark   depth / hover / pressed variant of accent
//   accentSubtle soft callout fills tinted from accent
//   band         dark fill that carries WHITE text (takeaway band, hot circles). May
//                differ from accent when the accent is too light for white text.
//   secondary    second data series only (never a second emphasis)
//   display      header/title font family (headers use bold:true)
//   body         body/label font family
//   cover        image-backed cover/closing treatment: { bg, align, eyebrow, ink }
//                bg = filename in assets/covers/, align = "left"|"right" (right clears a
//                baked-in brand mark), eyebrow/ink = text colors readable on the image
//   cat          category palette for multi-hue diagrams (Mode 2). Fixed jobs:
//                data, models, evaluation, risks, outputs, milestones, + 2 reserve.
//                Each entry is { t: textHex, b: bgTintHex } — flat tint fill, no
//                outline, label inside in the category text color.

const casper = {
  name: "casper",
  paper: "FFFFFF",
  surface: "FAFAFA",
  ink: "1E293B",       // deck-tradition slate ink (matches shipped Casper decks)
  sec: "475569",
  muted: "737373",     // DS neutral-500
  hair: "E5E5E5",      // DS neutral-200
  bar: "CBD5E1",       // de-emphasized chart marks (slate-300)
  accent: "5900FF",    // DS brand-500 — canonical, three-way consensus
  accentText: "5900FF",// same value: brand purple already clears 7.32:1 on paper as text
  accentDark: "4700CC",// DS brand-600
  accentSubtle: "EEE5FF", // DS brand-50
  quoteField: "FFFFFF",   // pull-quote background — paper on casper (accentSubtle read purple-on-purple)
  band: "5900FF",      // brand purple is dark enough to carry white text
  secondary: "14B8A6", // DS teal (data series 2 only)
  display: "DM Sans",
  displayMedium: "DM Sans Medium",   // mid weight for the quiet tier (step names, chips)
  body: "Inter",
  bodyMedium: "Inter Medium",        // table cells, milestone titles, column numbers
  serif: "Playfair Display SemiBold",       // editorial statement layouts only (manifesto, quote)
  serifItalic: "Playfair Display Italic",   // pull-quote
  cover: { bg: "casper-cover.png", align: "left", eyebrow: "FFFFFF", ink: "FFFFFF" },
  cat: {  // b tints deepened ~2x so diagrams carry ink weight instead of washing out on white
    data:       { t: "4700CC", b: "DDCBFF" },
    models:     { t: "B45309", b: "FADFBB" },
    evaluation: { t: "0F766E", b: "C6EBE3" },
    risks:      { t: "BE123C", b: "F8CFD8" },
    outputs:    { t: "0369A1", b: "C7E4F6" },
    milestones: { t: "4D7C0F", b: "DAE9BC" },
    reserve1:   { t: "92400E", b: "E9DAC6" },
    reserve2:   { t: "475569", b: "D3DCE7" },
  },
};

// Sphera corporate palette (navy primary + teal accent), matching approved brand materials.
// Navy is the brand text color (ink); teal is the single-emphasis mark
// that pops against neutral context; navy `band` carries white text. DM Sans (not Arial).
const sphera = {
  name: "sphera",
  paper: "FFFFFF",
  surface: "F5F5F5",   // n100 — light tint blocks
  ink: "1A1F5C",       // canonical Sphera deep navy — headers / primary text
  sec: "525252",       // n700 body
  muted: "737373",     // n500 footnotes / page numbers
  hair: "E5E5E5",      // n200
  bar: "D4D4D4",       // n300 de-emphasized chart marks
  accent: "22C8C9",    // canonical Sphera teal — single-emphasis SHAPES only (hot bar, tick, rules)
  // Text-safe tier of the SAME brand teal (hue held at ~180°, only value darkened) — not a new
  // brand color. Chosen as the LIGHTEST hue-true value that clears all three bars at once:
  // 5.73:1 on paper (AA), 4.68:1 on the quoteField tint (the worst instance, was 1.69:1), and
  // comfortably above muted's 4.74:1 so the argued mark always out-reads the de-emphasised one.
  // accentDark (3.40:1) and cat.outputs 0A8F8F (3.93:1) were both tried and are too light.
  accentText: "0A7272",
  accentDark: "0A9B9B",
  accentSubtle: "E5E8F2", // light navy tint (callout fills)
  quoteField: "E5E8F2",   // pull-quote background — sphera's calm navy tint reads fine, kept
  band: "1A1F5C",      // navy fill behind white text (takeaway band, hot circles)
  secondary: "05A97F", // Sphera green accent3 (second series)
  display: "DM Sans",
  displayMedium: "DM Sans Medium",
  body: "Inter",
  bodyMedium: "Inter Medium",
  serif: "Playfair Display SemiBold",       // editorial statement layouts (used sparingly; sphera is corporate)
  serifItalic: "Playfair Display Italic",
  cover: { bg: "sphera-cover.png", align: "right", eyebrow: "22C8C9", ink: "FFFFFF" },
  cat: {  // b tints deepened ~2x for ink weight
    data:       { t: "1A1F5C", b: "C9D0E8" }, // canonical navy
    models:     { t: "0187B9", b: "A7D3EC" }, // blueAlt (deepened — was washing out on white)
    evaluation: { t: "05A97F", b: "A9DEC9" }, // green (deepened)
    risks:      { t: "C03628", b: "F2CCC5" }, // red
    outputs:    { t: "0A8F8F", b: "C0EAEA" }, // teal-dark
    milestones: { t: "E17448", b: "F6D6C4" }, // orange
    reserve1:   { t: "525252", b: "DADADA" },
    reserve2:   { t: "737373", b: "E2E2E2" },
  },
};

// Ordered category list for diagrams that assign colors by position
// (architecture components, timeline lanes, roadmap phases).
const CAT_ORDER = ["data", "models", "evaluation", "risks", "outputs", "milestones", "reserve1", "reserve2"];

const THEMES = { casper, sphera };

function getTheme(name) {
  const t = THEMES[name];
  if (!t) throw new Error(`Unknown theme "${name}". Available: ${Object.keys(THEMES).join(", ")}`);
  return t;
}

module.exports = { THEMES, getTheme, CAT_ORDER };
