# Company Research Playbook

How to efficiently research companies for ICP matching using web search.

## Search Strategy

### Batch by Company, Not by Contact

If your contact list has 200 people across 80 companies, you need 80 searches — not 200.
Deduplicate companies first, research each once, then apply the results to all contacts at
that company.

### Search Query Templates

For each company, run targeted searches. Here are the queries that tend to yield the best results:

**Revenue / Size:**
- `"[Company Name]" revenue 2025` or `"[Company Name]" annual revenue`
- `"[Company Name]" AUM` (for financial firms)
- `"[Company Name]" employees OR headcount`

**Industry Classification:**
- `"[Company Name]" industry OR sector site:linkedin.com` (LinkedIn company pages are reliable)
- `"[Company Name]" what does [company] do`

**Tier / Rankings:**
- `"[Company Name]" Fortune 500 OR Fortune 1000 OR Fortune 2000`
- `"[Company Name]" Inc 5000 OR "fastest growing"`

**AI Signals (optional, for enrichment):**
- `"[Company Name]" artificial intelligence OR "AI initiative" OR "machine learning"`
- `"[Company Name]" hiring AI OR "head of AI" site:linkedin.com`

### Handling Edge Cases

**Subsidiaries:** If someone works at "AWS" but the parent is Amazon, research Amazon for
size/tier but note the subsidiary. The contact's relevance depends on whether they work in
a division relevant to the ICP.

**Name collisions:** "Mercury" could be a fintech, a car brand, or a NASA program. Use the
person's title and LinkedIn context to disambiguate. If the CSV has a LinkedIn URL column, that's
the fastest way to resolve.

**Recently acquired companies:** If a company was acquired, note this. The contact might still
list the old company name on LinkedIn. Research both the old company and the acquirer.

**Private companies:** Revenue data is harder to find. Look for:
- Funding announcements (Crunchbase-style: "raised $X Series Y" → infer rough valuation)
- Employee count on LinkedIn (useful proxy for company size)
- Industry reports or press coverage mentioning revenue ranges
- Job postings volume (proxy for growth)

If you truly can't find sizing data, classify as "insufficient data" and include the contact
anyway with a note. The user may have direct knowledge.

## Research Confidence Levels

Tag each company with a confidence level:

- **High** — Revenue/AUM from a reliable source (SEC filings, Fortune list, major publication).
  Industry clearly categorized.
- **Medium** — Revenue estimated from funding, headcount, or secondary sources. Industry is clear
  but size is approximate.
- **Low** — Minimal public data. Industry inferred from job titles or vague descriptions.
  Size unknown.
- **Unverified** — Couldn't find the company or results are ambiguous. Don't guess.

## Efficiency Tips

- Process the top 30-50 companies first (by how many contacts you have there), then ask the user
  if they want you to continue with the long tail of companies that have only 1 contact each.
- If the user gave a strict company tier requirement (e.g., "Fortune 2000 only"), you can
  pre-filter: search the Fortune list first, drop companies not on it, and save yourself from
  researching irrelevant companies.
- Cache results mentally — if three people work at Goldman Sachs, don't search Goldman Sachs
  three times.
