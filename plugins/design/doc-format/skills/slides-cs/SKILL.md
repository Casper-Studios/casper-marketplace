---
name: slides-cs
description: Build a branded, editable PowerPoint deck (.pptx + PDF) from a brief or an outline, in the Casper or Sphera brand theme, with zero image generation — the deck is authored as data and rendered by code, so it stays fully editable in PowerPoint and Google Slides. Use this whenever someone wants a slide deck, a client deck, a proposal deck, a readout, a pitch, a QBR, a one-pager as slides, or wants to turn notes / analysis / a doc into slides for Casper or a Casper client — even if they don't say "slides-cs" or name a theme. Also use it to restyle, re-skin, or edit a deck previously built with this skill. Not for infographics or single marketing images (that is /slides).
---

# slides-cs — code-native branded decks

Turn a brief or an outline into an editable `.pptx` (+ a PDF for review). Every slide is written as
plain data in a `content.js` file; a shared engine renders it against a brand theme and a library of
22 layouts. No image generation — chrome is drawn by code, so decks stay editable downstream and re-skin
between brands with a one-word theme change.

The design lives in the skill (`assets/themes.js`, `assets/layouts.js`, `scripts/render.js`). The words
live with the deck (`content.js`). **You only ever author `content.js`.** Never edit the design files to
make a single deck — that is the whole point of the split.

## STOP — read these first (in order)

Do NOT write any `content.js` or run a build until you have read, this session:

1. `assets/themes.js` — the two themes and every token role (what `accent`, `band`, `cat`, `serif`, `cover` mean).
2. `assets/layouts.js` — the 22 layout functions and, in each function's header comment, the exact
   `content:` slot names it reads. This is the schema. There is no other spec for a layout's fields.
3. `references/layouts.md` — when to use each layout, per-slot text budgets, and the writing contract.
4. `assets/example-content.js` — a 22-slide worked example that uses every layout once. Clone its shape.

If you skip these you will guess slot names and the build will throw `unknown layout` or silently drop content.

## Two modes

Detect the mode before doing anything else. It changes whether you may restructure the user's content.

| Mode | Trigger | What you do |
|---|---|---|
| **Create** (default) | A topic, a brief, rough notes, "make a deck about X" | Author the narrative: write talking headers, choose layouts, run the outline gate below. |
| **Format** | The user hands over finished content / their own outline / a doc to "just turn into slides" | Preserve their structure and wording. Map their sections onto layouts 1:1. Do **not** re-order, merge, split, or rewrite. Skip the outline gate — build directly. |

**Format mode is a hard boundary, not a preference.** Do not load or apply the narrative/talking-header
rewriting guidance in `references/layouts.md` when in Format mode — reading it will make you silently
restructure the user's content, which is the opposite of what Format mode is for. Skin their words; don't rewrite them.

## On invocation

First print a short "what happens next" card so a first-time user knows the shape of the run:

> **slides-cs** — I'll turn this into an editable `.pptx` + PDF.
> 1. Draft an outline you approve as a visual storyboard (a card per slide) — Create mode only.
> 2. Write it to a `content.js` data file.
> 3. Render the `.pptx`, export a PDF, and review the pages.
> 4. Deliver both, with speaker notes on every slide.

Then ask **at most 3 questions, and only for what the brief doesn't already answer** (someone who brought
content should not be interrogated):

1. **Theme** — casper or sphera? Skip if the client/context makes it obvious (a Sphera deck is sphera).
2. **Purpose** — client deliverable read async, or a live presentation? **Default: client deliverable.**
   This sets the text budget: a reading deck carries denser slide bodies with lighter notes; a presentation
   deck keeps slides sparse and moves the prose into speaker notes.
3. **Scope** — roughly how many slides, or how long is the meeting? (Create mode with no source only.)

If a slot is left after theme + scope, you may ask about speaker notes; otherwise **include them by default**
(hook, 2–4 points, transition on every slide, both purposes). **Never ask about output format** — it is always
`.pptx`; Google-Slides editability is guaranteed by the shape-based charts, and the deck gets dropped into
Drive after review (a manual step — this skill does not upload).

