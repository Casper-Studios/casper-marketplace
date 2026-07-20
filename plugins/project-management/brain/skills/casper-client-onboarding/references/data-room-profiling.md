# Data-Room Profiling (Phase 2, Step 5b reference)

*Loaded only on data-heavy engagements. Codified from the Cacique Foods engagement (May–June 2026) and generalized.*

## The premise: every data engagement has a data room

When a client hands over data, they are handing over three things, whether or not they label them:

- **Inputs** — raw data as it arrives from a source (vendor exports, system dumps, API pulls, manual extracts).
- **Transformations** — the logic that turns inputs into something usable (Excel/Power Query steps, SQL, mapping/crosswalk tables, the analyst's manual cleanup).
- **Outputs** — the finished artifacts leadership actually consumes (dashboards, weekly reports, decks).

The data room is almost never organized this way. It is a flat dump of files with inconsistent names. **The core job of profiling is to reconstruct the input → transformation → output triad from that flat dump, and to confirm or invalidate what the interviews claimed about it.** Reconstructing this triad *is* the technical discovery. The build spec falls out of it.

Treat profiling output as discovery evidence equal in weight to the interview transcripts. Where they disagree, the files win — but the disagreement itself is a finding (see "Hunt for inversions" below).

## When to run this

Run it whenever the client shares a folder of data files and the engagement builds against them (pipeline, analytics agent, ETL, migration, anything data-backed). Skip for pure advisory, design, or workflow engagements. If in doubt, the test is: *will an engineer write code against these files?* If yes, profile.

## Per-file mechanics: use the csv-analyzer skill

For the actual statistical profile of a single file — types, distributions, missing values, quality score, correlations — do not hand-roll it. Use the existing **`csv-analyzer`** skill:

```bash
cd ~/.claude/skills/csv-analyzer/scripts
python3 analyze_csv.py /path/to/file.csv
```

This reference file covers what csv-analyzer does **not**: cross-file structure, the triad reconstruction, join-key integrity across files, and reconciliation against discovery findings.

## How to run it: isolated passes, not one big read

Profile in **separate, isolated runs** — one focused pass per file or per small related group — rather than loading every file into one context. This is the fan-out pattern: each file gets a clean context so findings don't cross-contaminate, and a large file doesn't blow the context window for the others. On Cacique this was five runs across 28 files.

Within each run, do not load raw file contents into the main context. Run a script that reads the file and returns only the profile (structure, sample, key stats). The file bytes stay on disk; only the summary consumes tokens.

Practical guardrails for large data rooms:
- Cap how much of any file you read — header + structured sample + computed stats, never the full file into context.
- Avoid resource-heavy operations that would prevent parallelizing the runs.
- Number the runs and keep a running index of which files each run covered, so coverage is auditable and nothing is silently skipped.

## What to establish for every file

1. **True structure.** Format, delimiter, encoding. Critically: **how many preamble rows precede the real header?** Vendor exports frequently have 2–3 banner rows, which makes every metric column read as text until you skip them. Record the exact `skiprows` and the required type casts.

2. **Grain.** One row = what? (a UPC-week? a store-month? a brand-market?) Get this wrong and every aggregation downstream is wrong.

3. **Role in the triad.** Classify each file as raw input, transformation output, mapping/dimension table, or finished report. Then challenge the classification — see the next section.

4. **Join keys and their integrity.** Identify the intended primary/foreign keys and test them:
   - Uniqueness rate of the primary key (is it actually unique, or 99.5% unique with silent dupes?).
   - **Embedded keys** that need parsing out of a larger string before use.
   - **Composite keys built from raw concatenation with no delimiter** (e.g. `"Sabrosura Foodsfz Sausagela Morenita"`) — collision-prone and case-sensitive; they must be rebuilt with a safe separator before any join.
   - **Trailing/leading whitespace** in string keys (`"CACIQUE " ≠ "CACIQUE"`) — silently breaks joins; requires a strip pass on every string key.

5. **Staleness.** Latest data date *in* the file vs. when it was last refreshed. A "final" transformation file can be months stale relative to the raw sources that feed it.

6. **Coverage and caveats.** What slice of the world does the file actually represent (universe coverage %, included/excluded segments, modeled vs. actual)? These become the interpretation rules the agent must respect.

## Reconstruct the triad across files

Once individual files are profiled, map the relationships:
- Which raw files feed which transformation files feed which outputs?
- Which files are **central crosswalks** that many others join through? (A geography or product mapping table everything connects to is a hard dependency — if it's missing from the share, the whole pipeline breaks.)
- Are there raw files that bypass the transformation layer and go **straight into the output** with cleanup done invisibly inside the reporting tool? If so, there is no transformation file to extract logic from — the engineer must replicate that cleanup from scratch. Find these; they are easy to miss.
- Where transformation logic lives in a tool (Power Query M, SQL views, DAX), note that it must be **extracted from the tool** before the engineer can reimplement it, and say where it lives.

## Hunt for inversions (the highest-value output)

The most valuable profiling findings are the ones that **contradict an interview assumption**, especially assumptions that turned out to mean the *opposite* of what everyone believed. Real examples from Cacique:
- A file-naming convention that everyone read as meaning vendor A actually meant vendor B.
- Files assumed to be validation-only outputs turned out to be the freshest *primary inputs*.
- Time aggregations assumed to live in the transformation files were actually computed only inside the reporting tool — so they have to be rebuilt in ETL.

Explicitly compare each major profiling finding against what the transcripts implied. Every contradiction is a flag. These feed directly into the "What surprised us" and "Requirement changes" sections of the findings export (Phase 2, Step 6).

## Output: the engineering spec document

Profiling produces one durable artifact: an engineering spec (e.g. `engineering_requirements.md`) saved to the project folder. It should contain:
- The per-file inventory (structure, grain, role, keys, staleness, caveats).
- The reconstructed triad (input → transformation → output map), with central crosswalk files flagged as dependencies.
- Required pre-build steps (extract transformation logic from tools; obtain missing files).
- Hard blockers (missing crosswalk files, missing access).
- Data rules the build must enforce (key-rebuild steps, averaging-not-summing rules, coverage caveats, default analytical lenses like YoY).

This document is the definitive build reference handed to the engineer in Phase 2, Step 7. Findings and profiling detail go here and in Linear ticket *comments* — not in ticket descriptions, which stay lean.

## Where this connects back

- The contradictions feed **Step 6 → "What surprised us"** and **"Requirement changes."**
- Missing crosswalk files and access gaps become **Urgent "missing-but-implied" tickets** in **Step 6b**.
- The spec document is the engineer's primary reference in **Step 7**.
