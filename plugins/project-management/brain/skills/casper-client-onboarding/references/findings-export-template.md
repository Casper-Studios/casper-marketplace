# Discovery Findings Export — Template

*Phase 2, Step 6 reference. Copy this skeleton into the project folder as `[Client] Discovery Export` and fill it in. Delete the italic guidance notes as you go.*

---

# [Client] Discovery Export — Full Picture

*As of [date]. Zero context assumed — written so someone with no prior exposure to this engagement could read it and act.*

## Background

*One short paragraph: what is Casper building, for whom, and why does it matter to the client? Then list the discovery inputs — every session (date, attendees, track) and any async inputs (SME follow-up emails, doc drops, sponsor approvals). If a data-profiling branch ran, note how many files were analyzed across how many runs.*

---

## 1. Question-Status Table

*Reproduce the Phase 1 discovery question list, grouped by track. Mark each: Answered / Partially answered / Still open. Do not round a partial up to answered — the honesty of these marks is the point.*

### Technical Track
| # | Question | Status |
|---|----------|--------|
| T1 | | |

### Business Track
| # | Question | Status |
|---|----------|--------|
| B1 | | |

### Data / Validation Track
| # | Question | Status |
|---|----------|--------|
| D1 | | |

---

## 2. Findings Per Question

*For each Answered or Partially-answered question: the actual answer, with the source session named in-line. Preserve specifics — real table names, field names, file paths, percentages, business-rule definitions. Do not summarize the detail away; the detail is what the engineer needs. Mark partials as (Partial) and say what's still missing.*

### Technical Track
**T1 — [question] ([source session])**
[finding]

### Business Track
**B1 — [question] ([source session])**
[finding]

### Data / Validation Track
**D1 — [question] ([source session])**
[finding]

---

## 3. What Surprised Us

*The highest-value section. Anything that contradicted a prior assumption or wasn't anticipated. Explicitly hunt for inversions — things that turned out to mean the opposite of what was assumed. Number them; each should name what was assumed Before and what's true Now.*

1. **[short title]** — Before: [assumption]. Now: [reality]. Why it matters: [impact on build or scope].

---

## 4. Still Open / Unresolved

*Three buckets.*

**From the original question list (not yet answered):**
- [item] — [why still open / what's needed]

**New questions discovery created:**
- [item]

**Pending responses (who owes what):**
- [name] — [what they owe] — [channel, date sent]

---

## 5. Requirement Changes

*Each change as Before / Now / Why. Flag any scope nuance that wasn't in the original plan. This section is what the build and the Week-4 readout depend on.*

### Change 1: [title]
- **Before:** [original requirement/assumption]
- **Now:** [revised requirement]
- **Why:** [what discovery surfaced that forced the change]

*Scope nuances (anything that changes effort, risk, or what "done" means but isn't a clean requirement swap):*
- [nuance]

---

## 6. Linear Impact

*The proposed board reconciliation. List it here; execute it in Step 6b after PM confirmation.*

**Tickets to close + archive:**
- [ID] — [title]

**Build tickets needing description updates:**
- [ID] — update to reference [spec doc]; add [specifics]

**New tickets to create:**
- [title] — [assignee], [priority], [milestone]

**Tickets to cancel (no longer relevant):**
- [ID] — [reason]

**Missing-but-implied tickets (blockers with no ticket yet — mark Urgent):**
- [title] — [assignee]

**Hygiene checks before presenting:**
- Numbering integrity — no duplicated ticket IDs
- Milestone correctness — documentation tickets in build weeks, not Week 1

---

## Appendix: Sources Referenced

*List the transcripts and documents read in full for this export, so coverage is auditable. Note explicitly anything NOT checked — a thin section usually means a missing source, not a formatting problem.*

**Read in full:**
- [session / doc]

**Not checked / not available:**
- [item]
