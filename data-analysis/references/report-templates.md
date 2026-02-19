# Report Templates

Two primary structures for presenting analysis findings: Pyramid Principle and Standard Consulting format. Choose based on audience and analysis type.

---

## When to Use Each Format

| Format | Best For | Audience | Analysis Type |
|--------|----------|----------|---------------|
| **Pyramid Principle** | Clear recommendations | Executives, time-constrained | Recommendation-driven |
| **Standard Consulting** | Building understanding | Stakeholders wanting context | Exploratory, discovery |

### Decision Tree

```
Is there a clear answer/recommendation?
├── YES → Pyramid Principle
│   └── Lead with the answer, support with evidence
└── NO → Standard Consulting
    └── Lead with context, build to insights
```

---

## Pyramid Principle Structure

**Core concept:** Start with the answer, then provide supporting arguments, then evidence.

### Structure

```
1. ANSWER (Governing Thought)
   └── What should we do / what happened / what's the conclusion?

2. KEY ARGUMENTS (3-5 supporting points)
   └── Why is the answer true?

3. EVIDENCE (Data supporting each argument)
   └── What data proves each argument?
```

### Template

```markdown
# [Report Title]

## Executive Summary

[1-2 sentences: The main recommendation or conclusion]

**Key Finding:** [Single most important insight]

**Recommendation:** [Clear action to take]

---

## Supporting Analysis

### 1. [First Supporting Argument]

[2-3 sentences explaining this argument]

**Evidence:**
- [Data point 1]
- [Data point 2]
- [Chart/table if needed]

### 2. [Second Supporting Argument]

[2-3 sentences explaining this argument]

**Evidence:**
- [Data point 1]
- [Data point 2]

### 3. [Third Supporting Argument]

[2-3 sentences explaining this argument]

**Evidence:**
- [Data point 1]
- [Data point 2]

---

## Implications & Next Steps

1. [Immediate action]
2. [Short-term action]
3. [Longer-term consideration]

---

## Appendix

[Detailed data, methodology, caveats]
```

### Example Headers (Pyramid)

**Bad:** "Q3 Revenue Analysis"
**Good:** "Recommend Increasing Enterprise Investment: Q3 Data Shows 40% Higher LTV"

**Bad:** "Churn Analysis Results"
**Good:** "Product Onboarding Friction Drives 60% of Churn - Fix the First Week"

---

## Standard Consulting Structure

**Core concept:** Build context, present findings, lead audience to conclusions.

### Structure

```
1. SITUATION (Context)
   └── What's the background? Why are we looking at this?

2. COMPLICATION (Problem/Opportunity)
   └── What changed? What's the challenge?

3. FINDINGS (What the data shows)
   └── Key discoveries from analysis

4. IMPLICATIONS (So what?)
   └── What does this mean for the business?

5. RECOMMENDATIONS (Now what?)
   └── Suggested actions
```

### Template

```markdown
# [Report Title]

## Background

[2-3 sentences on context: Why this analysis was conducted, what question it answers]

---

## Situation

[Current state description]
- [Relevant context point 1]
- [Relevant context point 2]
- [Key metrics baseline]

---

## Complication

[What changed or what problem emerged]
- [Trigger for analysis]
- [Magnitude of issue/opportunity]

---

## Findings

### Finding 1: [Descriptive title]

[Explanation of finding]

[Supporting data/visualization]

### Finding 2: [Descriptive title]

[Explanation of finding]

[Supporting data/visualization]

### Finding 3: [Descriptive title]

[Explanation of finding]

[Supporting data/visualization]

---

## Implications

Based on these findings:

1. **[Implication 1]** - [What this means for the business]
2. **[Implication 2]** - [What this means for the business]
3. **[Implication 3]** - [What this means for the business]

---

## Recommendations

| Priority | Action | Owner | Timeline |
|----------|--------|-------|----------|
| 1 | [Action] | [Team/Person] | [When] |
| 2 | [Action] | [Team/Person] | [When] |
| 3 | [Action] | [Team/Person] | [When] |

---

## Appendix

[Methodology, detailed data, assumptions]
```

---

## Slide Deck Structure

For executive presentations, use a maximum of 5-7 slides.

### Standard Deck Template

| Slide | Content | Max Words |
|-------|---------|-----------|
| 1. Title | Title, date, author | 15 |
| 2. Executive Summary | Key finding + recommendation | 50 |
| 3-5. Supporting Points | One key argument per slide with visual | 30 each |
| 6. Implications/Next Steps | What this means, what to do | 50 |
| 7. Appendix (if needed) | Detailed backup | Variable |

### Key Message Per Slide

Every slide needs a **headline that makes a claim**, not just a topic.

**Bad:** "Q3 Revenue by Segment"
**Good:** "Enterprise Segment Grew 45% While SMB Declined 12%"

**Bad:** "Churn Analysis"
**Good:** "First-Week Onboarding Issues Drive 60% of Churn"

### python-pptx Code Patterns

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN

