#!/usr/bin/env node
// render.js — the deck engine. Wires a content module (pure data) to a theme and the
// layout library, emits a .pptx. This is skill infrastructure; it is not edited per deck.
//
// Usage:
//   node render.js <content.js> [out.pptx]
//
// The per-deck source of truth is content.js (data only). Everything visual lives in
// the skill's themes.js / layouts.js, so a deck rebuild never touches design code.

const path = require("path");
const fs = require("fs");
const { getTheme } = require("../assets/themes.js");
const { layouts } = require("../assets/layouts.js");

function buildDeck(content, outPath) {
  // `node_modules/` is gitignored, so a FRESH INSTALL of this skill has no dependencies and the
  // bare require fails with a stack trace that does not say what to do. Verified in a clean-room
  // checkout with no ancestor node_modules — the missing dependency is the ONLY thing between a
  // teammate and a working deck, so the message has to carry the fix.
  let pptxgen;
  try {
    pptxgen = require("pptxgenjs");
  } catch (err) {
    if (err.code !== "MODULE_NOT_FOUND") throw err;
    const dir = path.resolve(__dirname, "..");
    throw new Error(
      `dependencies are not installed yet.\n\n` +
      `  cd "${dir}" && npm install\n\n` +
      `  One-time, ~10 seconds. Installs pptxgenjs, the only dependency. Everything else the\n` +
      `  skill needs (fonts, layouts, themes) already ships with it.`
    );
  }
  // Theme is MANDATORY — a silent default here is exactly the bug the old pipeline had
  // (decks rendering in the wrong brand while building clean). Fail loud instead.
  if (!content.theme) {
    throw new Error(`content.theme is required ("casper" or "sphera") — refusing to guess a brand.`);
  }
  const T = getTheme(content.theme);
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "Casper Studios";
  pres.title = content.title || "Deck";
  // Overwrite the generator's fingerprint. Left at defaults, File > Info > Properties shows a
  // client `dc:subject` of "PptxGenJS Presentation" and `Company = PptxGenJS`.
  pres.company = "Casper Studios";
  pres.subject = content.title || "Deck";
  // Brand the THEME, not just the runs. Every text box the engine draws sets an explicit font and
  // colour, so existing text was always right — but theme1.xml shipped stock ("Office Theme",
  // Calibri Light / Calibri), which is what a NEW text box the client adds inherits. A deck whose
  // branding lives only in per-run overrides is branded until someone edits it.
  pres.theme = { headFontFace: T.display, bodyFontFace: T.body };

  // `confidential` is deck-level: true renders "CONFIDENTIAL" in the footer of every content
  // slide, or pass a string for a custom marker ("INTERNAL", "DRAFT — NOT FOR CIRCULATION").
  const ctx = { pageNo: 0, confidential: content.confidential || false };
  // Living-deck support: slides marked `hidden: true` stay in content.js as history but
  // are skipped at build time (page numbers renumber over the visible set).
  const all = content.slides || [];
  const slides = all.filter((sl) => !sl.hidden);
  const hiddenCount = all.length - slides.length;
  // Rung 3 of the improvisation ladder (references/layouts.md § When no layout fits). A deck may
  // export `customLayouts` — deck-local functions merged OVER the registry for this deck only, so
  // a one-off never becomes everyone's maintenance and the shared 22 stay untouched.
  //
  // This exists because the alternative is worse: without it, content that no layout fits gets
  // force-fitted into the nearest one (padding slots to satisfy the template), or hand-injected by
  // a side script afterwards — which is what actually happened on a real client deck. Both are
  // invisible to the review loop. A custom layout is at least a first-class slide.
  //
  // It is NOT a licence to freestyle: the hard floor is theme tokens only — no new colours, fonts,
  // chrome, or freeform spacing. A bespoke slide must look like it could have been the 23rd layout.
  const custom = content.customLayouts || {};
  const registry = { ...layouts, ...custom };
  const overridden = Object.keys(custom).filter((k) => k in layouts);
  if (overridden.length) {
    console.warn(`       NOTE: customLayouts overrides shared layout(s): ${overridden.join(", ")}.`);
    console.warn("       Deck-local only, but a shared layout that needs changing should be fixed in");
    console.warn("       assets/layouts.js instead, so every deck gets the improvement.");
  }
  slides.forEach((sl, i) => {
    const fn = registry[sl.layout];
    if (!fn) {
      const known = Object.keys(registry).join(", ");
      throw new Error(`Slide ${i + 1}: unknown layout "${sl.layout}". Known layouts: ${known}`);
    }
    fn(pres, T, ctx, sl);
  });

  return pres.writeFile({ fileName: outPath }).then(() => {
    const hiddenNote = hiddenCount ? ` (${hiddenCount} hidden slide${hiddenCount > 1 ? "s" : ""} skipped)` : "";
    console.log(`Wrote ${outPath} — ${slides.length} slides, theme "${content.theme}"${hiddenNote}.`);
    embedFonts(outPath);
    return outPath;
  });
}

// Embed the bundled brand faces into the package. pptxgenjs cannot emit <p:embeddedFontLst>, so
// this shells out to the Python post-processor. Confirmed 2026-07-19: PowerPoint opens an
// embedded deck with no repair prompt.
//
// WHY THIS IS ON BY DEFAULT: the skill's core promise is that a deck renders identically on any
// machine, and without embedding a deck carries only font NAMES — four of which are faces no
// standard install provides, because the bundle deliberately renames static weights so
// LibreOffice can resolve them. A teammate without the fonts silently gets Calibri.
//
// WHY IT FAILS SOFT: a font problem must never cost you the deck. Any failure here warns and
// leaves the un-embedded .pptx in place, which is exactly what shipped for every prior version.
function embedFonts(outPath) {
  const { execFileSync } = require("child_process");
  const script = path.join(__dirname, "embed_fonts.py");
  if (!fs.existsSync(script)) return;
  const tmp = outPath.replace(/\.pptx$/, ".embed.tmp.pptx");
  try {
    execFileSync("python3", [script, outPath, "-o", tmp], { stdio: "pipe" });
    fs.renameSync(tmp, outPath);       // atomic swap — never a half-written deck at outPath
    console.log("       fonts embedded (opens on machines without the brand fonts installed).");
  } catch (err) {
    if (fs.existsSync(tmp)) fs.unlinkSync(tmp);
    const why = (err.stderr && err.stderr.toString().trim().split("\n").pop()) || err.message;
    console.warn(`       NOTE: font embedding skipped — ${why}`);
    console.warn("       The deck is fine, but will fall back to system fonts on a machine");
    console.warn("       without the brand faces installed. Run scripts/setup-fonts.sh there.");
  }
}

if (require.main === module) {
  const contentArg = process.argv[2];
  const outArg = process.argv[3];
  if (!contentArg) {
    console.error("Usage: node render.js <content.js> [out.pptx]");
    process.exit(1);
  }
  const contentPath = path.resolve(process.cwd(), contentArg);
  const content = require(contentPath);
  const out = outArg
    ? path.resolve(process.cwd(), outArg)
    : contentPath.replace(/\.js$/, ".pptx");
  try {
    buildDeck(content, out).catch((err) => {
      console.error("Build failed:", err.message);
      process.exit(1);
    });
  } catch (err) {
    console.error("Build failed:", err.message);
    process.exit(1);
  }
}

module.exports = { buildDeck };
