# Layout catalog & writing contract

The 22 layouts, when to use each, and the per-slot text budgets that keep them from overflowing.
The **authoritative field list for any layout is the header comment above its function in
`../assets/layouts.js`** — this file is the *when* and *how much*; that code is the *what*. When they
disagree, the code wins (it's what renders).

Canvas is 13.333 × 7.5 in (16:9). Content margin `M = 0.85`. Budgets below are what fits cleanly at the
layout's font sizes; over-budget text either overflows (titles) or is clamped with a build warning (lists).

---

## The writing contract (read before authoring any Create-mode deck)

1. **Talking headers, written first.** Each content header is a full-sentence *finding*, not a label.
   "Onboarding cut first-week churn by 40%" — not "Onboarding results." Write every header before you
   pick a single layout; if the headers read as a coherent argument top to bottom, the deck works.
   Budget: **≤ 22 words, ≤ 2 lines** (~95 chars at the 22–23pt header size).
2. **Subtitles carry a *second* message** — the cause, the caveat, the "so what". Never a restatement of
   the header. Budget: **≤ 18 words, 1 line**.
3. **No explanatory clause after a comma in a header.** The model's default failure is a title with a
   subtitle glued to its tail: `<Topic> — <label>, <clause that re-explains the label>`. Each instance is
   individually defensible, which is why it survives every other check; at four-plus per deck it becomes
   the deck's signature and reads unmistakably machine-written.

   | Written | Fix |
   |---|---|
   | "Tool status — four pillars, what is real today" | "Tool status — the four pillars" |
   | "The road to launch, and what we need from you" | "The road to launch" |
   | "Programme delivery — the whole engagement, at a glance" | "Programme delivery — the whole engagement" |
   | "The decision engine — the gate, in detail" | "The decision engine — the gate" |
   | "The artifact index is live — collected, organized, and feeding the tool" | "The artifact index is live and feeding the tool" |

   The test: delete everything after the comma. If the header still names the thing, the clause was
   decoration — cut it. If the clause carried real information, it belongs in `sub`, not the header.
   A comma inside a genuine finding sentence is fine ("Churn fell 40%, and retention held") — the tell is
   the *appositive*, a clause that re-describes the noun before it.
4. **One emphasis per slide.** Set `hot: true` (or the accent stop) on exactly one element. The layouts
   render the hot mark in the theme accent and everything else neutral. Two accents = no accent.
5. **Sources on every data slide.** Any slide with a number carries `source`. End the deck with a `sources`
   slide. Mark estimates (`~`, "illustrative"); never fabricate figures.
6. **Takeaway band ≤ 1 per slide, ~1 per 3 slides deck-wide.** It's the loudest device; ration it.
7. **Split, don't cram.** If content exceeds a layout's item budget, make two slides. The clamp will warn
   and drop overflow — that warning is a content bug.

**Format mode:** ignore rules 1–3 (they govern how you *write* headers — in Format mode the user's wording
stands, appositives included). Rules 4–7 still apply to how you place their content. Do not restructure
their sequence.

---

## Openers & closers

**`cover`** — the fixed brand cover (auto-applied per theme; casper gradient / sphera navy S-mark). Title
is a short deck **name**, not a finding sentence. Slots: `title` (≤ 6 words), `kicker`, `subtitle` (1 line),
`footnote` (casper only). One per deck, first.

**`sectionDivider`** — a part label + hairline + the section stated as a talking header. Use between major
parts of a long deck. Slots: `part` ("Part 01"), `header` (the section as a finding, ≤ 12 words).

**`closing`** — bold statement on the solid brand field, accent contact line. Slots: `title` (≤ 10 words),
`sub`, `contact`. One per deck, last.

## Statement slides (serif — a rhythm break, ≤ 1 each per deck)

These two carry no top bar and set their statement in **Playfair Display** (the `serif` tier), which is why
they read as a deliberate pause, not another content slide. Use each **at most once per deck**, and never
back-to-back with the other — overuse turns the serif "breath" into noise. Both are prose-only, no `source`.

**`manifesto`** — one oversized serif line with an accent full-stop; a thesis or a turn in the argument,
placed early. Slots: `kicker` (optional, tracked caps), `statement` (the line itself — **≤ 130 chars**;
the engine steps the size down 44→40→36pt past 80 and 130 chars, so shorter reads bigger), `accentStop`
(default `true`; set `false` to drop the colored period), `body` (optional ≤ ~28-word gloss, lower-left).

**`quote`** — a serif-italic pull-quote on a full-bleed tint field with a tracked attribution. For a customer
or exec voice, once. Slots: `quote` (**≤ 160 chars**; sizes 37→32→28pt past 100 and 160), `attribution`
(name / role, rendered in accent caps). The quotation marks are added by the layout — don't include them.

## Text & argument

**`contentColumns`** — up to **3** flat columns (number, head, body). The workhorse for parallel points.
Slots: `kicker`, `header`, `sub`, `source` (yes — it takes a source footnote like any evidence slide; the doc
omitted this for several versions, so authors quoted figures here uncited), `columns:[{ title (≤ 3 words),
body (≤ 32 words), n? (overrides the auto "01/02/03" numeral — use a symbol or a short label when the columns
are not a sequence) }]`.

**`comparison`** — two options: the weaker flat on a gray tint (muted), the stronger inside an ink keyline
(accent kicker). Two only. Slots: `weak/strong: { label (≤ 3 words), title (≤ 5 words), body (≤ 28 words) }`.

**`numberedChallenges`** — up to **3** rows, each pairing a risk with its response. Slots: `kicker`, `header`,
`sub`, `leftLabel`, `rightLabel`, `items:[{ challenge (≤ 10 words), response (≤ 20 words) }]`.

**`agenda`** — a numbered agenda/section list with its own geometry (holds **6–7** rows, unlike challenges' 3).
Serif numeral, title, optional right-aligned owner/time. Slots: `kicker`, `header`, `sub`, `source`,
`items:[{ title (≤ 12 words), owner? (a name or time, ≤ 12 chars), desc? (≤ 14 words, shown only when ≤ 5
items) }]`. Use near the front of a readout, or as a section index.

> `sub` and `source` are **shared**, not per-layout: `sub` comes from `headerBlock`, `source` from
> `sourceNote`, so a layout that calls them accepts both even where the entry below does not repeat them.
> **All 18 content layouts call `sourceNote`.** The six that do not are the non-data slides where a footnote
> would be wrong — `cover`, `sectionDivider`, `manifesto`, `quote`, `closing`, and `sources` itself (it *is*
> the bibliography). Passing `source` to one of those six is silently ignored. Four content layouts
> historically forgot the call and dropped `source` without warning; that class is closed.

## Evidence (every one carries `source`)

**`chartTakeaway`** — the argument on a left rail, the chart as *evidence* on the right, accent takeaway band
beneath. The rail flows top-down (ink cap rule, stat, its label, a hairline sub-rule, then a short reading of
the chart), so it composes with any part missing — stat only, reads only, both. Slots: `statValue` (≤ 4 chars
holds the biggest size; 5 and 6+ step down), `statLabel` (≤ 8 words with `reads`, ≤ 12 without),
`reads:[str]` (≤ **3**, ≤ 10 words each — the "what this means" lines), `readsLabel` (small-caps rail label,
default "What this means"), `chartLabel` (optional small-caps unit label over the plot), `bars:[{ label
(≤ 4 chars), value, hot? }]` (≤ **6**, shape-based, handles negatives), `takeaway` (≤ 20 words), `source`.
The one accent is the hot bar and its value label — the rail stays neutral, the band uses its own role.

**`countChart`** — a ranked count / distribution exhibit: descending horizontal bars, rank numeral + category
in the left gutter, the exact count at each bar end, and a **derived** share-of-total column. Holds **8–10**
rows, which is the job `chartTakeaway`'s 6-bar vertical cap cannot take. The layout sorts rows descending and
rounds the axis itself, and it always prints its denominator. Slots: `rows:[{ label (≤ 3 words), value, hot? }]`
(≤ **10**, exactly one `hot`), `categoryLabel` (gutter head, ≤ 2 words), `unit` (names the thing counted,
default "items"), `total?` (the true population when the tail is deliberately not charted — shares then read
against it, not against the visible subset), `cumColumn?` (bool, adds a running cumulative column),
`topNote?` (a **number** k — derives "Top k of n account for X% of all <unit>"), `annotation?` (a string that
overrides that derived sentence, ≤ 16 words), `source`.

**`waterfall`** — start total, floating deltas, end total, hairline step connectors; the standard "how a number
moved" chart, plus the narrative that explains it. Give any delta a `note` and the plot narrows to make room for
a **numbered commentary rail** on the right, keyed to the columns by the same 01/02/03 numerals printed under
the axis. A bare bridge is an analyst artifact; the rail is what makes it partner-ready. Every piece of prose
furniture is opt-in, and each one shrinks the plot — with no note, no takeaway and no footnote it renders at the
original full-width geometry. Slots: `start:{ label, value }`, `deltas:[{ label (≤ 3 words), value (signed),
hot?, note? (≤ 14 words) }]` (≤ **5**), `end:{ label, value }` (omit `end.value` to auto-sum),
`commentaryTitle` (rail micro-label, default "What moved it"), `takeaway` (≤ 20 words, same band treatment as
`chartTakeaway`), `footnote` (an assumptions line above the source — the engine prefixes "Note:", so don't),
`source`. Totals use the band color; the one accent is the hot delta, carried on its bar, its value and its rail
numeral. Column labels shrink to 9.5pt once the rail is present, so keep them short.

**`matrix2x2`** — a positioning / prioritization quadrant: hairline frame, small-caps axis labels, italic
quadrant labels, plotted dots at normalized 0–1 coords, one `hot` accent dot. Slots: `xAxis:{ low, high }`,
`yAxis:{ low, high }` (axis-end captions, ≤ 3 words each), `quadrants:[TL, TR, BL, BR]` (optional, ≤ 3 words),
`points:[{ label (≤ 2 words), x (0–1), y (0–1), hot? }]` (≤ **8**), `source`. Right/top = the "good" end.

**`slopeChart`** — a before/after comparison, or a **2–4 point bump chart** when you pass `columns`. Hairline
axis per column, one line per item, and the derived columns a reader would otherwise compute by hand: aligned
label and value gutters, an optional rank column at each end, an optional change column. When one item is `hot`
every other line drops back hard, so the argued line is the only thing the eye lands on. Slots: `leftLabel`,
`rightLabel` (the 2-point form), `columns:[str]` (≤ **4**; wins over left/rightLabel), `items:[{ label
(≤ 3 words), left, right, values:[..] (wins over left/right), hot? }]` (≤ **6**), `showRank?` (default false —
turn it on when rank *change* is the story), `showDelta?` (default **true**), `deltaMode?:"abs"|"pct"`
(default abs), `deltaLabel?` (default "Change"), `reference?:{ value?, mode?:"mean"|"median", label? }`
(a dashed rule against the final column), `valueSuffix?`, `zeroBase?` (the frame is the data range by default,
since a slope chart reads change; zero-anchoring flattens the lines), `source`. Endpoint labels run through a
de-collision pass, so near-identical values no longer overprint — you no longer have to space the data by hand.

## Time & process

**`trendLine`** — change over time, drawn as shape segments so every vertex stays draggable downstream. **1–3
series**, labelled at the **end of the line** rather than in a legend (a legend is a tax the reader pays on
every glance). Baseline is **zero by default** — a truncated axis exaggerates slope, so `yMin` is deliberate,
never automatic. Slots: `xLabels:[str]` (≤ **12**, ≤ 4 chars each; ticks thin to ~5 past 8 points),
`series:[{ name (≤ 2 words — it shares a 2.4in gutter with its final value), values:[nums], hot?,
color?:"secondary" }]` (≤ **3**), `unit` (suffix on every printed value), `yMin?`, `yMax?`,
`event:{ at (x-index), label (≤ 3 words) }`, `projectFrom?` (x-index — everything after it goes dashed and
gets a "PROJECTED" rule), `projectionLabel?`, `projectionStyle?:"solid"` (kills the dash), `source`. Non-hot
series take a neutral tint ramp, not a second hue; `color:"secondary"` is for a second *identity*, never a
second emphasis. Values are rationed to first + interior peak on the hot series only.

**`timelineGantt`** — week grid with lane titles in a **left rail**, so bar length reads as duration instead of
as a text container, and the rail can carry a derived meta line the reader never has to compute. Bars are thin
against an adaptive row pitch: three lanes get air, six tighten rather than overrun the footer. Progress is
encoded by **fill vs hollow** (solid = elapsed, hairline outline = remaining), never by a second color.
**Monochrome by default**; `categorical: true` colors lanes by `catIndex`. Slots: `months:[≤ **4**]`, `weeks`,
`railLabel?` (default "Workstream"), `unitLabel?` (default "wks"), `lanes:[{ title (≤ 3 words), start, end,
pct? (0–100), meta? (≤ 2 words, appended after the auto duration), catIndex?, hot? }]` (≤ **6**),
`phases:[{ label (≤ 2 words), start, end }]` (≤ **4**, spanning brackets above the axis),
`milestones:[{ label (≤ 3 words), week, hot? }]` (≤ **4**, diamonds on the axis with hairline leaders),
`today?` + `todayLabel?` (a dashed status line across the plan), `categorical?`, `source`. The legacy singular
`milestone:{ label, week }` still renders. At most **one** `hot` across all lanes *and* milestones; diamonds and
the status line are ink, not accent. The rail meta line needs row height — with phases, milestones and a today
line all present it drops off at 6 lanes.

**`stepLine`** (Mode 1) — up to **5** numbered circles on one connector, which runs solid ink to the argued step
then hairline (encoding progress). The uplift is a ruled **detail rail** keyed to the step columns, so the slide
also answers who, how long, and what hands off — the `roadmap` idiom, so it reads as house furniture. Everything
past `steps` is optional and the geometry degrades to the original. Slots: `steps:[{ name (≤ 3 words),
desc (≤ 5 words), n? (overrides the auto 01/02 numeral), details:[str] (one per `detailRows` entry, ≤ 4 words
each), hot? }]` (≤ **5**), `detailRows:[label]` (≤ **3**, ≤ 2 words each — the row labels; cells come from
`step.details`), `phases:[{ label (≤ 2 words), from, to }]` (≤ **3**, 0-based *step index* spans bracketed above
the line), `gates:[{ after (0-based step index), label (≤ 3 words) }]` (≤ **4**, decision diamonds between
steps), `source`. The hot step's circle fills with the band color and its detail column steps up in weight —
weight, not a second color. Gate diamonds are hollow so they stay quieter than the gantt's solid milestones.

**`workflowMap`** (Mode 2, swimlane) — players are lanes, stages are columns, steps sit in the cells, and the
signature mark is the **handoff**: an arrow that crosses lanes where work changes hands. Only reach for it when
work actually changes owner — a flat left-to-right chain is `stepLine`. Each step declares who does it, and the
three modes render as a tint ramp plus a left-edge tick so the "here is what the agent takes over" read survives
greyscale. Slots: `lanes:[{ name (≤ 2 words), role? (≤ 3 words) }]` (≤ **5**, top to bottom),
`stages:[{ name (≤ 2 words), dur? (≤ 8 chars) }]` (≤ **6**, left to right — any `dur` adds a cycle-time row),
`steps:[{ lane (0-based), stage (0-based), span?=1, label (≤ 4 words), note? (≤ 5 words),
mode?:"human"|"hybrid"|"ai", hot? }]` (≤ **14**), `handoffs:[{ from, to, label? (≤ 2 words) }]` (≤ **9**;
`from`/`to` are **`steps[]` indices** — a bad index is dropped with a warning), `zebra?`, `cycleLabel?`
(default "Cycle time"), `legendLabels?` (overrides the Human / Human + AI / AI-assisted wording), `source`. Arrows are
routed elbows, never diagonals, with the vertical leg riding the column separator. Within-lane flow is light,
a cross-lane handoff is heavier — that weight difference *is* the exhibit. One `hot` step takes the accent.
Step `note`s only render when the rows are tall enough: budget for them at ≤ 4 lanes, and expect them dropped
at 5. The mode legend appears only when the steps actually use more than one mode.

## Diagrams (monochrome by default; color is opt-in)

**`architecture`** — a layered system exhibit: flat boxes and arrows, optionally organised on a **tier rail**
(horizontal planes with small-caps labels down the left gutter) with a **cross-cutting rail** on the right for
concerns that span every plane. **Monochrome by default**; depth comes from layering and typographic tiers —
lane rules, tech chips, sub-items, numbered flow badges, plated arrow labels — not from more color. Emphasis is
an ink keyline via `hot`, never a second accent. Boxes carry explicit `{x,y,w,h}` (keep within `M`..`W-M` =
0.85..12.48); everything past `boxes`/`arrows` is optional. Slots:

- `tiers:[{ label (≤ 2 words), y, h }]` (≤ **4**) — the planes. Canonical 3-tier geometry: `y 2.72 / 4.12 /
  5.52`, each `h 1.26`; boxes at `y = band.y + 0.13, h 1.00`, `x 2.10` to a right edge of `10.36`, rail at
  `x 10.60 w 1.88`. `tierFill?` washes each lane in surface; `tierLabelW?` sets the gutter (default 1.05).
- `boxes:[{ x, y, w, h, label (≤ 3 words), desc? (≤ 12 words), items?:[≤ **3**, ≤ 4 words each],
  chips?:[≤ **4**, ≤ 12 chars each], n? (a flow badge numeral), catIndex?, hot? }]` (≤ **12**). Chips pack into
  at most two rows and overflow is **dropped with a warning** — shorten them or grow the box.
- `arrows:[{ x, y, len, dir?:"down"|"up"|"left", to?:{x,y}, elbow?:"hv"|"vh", label? (≤ 3 words) }]` — pass `to`
  for an orthogonal elbow (`"hv"` default); diagonals are never drawn. Labels ride a paper plate.
- `rail:{ label (≤ 2 words), sub?, x, y, w, h, items:[{ label (≤ 3 words), desc (≤ 8 words) }] }` (≤ **5**).
- `groups:[{ label, x, y, w, h }]` — hairline sub-frames, unchanged.
- `legend:[{ label, catIndex }]` (≤ **6**) — only renders when a box uses `catIndex` **and** there are no
  `tiers`. With a tier rail the plane labels already decode the tints, so a `legend` is suppressed and warned.

Tint a box only by giving it a `catIndex`, and let it encode the **tier**, not decoration.

**`roadmap`** — up to **4** phase columns as a ruled matrix. Phase names sit **in ink directly over the ink
header rule** (the chips are gone — they said nothing the name did not, and made the accent compete with a
tint for the same band), and the **rule carries the emphasis**: a `hot` phase takes `accentText` on its name
plus a thickened accent segment of the rule beneath it, and its cells step from `sec` to `ink`. Row hairlines
fall **between rows only**. Column width is derived from the phase count, so 3 phases land on the pre-uplift
3.19in grid and 4 still clear the frame. Slots: `rowLabels:[≤ **3**]` (default Objective/Activities/
Deliverables; a 4th is accepted and the row pitch tightens), `phases:[{ title (≤ 2 words), meta? (≤ 4 words —
a per-phase dates/owner line), cells:[one per rowLabel] (≤ 8 words each), hot?, catIndex? }]` (≤ **4**),
`metaPos?:"above"|"below"`, `railLabel?` (fills the empty corner cell above the row labels), `categorical?`,
`source`.

The dashed "we are here" rule takes **one of two mutually exclusive fields**, and they are separate on
purpose: `nowAfterPhase?` is an **integer count of phases already complete** (the normal case — it draws in
the gutter that opens the next phase), while `now?` is a **fraction 0–1** across the phase span for a
mid-phase marker. A single overloaded field where 0–1 meant a fraction and >1 meant an index made
`now: 1` — the most natural way to write "one phase done" — silently mean "100% complete", drawing the rule
at the far right and inverting the slide's claim. Pair either with `nowLabel?` (default "Today"). A
*fractional* marker crosses cell text; prefer `nowAfterPhase` where you can.

**Monochrome by default**; `categorical: true` colours every name and rule segment by `catIndex` and is
**mutually exclusive with `hot`** — a hot passed alongside it is dropped with a warning, because category
tints already colour every phase, so a hot phase would read as a seventh hue rather than an emphasis.

**`roadmapTrack`** (Mode 1) — the same plan told as a **journey**: 3–5 equal segments of **one continuous
horizontal track**, one outcome sentence per segment, **hollow gate diamonds** at the boundaries. Progress is
the `timelineGantt` idiom — solid ink up to `pct`, hairline for what remains, fill vs hollow rather than a
second colour. Slots: `phases:[{ name (≤ 2 words), meta? (≤ 4 words), outcome (ONE sentence, ≤ 14 words),
items?:[≤ **3**, ≤ 5 words each], gate? (≤ 2 words at 5 phases, ≤ 3 at fewer — the diamond that *closes*
this phase), hot? }]` (≤ **5**), `pct?` (0–100 across the whole track; absent = solid end to end), `source`.
**Monochrome by design** — one track cannot carry six identities, so there is no `categorical`. At most
**one** `hot`: it takes `accentText` on the name and paints its whole segment accent, which **overrides
`pct` shading inside that span** — mark the phase you are arguing for, not a half-elapsed one. `items` are
**parallel rows**: item *r* should mean the same thing in every phase (scope / evidence / owner). Without
`items` the slide is deliberately airy and uses only ~62–70% of the canvas — if each phase needs three facts,
that is `roadmap`, not this.

## Provenance

**`sources`** — numbered bibliography, up to **16** (8 per column). The terminal provenance slide. Slots:
`header`, `sub?`, `sources:[strings]`. Keep each entry ≤ 1 line (~14 words) so it doesn't collide with the
next (row height is fixed).

---

## Category palette jobs (opt-in)

Diagrams are **monochrome by default now** — reach for category color only when the hues *encode meaning*
(distinct data/model/eval stages), never for decoration. When you do (`categorical: true` on gantt/roadmap,
or a per-box `catIndex` on architecture), `catIndex` maps to fixed jobs in order: **0 data · 1 models ·
2 evaluation · 3 risks · 4 outputs · 5 milestones · 6–7 reserve**. Assign by meaning so color reads
consistently across a deck. Both themes define all eight (`assets/themes.js` → `cat`).

## Choosing quickly

- One number that matters → `chartTakeaway`. A ranked breakdown with shares → `countChart`.
- How a number moved (buildup/bridge) → `waterfall`. A before/after across items, or rank change across 2–4
  points → `slopeChart`. A trend that holds (or breaks) across groups → `trendLine` with one series per group.
  Positioning / what-to-prioritize → `matrix2x2`.
- Parallel points → `contentColumns`. Two options → `comparison`. Risks → `numberedChallenges`. A meeting or
  section index → `agenda`.
- Time as phases → `timelineGantt`. A sequence of steps → `stepLine`. A system of parts → `architecture`.
  Phase plan → `roadmap` when each phase has three facts to line up; `roadmapTrack` when each has one
  sentence and the point is that they happen in order.

**Three routings worth getting right** — each pair looks interchangeable and isn't:

- **Ranked distribution → `countChart`. Change over time → `trendLine`.** "How is the total distributed" and
  "which way is it going" are different analytical questions and get different exhibits. A count chart states
  its `n` and derives share-of-total; a trend line states its baseline and labels its end points.
- **Neither one is a `chartTakeaway`.** `chartTakeaway` is an *argument* slide that happens to carry ≤ 6 bars
  as evidence. Don't fuse a 9-row ranking or a 12-point series into it — the bars will clamp and the reading
  rail is not where a dense table goes. If you need the count *and* the argument, that's two slides.
- **A sequence of steps → `stepLine`. The same sequence with ownership changing hands → `workflowMap`.** The
  test is whether anyone hands off. If every step has the same owner, the swimlanes are empty scaffolding and
  `stepLine` says it in half the ink. If work crosses from a person to a model, or from one team to another,
  the crossing *is* the finding and only `workflowMap` draws it.
- A thesis or a turn worth a full breath → `manifesto`. A customer/exec voice → `quote`. Each once, serif,
  as a rhythm break — not as a content slide.
- Vary layouts across a deck — a repeated component is the #1 "this is a template" tell.
- **Parallelism pre-check, before any multi-slot layout.** Say each slot's content aloud as one sentence
  stem. If the stem doesn't fit all of them, the items aren't parallel and a slotted layout will misread
  them — route to `comparison`, split the slide, or see § When no layout fits.
- **Never fill a slot by paraphrasing the header.** A slot you can only fill with a restatement is a slot
  the content doesn't have. Drop it and use the layout one size down.
- **Every content and data slide needs exactly one emphasis** — one `hot`, one keyline, one accent stop. If
  nothing deserves it, you have a list, not an argument; either find the finding or pick a lighter layout.
- **Capacity-match, don't pad.** Choose the layout whose capacity your content actually fills, or accept the
  whitespace deliberately. Half-empty grids read as generated faster than any repeated component.
- **When nothing routes cleanly, don't force the nearest.** Adapt it or compose from primitives — the ladder
  and its hard floor are in § When no layout fits.

## When no layout fits

The 22 layouts are **ideas to work off**, not molds. Force-fitting content into the nearest layout is the
failure this section exists to prevent — but improvisation ideates *from* the catalog, never away from it.
Three rungs, in order of preference:

1. **Template as-is.** The layout's designed job matches the content's job. The default; most slides.
2. **Adapt the nearest template.** It almost fits: swap the exhibit, **drop a slot rather than pad it**,
   borrow one element from a second layout. Still recognisably house language.
3. **Compose from house primitives.** Nothing is near. Build bespoke from the shared pieces — theme tokens,
   `headerBlock`, the geometry constants (`M`, the 13.333 × 7.5 canvas, the tier/row pitches), hairlines,
   the one-accent rule, `sourceNote`. A bespoke slide should look like it *could* have been the 23rd layout.

**Hard floor under all three:** no new colours, no new fonts, no new chrome, no freeform spacing.
Improvisation recombines the design system; it never exits it. Rung 3 is rare — reach for it only after
naming which layout you rejected and why.

**Signals a slide is on rung 2 or 3** — any one is enough:

- **The items are not genuinely parallel**, or not rankable against each other. Numbered columns assert a
  symmetry the content doesn't have, and the reader feels the lie before they read the words.
- **A slot you can only fill by paraphrasing the header.** A restated header is not a third point; it is an
  admission there are two.
- **The content wants a hybrid** — the left rail of one layout with the exhibit of another.
- **The argument form is absent from the catalog.** Branches and conditionals, ownership grids, and
  anything where one element explodes while its siblings stay flat.
- **Capacity far exceeds content.** The layout can hold much more than you have.

**Most "template-y" slides are under-filled capacity, not wrong routing.** An `agenda` holding 4 of its
6–7 rows, a `workflowMap` with empty cells, three columns where one is thin — gridded emptiness reads as
generated even when the routing was right. The remedy is **capacity-matching**: pick the lighter layout, or
deliberately accept the whitespace. Never pad words in to fill the grid.

**Worked example, rung 2.** Three non-parallel items — the ask, what's in scope, what's deferred — were
flattened into three equal numbered `contentColumns`, with the third column restating the slide header just
to fill the slot, and no emphasis anywhere. The adapt: `comparison`, with in-scope as the strong keyline
panel and deferred as the muted one; the ask belongs in the header, which is where an ask always belongs.

**Worked example, rung 3.** A four-phase plan where phase 1 explodes asymmetrically into a detailed ask-list
plus a "sign-off this week" badge. `roadmap` cannot explode one phase asymmetrically, and `roadmapTrack`'s
contract explicitly requires item *r* to mean the same thing in every phase. Correctly hand-built from
primitives — the archetypal rung-3 case.

**Hybrids to expect** (they recur, so recognise them early):

- **Three or more options weighed against each other.** `comparison` holds exactly two; `contentColumns`
  holds three but flattens the recommendation into a peer. Rung 2: three columns with the recommended one
  carrying the single accent and its `n` overridden to a mark, or a two-slide split (shortlist, then the pick).
- **A conditional or a branch** ("if the pilot clears, then X; if not, Y"). Nothing in the catalog forks —
  `workflowMap` draws handoffs, not decisions, and `stepLine` gates are markers, not branches. Rung 3.
- **An ownership or RACI grid.** No layout owns it. Rung 2 by borrowing `roadmap`'s ruled matrix with
  `rowLabels` recast as roles — same geometry, same hairlines, different job.

**Mechanism:** rung 3 needs no fork of the shared catalog. `content.js` may export `customLayouts` — a map of
deck-local layout functions merged over the registry for that deck only (see SKILL.md § Composing a bespoke
slide). The 22 shared layouts stay untouched, so a one-off never becomes everyone's maintenance.
