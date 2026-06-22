---
name: casper-client-onboarding
description: >
  Casper Studios client onboarding playbook for new engagements. Use this skill
  whenever a PM is onboarding a new client, ramping up on an existing engagement,
  setting up a new project in Linear, preparing for discovery sessions, drafting
  outreach to client stakeholders, or synthesizing post-discovery interview outputs
  back into project requirements. Triggers include: starting a new client, help me
  onboard to a client, set up Linear for a project, I have a new engagement, help
  me prep for discovery, I just got added to a client project, or any combination
  of reading client docs + setting up project infrastructure + reaching out to
  client contacts.
---

# Casper Client Onboarding Playbook

This skill codifies how Casper PMs ramp up on a new client engagement and get the project infrastructure in place. It is built from the Cacique Foods onboarding (May 2026), refined from the Pendra onboarding (June 2026), and further refined from the Blueberry engagement (June 2026); update it after each new engagement to capture refinements.

The playbook has two phases:
- **Phase 1: Pre-discovery** (fully codified) — ingest context, brief the PM, build question list, email sponsor, set up Linear
- **Phase 2: Post-discovery** (codified) — synthesize discovery sessions into a structured findings export, optionally profile client data, and reconcile requirements and Linear

**This is a sequential, dependent flow — not a checklist. Pause for PM confirmation at every marked checkpoint before proceeding.**

---

## Engagement Type: Fork Here

*Codified from the Blueberry engagement — June 2026.*

Before starting Phase 1, identify which type of engagement this is. The flow adapts to each.

**DISCOVERY** (default): Casper finds where the problems are, understands the current state, and recommends what to build. The client has not yet defined the solution. Pendra and Cacique are DISCOVERY examples. Run the full playbook as written.

**BUILD**: A working product already exists. Casper hardens it and adds features. The problem space is known; the work is prioritization and execution. Blueberry is the canonical BUILD example.

For BUILD engagements, adapt as follows:
- Skip problem-discovery questions. The problem is already known.
- Focus the kickoff on feature prioritization. Have the client stack-rank what matters most, then establish the MVP scope within each feature before any deeper discussion.
- Surface customer context and monetization angle early: who uses this, who pays, and what does a good outcome look like for them.
- Understand build sequencing and technical gotchas before writing tickets.
- In the Kickoff Prep Doc, replace the discovery question tracks with a prioritization agenda and a feature-by-feature deep dive plan. Defer technical details to sessions after the kickoff.

---

## Phase 1: Pre-Discovery Onboarding

### Step 1: Ingest all available context

**Before pulling any source, detect what has already happened.** Has a sponsor email already been sent? Is kickoff already booked? Has a weekly cadence been negotiated? Adapt to the actual state — augment what's in place, don't redo it. The playbook assumes a clean start; real engagements rarely are.

Pull and synthesize four sources **before taking any action**:

**1. Google Drive — project folder**
Look for and read all of:
- Statement of Work (SOW) — scope, deliverables, out-of-scope, timeline, fixed fee, team
- Onboarding brief — relationship history, key stakeholders, current status, immediate next steps
- POV or strategy doc — what Casper believes, recommended architecture, risks
- Data/access request doc — what Casper needs from the client
- Partner or legal agreement — IP ownership, data handling, confidentiality

Key things to extract:
- What does Casper own vs. what does the client own?
- What is explicitly out of scope?
- Who are the key client stakeholders and what are their roles?
- What are the gating assumptions (e.g. data movement approval)?
- What is the actual engagement timeline (SOW date vs. kickoff date — these are different)?

**Drive folder scaffold**
Locate the client's `[NNN] Client` folder. If the standard subfolders are missing, create exactly these four: `Agreements & SOW`, `Data & Access`, `Meetings & Onboarding`, `Discovery & Research`. Check whether folders already exist before creating anything — on Pendra (June 2026), we nearly duplicated an existing client folder. Consolidate strays — root-level docs and legacy subfolders — into the scaffold.

*Tooling constraint:* the Drive connector can copy but not move or delete. Shared or legal docs must be drag-moved manually by the PM to preserve links and comment history.

