// example-content.js — the skill's showcase deck. A SYNTHETIC, fictional Casper client
// engagement ("Northwind AI enablement pilot"). No real client, no real data — every figure
// is illustrative, marked as such on each source line. It doubles as the all-layouts smoke
// deck: one slide per layout in the registry (22 total), so `node scripts/render.js
// assets/example-content.js out.pptx` renders every template once.
//
// Why a client engagement and not "the skill describing itself": the evidence layouts (KPI,
// data table, chart) need external magnitudes to look their best — a deck about the tool has
// no adoption %, revenue, or deltas to show. Switch `theme` between "casper" and "sphera" to
// see the same deck re-skinned. Speaker notes (hook + points + transition) on every slide.

module.exports = {
  theme: "casper",
  title: "Northwind AI Enablement — Pilot Readout",
  slides: [
    // 1 · COVER — short deck NAME, not a finding sentence.
    {
      layout: "cover",
      kicker: "Pilot readout · Q3 2026",
      title: "Northwind AI enablement, from pilot to scale",
      subtitle: "A three-month, three-team pilot — what changed, and what to fund next.",
      footnote: "Synthetic example deck — Northwind is fictional, all figures illustrative.",
      notes: "Hook: we set out to test one claim — that adoption follows usefulness, not mandates. Point 1: three teams, ninety days. Point 2: the numbers held past the pilot. Transition: start with the thesis.",
    },
    // 2 · AGENDA — what the readout covers, in order.
    {
      layout: "agenda",
      kicker: "Today",
      header: "What we'll cover, in order.",
      items: [
        { title: "The thesis — why adoption is a usefulness problem", owner: "5 min" },
        { title: "What we piloted — three teams, ninety days", owner: "5 min" },
        { title: "The evidence — adoption, time saved, deflection", owner: "10 min" },
        { title: "How it's wired, and how we rolled it out", owner: "5 min" },
        { title: "What scale looks like, and what we're asking to fund", owner: "10 min" },
      ],
      notes: "Hook: five parts, thirty-five minutes. Point: evidence in the middle, the ask at the end. Transition: start with the thesis.",
    },
    // 3 · MANIFESTO — the thesis, one oversized serif line. Early breath slide.
    {
      layout: "manifesto",
      kicker: "The thesis",
      statement: "Every hour the pilot gave back went to work only people can do",
      body: "We did not measure the tool. We measured what teams did with the time it returned — and whether they kept using it once the mandate ended.",
      notes: "Hook: the point was never hours saved for their own sake. Point: time returned only matters if it moves to higher-value work. Transition: here is what we set out to prove.",
    },
    // 3 · SECTION DIVIDER — the single part break.
    {
      layout: "sectionDivider",
      part: "Part 01",
      header: "Adoption is a usefulness problem before it is a training problem.",
      notes: "Hook: name the reframe. Point: most rollouts fail on relevance, not on enablement. Transition: contrast the old way of working with the assisted one.",
    },
    // 4 · COMPARISON — old vs assisted way of working.
    {
      layout: "comparison",
      kicker: "How the work changed",
      header: "The assisted flow removed the search-and-assemble step, not the judgment step.",
      weak: {
        label: "Before",
        title: "Search, then assemble",
        body: "Analysts spent the first half of every task finding prior work, reconciling versions, and rebuilding context by hand before any thinking began.",
      },
      strong: {
        label: "With the pilot",
        title: "Draft, then decide",
        body: "The assistant returned a sourced first draft in seconds; the analyst's time moved to checking, deciding, and shaping — the part clients actually pay for.",
      },
      notes: "Hook: the split is the whole story. Point: automation took the assembly, not the judgment. Transition: which teams we scoped in.",
    },
    // 5 · CONTENT COLUMNS — the three workstreams.
    {
      layout: "contentColumns",
      kicker: "What we piloted",
      header: "Three teams, chosen because their work was repetitive at the front and expert at the back.",
      sub: "Same tool, three very different jobs to be done.",
      columns: [
        { title: "Support", body: "First-response drafting against the knowledge base. High volume, clear ground truth, fast feedback loop." },
        { title: "Operations", body: "Shift reports and exception summaries. Structured inputs, tight deadlines, low tolerance for error." },
        { title: "Finance", body: "Variance narratives and reconciliation notes. Fewer tasks, higher stakes, heavy review already built in." },
      ],
      notes: "Hook: three teams, picked deliberately. Point: repetitive front, expert back — the shape the tool fits. Transition: the objections we heard going in.",
    },
    // 6 · NUMBERED CHALLENGES — adoption risks paired with responses.
    {
      layout: "numberedChallenges",
      kicker: "What we heard, and what we did",
      header: "Every objection to the rollout had a concrete answer built into how we ran it.",
      leftLabel: "The concern",
      rightLabel: "How we handled it",
      items: [
        { challenge: "It will hallucinate and someone will ship it.", response: "Every draft carries its sources inline; the human-review step stayed mandatory and was never automated away." },
        { challenge: "People will use it once and drift back.", response: "We measured week-8 usage, not week-1 — the number that tells you whether it stuck after the novelty." },
        { challenge: "It only helps the junior analysts.", response: "Finance, the most senior team, saved the most hours per person — even though it runs the fewest tasks." },
      ],
      notes: "Hook: three objections, up front. Point: each had a mechanism, not a promise. Transition: now the evidence, starting with where the rework actually was.",
    },
    // COUNT CHART — ranked distribution: where the review comments came from.
    {
      layout: "countChart",
      kicker: "Where the rework was \u00b7 illustrative",
      header: "Two in three returned drafts trace back to three fixable causes.",
      sub: "Three categories a pre-send check can catch before a draft reaches a customer.",
      categoryLabel: "Rework reason",
      unit: "flagged drafts",
      cumColumn: true,
      topNote: 3,
      rows: [
        { label: "Missing source citation", value: 96, hot: true },
        { label: "Stale or outdated figure", value: 78 },
        { label: "Tone off-register", value: 57 },
        { label: "Scope creep in the ask", value: 29 },
        { label: "Broken cross-reference", value: 24 },
        { label: "Formatting drift", value: 19 },
        { label: "Duplicated content", value: 15 },
        { label: "Ambiguous owner", value: 12 },
        { label: "Terminology mismatch", value: 10 },
      ],
      total: 340,
      source: "Northwind review log, weeks 1\u201312 \u00b7 340 drafts returned for rework \u00b7 illustrative sample data.",
      notes: "Hook: 340 returned drafts, nine causes, one that dwarfs the rest. Point: missing citations alone are 28% \u2014 and it is the cheapest to fix, because the assistant already has the sources. Transition: what the trend looks like once we fixed it.",
    },
    // SLOPE / BUMP CHART — three time points, rank change at each end, derived % change,
    // and a mean reference rule. Week-1 values are deliberately clustered (41 / 39 / 38) to
    // exercise the label de-collision pass. The legacy two-point form still renders unchanged.
    {
      layout: "slopeChart",
      kicker: "Before and after",
      header: "Every team ended higher than it started, and Finance closed a nineteen-point gap to lead.",
      sub: "Share of eligible tasks done with assistance, by team.",
      columns: ["Week 1", "Week 6", "Week 12"],
      showRank: true,
      deltaMode: "pct",
      reference: { mode: "mean", label: "Week 12 average" },
      items: [
        { label: "Support", values: [41, 47, 57] },
        { label: "Operations", values: [39, 44, 51] },
        { label: "Finance", values: [22, 38, 64], hot: true },
      ],
      source: "Northwind assisted-task share by team, weeks 1 / 6 / 12 \u00b7 illustrative sample data.",
      notes: "Hook: four lines, all up \u2014 but read the rank column, not the slopes. Point: Finance started #4 and finished #1, a 177% gain from the worst starting position. Point 2: the dashed rule is the pilot average; only Finance and Support finish above it. Transition: the week-by-week shape, team by team.",
    },
    // CHART + TAKEAWAY — the metric that jumped. The left rail carries the argument
    // (stat + reading); the plot is sized as evidence, not as the subject.
    {
      layout: "chartTakeaway",
      kicker: "Evidence \u00b7 illustrative",
      header: "Support deflection jumped the week we connected the assistant to the live knowledge base.",
      sub: "Deflection settled at 58% after the spike, so the lift held rather than faded.",
      statValue: "61%",
      statLabel: "of support tickets deflected at first response, peaking in week 9",
      readsLabel: "What this means",
      reads: [
        "Week 9 is when the live knowledge base landed.",
        "No extra training shipped that week; relevance did it.",
        "Week 12 settles at 58%, so the gain held.",
      ],
      chartLabel: "First-response deflection, % of tickets",
      bars: [
        { label: "Wk2", value: 34 },
        { label: "Wk4", value: 39 },
        { label: "Wk6", value: 42 },
        { label: "Wk9", value: 61, hot: true },
        { label: "Wk12", value: 58 },
      ],
      takeaway: "Connect the assistant to live ground truth first; relevance is what makes adoption stick.",
      source: "Northwind support queue, weekly deflection rate \u00b7 n \u2248 1,200 tickets/wk \u00b7 illustrative sample data.",
      notes: "Hook: one week changed the curve. Point: the jump followed the knowledge-base connection, not more training. Transition: the same climb, team by team.",
    },
    // TREND LINE — change over time: adoption curve, one event, a modelled tail.
    {
      layout: "trendLine",
      kicker: "Adoption by team \u00b7 illustrative",
      header: "Support tripled its use after the knowledge base landed, and the other teams followed the same shape.",
      sub: "Share of tasks drafted with assistance, by team.",
      unit: "%",
      xLabels: ["Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
      series: [
        { name: "Support", values: [12, 19, 26, 22, 31, 47, 61, 72, 68, 71], hot: true },
        { name: "Operations", values: [9, 14, 17, 15, 21, 28, 35, 41, 44, 48] },
        { name: "Finance", values: [6, 8, 11, 10, 13, 16, 19, 23, 25, 27] },
      ],
      event: { at: 4, label: "Knowledge base live" },
      projectFrom: 7,
      projectionLabel: "Projected",
      source: "Northwind telemetry, Mar\u2013Oct 2026 actuals; Nov\u2013Dec modelled from the trailing three-month rate \u00b7 illustrative sample data.",
      notes: "Hook: one line, one inflection. Point: nothing moved until the knowledge base gave people a reason \u2014 the June dip is the holiday week, not a reversal. Caveat: October includes a one-off program launch, which is why the forecast normalises below the spike. Transition: where the saved hours actually came from.",
    },
    // WATERFALL — where the saved hours came from, with the commentary that explains
    // each move. Notes on the deltas build the keyed right-hand rail automatically.
    {
      layout: "waterfall",
      kicker: "Where the time went",
      header: "Most of the saved hours came from assembly, not from the thinking itself.",
      sub: "Mean analyst week, before and after the pilot.",
      start: { label: "Baseline hrs / wk", value: 40 },
      deltas: [
        { label: "Search & gather", value: -7, note: "Retrieval time collapsed once the knowledge base became the single source of truth." },
        { label: "Draft assembly", value: -9, hot: true, note: "The largest single move: first drafts now arrive sourced, not blank." },
        { label: "Version reconciling", value: -4, note: "One canonical draft per task removed the merge step entirely." },
        { label: "Added review", value: 2, note: "A deliberate cost. Every send is still read by a human before it ships." },
      ],
      end: { label: "Net hrs / wk", value: 22 },
      commentaryTitle: "What moved it",
      takeaway: "Automating assembly returned 20 hours a week; we spent 2 back on review, on purpose.",
      footnote: "Hours self-estimated against a pre-pilot baseline; review time measured from the send log. Excludes onboarding weeks 1\u20132.",
      source: "Northwind time-tracking, mean analyst week \u00b7 illustrative sample data.",
      notes: "Hook: forty hours in, twenty-two out. Point: the biggest single drop is draft assembly \u2014 the judgment work was never the target. Transition: how the system is wired.",
    },
    // ARCHITECTURE — a layered AI-system exhibit, MONOCHROME: surface-washed tier lanes, paper
    // boxes with hair keylines, ink labels. The tier-rail gutter labels decode the planes, so
    // category tints (catIndex) stay opt-in and unused here; the single emphasis is the ink
    // keyline on the review gate.
    //
    // Geometry: tiers y 2.72 / 4.12 / 5.52, each h 1.26 (field 2.72\u21926.78, clears the footer).
    // Boxes y band+0.13, h 1.00. All right edges land on 10.36; the rail runs 10.60\u219212.48.
    {
      layout: "architecture",
      tierFill: true,
      kicker: "Reference architecture",
      header: "Nothing reaches a client unread, and every review turns into an eval case.",
      sub: "Three planes, plus one governance column that spans all of them.",
      tiers: [
        { label: "Data plane", y: 2.72, h: 1.26 },
        { label: "Model plane", y: 4.12, h: 1.26 },
        { label: "Application plane", y: 5.52, h: 1.26 },
      ],
      boxes: [
        { n: 1, x: 2.10, y: 2.85, w: 1.81, h: 1.00, label: "Connectors", desc: "Confluence, Drive, Jira, S3", chips: ["Airbyte CDC"] },
        { n: 2, x: 4.25, y: 2.85, w: 1.81, h: 1.00, label: "Chunk & enrich", desc: "Semantic split, ACL tags", chips: ["Unstructured.io"] },
        { n: 3, x: 6.40, y: 2.85, w: 1.81, h: 1.00, label: "Embeddings", desc: "Batch and incremental re-embed", chips: ["voyage-3-large"] },
        { n: 4, x: 8.55, y: 2.85, w: 1.81, h: 1.00, label: "Vector store", desc: "Hybrid index, tenant-scoped", chips: ["pgvector", "HNSW"] },
        { n: 5, x: 7.87, y: 4.25, w: 2.49, h: 1.00, label: "Hybrid retrieval", desc: "BM25 plus dense, top-40 down to 8", chips: ["Cohere Rerank 3.5"] },
        { n: 6, x: 4.99, y: 4.25, w: 2.49, h: 1.00, label: "Agent orchestration", desc: "Plans steps, calls tools, retries", chips: ["MCP tools", "LangGraph"] },
        { n: 7, x: 2.10, y: 4.25, w: 2.49, h: 1.00, label: "Generation", desc: "Structured output, inline citations", chips: ["Primary model", "Fallback model"] },
        { n: 8, x: 2.10, y: 5.65, w: 2.49, h: 1.00, label: "Assisted workspace", desc: "Drafts land in the analyst queue", chips: ["Slack", "Web app"] },
        { n: 9, x: 4.99, y: 5.65, w: 2.49, h: 1.00, label: "Human review gate", hot: true, items: ["Approve, edit, or reject", "Sampled QA on approvals", "No unreviewed send"] },
        { n: 10, x: 7.87, y: 5.65, w: 2.49, h: 1.00, label: "Delivery & audit trail", desc: "Every send stored with its sources", chips: ["Immutable log"] },
      ],
      arrows: [
        { x: 3.91, y: 3.35, len: 0.34 },
        { x: 6.06, y: 3.35, len: 0.34 },
        { x: 8.21, y: 3.35, len: 0.34 },
        { x: 9.45, y: 3.85, len: 0.40, dir: "down", label: "top-40" },
        { x: 7.87, y: 4.75, len: 0.39, dir: "left" },
        { x: 4.99, y: 4.75, len: 0.40, dir: "left" },
        { x: 3.345, y: 5.25, len: 0.40, dir: "down", label: "sourced draft" },
        { x: 4.59, y: 6.15, len: 0.40 },
        { x: 7.48, y: 6.15, len: 0.39 },
        { x: 10.36, y: 6.15, len: 0.24 },
      ],
      rail: {
        label: "Governance",
        sub: "spans every plane",
        x: 10.60, y: 2.72, w: 1.88, h: 4.06,
        items: [
          { label: "Evaluation harness", desc: "Golden set and LLM-judge scoring gate every prompt or model change." },
          { label: "Guardrails & PII", desc: "Input and output filters; redaction runs before any model call." },
          { label: "Observability & cost", desc: "Traces, token spend and latency, per request and per team." },
          { label: "Feedback loop", desc: "Reviewer edits and delivery outcomes become new eval cases." },
        ],
      },
      source: "Illustrative reference architecture \u2014 component names are examples, not a vendor recommendation.",
      notes: "Hook: ten components, but only one of them can stop a send. Point 1: the flow snakes left, back, and left again \u2014 the numbered badges are the reading order. Point 2: the review gate is the single emphasis. Point 3: governance is a column, not a step. Transition: how we rolled it out.",
    },
    // STEP LINE — the rollout method: phase brackets, two sign-off gates, detail rail.
    {
      layout: "stepLine",
      kicker: "The method",
      header: "The pilot only widened after the review step had proved itself reliable.",
      sub: "Owner, elapsed time, and the artifact each step hands to the next.",
      phases: [
        { label: "Build the pilot", from: 0, to: 2 },
        { label: "Prove and widen", from: 3, to: 4 },
      ],
      gates: [
        { after: 1, label: "Data sign-off" },
        { after: 3, label: "Go / no-go" },
      ],
      detailRows: ["Owner", "Elapsed", "Hands off"],
      steps: [
        { name: "Scope", desc: "Three teams, clear ground truth", details: ["Casper", "2 wks", "Scoping memo"] },
        { name: "Connect", desc: "Live knowledge base", details: ["Platform", "3 wks", "Indexed corpus"] },
        { name: "Measure", desc: "Week-8 usage, not week-1", details: ["Analytics", "4 wks", "Usage baseline"] },
        { name: "Prove the review", desc: "Zero unreviewed sends", details: ["Risk + Legal", "3 wks", "Review log"], hot: true },
        { name: "Widen", desc: "Add teams on evidence", details: ["Client PMO", "Ongoing", "Rollout plan"] },
      ],
      source: "Northwind rollout plan \u00b7 elapsed time as run, not as planned \u00b7 illustrative.",
      notes: "Hook: the order was deliberate. Point: the argued step is proving review \u2014 the connector goes hairline after it because scale waited on that gate. Transition: who actually does each step.",
    },
    // WORKFLOW MAP — swimlane: who owns each stage and where work changes hands. Four lanes,
    // five stages, nine handoffs (seven of them cross lanes). The hot step is the one leg the
    // assistant took over outright.
    {
      layout: "workflowMap",
      kicker: "How the work moves",
      header: "Design still ends with the consultant; what changed is who does the assembly in between.",
      sub: "Same five stages, same sign-off \u2014 three legs moved to the assistant.",
      zebra: true,
      cycleLabel: "Cycle time",
      lanes: [
        { name: "Delivery PM", role: "Scope, schedule, gate" },
        { name: "Client SMEs", role: "Source data, sign-off" },
        { name: "Lead consultant", role: "Owns the design" },
        { name: "Assistant", role: "Casper agents" },
      ],
      stages: [
        { name: "Intake", dur: "\u2248 2 wks" },
        { name: "Review", dur: "\u2248 1 wk" },
        { name: "Design", dur: "\u2248 3 wks" },
        { name: "Workshop", dur: "\u2248 4 days" },
        { name: "Handover", dur: "\u2248 2 wks" },
      ],
      steps: [
        /* 0 */ { lane: 0, stage: 0, span: 2, label: "Scope and schedule", note: "Sets the freeze date", mode: "human" },
        /* 1 */ { lane: 1, stage: 0, label: "Return the workbook", note: "1,200+ rows of intent", mode: "human" },
        /* 2 */ { lane: 3, stage: 1, label: "Gap and unit check", note: "Flags what is missing", mode: "ai" },
        /* 3 */ { lane: 2, stage: 1, label: "Confirm the gaps", note: "Consultant calls it", mode: "hybrid" },
        /* 4 */ { lane: 3, stage: 2, label: "Propose groupings", note: "Options A/B/C, sourced", mode: "ai", hot: true },
        /* 5 */ { lane: 2, stage: 2, label: "Choose the design", note: "Final authority here", mode: "human" },
        /* 6 */ { lane: 2, stage: 3, label: "Run the workshop", note: "Four days, live", mode: "human" },
        /* 7 */ { lane: 1, stage: 3, label: "Confirm intent", note: "SMEs in the room", mode: "human" },
        /* 8 */ { lane: 3, stage: 4, label: "Draft the design doc", note: "Every field sourced", mode: "ai" },
        /* 9 */ { lane: 2, stage: 4, label: "Edit and sign off", note: "Consultant owns wording", mode: "hybrid" },
        /* 10 */ { lane: 0, stage: 4, label: "Freeze the package", note: "Nothing builds before", mode: "human" },
      ],
      handoffs: [
        { from: 1, to: 2, label: "hands off" },
        { from: 2, to: 3, label: "flags" },
        { from: 3, to: 4 },
        { from: 4, to: 5, label: "decides" },
        { from: 5, to: 6 },
        { from: 6, to: 7 },
        { from: 6, to: 8 },
        { from: 8, to: 9 },
        { from: 9, to: 10, label: "gate" },
      ],
      source: "Northwind delivery workflow, current state vs. assisted \u00b7 stage durations are medians across three engagements \u00b7 illustrative.",
      notes: "Hook: follow the workbook, not the calendar \u2014 it changes hands seven times. Point: the accent step is the only leg the assistant took outright; every other AI cell still lands on a consultant. Transition: what that does to the schedule.",
    },
    // TIMELINE GANTT — left rail, elapsed/remaining bars, gate on the axis, week-8 status.
    {
      layout: "timelineGantt",
      kicker: "How the quarter ran",
      header: "Enablement, measurement, and review overlapped; only the go/no-go gate could move the date.",
      sub: "Solid bars are work already elapsed; hairline outlines are what remains at week 8.",
      months: ["Month 1", "Month 2", "Month 3"],
      weeks: 12,
      railLabel: "Workstream",
      unitLabel: "wks",
      phases: [
        { label: "Stand up", start: 0, end: 4 },
        { label: "Run and measure", start: 4, end: 10 },
        { label: "Decide", start: 10, end: 12 },
      ],
      lanes: [
        { title: "Enablement", catIndex: 0, start: 0, end: 4, pct: 100, meta: "Casper + L&D" },
        { title: "Live pilot", catIndex: 1, start: 2, end: 11, pct: 67, meta: "3 teams" },
        { title: "Measurement", catIndex: 2, start: 4, end: 12, pct: 50, meta: "Analytics" },
        { title: "Review hardening", catIndex: 4, start: 5, end: 9, pct: 75, meta: "Risk + Legal" },
      ],
      milestones: [
        { label: "KB connected", week: 3 },
        { label: "Go / no-go", week: 9, hot: true },
      ],
      today: 8,
      todayLabel: "Week 8",
      source: "Northwind pilot plan, weeks 1\u201312 \u00b7 completion self-reported at week 8 \u00b7 illustrative.",
      notes: "Hook: phases overlapped by design. Point: the week-9 gate is the only true dependency \u2014 everything else is already 60\u2013100% elapsed. Transition: which teams come next.",
    },
    // MATRIX 2×2 — which teams to add next (impact × onboarding effort).
    {
      layout: "matrix2x2",
      kicker: "What to fund next",
      header: "The next teams to add are the ones with clear ground truth and high volume.",
      xAxis: { low: "Harder to onboard", high: "Easier to onboard" },
      yAxis: { low: "Lower impact", high: "Higher impact" },
      quadrants: ["Fund on evidence", "Fund now", "Hold", "Quick wins"],
      points: [
        { label: "Claims", x: 0.72, y: 0.8, hot: true },
        { label: "Procurement", x: 0.58, y: 0.56 },
        { label: "Legal", x: 0.28, y: 0.68 },
        { label: "Field ops", x: 0.42, y: 0.3 },
        { label: "HR", x: 0.72, y: 0.27 },
      ],
      source: "Northwind expansion scoring, impact vs onboarding effort · illustrative.",
      notes: "Hook: not every team next. Point: Claims is the clear first add — high impact, easy to onboard. Transition: the phased plan to get there.",
    },
    // ROADMAP MATRIX — what scale looks like. The ask carries the accent on its name and on the
    // rule beneath it; the dashed rule marks where the plan actually stands.
    {
      layout: "roadmap",
      kicker: "What scale looks like",
      header: "Three more quarters take it from three teams to the whole operation, funding gated on evidence.",
      railLabel: "Phase",
      metaPos: "above",
      nowAfterPhase: 1,
      nowLabel: "We are here",
      rowLabels: ["Objective", "Scope", "Gate to fund"],
      phases: [
        { title: "Pilot", meta: "Jul–Sep · complete", cells: ["Test whether it sticks", "Support, Operations, Finance", "Cleared — deflection held at 58%"] },
        { title: "Q4 FY26", meta: "Oct–Dec · decision 15 Oct", hot: true, cells: ["Prove durability", "Same 3 teams, no support wheels", "Assisted-task share holds above 55%"] },
        { title: "Q1 FY27", meta: "Jan–Mar", cells: ["Widen carefully", "Add 4 teams with clear ground truth", "Per-team time saving beats 2 hrs"] },
        { title: "Q2 FY27", meta: "Apr–Jun", cells: ["Operate as normal", "Org-wide, embedded in the workflow", "Review step fully self-sustaining"] },
      ],
      source: "Northwind scale plan · phases and gates as proposed, not yet funded · illustrative.",
      notes: "Hook: four phases, each one gated. Point: the accent is the only phase we are asking you to fund today — everything right of the dashed rule is conditional on evidence we do not have yet. Transition: the same plan as a single line.",
    },
    // ROADMAP TRACK — the same arc as a journey: one track, one outcome per phase, four gates.
    {
      layout: "roadmapTrack",
      kicker: "The same plan, in one line",
      header: "Each phase only starts once the one before it has cleared its gate.",
      sub: "Solid track is elapsed; the hairline is what a yes today would fund.",
      pct: 25,
      phases: [
        {
          name: "Pilot", meta: "Jul–Sep", gate: "Week-8 review",
          outcome: "Three teams ran the assistant for a full quarter without a mandate.",
          items: ["3 teams", "Deflection 34% → 58%", "Risk + Legal see every send"],
        },
        {
          name: "Prove", meta: "Oct–Dec", gate: "Go / no-go", hot: true,
          outcome: "Usage holds after the support wheels come off, or we stop here.",
          items: ["Same 3 teams", "Assisted-task share above 55%", "Risk + Legal, unchanged"],
        },
        {
          name: "Widen", meta: "Jan–Mar", gate: "2 hrs saved",
          outcome: "Four more teams onboard on the same review path, no new tooling.",
          items: ["7 teams", "2+ hrs saved per person", "Team leads review, Risk audits"],
        },
        {
          name: "Operate", meta: "Apr–Jun", gate: "Casper exits",
          outcome: "Northwind runs it: own eval set, own budget line, own gate.",
          items: ["Org-wide", "Cost per request in budget", "Runs without Casper"],
        },
      ],
      source: "Northwind scale plan · one quarter elapsed of four · illustrative.",
      notes: "Hook: one line, four gates. Point: the accent phase is the only decision on the table — the three after it are what a yes buys the option on. Transition: a line from the pilot team.",
    },
    // 14 · QUOTE — a client line. Second breath slide, near the end.
    {
      layout: "quote",
      quote: "By week eight nobody asked whether to use it. They asked what to do with the afternoon it gave back.",
      attribution: "Support team lead, Northwind pilot",
      notes: "Hook: let the team speak. Point: the shift from 'should we' to 'what now' is the adoption signal. Transition: the sources behind these numbers.",
    },
    // 15 · SOURCES.
    {
      layout: "sources",
      header: "Sources & methodology",
      sub: "Northwind is a fictional example; the figures above are illustrative. These are the inputs a real readout would cite.",
      sources: [
        "Pilot telemetry — weekly active users, deflection rate, weeks 1–12.",
        "Time-tracking — hours self-estimated against a pre-pilot baseline.",
        "Usefulness survey — 180 responses, 5-point scale, week 12.",
        "Support queue — ~1,200 tickets/week, first-response deflection.",
        "Review log — count of sends, unreviewed-send exceptions.",
        "All figures illustrative for template demonstration; no real client data.",
      ],
      notes: "Hook: the numbers were illustrative; the method is real. Point: five instrumented sources, one honest caveat. Transition: close.",
    },
    // 16 · CLOSING.
    {
      layout: "closing",
      title: "The pilot worked. We are asking to fund Q4",
      sub: "Same three teams, one more quarter, decision by 15 October.",
      contact: "casperstudios.xyz",
      notes: "Hook: one-line recap, then the ask. Point: same three teams, one more quarter, decision by 15 October \u2014 say the number out loud and stop talking. Transition: take questions.",
    },
  ],
};