**Thin brief? Co-develop the outline before drafting.** In Create mode, if the input is a one-liner or vague,
do not invent a whole deck from a guess. First walk the user through what to cover: propose the 4–6 beats you
would build the deck around, in a sentence each, and ask them to confirm, add, or redirect. Only then draft the
full outline. **Skip this when the brief is already specific enough to outline directly** (a detailed doc, a
clear list of points), and always in Format mode — there the user's own structure is the outline, so co-developing
it would be overriding them.

## First run (once per machine) — YOU run this, the user never should

**Before the first render on any machine, check whether `node_modules/` exists in the skill folder. If it
does not, say so and offer to install** — one line, then run it on a yes:

> First run on this machine — I need to install one package (`pptxgenjs`, ~10 s, one-time). OK?

```
cd <this skill folder> && npm install
```

`node_modules/` is not committed, so a fresh install of the skill has no dependencies and the first render
fails. **This is the only setup step** — verified in a clean-room checkout, it is the single thing standing
between a fresh install and a working deck. The user should never have to discover it: this skill is always
driven by an agent, so the agent absorbs the setup. `render.js` printing the command is the backstop for
someone running it by hand, not the intended path.

Everything else the skill needs already ships with it: fonts, layouts, themes, cover art. Two optional extras,
neither needed to produce a `.pptx` — **LibreOffice** for `render_pdf.sh` (PDF + page images for review), and
**python3** for font embedding (present on macOS by default; if missing, the deck still builds and warns).

## Building a deck

Output folder: `slides/YYMMDD-slug/` (or the caller's folder). One deck = one folder. For a recurring client
deck (for example, a weekly programme readout), keep ONE living deck and append/hide slides in its `content.js` rather
than spawning a new folder each time.

1. **Outline** (`outline.js`) — author the plan as `{ theme, title, slides: [{ header, layout, evidence }] }`,
   one entry per slide: the talking header (a full-sentence finding), the layout name, and the evidence it
   rests on. This is the plan, NOT `content.js` — no slot data yet.
2. **Outline gate** (Create mode only) — render the plan for a visual OK before building:
   `node scripts/render_outline.js outline.js` produces `outline.html` (a brand-coloured storyboard, one card
   per slide showing its layout and header) and `outline.md` (the same plan as a list) from that one file.
   **Share the storyboard and get an OK before writing any `content.js`.** In Format mode, skip the gate.
   **Run the fit test here, per slide, before any code exists:** does the layout's designed job match this
   slide's job? Two checks catch most of it — are the items genuinely parallel (say each slot aloud as one
   sentence stem), and can every slot be filled with real content rather than a paraphrase of the header? A
   slide failing either is on rung 2 or 3 below. The storyboard flags a layout used more than once (an amber
   "repeated" tag) — a cue to vary the deck before it reads template-stamped.
3. **`content.js`** — author the data: `{ theme, title, slides: [ { layout, ...slots, notes } ] }`. Each slide
   names a layout from `layouts.js` and fills that layout's documented slots. Add `notes` to every slide.
   This is the only file you write. See `example-content.js` for the exact shape.
   Optional deck-level keys: `confidential: true` (renders CONFIDENTIAL in every content-slide footer; pass a
   string for a custom marker) and `customLayouts` (see below).

### Templates are ideas to work off, not molds

The 22 layouts are a starting catalog, and most slides genuinely fit one. But **forcing content into the
nearest layout is a content bug**, and it is the failure this section exists to prevent. Three rungs:

1. **Template as-is** — the layout's job matches the content's job. The default.
2. **Adapt the nearest** — swap the exhibit, **drop a slot rather than pad it**, borrow an element from a
   second layout. Still house language.