**2. Slack — internal client channel**
Look for channels named `#internal-[client]` or `#emblem-[client]`. Read for:
- Relationship history and how the engagement was sold
- Decisions already made before the PM joined
- Current blockers or open questions
- Team dynamics — who's the lead, who's the engineer, who's the client sponsor

**3. Fireflies — most recent internal call transcript**
Pull the most recent PM + engineer sync transcript. Look for:
- Current status and what's in motion
- PM's immediate action items
- Engineer's action items
- Any constraints or dependencies called out on the call

Also pull the sales or pre-engagement call transcript if one exists. Read it before building any question list. Only ask what is genuinely still open after reading it. Do not re-discover what the client already walked you through during the sale or a product demo.

**4. Gmail — client-facing threads**
Search for threads involving the client's domain. Look for:
- Intro threads and "Week 0" kickoff setup
- Scheduling and logistics chains
- Attachments (data files, SOW drafts, access requests)
- Any sponsor or client reply that carries philosophy, constraints, or approval signals

On Pendra (June 2026), the Week 0 email thread was the highest-signal source — access status, kickoff scheduling, client philosophy, and the discovery attachments all lived there, none of it in Slack or Drive.

*Tooling constraint:* the Gmail connector cannot download attachments — the PM saves them to `Data & Access` by hand, then verify they arrived.

**Data & Access dedupe pass**
After saving email attachments, scan `Data & Access` for duplicates. Flag byte-identical files for the PM to delete. Flag near-identical files (e.g. two versions a few bytes apart) for a content diff or a question to the client — don't assume which is canonical.

**Connector completeness**
Never assert a thread or channel was read "end to end" from connector data alone — confirm coverage with the PM. Known blind spot: emails in the sent folder may be invisible to the Gmail connector.

**Do not take any action until all four sources are ingested.**

---

### Step 1b: Brief the PM

Write a PM briefing before doing anything else. This is not a bullet-point summary of facts — it is a narrative briefing written the way a smart colleague who has already done all the reading would brief you before a meeting. It should read in under 2 minutes.

**The briefing must cover:**

