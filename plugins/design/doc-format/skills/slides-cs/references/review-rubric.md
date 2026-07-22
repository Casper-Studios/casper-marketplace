# Review rubric

What a review agent checks on a rendered deck. Two roles: a **per-slide reviewer** (one slide's page
JPEG + its `content.js` entry) and a **consistency reviewer** (all page JPEGs at once). Both are cold —
they never saw the prompts or the source data. Report each issue with slide number, what's wrong, and a
one-line fix to `content.js` (never the design files).

Coordinates below are the layout's fixed anchors (from `../assets/layouts.js`); use them to judge whether
something has drifted or overflowed. Canvas is 13.333 × 7.5 in; margin `M = 0.85`.

## Fixed chrome (every content slide) — flag any deviation

- **Accent corner tick** — a short accent bar in the top-left corner only (x 0, y 0, w ~1.35, h ~0.09), *not*
  a full-width band. Present on standard content slides; absent by design on cover, closing, and the two serif
  statement slides (`manifesto`, `quote`). A tick that stretches across the page would be a regression.
- **Kicker** (if present): top-left at x 0.85, y ~0.55, in `accentText`, ALL CAPS, letter-spaced. On sphera
  that is a **darker teal (#0A7272) than the corner tick** — this is correct, not an off-palette stray. The
  accent splits into two tiers: `accent` for shapes (ticks, bars, hot marks) and `accentText` for text, which
  has to clear 4.5:1 on paper. Flagging the darker text teal as a mismatch is a false positive.
- **Header** starts at x 0.85 (y ~0.55 with no kicker, ~0.93 with one). Must not run past 2 lines or collide
  with the content block below. The **earliest** content anchor is ~y **2.72** (`architecture`); most layouts
  start 2.80–2.95. Reviewing against the older ~3.35 figure passes headers that actually collide.
- **Subtitle** (if present) sits directly under the header, in the secondary text color, 1 line.
- **Page number** bottom-right (x ~11.48, y ~7.08), muted. Numbers run in slide order, skipping cover/closing
  and any `hidden` slide. A gap or repeat is a bug. (The `quote` slide also drops the footer/page number by design.)
- **Source note** (data slides) bottom-left (x 0.85, y ~7.08), muted, prefixed "Source:".

## Per-slide checks

Run every applicable item; most map to a single `content.js` field.

1. **Talking header, not a label.** The header is a full-sentence finding ("Churn fell 40%…"), not a topic
   word ("Churn"). A label-style header is the most common miss → rewrite as a finding.
2. **Header fits.** No overflow past 2 lines, no collision with the body. Over-budget → trim.
3. **Subtitle earns its place.** It adds a second message (cause/caveat/consequence), not a restatement of
   the header. If it echoes the header, cut or replace it.
4. **No trailing appositive in the header.** Flag any header of the shape `<Topic> — <label>, <clause that
   re-explains the label>` ("Tool status — four pillars, what is real today"; "The road to launch, and what
   we need from you"). Test: delete everything after the comma — if the header still names the thing, the
   clause is decoration and gets cut; if it carried information, it moves to `sub`. A comma inside a real
   finding sentence is fine — the tell is the appositive. **Also count it deck-wide** (see Consistency): each
   instance passes on its own, so only the frequency exposes it.
5. **One emphasis only.** Exactly one accent-colored mark on the slide (one `hot`, one accent stop, one
   accent bar). Zero accents (nothing stands out) or two+ (competing) both fail. One *object* may carry the
   mark in both tiers — an accent-shape plus its `accentText` label (the gantt milestone, the roadmap hot
   phase) is **one** emphasis, not two.
   5b. **Emphasis must not invert.** Read the slide and ask which mark your eye lands on first. If a
   de-emphasised label out-reads the highlighted one, that is a failure even when every token is "correct" —
   it is what a too-light accent looks like, and it shipped undetected across every sphera slide because the
   layouts were authored on casper, where the same token happens to be dark. `bash scripts/check_tokens.sh`
   gates the token half; this check covers the half a script cannot see.
6. **No overflow / collision.** No text clipped by a box edge, no two elements overlapping, no bar or card
   past the frame. (The comparison "stronger" panel and the sources list are the historical overflow spots.)
7. **Source present on data.** Any number on the slide → a `source` footnote exists. Missing = fail.
8. **Clamp not silently hit.** If the build logged a `clamped N → M … DROPPED` warning for this slide, content
   was lost — split the slide. (The reviewer won't see the dropped items on the page; check the build log.)
9. **Legible at size.** All text readable at display size; no font shrunk to fit (a sign of over-budget content).
10. **Diagrams are monochrome unless color earns its place.** `timelineGantt`, `architecture`, and `roadmap`
   render **monochrome by default** — do NOT flag a single-tint gantt/roadmap or neutral architecture boxes as
   "missing colors"; that is the intended, more consulting-grade look. Category color appears only when the deck
   opts in (`categorical: true`, or a per-box `catIndex`); *then* each `catIndex` must match its fixed job
   (0 data, 1 models, 2 evaluation, 3 risks, 4 outputs, 5 milestones, plus **6 and 7 as unnamed reserve** —
   a `catIndex` of 6 or 7 is legal and carries no fixed job) and a mismatch is the bug. Multiple hues
   with no encoded meaning is itself a finding — recommend monochrome.
11. **Notes present.** Speaker notes exist (hook + 2–4 points + transition). Empty notes = fail.
12. **Parallel items, no filler slot.** Items in a numbered set or column group must be the same *kind* of
    thing at the same altitude — three risks, three phases, three asks. Two tells that a slot was filled to
    satisfy the layout rather than the argument: an item that restates the slide header in other words, and an
    item that is a different species from its siblings (a "how" sitting beside two "whats"). Fix is content:
    merge the weak item into a sibling and run the layout at two columns, or replace it with the real third
    point. **Not a defect:** unequal *length*. A genuinely short third column beside two long ones is fine, and
    a set of two is a legitimate set. Flag only when the item carries no information its siblings don't.
13. **Emphasis exists at all.** Check 5 judges whether the emphasis competes; this one catches its total
    absence. Every content and data slide must declare exactly one emphasis in `content.js` (one `hot`, one
    accent stop, one accent bar). A slide that renders entirely in neutrals means the field was never authored:
    the reader gets no entry point and the deck flattens into wallpaper. Fix is to mark the one number, word, or
    phase the slide exists to land. **Not a defect:** cover, agenda, section dividers, closing, the terminal
    `sources` slide, and the serif statement slides (`manifesto`, `quote`) are exempt by design. An all-neutral
    cover is correct, not a miss.
14. **Capacity match — filled, or deliberately airy.** Compare what the layout is sized to hold against what it
    actually holds. An agenda showing 4 of its 6–7 rows, a swimlane with empty cells, a content block floating
    mid-canvas with a third of the page dead beneath it: under-filled capacity is the strongest "template-y,
    unfinished" tell in this rubric, and it reads as sloppiness before anyone reads a word. Fix is always
    structural — move to a layout sized for the content you have, merge with a neighbouring slide, or pull real
    content forward. **Never pad words in.** Inflating items to fill rows manufactures filler (check 12) and
    trades one failure for a worse one. **Not a defect:** whitespace is the house rhythm and airiness is the
    brand. A slide *composed* short — a 3-item list on a 3-item layout, a statement slide with one line and a
    lot of air, a chart with a clean margin — passes. The failure is a container visibly larger than its
    contents, not a low word count.

## Findings that need the project log

Cold reviewers never see decision history. Some things that read as boilerplate are the opposite: a sanctioned
label someone argued over and then wrote down.

**Reviewer rule.** Treat anything that looks client-specific as **presumed intentional** — a programme or
engagement name, an unusual capitalisation, a cover footnote, a standing line that recurs across decks, any term
you would not have written yourself. Do not call it filler, boilerplate, generic, or a defect. Report it as
`CONFIRM-AGAINST-LOG:` with the exact string quoted and one line on why it caught your eye, and keep it out of
the defect count. You are flagging that it *looks* odd, never asserting that it *is* wrong.

**Main-agent rule (reciprocal).** Never act on a `CONFIRM-AGAINST-LOG` item — or on any reviewer finding about
naming, labels, or footnotes — before reading the target deck's project log / memory-log entry. If the log
sanctions the string, close the finding and record the closure there so the next cycle stops re-raising it. If
the log is silent, ask the user; do not edit a client deck on a cold reviewer's hunch. Precedent: one cover
footnote naming the client's engagement programme was flagged as "filler boilerplate" by three separate cold
reviews, and on the third the deck was edited before the log was read.

## Consistency checks (all slides together)

1. **Headers argue in sequence.** Read every header top to bottom: they should form the deck's whole argument.
   A header that doesn't advance the story, or a gap in the logic, is a content fix.
2. **Count the trailing appositives.** Reading only the headers, count those ending in a comma plus an
   explanatory clause. **More than two in a deck = flag the set**, not the individual slides — this is a
   frequency tell in the same family as the em-dash cap (`output-style.md` § Prose Style: density is the
   signature, not any single instance). Rewrite the offenders per per-slide check 4.
3. **Layout variety.** No layout repeated back-to-back where it reads as a template; a repeated component is
   the #1 "this is a generated deck" tell. Vary the layout across adjacent slides.
4. **Takeaway ratio.** At most one takeaway band per slide, and ~1 per 3 slides across the deck. A band on
   every slide (or several in a row) fails — demote the weaker ones to plain slides.
5. **Token consistency.** One theme throughout; the accent color is the same everywhere; no stray off-palette
   color. (A slide in the wrong theme is usually a `theme` set on the wrong object.)
6. **Page numbers + covers.** Numbers are contiguous in order; exactly one cover (first) and one closing (last);
   no orphaned duplicate cover.
7. **Sources reconcile.** Every figure cited on a content slide traces to an entry on the terminal `sources`
   slide, and vice-versa (no cited-but-unlisted, no listed-but-unused).

## Client-facing decks — extra checks

- No internal workflow or programme names, no automation percentages, and no coverage-completeness claims.
- "Helps / supports" framing, not "automates / replaces". Inferred asks marked "(to confirm)".

## Verify the artifact, not a proxy

A check that passes on a *derived* view proves nothing about the artifact you ship. Three failures in one session, same shape:

- A `.pptx` with 31 invalid negative extents passed every PDF check, because LibreOffice silently normalizes them and PowerPoint refuses to open the file.
- Markdown sub-bullets read correctly in source and rendered flat, because the parser needed a blank line the eye does not.
- Checkboxes rendered as ovals while their HTML was byte-identical to working rows, because only layout differed.

Rule: open the real file in the real reader, or measure the rendered result. Source review and proxy-format checks are screening steps, never the verification.

## Closing pass — two whole-artifact lanes, always both

Per-slide reviewers see slides. Neither of these lanes is optional, and neither substitutes for the other:
they read **different artifacts** and catch different failure classes. Run both after the last fix cycle.

**Lane A — the PDF, end to end.** What a reader sees. One reviewer reads every page in order and judges the
deck as a *document*: does the header sequence argue, does the density vary, does any slide look unfinished
next to its neighbours, is the emphasis rhythm right across the whole deck. This lane owns the § Consistency
checks above.

**Lane B — the .pptx, end to end.** What an *editor* gets — and what the client actually opens. A PDF cannot
prove a .pptx is valid, because **LibreOffice silently normalises XML that PowerPoint rejects.** For most of
v1.8–v1.9 the exported PDFs looked perfect while the shipped deck triggered PowerPoint's "repair" prompt and
flattened every rising line in every chart. Only opening the real file exposed it. This lane checks:

1. **Run `scripts/check_pptx.sh <deck>` first.** It fails on negative shape extents, the defect above.
   Also run `scripts/check_tokens.sh` (no args) — a **source** lint that fails if `T.accent` is used as a
   text color or if any theme's `accentText` drops below 4.5:1 on paper. Both scripts are negative-tested;
   neither replaces looking at the file.
2. **Open the deck in PowerPoint** (or state plainly that you could not). A repair prompt is a hard fail.
3. **Editability** — text is real text frames, charts are real shapes. Anything flattened to an image defeats
   the skill's entire purpose. Spot-check by selecting a bar and a header.
4. **Fonts resolve** — no silent fallback. A serif where DM Sans belongs means the bundled font did not load.
5. **Structure** — slide count matches, no orphaned or duplicated slides, speaker notes present.

A finding from Lane B outranks anything from Lane A: a beautiful deck nobody can open is worth nothing.

## Stop condition

Cap at 3 review cycles. After each, fixes go to `content.js` only and the deck re-renders. If cycle 3 still
surfaces material issues, hand back to the user rather than looping — the remaining issues are usually content
decisions, not layout bugs.