3. **Compose from house primitives** — nothing is near. Export `customLayouts` from `content.js` (a map of
   deck-local layout functions, merged over the registry for that deck only) and build from the shared
   pieces, which `layouts.js` already exports for exactly this:

   ```js
   const { helpers, W, H, M } = require("<skill>/assets/layouts.js");
   // helpers: slide, headerBlock, sourceNote, clamp, luminance, onFill
   customLayouts: {
     myLayout(pres, T, ctx, c) {
       const s = helpers.slide(pres, T, ctx);        // ALWAYS start here
       helpers.headerBlock(s, T, c);                 // kicker + talking header + sub
       /* ...your geometry, using T.* tokens only... */
       helpers.sourceNote(s, T, c.source);
       s.addNotes(c.notes || "");
       return s;
     },
   }
   ```

   **Start from `helpers.slide()`, never `pres.addSlide()`.** It draws the accent tick, the footer, the
   CONFIDENTIAL marker, and — critically — increments `ctx.pageNo`. A bespoke slide that bypasses it loses
   its own page number *and* misnumbers every slide after it. Verified: a custom layout built on raw
   `addSlide()` rendered with no footer at all.

**Hard floor under all three: no new colours, no new fonts, no new chrome, no freeform spacing.**
Improvisation recombines the design system; it never exits it. A bespoke slide must look like it could have
been the 23rd layout — that is the test, and it is what keeps brand and balance intact while still letting a
slide be what it needs to be. Rung 3 is rare; reach for it only after naming the layout you rejected and why.

**Two traps worth naming.** Never fill a slot by paraphrasing the header — that is padding to satisfy a
template, and it reads as generated. And what usually makes a deck feel template-y is not wrong routing but
**under-filled capacity**: an agenda holding 4 of its 7 rows, a swimlane with empty cells. The remedy is
capacity-matching (pick the lighter layout, or accept the whitespace deliberately), never adding words.

Signals, worked examples, and the recurring hybrids: `references/layouts.md` § When no layout fits.
4. **Render** — `node scripts/render.js <content.js> <out.pptx>` (run from the skill dir, or use an absolute
   content path — `render.js` resolves content against the cwd and assets against itself). The bundled brand
   fonts are **embedded automatically**, so the deck renders correctly for a recipient who does not have them
   installed. Embedding fails soft: if it cannot run you still get the deck, plus a warning naming the cause.
5. **Validate the package** — `bash scripts/check_pptx.sh <out.pptx>`. Catches negative extents (PowerPoint
   refuses to open those and offers only to "repair", which flattens every sloped line) and reports whether
   fonts embedded. **A PDF check is not a substitute** — LibreOffice silently normalises XML that PowerPoint
   rejects, so a perfect-looking PDF has come from an unopenable `.pptx` before.
6. **PDF + pages** — `bash scripts/render_pdf.sh <out.pptx>` → PDF + per-page JPEGs for review. (LibreOffice
   needs the sandbox OFF; see harness notes.)
7. **Review loop** — below.
8. **Deliver** — the `.pptx` and the `.pdf`, dual-linked, with a note that speaker notes are on every slide.

## The writing contract (Create mode)

These are non-negotiable; they are what make a deck read on its own. Full detail + per-slot budgets in
`references/layouts.md`.

- **Talking headers, written first.** Every content header is a full-sentence *finding*, not a label
  ("Churn fell 40% after the redesign", not "Churn"). ≤ ~22 words, ≤ 2 lines. Someone reading only the
  headers in order should get the whole argument. Write all headers before choosing a single layout.
- **The subtitle adds a second message** (the cause, caveat, or consequence). It never restates the header.
- **No explanatory clause after a comma in a header.** `<Topic> — <label>, <clause re-explaining the label>`
  ("Tool status — four pillars, what is real today") is this skill's loudest AI tell: every instance looks
  defensible alone, and four per deck reads as machine-written. Delete everything after the comma — if the
  header still names the thing, the clause was decoration; if it carried real information, move it to `sub`.
  A comma inside a genuine finding sentence is fine; the tell is the appositive.
- **One emphasis per slide.** Exactly one accent-colored mark per Mode-1 slide (the number that moved, the
  argued step, the proving cell). Everything else is neutral. The layouts enforce this via a `hot` flag —
  set it on at most one item.
- **Sources are mandatory on any data slide.** Fill `source` (a bottom-left footnote) whenever a slide shows
  a number. A terminal `sources` slide collects the full list. Missing sources is a bug, not a style choice.
  Mark uncertainty (`~`, "estimated", "illustrative"); never invent figures.