- **The engagement in one paragraph** — what is Casper actually being asked to build, for whom, and why does it matter to the client?
- **The people** — who are the real decision makers (not just who's listed in the SOW), what do you know about their personalities or priorities from Slack, and who is the Casper team you're working with?
- **The vibe** — what's the tone of the internal Slack channel? Is this smooth and well-sold, or is there tension, ambiguity, or something unresolved? Read between the lines.
- **What's already been decided** — commitments or directions set before the PM joined that they need to know about
- **The actual timeline** — kickoff date, key milestones, end date. Not the SOW date — the real dates.

**The briefing must also include a FLAGS section.** This is non-negotiable. Explicitly call out:
- Any scope ambiguity that could cause problems later
- Any gating blockers that must be resolved before work can start
- Any tension, risk, or sensitivity picked up from Slack or transcripts
- Anything that was promised or implied that isn't clearly in the SOW
- If there are no flags, say so explicitly: "No flags identified."

**The briefing must also include a WHAT WE NEED TO DO NOW section** — a short, prioritized list of the PM's immediate next moves. Not findings. Concrete actions, in order.

**Quality bar:** After reading this briefing, the PM should feel like they've been on the project for a week. Write in plain, direct sentences — avoid negation-heavy phrasing. Hard cap: readable well under 2 minutes. If it reads like a document summary, rewrite it.

> **⏸ CHECKPOINT — pause here.** Show the briefing to the PM and wait for explicit confirmation before proceeding. The PM may have corrections, additional context, or want to resolve a flag before moving forward. Do not proceed to Step 2 until the PM says so.

---

### Step 1c: Confirm Week 0 gates are clear

Before outreach starts, review this checklist with the PM. Mark each item live — don't assume. The build clock doesn't start until these are resolved.

- [ ] Client-environment access confirmed (e.g. email alias inside the client's Claude org, if applicable)
- [ ] Pilot corpus / initial data received, or delivery date confirmed
- [ ] Data request issued to the client
- [ ] Upfront payment confirmed
- [ ] Kickoff call booked
- [ ] Weekly cadence (day, time, attendees) confirmed

Surface any open item as a flag. If the PM is unsure, ask — don't skip.

---

### Step 2: Build the Kickoff Prep Doc

*Codified from the Pendra engagement — June 2026.*

The output of this step is a single artifact: the Kickoff Prep Doc. It serves as the PM's prep document for the kickoff call and as the Phase 1 checkpoint deliverable. Draft it section by section with the PM in chat. Only save to Drive after the PM approves the assembled doc. Do not stack v1/v2/v3 files.

**The doc has seven sections, in this order:**

**1. Title line**
`[Client] Kickoff Prep · [date]`

**2. Framing paragraph**
Two sentences, plain English: what we are actually building this engagement, and what is deliberately deferred. Written so a non-technical exec gets it in one read. Doubles as the anchor slide on the kickoff deck.

**3. Attendees**
Name, role, one parenthetical of context each.

**4. What We Already Know**
~4 bullets max, one line each. Client business facts only: what the company does, who its customers are, what the pain is. Never engagement logistics (scope, timeline, deliverables). Those belong in the briefing, not here. Hard facts pulled from the SOW, proposal, client memos, and prior comms. These mark what not to re-ask on the call.

**5. Session Objectives**
~4 bullets. Learning goals and plan confirmations only. Never asks or document requests — those are "What We Need" items, not objectives. Test: an objective starts with *understand / get specific / identify / confirm / build rapport.*

**6. Questions**
Split into two layers.

*Kickoff-call questions* (include in this doc): high-level questions about why, success, and prioritization. Sized for a 30-minute slot. Order by priority because you rarely finish. Mark lower-priority categories as deferred to deep-dive sessions so the PM knows what to skip if time runs short.

*Deep-dive questions* (draft after the kickoff, not now): detailed and technical, written after reviewing the data and the kickoff output. Do not write these at pre-kickoff stage.

Grouped under category headers. Adapt to the engagement (e.g. Success metrics and goals, Business context, Pain points, Workflows and systems, AI readiness and compliance). Draw from the Discovery Kickoff Playbook standard question set and adapt to the client. Offer the full relevant kickoff-call menu and let the PM prune to 8-12. Do not pre-cut for time without asking.

**7. Hypotheses to Test**
3-4 bullets. A hypothesis is a falsifiable pre-work guess where being right or wrong changes what we build. Facts the client already stated belong in What We Already Know, not here. Strongest form: claim plus consequence — "If true, X. If false, Y."

---

**Style rules — non-negotiable. The PM has rejected drafts that violate these.**
- Plain short sentences. No em dashes anywhere. No brackets, inline citations, parenthetical source references, or quotes inside bullets.
- One line per bullet in What We Already Know and Hypotheses.
- No "derived from" metadata, no version-note clutter, no decorative dividers, no ALL-CAPS section heads.
- Simple words over consulting words: "grades people" not "executive assessment tooling", "shared filing system" not "knowledge repository".
- Sources feed the content; they never appear in the document.

**Sources — build in this order:**
1. Discovery Kickoff Playbook standard questions
2. SOW and proposal
3. Client data room and any profiling output
4. Prior client comms — email, Slack, and any working artifacts (skill files, prompt sheets, sample outputs) that arrived before the session. Save artifacts to `Data & Access` before pulling from them. Treat them as primary methodology-capture evidence and book a walkthrough with whoever built them.

---

**Example: Pendra Kickoff Prep, June 2026**

*The gold-standard reference output. Use this to calibrate framing, bullet length, question depth, and hypothesis form.*

---

Pendra Kickoff Prep · June 3, 2026

In the next 6 weeks we build the foundation: a shared filing system for the firm, the methodology written down in one place, naming conventions, one past engagement loaded in as a test, and the partners trained to use it. The analytical brains, the judgment layer, and the compounding memory come in later phases, but everything we build now is shaped so they can sit on top.

Attendees (Kickoff: Mon June 8, 1:30-2:00 PM ET)
Brandon Heck, Partner (engagement sponsor, signed agreement)
Chris Nichols, Partner (runs the Pendra and Blueberry relationships)
Trendler and Danie, Partners (attendance TBD)
Hirsch Keshav, Casper Studios PM
Michael Slocum, Casper Studios AI Engineer
Giorgio Barilla, Casper Studios AI Ops

What We Already Know
Pendra is a 4-partner human capital diligence firm serving PE sponsors
Three engagement types: full org diligence on new platform deals, standalone executive assessments, and modular reviews like AI readiness
Each partner uses their own Claude instance their own way. Files sit across personal computers and cloud storage with no shared process
Methodology splits two ways: the 7-dimension OQ Framework is Pendra owned, the individual assessment framework is licensed from Blueberry
Core tools today: Claude, Hogan assessments, an org readiness survey, Fireflies for transcription, Word and PowerPoint deliverables
Biggest stated pain: post-interview synthesis, and the fact that practitioner knowledge never accumulates across engagements

Session Objectives
Understand where the partners lose the most time in a typical engagement, in their words
Get specific on how the four workflows differ and how much is style vs methodology
Identify 2-3 hypothesis areas for the partner working sessions to probe
Confirm the discovery plan: one session per partner, pilot deal materials, methodology docs

Questions
Success metrics and goals:
What does success look like at the end of these six weeks? If Pendra OS solved one thing, what would make the investment worthwhile?
What would each of you need to see to actually use this system on your next live engagement, rather than falling back to your own Claude setup?
Are there specific metrics or KPIs you'd want to move?
What would the team need to see to feel confident about adopting new tools?
Business context:
What are the key priorities for the business right now? Where is leadership focused?
Are there any major initiatives, transitions, or milestones coming up that we should be aware of?
How many engagements does the firm run per year, by type (full diligence, standalone assessment, modular)? How do you expect that mix to change?
Any upcoming engagements, hires, or commitments in the next 8 weeks we should plan around, including live deals that could serve as the pilot?
Pain points:
In a typical engagement, where does the most manual time go? What feels like it should be easier than it is?
When deal timeline pressure hits, what gets rushed or cut first?
Workflows and systems:
How does information flow between the four of you? Are there any handoff points that create friction?
AI readiness and compliance:
Where has AI output burned you or come closest to it: confident sounding errors, missed nuance, misattributed quotes? What do you double check every time?
Any client side compliance, confidentiality, or bias concerns we must design around, given outputs inform hiring and investment decisions?

Hypotheses to Test
The four partners differ in tools and prompts, but the underlying method is the same. If true, one shared system works. If false, Pendra OS needs flexibility per partner
Post-interview synthesis takes the most time and is the first thing to suffer under deal pressure
Migrating scattered historical materials into one system is the key delivery risk, and we need to scope it early

---

> **⏸ CHECKPOINT — pause here.** Present the assembled Kickoff Prep Doc to the PM section by section. Wait for explicit approval before saving to Drive or proceeding to Step 3. Confirm: the framing is accurate, questions are specific to this engagement, hypotheses are falsifiable, and nothing in What We Already Know needs re-asking on the call. Do not proceed to Step 3 until the PM approves.

---

### Client-Facing Document Style

*Applies to the Kickoff Prep Doc, kickoff decks, and any other document the client sees. Codified from the Blueberry engagement (June 2026).*

- Terse. One fact per bullet. No padding.
- Narrative opener of around 50 words max. State what we are building and what is deferred. Nothing else.
- Low fanfare. Push credentials to an appendix. Trim any team slide to the people actually working this engagement.
- Frame asks as collaborative questions, not requirements or demands.
- No em dashes. No en dashes. Use a colon or a comma instead.

---

### Step 3: Email the executive sponsor to set up SME access

**This step is conditional.** Skip it if the kickoff is already booked and the relevant client contacts are already engaged. Augment what exists rather than redoing it. On Blueberry (June 2026), this step was skipped entirely because access and the kickoff were already arranged.

When you do run this step: do not go directly to the SME. Go through the executive sponsor first.

**The rule:** the sponsor email must be specific enough that the SME could read it and immediately know what to prepare. If you can't write a specific email yet, the Kickoff Prep Doc isn't done.

**Email structure:**
- One-line self-intro (name, role, company, engagement)
- One-sentence ask (intro to [SME name] for [specific purpose])
- 3-5 bullet points drawn directly from the approved Kickoff Prep Doc questions — what the call will cover
- Short sign-off

**Voice rules (Casper):**
- No filler openers ("Hope you're doing well", "I hope this finds you")
- First-person ownership of the ask ("I'd love to" not "we'd love to")
- "Thanks a ton" not "Thanks so much"
- Short, punchy sentences — no redundancy

Every engagement will follow this flow: **sponsor → SME intro → technical discovery session → business discovery session.** The two discovery sessions may be with the same SME or different people depending on the client.

> **⏸ CHECKPOINT — pause here.** Show the draft email to the PM and wait for explicit approval before any further action. The PM must review tone, specificity, and accuracy before this goes anywhere. Do not proceed to Step 4 until the PM approves.

---

### Step 4: Set up Linear

**Before building the board:** if any flags from Step 1b remain unresolved — especially scope ambiguity or timeline uncertainty — surface them now and ask the PM how to proceed. Do not build a Linear board on a shaky foundation.

**Project setup:**
- Team: Product & Delivery
- Name: `[Client] — [Project Name]`
- Description: full scope summary including what Casper owns, what client owns, out-of-scope, Casper team, client stakeholders
- Start date: SOW effective date
- Target date: engagement end date

**Milestones:**
- Set based on the **actual engagement timeline** — use the kickoff date, not the SOW date
- Typical 4-week engagement: Week 0 (provisioning), Week 1 (discovery), Weeks 2-3 (build), Week 4 (evaluation + readout)
- Set target dates per milestone accordingly

**Ticket principles:**
- **Outcome-oriented, not task-oriented.** The ticket is what "done" looks like, not the steps to get there. Scheduling and coordination are PM overhead — they live in Slack, not Linear.
  - Wrong: "Schedule Jack Fish discovery call"
  - Right: "Circana data structure & Power BI discovery with Jack Fish"
- **The output test:** before creating a ticket, ask "is this a distinct output, or is it a step inside an existing output?" If it's a step, don't create it — it belongs in your head or in Slack.
  - Wrong: "Get Alan approval to share Q&A examples" (a step toward building the evaluation set)
  - Right: "Build evaluation question set" (the output)
- **Titles can be self-explanatory.** Not every ticket needs a description. If the title is clear and unambiguous, leave the description empty. Do not pad tickets with descriptions for the sake of it.
- **Don't create intermediary step tickets.** Collecting reports, scheduling calls, getting approvals — these are steps inside bigger outcome tickets. Only create a ticket if there is a distinct deliverable at the end of it.
- **One ticket per distinct output.** If two tickets are feeding the same outcome, they're the same ticket.

**Milestone assignment rules:**
- **Week 0** — only for tasks that happen before kickoff (provisioning, access, legal). If a task runs concurrently with the build, it belongs in Weeks 2-3.
- **Week 1** — discovery outputs only (sessions with client, data received, question list). Do not put build deliverables here.
- **Documentation tickets (data dictionary, business logic layer, ETL docs) belong in Weeks 2-3** — they are build-phase outputs, not discovery outputs. A common mistake is putting them in Week 1 because they were discussed during discovery.
- **Weeks 2-3** — all engineering build work, plus any PM tasks running concurrently with the build (API research, ingestion architecture, stakeholder coordination)
- **Week 4** — evaluation, readout, handoff only

**Ticket lifecycle rules:**
- Move tickets to **In Progress** when work actually starts — don't leave them in Backlog if someone is actively working on them
- **Archive Done tickets** after they complete to keep the board clean — Done tickets that are visible create noise
- Cancel tickets that are no longer relevant immediately — don't leave them in Backlog as clutter

**Labels (Product & Delivery team):**
- `Administrative` — PM coordination, client-facing logistics
- `Discovery` — research, interviews, data collection
- `Delivery` — build work, outputs, deliverables
- `Document` — documentation artifacts (data dictionary, ETL docs, business logic)

**Priorities:**
- Urgent (1) — gating items, blockers, current week
- High (2) — required deliverables
- Medium (3) — advisory, nice-to-have
- Low (4) — future consideration

**Dependencies:**
- Always check for blocker relationships before finalizing the board
- Common pattern: data movement approval blocks environment setup

**Assignees:**
- PM owns: discovery coordination, client-facing work, evaluation sessions, readout
- Engineer owns: technical build, data prep, ETL, agent, MCP server, validation

**Reference: ITA Group project in Linear** is the canonical Casper template for a short client engagement. Check it when in doubt.

> **⏸ CHECKPOINT — pause here.** Show the PM the proposed board structure before creating anything in Linear. Confirm project name, milestones, and key tickets are correct. Do not create tickets until the PM approves.

---

## Phase 2: Post-Discovery Synthesis

*Codified from the Cacique Foods engagement — May–June 2026.*

Phase 2 turns raw discovery (interview transcripts, plus client data files on technical engagements) into a single authoritative findings export, then reconciles that export against the requirements and the Linear board. The findings export is the deliverable — everything downstream (engineer handoff, the Week-4 readout, requirement changes) is generated from it.

**Discovery is rarely a clean two-interview set.** The original plan assumed one technical + one business session. In practice it is a *cluster* of 3–5 sessions over a few days, often anchored on one SME (the analyst who owns the data), with the executive sponsor and others appearing in subsets. Do not hardcode a fixed session count. The first action of Phase 2 is to establish what the actual session set was.

### Step 5: Establish the discovery session set

Before synthesizing anything, list every discovery input that actually occurred:
- Pull all relevant Fireflies transcripts for the discovery window (search by client name and date range, not by assumed meeting titles).
- For each session, record: date, attendees, and which discovery track it served (technical / business / mixed).
- Note any async inputs that carry discovery signal — follow-up emails from the SME, a shared documentation drop, a sponsor reply approving access.

Identify the **anchor SME** (usually the single person who owns the data and reporting) and the **sponsor** separately. They have different roles in the synthesis: the anchor gives you ground truth on data and workflow; the sponsor gives you success criteria and business questions.

> **⏸ CHECKPOINT — pause here.** Confirm the session list with the PM before synthesizing. If a session the PM expected is missing from Fireflies, resolve that first — a missing transcript means a hole in the synthesis.

---

### Step 5b: (Conditional) Profile the client data — data-heavy engagements only

**Run this branch only if the engagement involves building against client data files** (a data pipeline, analytics agent, ETL, or anything where the client hands over raw exports). Skip entirely for pure advisory, design, or workflow engagements.

Profile every file the client shared, in isolated runs, and treat the output as discovery evidence on equal footing with the interviews. The goal is to confirm or *invalidate* what the interviews implied about the data.

For each file, establish:
- True format and structure (delimiter, header rows/preambles, encoding), the grain (one row = what?), row count, and column inventory with real types.
- The join keys, and whether they are clean. Flag composite keys built from raw string concatenation, embedded keys that need parsing, trailing whitespace, and uniqueness rate of the intended primary key.
- Whether the file is a raw fact source, a transformation output, a mapping/dimension table, or a finished report — and whether any "report" is secretly a primary ETL input.
- Staleness: latest data date in the file vs. when it was last refreshed.

**Why this branch matters:** on Cacique, data profiling drove roughly half the requirement changes and caught assumption inversions the interviews alone would have missed (e.g. a file naming convention that meant the opposite of what everyone assumed; four raw files that bypassed the transformation layer entirely). Profiling is not optional polish on these engagements — it is where the real spec comes from.

Capture the profiling output as an engineering spec document in the project (e.g. `engineering_requirements.md`). This becomes the definitive build reference handed to the engineer in Step 7.

> 📄 Reference: [references/data-room-profiling.md](references/data-room-profiling.md) — full per-file mechanics, triad reconstruction, join-key integrity checks, and inversion-hunting guide.

> **⏸ CHECKPOINT — pause here.** Share the data-profiling findings with the PM. Specifically surface any finding that contradicts what an interview implied — those are the highest-value items and the most likely to change scope.

---

### Step 6: Produce the discovery findings export

Synthesize all sessions (and, if applicable, the data profiling) into a single **findings export** — one self-contained document that someone with zero context could read and act on. This is the canonical Phase 2 artifact. Save it to the project folder and title it `[Client] Discovery Export`.

The export has six required sections, in this order:

1. **Question-status table** — every discovery question from the Phase 1 list, grouped by track, marked `Answered`, `Partially answered`, or `Still open`. The honesty of the "partial" and "open" marks is the point — do not round a partial up to answered.

2. **Findings per question** — for each answered/partial question, the actual answer, with the **source session named** (e.g. "Data Deep Dive Round 2"). Preserve specifics: real table names, field names, file paths, percentages, business-rule definitions. Do not summarize the detail away — the detail is what the engineer needs.

3. **What surprised us** — anything that contradicted a prior assumption or wasn't anticipated. Treat this as a required muscle, not a footnote: explicitly hunt for assumption *inversions* (things that turned out to mean the opposite of what was assumed). This section is where discovery earns its cost.

4. **Still open / unresolved** — questions not yet answered, PLUS new questions discovery created, PLUS who owes a response and on what (SME, sponsor, IT).

5. **Requirement changes** — for each change, state it as **Before / Now / Why**. Flag any scope nuance that wasn't in the original plan. This is the section the readout and the build both depend on.

6. **Linear impact** — the proposed board reconciliation (see Step 6b). List tickets to close, descriptions to update, tickets to create, and tickets to cancel — but do not execute yet.

> 📄 Reference: [references/findings-export-template.md](references/findings-export-template.md) — copy this skeleton into the project folder as `[Client] Discovery Export` to start the export.

> **⏸ CHECKPOINT — pause here.** Share the full export with the PM. Confirm the synthesis is accurate and complete before any Linear changes. The export can only contain what discovery actually surfaced — if a section looks thin, that is a real gap to fill, not a formatting problem.

---

### Step 6b: Reconcile Linear (auto-update with a confirm gate)

After the PM confirms the export, **apply the Linear changes directly** — do not ask for per-ticket approval. Make all of the following changes, then present the full diff in one confirmation at the end.

Apply:
- **Close + archive** discovery tickets whose sessions happened and outputs were received.
- **Update build-ticket descriptions** with discovery specifics — but keep them lean: reference the engineering spec document and link it rather than pasting the spec into the description. Research findings and profiling output go in ticket *comments*, not descriptions (per Step 7).
- **Create new tickets** for distinct outputs discovery surfaced (new data sources, new blockers, new research tasks). Apply the Step 4 ticket principles — outcome-oriented, one ticket per output, no intermediary-step tickets.
- **Cancel** tickets discovery made irrelevant (e.g. a planned session that's no longer needed, intermediary steps that got absorbed into a larger ticket).
- **Create missing-but-implied tickets** — blockers that have no ticket yet (e.g. a missing mapping file that gates the build, an access-provisioning task). Mark these Urgent.

Then run two hygiene checks before presenting:
- **Numbering integrity** — confirm no ticket identifier is duplicated. (On Cacique, one ID got reused for two different tickets — catch this.)
- **Milestone correctness** — apply the Step 4 rules. Documentation tickets (data dictionary, ETL docs, business logic) belong in the build weeks, not Week 1, even though they were discussed during discovery.

> **⏸ CHECKPOINT — pause here.** Present the complete set of Linear changes as one diff — closed, updated, created, cancelled — and wait for the PM's confirmation. This is the single confirm gate for all board changes; the PM is reviewing the whole reconciliation at once, not approving tickets one by one.

---

### Step 7: Prepare engineer handoff

Before the engineer starts building, prepare a clean handoff package:

**What the engineer needs:**
- Link to the engineering spec document (the Step 5b profiling output) — the definitive build spec
- Link to the discovery findings export
- The Linear board with their assigned tickets
- Access to any raw files or data they need

**What goes in Linear ticket descriptions (engineer's perspective):**
- The outcome (what "done" looks like)
- Link to the spec document
- Hard blockers called out explicitly
- Pre-build steps if any (e.g. "extract Power Query M scripts before writing ETL code")
- Keep it short — engineers prefer lean tickets with a spec reference over walls of text

**What goes in ticket comments (not descriptions):**
- Research findings, data profiling outputs, background context
- Per Michael Slocum (Casper engineer): "Keep the ticket macro-focused on what needs to be done. Any findings you've done on your own are attached in the comments."

> **⏸ CHECKPOINT — pause here.** Confirm with the engineer that they have everything they need to start. Do not assume — ask explicitly.

---

## The Through-Line

Every step feeds the next:
- Can't brief the PM accurately without reading between the lines of Slack and transcripts
- Can't write good discovery questions without the briefing as a foundation
- Can't email the sponsor without an approved question list
- Can't build Linear without knowing scope boundaries and actual timeline
- Can't update Linear post-discovery without good questions going in

It is a sequential, dependent flow — not a checklist. The checkpoints are not optional.