def create_title_slide(prs, title, subtitle):
    """Create title slide."""
    slide_layout = prs.slide_layouts[0]  # Title slide layout
    slide = prs.slides.add_slide(slide_layout)

    title_shape = slide.shapes.title
    subtitle_shape = slide.placeholders[1]

    title_shape.text = title
    subtitle_shape.text = subtitle

    return slide

def create_content_slide(prs, headline, bullets):
    """Create content slide with headline and bullets."""
    slide_layout = prs.slide_layouts[1]  # Title and content layout
    slide = prs.slides.add_slide(slide_layout)

    title_shape = slide.shapes.title
    body_shape = slide.placeholders[1]

    title_shape.text = headline

    tf = body_shape.text_frame
    for i, bullet in enumerate(bullets):
        if i == 0:
            tf.text = bullet
        else:
            p = tf.add_paragraph()
            p.text = bullet
            p.level = 0

    return slide

def add_chart_to_slide(slide, fig, left, top, width, height):
    """Add matplotlib figure to slide."""
    import io

    # Save figure to bytes
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png', dpi=150, bbox_inches='tight')
    img_stream.seek(0)

    # Add to slide
    slide.shapes.add_picture(
        img_stream,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height)
    )
```

---

## Transition Phrases

### For Pyramid Principle

| Purpose | Phrases |
|---------|---------|
| Introduce recommendation | "We recommend...", "The data supports...", "Our analysis indicates..." |
| Introduce supporting point | "This is supported by...", "Evidence shows...", "Three factors drive this:" |
| Connect evidence | "Specifically,", "For example,", "The data shows..." |

### For Consulting Structure

| Purpose | Phrases |
|---------|---------|
| Set context | "Over the past quarter...", "Given the current...", "In the context of..." |
| Introduce complication | "However,", "Recently,", "The challenge is...", "What's changed is..." |
| Present findings | "Our analysis revealed...", "The data shows...", "We observed..." |
| Draw implications | "This means...", "The implication is...", "As a result..." |
| Make recommendations | "We suggest...", "The path forward is...", "Our recommendation is..." |

---

## Client vs Internal Terminology

When preparing deliverables for external stakeholders, translate internal process language to client-friendly alternatives.

### Terminology Translation Table

| Internal Term | Client-Friendly Alternative |
|--------------|----------------------------|
| "Data Quality Validation Results" | "Data Quality & Limitations" |
| "Data Quality Validation" | "Validation Checks" |
| "Sanity Checks" | "Verification Steps" |
| "Smell Test" | "Reasonableness Check" |
| Internal methodology names | Omit entirely |
| Tool/script names | Omit or generalize ("our analysis pipeline") |

### Key Principles

**1. Keep domain terminology the client uses:**
- If client talks about "Skill vs Luck" analysis, use that language
- Match their metric names (ARR, NRR, MRR as they define them)
- Use their segment names and internal jargon

**2. Remove internal process labels:**
- Don't include methodology section headers like "Phase 5: Interpretation"
- Don't reference internal tools by name
- Don't mention "ran the bias checklist"—just apply it and state the caveats

**3. Consolidate caveats:**
- Put all limitations in a dedicated "Limitations" or "Data Quality" section
- Don't scatter warning boxes throughout the document
- Lead with findings, follow with caveats in one place

**4. Add "What This Means" translations:**
- Every technical finding needs a plain-language interpretation
- Don't assume statistical literacy—translate significance to business impact
- Use concrete examples and analogies

### Example Transformation

**Internal Version:**
```
## Data Quality Validation Results

Ran the survivorship bias check. 29% of reps excluded due to
incomplete data. Simpson's paradox detected in segment analysis.
```

**Client Version:**
```
## Data Quality & Limitations

**Coverage:** This analysis includes 71% of the sales team (32 of 45 reps).
Thirteen reps were excluded due to incomplete data from territory changes
or recent hiring.

**Segment Note:** While overall team performance declined, the Enterprise
and SMB segments individually showed growth. This reflects shifting
headcount allocation rather than contradictory trends.

**What This Means:** Conclusions are most reliable for tenured reps in
stable territories. Findings about newer reps should be treated as
directional only.
```

---

## Caveats and Hedging

Always include appropriate caveats. Use this language:

### Confidence Levels

| Confidence | Language |
|------------|----------|
| High | "The data clearly shows...", "We are confident that..." |
| Medium | "The data suggests...", "This indicates...", "Evidence points to..." |
| Low | "Preliminary analysis suggests...", "Directionally, we see...", "This may indicate..." |

### Sample Size Hedges

- "Based on n=X observations..."
- "While sample size is limited..."
- "With the caveat that this is based on [X] data points..."

### Data Quality Hedges

- "Using [proxy] as an approximation for [ideal data]..."
- "Note: This analysis excludes [what's missing]..."
- "Data quality limitations include..."

---

## Report Checklist

Before finalizing any report:

- [ ] **Clear headline** - Main message in first sentence
- [ ] **Action-oriented** - Clear what to do with findings
- [ ] **Evidence-backed** - Every claim has supporting data
- [ ] **Appropriately hedged** - Confidence levels stated
- [ ] **Bias-checked** - Ran through bias checklist
- [ ] **Data wishlist** - Documented what's missing
- [ ] **Audience-appropriate** - Detail level matches reader
