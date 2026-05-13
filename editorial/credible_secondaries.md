# Credible secondary sources — allowlist

A credible secondary source is an outlet whose institutional incentives —
legal liability, established editorial process, government accountability,
or domain expertise tied to reputation — make it likely to reproduce a
primary source accurately. We rely on these only when the primary itself
is unreachable (a WAF-protected PDF, a JavaScript-rendered page, a
licensed feed); when the primary is reachable, the primary is the source.

A claim is **triangulated** when at least two independent credible
secondaries reproduce the same number or wording, with consistent
context. Independent means different institutional affiliations and
different incentive structures — a Reuters story republished across ten
outlets is one secondary, not ten.

## What counts as credible

### Canadian government secondary

- Parliamentary Budget Officer (PBO) reports and briefings
- Library of Parliament research publications
- Department of Finance Canada press releases and backgrounders
- Office of the Superintendent of Financial Institutions (OSFI) advisories and bulletins
- Bank of Canada press releases (when not themselves the primary)
- Statistics Canada methodological documents, "The Daily" releases,
  and Economic and Social Reports (when reproducing or contextualizing
  a primary table)

### Foreign-government secondary

- Congressional Research Service (CRS) reports
- US Treasury and Treasury Department press releases
- US Federal Reserve communications (when not themselves the primary)
- Office of the United States Trade Representative (USTR) press materials
- US Government Accountability Office (GAO) reports
- Bank for International Settlements (BIS) publications

### Tier-1 financial / business press

Outlets whose business is accurate reproduction of news, with established
editorial standards and correction protocols:

- Reuters
- Bloomberg
- Financial Times
- Wall Street Journal
- Globe and Mail (business section)
- Financial Post (Postmedia)
- The Logic (Canadian tech/business)
- La Presse (business section, French-language)
- Toronto Star (business reporting only)
- The Economist

### Domain-expert professional services

These outlets quote primary sources under liability discipline — they
have a contractual and reputational stake in accurate reproduction.
Citable only when reproducing fact, not when offering opinion or
analysis:

- Big-Four audit firms (Deloitte, EY, KPMG, PwC) — for tax / regulatory
  / accounting standards reproduction
- Top-tier Canadian law firms — for legal / regulatory primaries:
  Stikeman Elliott, Osler Hoskin & Harcourt, McCarthy Tétrault,
  Blakes (Blake Cassels & Graydon), Norton Rose Fulbright Canada,
  Torys, Goodmans, Bennett Jones, MLT Aikins
- Global immigration law firms — for immigration policy reproduction:
  Fragomen, Berry Appleman & Leiden, BAL Canada
- Specialty regulatory boutiques when on-topic (Cassels Brock for
  cannabis, McMillan for trade, etc.)

### Established trade press

Domain-specific outlets with subject-matter editorial discipline:

- Canadian Mortgage Trends (mortgage / housing finance)
- CIC News (immigration policy)
- Mortgage Professionals Canada releases
- Mining.com (mining / commodities)
- The Logic (tech, when reproducing factual filings)
- Government-contract trade press for procurement matters

### Academic and archive mirrors

- BIS Review (mirrors central bank speeches with verbatim text)
- National Bureau of Economic Research (NBER) Working Papers
- Social Science Research Network (SSRN) preprints
- IMF Data Portal and Working Papers
- OECD Data Portal and Working Papers
- Federal Reserve Economic Data (FRED) for series metadata
- St. Louis Fed FRASER archive for historical Federal Reserve documents
- Wikidata / OpenAlex for entity-level academic citations (not factual
  claims about current data)

## What does NOT count

The following are NOT credible secondary sources for fact reproduction:

### Bank economics desks

**Bank economics desks are competitors, not fact-reproducers.** Sibley
Creek is an independent macro research provider. Citing a bank desk's
reproduction of a BoC press release or a StatCan table number adds
nothing — the primary is the same, and citing the desk implies an
authority we should not lend competitors.

This rule covers:

- RBC Economics, BMO Capital Markets / Economics, TD Economics,
  Scotiabank Economics, CIBC Economics, National Bank Economics
- Capital Economics, Oxford Economics, Pantheon Macroeconomics,
  BCA Research, Empire State Manufacturing index economists
- Independent macro shops with peer competitive positioning
  (BCA, Variant Perception, Bridgewater Daily Observations, etc.)

Bank desks may appear in two narrow modes documented in
`editorial/writing-style.md` §8c:

- **Consensus framing**: aggregated across multiple desks as a range or
  median; no single desk named as authority. This is reproduction of
  the *consensus*, not citation of any one source.
- **Analysis citation (Mode 3)**: when a bank desk has published
  something genuinely unique that becomes the subject of discussion
  ("CIBC has argued that StatCan undercounted the population"). Always
  framed as a claim made by them, never as fact. Requires explicit
  user approval before shipping (see writing-style.md §8c and
  review_protocol.md).

### Wikipedia for current data

Wikipedia may be cited for historical or stabilized facts (multi-decade
context) but is not credible for current data — anyone can edit, and
even good Wikipedia editors are reproducing themselves from secondary
sources, not the primary.

### Search-result snippets without an identified institutional source

If a search engine returns a quote-looking excerpt but the source page
itself can't be identified or reached, the excerpt is not a citation.

### AI-generated summaries

News summarization tools (AI-driven aggregators, automated newsletter
digests) are not citable. The chain of accuracy depends on an
identifiable human editorial process.

### Blog posts and substacks without editorial review

Single-author commentary blogs and substack newsletters — including
those run by reputable analysts — are not credible secondaries for fact
reproduction. They may occasionally surface in Mode 3 (analysis
citation) when the analyst's claim itself is the news, with explicit
user approval.

### Social media

X / Twitter / LinkedIn / Bluesky posts are not credible secondaries.

### Self-citations

Sibley Creek does not cite its own past work as a credible secondary
for a new claim. Past pieces may be linked for reader context, but the
fact must still trace to a primary or independently triangulated
external source.

## How to use this list

When drafting a card whose primary is unreachable:

1. Find at least one credible secondary from the allowlist above that
   reproduces the claim verbatim or near-verbatim. For numeric or
   dated facts, two are required.
2. Capture the secondary's URL, the verbatim excerpt, and a one-line
   credibility statement (which category from this list it falls in,
   why it's credible for this claim).
3. Note in the card whether the primary URL is publicly reachable in a
   browser even when WebFetch can't reach it (a frequent case — WAF
   rules block bots but not human users); this affects how easy the
   user-verification step is.
4. The card lands in `editorial/source_cards/_pending/` and awaits user
   approval. See `editorial/review_protocol.md` for the full workflow.

## Maintenance

This list evolves with the publication. New credible outlets are added
by the editorial-director when they earn the trust through repeated
accurate reproduction; outlets are removed when their editorial
standards visibly slip. Changes to this file should be discussed before
landing.

Last reviewed: 2026-05-13.
