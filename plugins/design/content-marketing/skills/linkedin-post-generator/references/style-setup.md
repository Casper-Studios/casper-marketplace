# Style Setup Guide

This document describes the style analysis process for first-time users.

## Storage Location

Personal style profiles are stored at `~/.config/casper/linkedin-style.md` — local to each user's machine, never committed to the repo.

## Analysis Framework

When a user provides 3 sample LinkedIn posts (either as pasted text or fetched from LinkedIn URLs via the apify-scrapers skill), analyze them across these dimensions:

### Tone
- Formal vs casual spectrum
- Confident vs tentative
- Optimistic vs realistic vs contrarian
- Personal vs professional

### Structure Patterns
- Average paragraph length (sentences per paragraph)
- Use of single-sentence paragraphs
- Line break frequency
- Use of lists, bullet points, numbered items
- Overall post length (short/medium/long)

### Hook Style
- Question-led openings
- Bold statement openings
- Story/scenario openings
- Data/statistic openings
- Counterintuitive take openings

### CTA / Closing Style
- Open questions to audience
- Direct challenges or calls to action
- Reflective statements
- Forward-looking predictions
- No closing (just ends)

### Vocabulary & Phrases
- Distinctive phrases or verbal tics
- Jargon level (industry-specific vs plain language)
- Energy level (high energy vs measured)
- Use of "I" vs "we" vs "you"
- Sentence length distribution (short punchy vs flowing)

## Output Format

Save the analysis as:

```markdown
# LinkedIn Style Profile
Generated: [YYYY-MM-DD]

## Tone
[findings]

## Structure Patterns
[findings]

## Hook Style
[findings]

## CTA / Closing Style
[findings]

## Vocabulary & Phrases
[findings]

## Sample Posts

### Post 1
[original text]

### Post 2
[original text]

### Post 3
[original text]
```