- **Takeaway band: at most one per slide, ~one per three slides across the deck.** The band is the strongest
  device and the most repetitive-looking if overused. A 10-slide deck lands 3–4, not 10.
- **Don't fight the clamps.** Layouts clamp lists to what the geometry holds (e.g. 3 columns, 3 KPIs, 6 bars).
  If you have more items, that's a signal to split the slide, not to cram — extra items are dropped and the
  build prints a `clamped N → M ... DROPPED` warning. Treat that warning as a content bug to fix, not noise.

## Themes

Two themes, same geometry, different tokens (`assets/themes.js`):

- **casper** — white paper, slate ink, brand purple `#5900FF` as the single emphasis, DM Sans headers. The
  agency's own deck brand.
- **sphera** — the approved Sphera corporate look: navy `#1A1F5C` ink, teal `#22C8C9`
  emphasis, navy `band` behind white text, DM Sans (an upgrade over the decks' Arial). Its cover is the real
  Sphera navy title slide. This is NOT the cream "Casper × Sphera" blend — that's a separate deferred variant.

**Type system (shared, three tiers).** Both themes carry the same font roles in `themes.js`: a sans base
(`display` DM Sans + `body` Inter, bold via family+bold), a quiet **Medium** tier (`displayMedium`,
`bodyMedium`) for step names, chips, table cells, and column numbers, and a **serif** tier (`serif` Playfair
Display SemiBold, `serifItalic` for pull-quotes) used only on the editorial statement layouts (`manifesto`,
`quote`) and a few oversized numerals. These resolve as STATIC named faces because LibreOffice cannot pull a
named instance from a variable TTF — run `scripts/setup-fonts.sh` once so all three families are installed.

Switch by setting `theme` in `content.js`. Covers are fixed per theme and applied automatically (the cover
title is a short deck *name*, not a talking-header sentence — findings live on the content slides). **Never
regenerate a cover** — each theme's cover is the brand's real title slide, not an AI image.

## Client-facing guardrails

Bake these into the content for every external deck: do not expose internal workflow names, automation
percentages, or coverage-completeness claims. Use "helps / supports" framing, and mark inferred asks
"(to confirm)". Brand themes may be named; client workstreams and internal programme labels may not.

## Review loop

Cheap checks first, expensive last, capped at 3 cycles.

0. **Scripted (free, every build):** clamp warnings from the render; `bash scripts/check_content.sh` diffs the
   approved `outline.md` headers against the `content.js` strings and spot-checks the rendered PDF text.
1. **Cycle 1:** one review agent per slide (its page JPEG + its `content.js` entry + `references/review-rubric.md`,
   which carries the exact expected coordinates so header-drift is judgeable), plus one consistency agent across
   all pages (headers argue in sequence, layout variety, token consistency, takeaway ratio, page numbers).
   **Above ~10 slides, batch 3–4 slides per agent** rather than one-each.
2. **Cycles 2–3:** a single cold reviewer on the changed slides only.
3. Apply fixes to **`content.js` only** — never the design files. Re-render. Stop at 3 cycles.

## Harness adaptation

The shared skill is the source of truth for both Claude Code and Codex. The data contract, scripts, assets,
validation gates, and review rubric are identical in either harness. Only orchestration adapts:

- **Claude Code:** use native parallel review subagents when available and follow the active Claude runtime
  policy for model choice and permissions.
- **Codex:** use native collaboration subagents when available and follow the active Codex runtime policy for
  model choice and reasoning effort.
- **No subagent support:** run the same rubric sequentially. Do not skip the review or change the build files.

The shared package must not hard-code a model name or one harness's tool syntax. Thin local wrappers may add
those details without changing this file.

## Environment notes

- **LibreOffice (`soffice`) needs the sandbox OFF** to write its profile; the render silently produces nothing
  otherwise. `pdftoppm` runs fine in-sandbox. `pptxgenjs` installs with `npm install` (sandbox off for the cert
  writes); once `node_modules/` exists, rendering runs in-sandbox.
- The engine never needs editing to build a deck. If a layout genuinely can't express something, that's a
  skill-maintenance change (edit `layouts.js` deliberately, outside any deck), not a per-deck edit.
